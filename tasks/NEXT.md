# Next Session Handoff

- **Date:** 2026-08-04
- **Branch:** `main`
- **HEAD:** the Task 006 paraphrase-evaluation commit (after `d666a74 Move rule data to a single shared source with workflow generator`).
- **Repository status at handoff:** all Task 003–006 work is committed locally. Push remains unauthorized.

## Completed this session

- Task 004: word-boundary and negation hardening, natively verified on self-hosted n8n 2.14.2 (16/16 exact parity, ADR-009/ADR-010).
- Task 005: single-source rule data in `support_copilot/rules.json` with a byte-identical workflow generator (`n8n/src/` templates, `scripts/build_workflow.py`, ADR-011).
- Task 006: 33-case out-of-distribution paraphrase evaluation with semantic frozen labels; honest committed result of 5/33 expected assertions with 100% contract/human-review/parity invariants (ADR-012, `docs/10-paraphrase-evaluation.md`).

## Validation

- `python3 -m unittest discover -s tests -v` — 51 tests passed.
- `python3 scripts/build_workflow.py` — workflow JSON matches its sources.
- `python3 scripts/evaluate_requests.py --format json` — aligned: 44 cases, no failures, 44/44 parity.
- `python3 scripts/evaluate_requests.py --dataset paraphrase --format json` — paraphrase: 33 cases, 5/33 expected assertions, 33/33 safety invariants; matches `docs/paraphrase-results.json`.

## Unfinished work and risks

- Task 007 has no approved scope. Measured candidates from the paraphrase results: semantic classification (requires an approved LLM decision) or bounded rule additions justified case by case — but ADR-012 forbids chasing the paraphrase set with rule patches.
- The paraphrase labels were authored in the same session that maintains the rules; owner review of `fixtures/paraphrase_cases.json` labels is invited and disputes should be recorded, not resolved by rerunning.
- Future rule edits must go through `rules.json` plus `scripts/build_workflow.py --write`; a regenerated workflow revision needs a new native n8n verification.
- Compatibility with n8n versions newer than 2.14.2 is unverified.
- The workflow must remain inactive, manual-only, synthetic-data-only, and human-reviewed.

## Do not perform yet

Do not begin Task 007, add an LLM or interface, introduce an external integration, upgrade or activate n8n, add credentials or external-action nodes, connect to production, use real personal data, or deploy.

## Repository operations

- **Commit:** Task 006 committed; nothing pending.
- **Push:** pending only if/after explicitly authorized.
- **Merge:** not pending.
- **Deployment:** not pending and not authorized.
