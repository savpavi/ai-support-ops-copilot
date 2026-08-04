# Task 005: Single-Source Rule Data for Python and Workflow JavaScript

## Status

- **State:** complete — 2026-08-04. All acceptance criteria verified: 44 tests pass, `scripts/build_workflow.py --check` passes, and the generated workflow JSON is byte-identical to the natively verified Task 004 artifact.
- **Approved scope:** eliminate the duplicated rule data between the Python baseline and the committed workflow Code-node JavaScript by introducing one shared, reviewable rule-data file and a deterministic generator. Approved by the project owner on 2026-08-04 as the first of two follow-ups from the external review (the second, an out-of-distribution paraphrase evaluation set, is a separate future task).

## Problem

The classifier logic exists twice: once in `support_copilot/classifier.py` and once as JavaScript embedded in `n8n/workflows/ai-support-operations-copilot.json`. Parity tests catch behavioral drift after the fact, but every rule change (Task 003 credential terms, Task 004 word boundaries) must be applied by hand in both places, and the embedded 8.5k-character JavaScript string is hard to review and diff. The rule *data* — term lists and regular-expression patterns — is the part that changes and drifts; the surrounding logic is small and stable.

## Approach

1. Add `support_copilot/rules.json` as the single source for rule data: category rules, urgency rules (including the negated-urgency pattern), missing-information rules, security term lists and patterns, contract enums, the synthetic-identifier pattern, schema version, and message length limit.
2. Load that file in `support_copilot/classifier.py` at import time (standard library only) so the Python baseline derives all rule structures from it. Public module constants keep their current names.
3. Store the two Code-node JavaScript bodies as reviewable template files under `n8n/src/`, with placeholders where the rule-data literals sit.
4. Add `scripts/build_workflow.py`, a deterministic generator that renders the templates with data from `rules.json` and writes the embedded `jsCode` values in the committed workflow JSON. It must support a check mode that fails when the committed artifact differs from the generated output.
5. The generated JavaScript must be byte-identical to the currently committed, natively verified Task 004 revision. This proves the generator reproduces the verified artifact and keeps the 2026-08-04 native verification claim valid without any new n8n connection.
6. Shared regular expressions are stored in a portable form usable by both engines (for example `[\s\S]` instead of a Python-only DOTALL flag); flags are stored explicitly. Python compiles the shared strings; behavior must not change.

## Out of scope

- Any behavior change to classification, validation, or the workflow (byte-identical artifact is a requirement).
- New n8n connections or verification runs.
- The paraphrase evaluation set (future task).
- Sharing the stable prose templates (rationales, replies) or restructuring the workflow topology.

## Acceptance criteria

1. `support_copilot/rules.json` exists, is schema-validated by a dependency-free check, and is the only place category, urgency, missing-information, and security rule data is written.
2. The Python classifier derives its rule structures from `rules.json`, with unchanged public API and unchanged behavior: all existing tests pass and the 44-case evaluation still reports no failures and 44/44 parity.
3. `scripts/build_workflow.py --check` verifies that the committed workflow JSON is exactly what the templates plus `rules.json` generate, and a test enforces this so the artifact cannot drift from its sources.
4. The regenerated workflow JSON is byte-identical to the natively verified Task 004 revision.
5. A focused test demonstrates that editing a rule in `rules.json` is reflected in both the Python classifier and the generated JavaScript without touching either implementation by hand.
6. Documentation records the new source-of-truth layout (ADR-011, README repository map, worklog, status).
