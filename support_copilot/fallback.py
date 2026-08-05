"""Baseline fallback: make the LLM path safe for a caller to depend on.

The LLM classifier fails closed by raising `LLMClassifierError` whenever it
cannot produce a contract-safe result. That is the right behavior for a
component and the wrong behavior for a caller, which still needs an answer.
This wrapper turns any analyzer into one that always returns a contract-valid
result, degrading to the deterministic baseline when the LLM path cannot
deliver.

Three failure modes are covered: the typed error, an unexpected exception, and
a provider that neither succeeds nor fails within a time budget. The last one
matters because the OpenRouter transport retries three times at a 180-second
timeout, so a hung provider would otherwise take about nine minutes to surface
an error. The budget is enforced from outside the attempt, leaving the
transport's own retry ladder untouched for direct callers.

The wrapper restores availability, not accuracy. A fallback result is exactly
what the keyword baseline would have produced, including the paraphrased
security solicitations the baseline is measured as missing. It can never carry
fewer security flags than the baseline, because it is the baseline.

Provenance travels beside the result, never inside it: `validate_output`
requires the contract's exact field set, so an added `engine` field would mean
leaving schema version 1.0 and breaking the byte-identical workflow artifact.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable

from .classifier import analyze_request, validate_input, validate_output
from .llm_classifier import LLMClassifierError

DEFAULT_BUDGET_SECONDS = 20.0

#: One record per wrapped call, in call order. Mirrors `llm_classifier.USAGE`.
PROVENANCE: list[dict[str, Any]] = []


def reset_provenance() -> None:
    """Clear the recorded provenance, for a fresh evaluation run."""

    PROVENANCE.clear()


def last_provenance() -> dict[str, Any] | None:
    """The provenance of the most recent wrapped call, or None."""

    return PROVENANCE[-1] if PROVENANCE else None


def _record(engine: str, fallback: bool, reason: str | None, elapsed: float) -> None:
    PROVENANCE.append(
        {
            "engine": engine,
            "fallback": fallback,
            "reason": reason,
            "elapsed_seconds": round(elapsed, 3),
        }
    )


def _call_within(analyzer: Callable[[Any], Any], value: Any, budget: float) -> tuple[str, Any]:
    """Run analyzer with a wall-clock ceiling.

    Returns ("ok", result), ("error", exception) or ("timeout", None). The
    worker is a daemon thread so an abandoned call cannot delay interpreter
    exit; it may still finish later, and anything it records (token usage, for
    instance) belongs to a result nobody reads.
    """

    box: dict[str, Any] = {}

    def run() -> None:
        try:
            box["result"] = analyzer(value)
        except BaseException as error:  # noqa: BLE001 - re-raised on the calling side
            box["error"] = error

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(budget)
    if worker.is_alive():
        return "timeout", None
    if "error" in box:
        return "error", box["error"]
    return "ok", box.get("result")


def with_baseline_fallback(
    analyzer: Callable[[Any], Any],
    *,
    budget_seconds: float = DEFAULT_BUDGET_SECONDS,
    baseline: Callable[[Any], Any] = analyze_request,
) -> Callable[[Any], dict[str, Any]]:
    """Wrap an analyzer so it always returns a contract-valid result.

    The returned callable keeps the one-argument analyzer signature, so it
    drops into `evaluate_cases(analyzer=...)` and anywhere else an analyzer is
    accepted. Provenance for each call is appended to `PROVENANCE`.
    """

    if budget_seconds <= 0:
        raise ValueError("budget_seconds must be positive")

    def wrapped(value: Any) -> dict[str, Any]:
        started = time.monotonic()

        # Input rejection is a verdict, not a failure: the deterministic path
        # owns it, no tokens are spent, and it is not counted as a fallback.
        if validate_input(value):
            result = baseline(value)
            validate_output(result)
            _record("baseline", False, "input_rejected", time.monotonic() - started)
            return result

        outcome, payload = _call_within(analyzer, value, budget_seconds)
        if outcome == "ok":
            try:
                validate_output(payload)
            except (ValueError, TypeError) as error:
                reason = f"contract_violation: {error}"
            else:
                _record("llm", False, None, time.monotonic() - started)
                return payload
        elif outcome == "timeout":
            reason = f"timeout after {budget_seconds:g}s"
        else:
            reason = (
                f"llm_error: {payload}"
                if isinstance(payload, LLMClassifierError)
                else f"unexpected {type(payload).__name__}: {payload}"
            )

        result = baseline(value)
        validate_output(result)
        _record("baseline", True, reason, time.monotonic() - started)
        return result

    return wrapped
