# Next Session Handoff

- **Date:** 2026-08-04
- **Branch:** `main`
- **HEAD:** the Task 005 single-source-rules commit (after `e1350fe Record Task 004 native n8n verification`).
- **Repository status at handoff:** all Task 003–005 work is committed locally. Push remains unauthorized.

## Completed this session

- Completed Task 004 (word-boundary and negation hardening) with native n8n 2.14.2 verification (16/16 exact parity, ADR-010).
- Completed Task 005: `support_copilot/rules.json` is now the single source for all rule data; the Python classifier compiles from it, the workflow JavaScript is generated from `n8n/src/` templates by `scripts/build_workflow.py`, and the generated artifact is byte-identical to the natively verified Task 004 revision (ADR-011).
- Added six Task 005 tests; the full suite is 44 tests, all passing.

## Validation

- `python3 -m unittest discover -s tests -v` — 44 tests passed.
- `python3 scripts/build_workflow.py` — workflow JSON matches its sources.
- `python3 scripts/evaluate_requests.py --format json` — 44 cases, no failures, 44/44 parity, 7/7 safe rejection.

## Unfinished work and risks

- Task 006 (out-of-distribution paraphrase evaluation set) is approved and is the next task.
- Future rule edits must go through `rules.json` plus `scripts/build_workflow.py --write`; a regenerated workflow revision needs a new native n8n verification before runtime claims are repeated.
- Compatibility with n8n versions newer than 2.14.2 is unverified.
- The workflow must remain inactive, manual-only, synthetic-data-only, and human-reviewed.

## Recommended next task

Task 006: an out-of-distribution paraphrase evaluation set with semantically reviewed expected labels, measuring where the keyword baseline actually fails. Honest sub-100% results are the expected outcome and must be reported as measurements, not fixed by aligning labels to the implementation.

## Do not perform yet

Do not add an LLM or interface, introduce an external integration, upgrade or activate n8n, add credentials or external-action nodes, connect to production, use real personal data, or deploy.

## Repository operations

- **Commit:** Task 005 committed; nothing pending.
- **Push:** pending only if/after explicitly authorized.
- **Merge:** not pending.
- **Deployment:** not pending and not authorized.
