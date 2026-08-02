#!/usr/bin/env python3
"""Analyze one JSON request from a file or standard input."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from support_copilot import analyze_request  # noqa: E402


def _load_input(path: str | None) -> Any:
    try:
        if path:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        return json.load(sys.stdin)
    except (OSError, json.JSONDecodeError) as exc:
        return {"request_id": None, "message": None, "_parse_error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify one synthetic support request.")
    parser.add_argument("path", nargs="?", help="JSON file; omit to read JSON from standard input")
    args = parser.parse_args()
    result = analyze_request(_load_input(args.path))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result["status"] == "accepted" else 2


if __name__ == "__main__":
    raise SystemExit(main())
