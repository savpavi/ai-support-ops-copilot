#!/usr/bin/env python3
"""Draft a reply for each reply-safety case and record what the guard did.

The reply dataset measures drafts, not classification assertions, so it does
not fit `evaluate_cases`. This script runs the drafted-reply path over
`fixtures/reply_safety_cases.json` and writes every draft together with the
deterministic guard's verdict, so that the drafts which survived the guard can
be read one by one. A guard pass rate on its own would only measure the floor,
not what got past it.

Requires OPENROUTER_API_KEY. Sends only the committed synthetic fixtures.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from support_copilot.classifier import validate_output  # noqa: E402
from support_copilot.llm_classifier import (  # noqa: E402
    USAGE,
    LLMClassifierError,
    REPLY_EVENTS,
    analyze_request_openrouter,
    openrouter_available,
    reset_reply_events,
    reset_usage,
)

CASES = ROOT / "fixtures" / "reply_safety_cases.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="append", required=True, help="repeatable OpenRouter model id")
    parser.add_argument("--out", default=str(ROOT / "docs" / "reply-safety-results.json"))
    parser.add_argument("--generated", required=True, help="ISO date stamp for the snapshot")
    args = parser.parse_args()

    if not openrouter_available():
        print("set OPENROUTER_API_KEY", file=sys.stderr)
        return 2

    cases = json.loads(CASES.read_text(encoding="utf-8"))
    runs: dict[str, dict] = {}

    for model in args.model:
        reset_usage()
        records = []
        for case in cases:
            reset_reply_events()
            record = {"case_id": case["case_id"], "expectation": case["reply_expectation"]}
            try:
                result = analyze_request_openrouter(
                    case["input"], model=model, drafted_replies=True
                )
                validate_output(result)
            except LLMClassifierError as error:
                record["error"] = str(error)
                records.append(record)
                continue
            event = REPLY_EVENTS[-1] if REPLY_EVENTS else None
            record["draft"] = event["draft"] if event else None
            record["guard_accepted"] = bool(event and event["accepted"])
            record["guard_errors"] = event["errors"] if event else ["no draft returned"]
            record["reply_used"] = result["suggested_reply"]
            records.append(record)

        drafts = [r for r in records if "draft" in r]
        runs[model] = {
            "usage": dict(USAGE),
            "cases": len(cases),
            "drafts_produced": len(drafts),
            "guard_accepted": sum(1 for r in drafts if r["guard_accepted"]),
            "guard_rejected": sum(1 for r in drafts if not r["guard_accepted"]),
            "records": records,
        }
        print(
            f"{model}: {runs[model]['guard_accepted']}/{len(drafts)} drafts accepted by the guard",
            file=sys.stderr,
        )

    Path(args.out).write_text(
        json.dumps(
            {
                "generated": args.generated,
                "note": (
                    "Dated snapshot, not reproducible: model outputs vary. Guard acceptance is a "
                    "deterministic floor; every accepted draft still requires human reading, which "
                    "is recorded separately in docs/14-reply-safety.md."
                ),
                "provider": "openrouter",
                "runs": runs,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
