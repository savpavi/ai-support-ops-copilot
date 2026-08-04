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

DEFAULT_DATASET = ROOT / "fixtures" / "evaluation_cases.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate synthetic support requests locally.")
    parser.add_argument("dataset", nargs="?", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()

    try:
        cases = json.loads(args.dataset.read_text(encoding="utf-8"))
        report = evaluate_cases(cases)
    except (OSError, json.JSONDecodeError, RuntimeError, ValueError) as error:
        print(f"evaluation failed: {error}", file=sys.stderr)
        return 2

    if args.format == "json":
        sys.stdout.write(render_json_report(report))
    else:
        sys.stdout.write(render_markdown_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
