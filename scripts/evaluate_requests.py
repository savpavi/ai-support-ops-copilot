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
        help="baseline: deterministic keyword rules; llm: an LLM classifier behind the same contract",
    )
    parser.add_argument(
        "--provider",
        choices=("anthropic", "openrouter"),
        default="anthropic",
        help="llm only: anthropic (ANTHROPIC_API_KEY + anthropic SDK) or openrouter (OPENROUTER_API_KEY, standard library)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="llm only: model id; defaults to claude-haiku-4-5 (anthropic) or anthropic/claude-haiku-4.5 (openrouter)",
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
                make_openrouter_analyzer,
                openrouter_available,
                reset_usage,
            )

            if args.provider == "openrouter":
                if not openrouter_available():
                    print("llm classifier unavailable: set OPENROUTER_API_KEY", file=sys.stderr)
                    return 2
                model = args.model or "anthropic/claude-haiku-4.5"
                analyzer = make_openrouter_analyzer(model)
            else:
                if not is_available():
                    print(
                        "llm classifier unavailable: install the anthropic SDK and set ANTHROPIC_API_KEY",
                        file=sys.stderr,
                    )
                    return 2
                model = LLM_MODEL
                if args.model and args.model != LLM_MODEL:
                    print(
                        f"note: the anthropic provider is pinned to {LLM_MODEL}; ignoring --model",
                        file=sys.stderr,
                    )
                analyzer = analyze_request_llm
            reset_usage()
            report = evaluate_cases(
                cases,
                validation=validation,
                analyzer=analyzer,
                include_parity=False,
            )
            engine = {
                "classifier": "llm",
                "provider": args.provider,
                "model": model,
                "usage": dict(USAGE),
            }
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
