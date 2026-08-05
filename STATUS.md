# Project Status

## Overall status

Tasks 001 through 010 complete. Task 002 was manually verified on self-hosted n8n 2.14.2. Task 003 established the reviewed synthetic evaluation baseline. Task 004 hardened all keyword rules with word-boundary matching and negation handling, and was natively re-verified. Task 005 moved all rule data into a single shared source with a byte-identical workflow generator. Task 006 measured the baseline honestly against out-of-distribution paraphrases: 5/33 expected assertions with all safety invariants at 100%. Task 008 added an optional LLM classifier behind the same contract and measured four models: paraphrase category recognition rose to 31-33/33 and the guard rejected all nonconforming model output fail-closed. Task 009 audited the paraphrase labels themselves under a rubric frozen in advance, confirmed the category and security-flag labels unchanged, corrected nine fields in eight cases, and published the resulting fall in the baseline's own score. Task 010 implemented the baseline fallback that documentation had already claimed but the code did not have, bounded by a 20-second wall-clock budget so a hung provider cannot hold a caller.

## Completed

- Created the initial repository structure and project documentation.
- Documented purpose, scope, requirements, architecture proposal, security principles, decisions, and working rules.
- Defined Task 001 as the local, n8n-independent contract and validation baseline without implementing it.
- Defined Task 002 as the later development n8n integration without implementing or connecting it.
- Reserved empty directories for future n8n workflows, synthetic fixtures, tests, and scripts.
- Added ignore rules for local environments, secrets, credentials, dependencies, caches, logs, and generated output.
- Implemented the local, n8n-independent deterministic classifier and validation baseline.
- Documented the versioned JSON input/output contracts.
- Added five required synthetic fixture scenarios and 13 automated tests.
- Verified safe rejection of empty, malformed, and non-JSON input and enforcement of human review.
- Ran the complete test suite successfully on 2026-08-02.
- Completed the Task 002 development-integration plan without connecting to n8n or creating a workflow.
- Created a sanitized, inactive, manual-only four-node workflow JSON under `n8n/workflows/`.
- Replicated Task 001 behavior in a Code node and added a separate Human Review Guard.
- Added five synthetic adverse-input fixtures and repeatable manual n8n import/test instructions.
- Added nine automated workflow structure and local JavaScript/Python parity tests; all passed on 2026-08-02.
- Corrected the prompt-injection detector after native manual verification exposed an untested control-manipulation phrase.
- Manually verified successful import, inactive/manual-only operation, normal and urgent execution, normalized and malformed prompt-injection handling, and export/re-import on self-hosted n8n 2.14.2.
- Confirmed during native verification that no credentials, external APIs, LLMs, webhooks, messaging, or production systems were used.

## Task 003 completion

- Added a 40-case synthetic evaluation dataset with explicit expected assertions.
- Added dependency-free dataset validation for schema, JSON compatibility, unique synthetic case identifiers, enums, safety invariants, and required coverage.
- Added five Phase 1 tests; the full 27-test suite passed on 2026-08-03.
- Added a dependency-free runner, deterministic JSON/Markdown reports, explicit quality and safety metrics, and a reusable local workflow harness.
- Measured 40/40 Python/n8n parity, 40/40 contract validity, 40/40 human-review enforcement, and 7/7 safe rejection.
- The first run exposed a `passwordless` credential false positive and incorrect high urgency; bounded credential terms corrected the defect in Python and workflow JavaScript without changing contract version `1.0`.
- Added six Phase 2 tests; the full 33-test suite passed on 2026-08-03.
- Added methodology, deterministic machine-readable results, representative synthetic evidence, an implemented data-flow diagram, result-drift testing, portfolio updates, and honest limitations.
- Final evaluation: 40/40 for all expected assertions, output-contract validity, human-review enforcement, and Python/n8n parity; safe rejection passed 7/7.
- The final full suite passed: 34 tests.

## Task 004 completion

- An external review demonstrated three live defects from the Task 003 substring class: `not urgent` classified as high urgency, `update` satisfied the billing date check, and `discharged` classified as billing.
- Converted all remaining category, urgency, missing-information, and payment/identity term rules to word-bounded matching in both Python and the committed workflow JavaScript, preserving intended matches through explicit variants.
- Treated explicitly negated urgency (`not urgent`, `non-urgent`, `non urgent`) as a low-urgency indicator and removed the dead always-`general` Python category branch.
- Added four classifier regression tests and four `keyword_boundary` evaluation cases; three of each failed against the pre-fix baseline.
- Final evaluation on the 44-case dataset: 44/44 for all expected assertions, output-contract validity, human-review enforcement, and Python/n8n parity; safe rejection passed 7/7.
- Regenerated `docs/evaluation-results.json` and recorded ADR-009. The full suite passed: 38 tests on 2026-08-04.
- Natively verified the Task 004 revision on the owner-confirmed self-hosted n8n 2.14.2 instance through the official n8n MCP connector (ADR-010): 16 synthetic cases executed with 16/16 exact Human Review Guard parity against the Python oracle; the temporary inactive verification workflow was archived afterward.

## Task 005 completion

- Added `support_copilot/rules.json` as the single source for all term lists, shared regular-expression patterns, contract enums, and limits, with dependency-free structural validation.
- The Python classifier now compiles its matching structures from the shared file; behavior, public API, and the 44-case evaluation results are unchanged.
- The Code-node JavaScript now lives as reviewable templates under `n8n/src/`; `scripts/build_workflow.py` deterministically regenerates the committed workflow JSON, and its output is byte-identical to the natively verified Task 004 artifact.
- A permanent drift test and a `--check` mode fail whenever the committed workflow differs from its sources; a flow-through test proves a rule edit reaches both implementations.
- Recorded ADR-011. The full suite passed: 44 tests on 2026-08-04.

## Task 006 completion

- Parameterized the dataset validator with explicit coverage options; defaults and all existing tests unchanged.
- Added the 33-case paraphrase dataset with semantic expected labels frozen before the first classifier run, four in-distribution controls, and a `--dataset aligned|paraphrase` CLI option.
- Committed the honest measurement: 5/33 full expected assertions (category 14/33, urgency 16/33, security flags 28/33, missing information 21/33) with zero false positives and 0 paraphrase recall on all five paraphrased security solicitations. Superseded by the Task 009 label review on 2026-08-05: the current figures are 4/33 and missing information 16/33; category and security flags were confirmed unchanged.
- Safety invariants held at 100% throughout: output contract, human review, and Python/n8n parity all 33/33.
- Added seven tests including a results drift test; the full suite passed: 51 tests on 2026-08-04. Recorded ADR-012 and `docs/10-paraphrase-evaluation.md`.

## Task 007 completion

- Added dependency-free GitHub Actions CI: full suite on Python 3.10 and 3.13, workflow artifact source check, and both evaluation summaries on every push and pull request; README badge; no secrets or n8n access (ADR-013).
- Refreshed the portfolio case study with Task 005/006 evidence and the measured paraphrase limitation.

## Task 008 completion

- Added the optional LLM classifier (`support_copilot/llm_classifier.py`) behind the unchanged contract: deterministic validation first, union-only security-flag merging, templated replies, fail-closed contract enforcement.
- Added two providers (optional `anthropic` SDK pinned to `claude-haiku-4-5`; OpenRouter via the standard library) and `--classifier/--provider/--model` CLI options; keys live in environment variables only.
- Added thirteen offline stub tests; the suite is 64 tests, still key-less in CI.
- Ran the four-model, 308-call live sweep (~$0.10): paraphrase category 14/33 (baseline) to 31-33/33; paraphrased security solicitations 0/5 (baseline) to 4-5/5; ten nonconforming outputs rejected by the guard, zero unsafe passes.
- Committed dated snapshot results and methodology (`docs/llm-evaluation-results.json`, `docs/11-llm-evaluation.md`); recorded ADR-014.

## Task 009 completion

- Reviewed the paraphrase labels under a method fixed before the result: a rubric derived from the contract and requirements with the rule data deliberately not consulted (`docs/12-labeling-rubric.md`, committed alone), then a blind re-derivation of all 33 cases (`docs/blind-relabel.json`, committed before the originals were opened), then adjudication. Git history carries the ordering claim.
- Confirmed category and security-flag labels 33/33 unchanged. Changed nine fields in eight cases under a unanimous-convergence rule, all additions, all the same error: a detail treated as supplied because the message named the kind of thing that would carry it.
- Re-scored the 2026-08-04 four-model snapshot with no new API call, by reconstructing per-case outputs from stored mismatches; the reconstruction reproduces the published counts exactly on both datasets.
- Published against interest: baseline missing information 21/33 to 16/33 and all assertions 5/33 to 4/33, with superseded figures retained; every model rose.
- Recorded three findings against the task's own premise (the Task 008 system prompt hands models the baseline's urgency conventions; the aggregate keyword-echo hypothesis is unsupported; the rubric's pre-registered expectation was refuted), the adjudication rule's built-in circularity, and the two in-distribution controls that now fail.
- Full suite passed: 64 tests on 2026-08-05. Recorded ADR-015 and `docs/13-label-review.md`.

## Task 010 completion

- Found that the fallback documented in `docs/11-llm-evaluation.md` did not exist: `LLMClassifierError` was caught nowhere outside `llm_classifier.py`, and the only thing between a provider failure and a dead call was the evaluation runner's per-case `except`, which is a sweep boundary rather than production behavior.
- Added `support_copilot/fallback.py`. `with_baseline_fallback` degrades to the deterministic baseline on the typed error, on unexpected exceptions recorded under a distinct reason, and on a wall-clock budget enforced outside the attempt (default 20 seconds, owner-set) so a hung provider cannot hold a caller for the transport's ~9-minute retry ladder.
- Input rejection returns the deterministic result without spending tokens and is not counted as a fallback. Provenance travels beside the result, since `validate_output` requires the contract's exact field set; schema `1.0`, `validate_output`, and the workflow artifact are unchanged.
- Added `--classifier llm-fallback` with `--budget-seconds` and degraded-case reporting; `--classifier llm` keeps its exact prior behavior so the Task 008 snapshot stays reproducible in method.
- Added 15 offline tests: every failure class, a hung-provider test that itself runs fast, the security-flag floor asserted across all 77 committed fixture cases, and an explicit test of the semantic recall that degradation loses.
- Corrected the false claim in `docs/11-llm-evaluation.md` rather than deleting it. Full suite passed: 79 tests on 2026-08-05. Recorded ADR-016.

## Not started or out of scope

- Task 011 (LLM-drafted replies), which the owner approved in sequence on 2026-08-05 but which has no written scope yet.
- Any live measurement of the `llm-fallback` path; the wrapper is verified offline on stubs and no sweep has been run through it.
- Redesigning the in-distribution controls so they anchor to operator judgment rather than to rule phrasings.
- Acting on the `_system_prompt` confound found in Task 009; it is recorded, not fixed.
- Native re-exercise of the manual file-import and export/re-import path for the current revision; the 2026-08-04 native verification ran through the MCP connector with byte-identical Code-node JavaScript instead.
- Compatibility verification with n8n versions newer than 2.14.2.
- External integrations and production deployment.

## Next authorized action

Stop after Task 010. Task 011 is approved in principle but has no written scope; write and approve its proposal before implementing anything. Do not add LLM-drafted replies, change `_system_prompt`, redesign the controls, run a live sweep, introduce further integrations, upgrade or activate n8n, add credentials or external-action nodes, connect to production, use real data, or deploy.

Last updated: 2026-08-05