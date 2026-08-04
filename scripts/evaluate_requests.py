#!/usr/bin/env python3
"""Run the local synthetic evaluation without network or external systems."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from support_copilot import evaluate_cases, render_json_report, render_markdown_report
from support_copilot.evaluation import PARAPHRASE_VALIDATION

DATASETS = {
    "aligned": (ROOT / "fixtures" / "evaluation_cases.json", None),
    "paraphrase": (ROOT / "fixtures" / "paraphrase_cases.json", PARAPHRASE_VALIDATION),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate synthetic support requests locally.")
    parser.add_argument(
        "--dataset",
        choices=sorted(DATASETS),
        default="aligned",
        help="aligned: Task 003 implementation-aligned assertions; paraphrase: Task 006 semantic out-of-distribution assertions",
    )
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument(
        "--classifier",
        choices=("baseline", "llm"),
        default="baseline",
        help="baseline: deterministic keyword rules; llm: the optional Claude classifier (requires the anthropic SDK and ANTHROPIC_API_KEY)",
    )
    args = parser.parse_args()

    dataset_path, validation = DATASETS[args.dataset]
    engine: dict | None = None
    try:
        cases = json.loads(dataset_path.read_text(encoding="utf-8"))
        if args.classifier == "llm":
            from support_copilot.llm_classifier import (
                LLM_MODEL,
                USAGE,
                analyze_request_llm,
                is_available,
                reset_usage,
            )

            if not is_available():
                print(
                    "llm classifier unavailable: install the anthropic SDK and set ANTHROPIC_API_KEY",
                    file=sys.stderr,
                )
                return 2
            reset_usage()
            report = evaluate_cases(
                cases,
                validation=validation,
                analyzer=analyze_request_llm,
                include_parity=False,
            )
            engine = {"classifier": "llm", "model": LLM_MODEL, "usage": dict(USAGE)}
        else:
            report = evaluate_cases(cases, validation=validation)
    except (OSError, json.JSONDecodeError, RuntimeError, ValueError) as error:
        print(f"evaluation failed: {error}", file=sys.stderr)
        return 2

    if args.format == "json":
        if engine is not None:
            sys.stdout.write(json.dumps({"engine": engine, "report": report}, indent=2, sort_keys=True) + "\n")
        else:
            sys.stdout.write(render_json_report(report))
    else:
        sys.stdout.write(render_markdown_report(report))
        if engine is not None:
            usage = engine["usage"]
            sys.stdout.write(
                "\n## Engine\n\n"
                f"- Classifier: llm ({engine['model']})\n"
                f"- Requests: {int(usage['requests'])}\n"
                f"- Tokens: {int(usage['input_tokens'])} in / {int(usage['output_tokens'])} out\n"
                f"- Total model latency: {usage['latency_seconds']:.1f}s\n"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
