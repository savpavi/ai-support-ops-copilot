"""Check or regenerate the committed workflow Code-node JavaScript from source.

`--check` (the default) exits with status 1 when the committed workflow JSON
differs from what `n8n/src/` templates plus `support_copilot/rules.json`
generate. `--write` regenerates the committed artifact in place.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from support_copilot.rules import load_rules, validate_rules
from support_copilot.workflow_build import WORKFLOW_PATH, generate_workflow_text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate the committed workflow JSON instead of checking it",
    )
    args = parser.parse_args()

    errors = validate_rules(load_rules())
    if errors:
        print("invalid rules.json:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    generated = generate_workflow_text()
    committed = WORKFLOW_PATH.read_text(encoding="utf-8")
    if args.write:
        if generated == committed:
            print("workflow JSON already matches its sources")
        else:
            WORKFLOW_PATH.write_text(generated, encoding="utf-8")
            print("workflow JSON regenerated from sources")
        return 0
    if generated != committed:
        print(
            "workflow JSON differs from its sources; run scripts/build_workflow.py --write",
            file=sys.stderr,
        )
        return 1
    print("workflow JSON matches its sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
