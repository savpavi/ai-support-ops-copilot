# Task 004: Keyword Boundary and Negation Hardening

## Status

- **State:** complete — 2026-08-04. All acceptance criteria verified: 38 tests pass, the 44-case evaluation reports no failed cases, and Python/n8n local parity is 44/44.
- **Approved scope:** apply the Task 003 keyword-boundary lesson to all remaining substring rules and remove dead classifier logic. Approved by the project owner on 2026-08-04 after an external review found the same defect class outside the credential detector.

## Problem

Task 003 replaced the credential `password` substring check with a bounded term pattern after the `passwordless` false positive. The category, urgency, missing-information, and payment/identity flag rules still use raw substring matching and exhibit the same defect class:

- `"This is not urgent"` raises urgency to `high` because `urgent` matches inside the negated phrase.
- `"My invoice needs an update"` silently satisfies the billing date check because `date` matches inside `update`.
- `"my phone was discharged"` is classified as `billing` because `charge` matches inside `discharged`.

Additionally, `_category` in the Python baseline contains a conditional whose branch and fallback both return `"general"`; the committed workflow JavaScript has no such branch. The dead branch must be removed without behavior change.

## Scope

1. Convert all remaining substring term rules (category, urgency, missing information, payment-data, identity-data) to word-boundary matching in both the Python baseline and the committed workflow Code-node JavaScript.
2. Preserve intended matches that substring matching provided by listing explicit bounded variants (for example `charges`, `overcharged`, `urgently`, `minutes`, `hours`, `application`, `problems`).
3. Treat explicitly negated urgency (`not urgent`, `non-urgent`, `non urgent`) as a low-urgency indicator, not a high-urgency match.
4. Remove the dead `_category` conditional in the Python baseline.
5. Add focused unit regression tests and new `keyword_boundary`-tagged evaluation cases covering the three defects above.
6. Keep contract version `1.0`; no contract field or enum changes.
7. Update evaluation results, documentation, decision record, status, and worklog.

## Out of scope

- Connecting to or retesting on native n8n (requires separate authorization).
- Restructuring the duplicated Python/JavaScript logic into a single generated source.
- New out-of-distribution paraphrase evaluation sets.
- Any LLM, integration, activation, credential, or deployment work.

## Acceptance criteria

1. No term rule in Python or workflow JavaScript matches inside a longer word.
2. Negated urgency phrases classify as `low`, and plain `urgent`/`urgently` still classify as `high`.
3. The dead `_category` branch is removed with no behavior change.
4. New unit tests and evaluation cases fail against the pre-fix baseline and pass after the fix.
5. Full test suite passes; the evaluation reports no failed cases and full Python/n8n local parity.
6. `docs/evaluation-results.json`, `docs/09-evaluation.md`, `docs/04-decisions.md` (ADR-009), `docs/05-worklog.md`, `README.md`, and `STATUS.md` reflect the new dataset size and results.
7. The workflow remains inactive, manual-only, credential-free, and synthetic-only.
