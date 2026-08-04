# Next Session Handoff

- **Date:** 2026-08-04
- **Branch:** `main`
- **HEAD:** the Task 008 completion commit (after `f1f476b Add optional LLM classifier behind the existing contract`).
- **Repository status at handoff:** everything through Task 008 is committed and pushed; CI runs on GitHub Actions and stays key-less.

## Completed this session

- Tasks 004–008: word-boundary hardening with native n8n verification, single-source rule data with a byte-identical generator, the honest paraphrase evaluation, CI plus the case-study refresh, and the optional LLM classifier with a four-model live sweep.
- Task 008 highlights: paraphrase category recognition 14/33 (baseline) → 31–33/33 (LLMs); paraphrased security solicitations 0/5 → 4–5/5; ten nonconforming model outputs rejected fail-closed; the whole 308-call sweep cost ~$0.10 via OpenRouter.

## Validation

- `python3 -m unittest discover -s tests -v` — 64 tests passed, offline and key-less.
- `python3 scripts/build_workflow.py` — workflow JSON matches its sources.
- Baseline evaluations unchanged: aligned 44/44, paraphrase 5/33 with 100% safety invariants; both drift-tested.
- LLM results are dated snapshots in `docs/llm-evaluation-results.json` (no drift test by design).

## Unfinished work and risks

- Task 009 has no approved scope. Natural candidates: LLM-drafted replies behind the same guard, a baseline-fallback wrapper for production-style resilience, independent review of the paraphrase labels (models disputed the missing-information judgments), or an n8n path for the LLM engine (would require revisiting the no-credentials workflow rule).
- API keys live only in the owner's environment (`~/.bashrc.d/99-secrets.sh`, mode 600); nothing in the repo. The sweep's OpenRouter route sends synthetic text to third-party providers — acceptable per ADR-014, revisit if data ever stops being synthetic.
- Compatibility with n8n versions newer than 2.14.2 is unverified; the workflow remains inactive, manual-only, and deterministic-baseline-only.

## Do not perform yet

Do not begin Task 009, add LLM-drafted replies, introduce further integrations, upgrade or activate n8n, add credentials or external-action nodes, connect to production, use real personal data, or deploy.

## Repository operations

- **Commit/Push:** up to date with `origin/main`.
- **Merge/Deployment:** not pending; deployment not authorized.
