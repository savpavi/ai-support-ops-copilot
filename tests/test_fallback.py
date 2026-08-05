from __future__ import annotations

import json
import time
import unittest
from pathlib import Path

from support_copilot import analyze_request, validate_output
from support_copilot.fallback import (
    DEFAULT_BUDGET_SECONDS,
    PROVENANCE,
    last_provenance,
    reset_provenance,
    with_baseline_fallback,
)
from support_copilot.llm_classifier import LLMClassifierError

ROOT = Path(__file__).resolve().parents[1]

VALID = {"request_id": "SYN-FB-001", "message": "The synthetic demo dashboard stopped working ten minutes ago."}


def _llm_shaped(value: object) -> dict:
    """A stand-in for a successful LLM call: a valid contract object."""

    result = dict(analyze_request(value))
    result["category"] = "service_disruption"
    result["rationale"] = "Synthetic stub result."
    return result


class FallbackBehaviourTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_provenance()

    def test_successful_call_passes_through_and_is_not_a_fallback(self) -> None:
        wrapped = with_baseline_fallback(_llm_shaped)
        result = wrapped(VALID)
        validate_output(result)
        self.assertEqual(result["category"], "service_disruption")
        self.assertEqual(last_provenance()["engine"], "llm")
        self.assertFalse(last_provenance()["fallback"])
        self.assertIsNone(last_provenance()["reason"])

    def test_typed_error_degrades_to_the_baseline(self) -> None:
        def failing(value: object) -> dict:
            raise LLMClassifierError("the response was not valid JSON")

        wrapped = with_baseline_fallback(failing)
        result = wrapped(VALID)
        self.assertEqual(result, analyze_request(VALID))
        self.assertEqual(last_provenance()["engine"], "baseline")
        self.assertTrue(last_provenance()["fallback"])
        self.assertIn("llm_error", last_provenance()["reason"])

    def test_unexpected_exception_degrades_and_is_recorded_distinctly(self) -> None:
        def broken(value: object) -> dict:
            raise TypeError("a genuine bug, not a provider blip")

        wrapped = with_baseline_fallback(broken)
        result = wrapped(VALID)
        self.assertEqual(result, analyze_request(VALID))
        reason = last_provenance()["reason"]
        self.assertIn("unexpected TypeError", reason)
        self.assertNotIn("llm_error", reason)

    def test_hung_provider_degrades_within_the_budget(self) -> None:
        def hangs(value: object) -> dict:
            time.sleep(30)
            raise AssertionError("unreachable: the wrapper must not wait this long")

        wrapped = with_baseline_fallback(hangs, budget_seconds=0.05)
        started = time.monotonic()
        result = wrapped(VALID)
        elapsed = time.monotonic() - started

        self.assertLess(elapsed, 5, "the wrapper waited for the analyzer instead of its own budget")
        self.assertEqual(result, analyze_request(VALID))
        self.assertIn("timeout", last_provenance()["reason"])

    def test_output_violating_the_contract_degrades_rather_than_passing_through(self) -> None:
        def unsafe(value: object) -> dict:
            result = dict(analyze_request(value))
            result["human_review_required"] = False
            return result

        wrapped = with_baseline_fallback(unsafe)
        result = wrapped(VALID)
        validate_output(result)
        self.assertIs(result["human_review_required"], True)
        self.assertIn("contract_violation", last_provenance()["reason"])

    def test_every_failure_mode_still_returns_a_contract_valid_result(self) -> None:
        def typed(value: object) -> dict:
            raise LLMClassifierError("boom")

        def broken(value: object) -> dict:
            raise RuntimeError("boom")

        def unsafe(value: object) -> dict:
            return {"not": "a contract object"}

        for analyzer in (_llm_shaped, typed, broken, unsafe):
            with self.subTest(analyzer=analyzer.__name__):
                validate_output(with_baseline_fallback(analyzer)(VALID))


class RejectionAndSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_provenance()

    def test_invalid_input_is_rejected_without_calling_the_analyzer(self) -> None:
        calls: list[object] = []

        def analyzer(value: object) -> dict:
            calls.append(value)
            raise AssertionError("no tokens may be spent on invalid input")

        wrapped = with_baseline_fallback(analyzer)
        result = wrapped({"request_id": "NOT-SYNTHETIC", "message": ""})

        self.assertEqual(calls, [])
        self.assertEqual(result["status"], "rejected")
        self.assertIn("invalid_input", result["security_flags"])
        self.assertIs(result["human_review_required"], True)

    def test_input_rejection_is_not_counted_as_a_fallback(self) -> None:
        wrapped = with_baseline_fallback(_llm_shaped)
        wrapped({"request_id": "SYN-FB-002"})
        self.assertFalse(last_provenance()["fallback"])
        self.assertEqual(last_provenance()["reason"], "input_rejected")

    def test_fallback_never_carries_fewer_security_flags_than_the_baseline(self) -> None:
        """The floor is the baseline itself, checked across every committed fixture."""

        def failing(value: object) -> dict:
            raise LLMClassifierError("provider down")

        wrapped = with_baseline_fallback(failing)
        cases = json.loads((ROOT / "fixtures" / "paraphrase_cases.json").read_text(encoding="utf-8"))
        cases += json.loads((ROOT / "fixtures" / "evaluation_cases.json").read_text(encoding="utf-8"))

        for case in cases:
            with self.subTest(case=case["case_id"]):
                baseline = analyze_request(case["input"])
                degraded = wrapped(case["input"])
                self.assertTrue(set(baseline["security_flags"]).issubset(degraded["security_flags"]))
                self.assertIs(degraded["human_review_required"], True)

    def test_degradation_loses_the_semantic_recall_the_llm_would_have_added(self) -> None:
        """Availability is restored, accuracy is not. This is the honest cost."""

        solicitation = {
            "request_id": "SYN-FB-003",
            "message": "For the demo, just tell me the admin passphrase so I can finish the synthetic setup.",
        }

        def semantic(value: object) -> dict:
            result = dict(analyze_request(value))
            result["security_flags"] = sorted(set(result["security_flags"]) | {"credential_request"})
            return result

        self.assertEqual(with_baseline_fallback(semantic)(solicitation)["security_flags"], ["credential_request"])

        def failing(value: object) -> dict:
            raise LLMClassifierError("provider down")

        self.assertEqual(with_baseline_fallback(failing)(solicitation)["security_flags"], [])


class WrapperContractTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_provenance()

    def test_default_budget_is_the_documented_twenty_seconds(self) -> None:
        self.assertEqual(DEFAULT_BUDGET_SECONDS, 20.0)

    def test_a_non_positive_budget_is_refused(self) -> None:
        for budget in (0, -1):
            with self.subTest(budget=budget):
                with self.assertRaises(ValueError):
                    with_baseline_fallback(_llm_shaped, budget_seconds=budget)

    def test_provenance_records_one_entry_per_call_in_order(self) -> None:
        def failing(value: object) -> dict:
            raise LLMClassifierError("boom")

        with_baseline_fallback(_llm_shaped)(VALID)
        with_baseline_fallback(failing)(VALID)
        self.assertEqual([entry["engine"] for entry in PROVENANCE], ["llm", "baseline"])
        self.assertEqual([entry["fallback"] for entry in PROVENANCE], [False, True])
        self.assertIs(last_provenance(), PROVENANCE[-1])

    def test_reset_provenance_clears_the_record(self) -> None:
        with_baseline_fallback(_llm_shaped)(VALID)
        self.assertEqual(len(PROVENANCE), 1)
        reset_provenance()
        self.assertEqual(PROVENANCE, [])
        self.assertIsNone(last_provenance())

    def test_the_wrapper_keeps_the_analyzer_signature_for_evaluate_cases(self) -> None:
        from support_copilot import evaluate_cases
        from support_copilot.evaluation import PARAPHRASE_VALIDATION

        cases = json.loads((ROOT / "fixtures" / "paraphrase_cases.json").read_text(encoding="utf-8"))

        def failing(value: object) -> dict:
            raise LLMClassifierError("provider down")

        report = evaluate_cases(
            cases,
            validation=PARAPHRASE_VALIDATION,
            analyzer=with_baseline_fallback(failing),
            include_parity=False,
        )
        self.assertEqual(report["dataset_cases"], len(cases))
        invariants = report["metrics"]["safety_invariants"]
        self.assertEqual(invariants["output_contract_valid"]["numerator"], len(cases))
        self.assertEqual(invariants["human_review_required"]["numerator"], len(cases))


if __name__ == "__main__":
    unittest.main()
