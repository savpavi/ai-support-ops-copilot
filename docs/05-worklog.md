# Worklog

## 2026-08-02 — Project initialization

- Inspected the initially empty project workspace.
- Created project governance, overview, status, security, architecture, requirements, decision, worklog, and portfolio documentation.
- Defined but did not implement Task 001.
- Created empty reserved directories for future workflows, fixtures, tests, and scripts.
- Added repository ignore rules for dependencies, caches, generated files, environment files, secrets, credentials, and local tooling metadata.
- Confirmed that application implementation, n8n connection, workflow creation, and deployment remain not started.

## 2026-08-02 — Task sequencing plan

- Clarified that Task 001 owns the local, n8n-independent input/output contract, validation, synthetic fixtures, and repeatable test baseline.
- Added Task 002 for later integration of the validated baseline with an authorized development n8n instance and export of an importable workflow JSON.
- Kept both tasks unimplemented and retained the prohibitions on external message sending and production deployment.

## 2026-08-02 — Task 001 implementation

- Implemented a dependency-free Python classifier with explicit input and output validation.
- Added a versioned plain-JSON contract and a local CLI that processes one request.
- Added synthetic normal, urgent, incomplete, ambiguous, and security-sensitive fixtures.
- Added tests for fixture behavior, malformed input, output tampering, prompt-injection isolation, draft safety, and CLI execution.
- Fixed the disruption rule after the first test run exposed an overly narrow phrase match.
- Re-ran the complete suite: 11 tests passed.
- Confirmed that Task 001 has no n8n integration, network service, LLM call, external messaging, or deployment behavior.

## 2026-08-02 — Task 002 integration planning

- Inspected the Task 001 implementation, JSON contracts, fixtures, CLI, and automated tests.
- Selected an inactive manual-only workflow using built-in n8n nodes and workflow JSON import/export as the smallest integration boundary.
- Chose to replicate the deterministic rules in a Code node while retaining Python as the parity oracle; rejected shell execution and a new local API as unnecessary risk and complexity.
- Excluded n8n REST API and MCP management from the baseline because no programmatic control channel or credential is needed.
- Defined development connection prerequisites, credential controls, parity and adverse-input testing, sanitized export, human approval gates, and rollback steps.
- Made planning changes only; no n8n connection, workflow, credential, LLM call, or deployment was created.

## 2026-08-02 — Task 002 local implementation

- Created the inactive four-node workflow artifact at `n8n/workflows/ai-support-operations-copilot.json` using only built-in node types and synthetic default input.
- Replicated the Task 001 deterministic behavior in Analyze and Validate and added an independent Human Review Guard.
- Added five synthetic adverse-input fixtures covering empty, wrong-type, invalid-identifier, extra-field, and review-override attempts.
- Added local workflow tests for sanitized structure, exact topology, forbidden capabilities, full Task 001 parity, adverse inputs, non-object/overlong input, and guard tampering.
- Task 001 regression: 11 tests passed. Task 002 local structure/parity suite: 8 tests passed.
- Parsed the workflow JSON successfully and confirmed it is inactive and contains no credential attachment.
- Did not connect to n8n, use MCP or REST, create credentials, call an LLM or external API, send a message, activate a workflow, or deploy.
- Native development n8n import, execution, export/re-import, and version compatibility remain pending manual verification.

## 2026-08-02 — Task 002 prompt-injection regression fix

- Investigated a native manual result where the review invariant held but a synthetic autonomy-bypass request had no prompt-injection flag.
- Confirmed the original detector used narrow literal phrases and the exact native phrase was absent from fixtures; Python and workflow parity tests shared the same flawed pattern set.
- Confirmed the reported payload also violated the contract by using `request_text` plus `schema_version` instead of exactly `request_id` and `message`.
- Before correction, the repository Python implementation returned `invalid_input` for that raw object rather than the reported empty list, so native input normalization or artifact drift remains possible and must be checked during retest.
- Added the exact payload as a permanent synthetic adverse fixture and scan known text fields even when input shape is rejected.
- Replaced literal matching in Python and workflow JavaScript with bounded deterministic patterns covering instruction override, review disablement, automatic action, protected-field changes, hidden-instruction disclosure, and safety bypass.
- Added conservative negative coverage for ordinary approval wording and exact raw/normalized regression assertions in both Python and workflow parity tests.
- Corrected artifact passed local regression and parity validation. It has not been rerun in n8n; native retesting is pending.

## 2026-08-02 — Task 002 native completion verification

- Manually verified the corrected artifact in an authorized self-hosted n8n 2.14.2 development instance.
- Imported successfully and remained inactive with Manual Trigger as the only trigger.
- Executed a normal synthetic request successfully and confirmed an urgent synthetic request returned `urgency: high`.
- Confirmed normalized prompt-injection input returned `prompt_injection` and `human_review_required: true`.
- Confirmed the malformed raw prompt-injection payload returned `status: rejected`, `invalid_input` plus `prompt_injection`, and `human_review_required: true`.
- Exported the workflow, imported it again as a new workflow, and reproduced the malformed-input result.
- Confirmed no credentials, external APIs, LLMs, webhooks, messaging, or production systems were used.
- Marked all Task 002 acceptance criteria complete for self-hosted n8n 2.14.2. Compatibility with newer n8n versions remains unverified; no upgrade was recommended or performed.

## 2026-08-03 — Completion-document reconciliation

- Reconciled README, architecture, ADR-006, and Task 001 acceptance evidence with the completed Task 002 native verification and current 13-test Task 001 suite.
- Preserved historical worklog test counts because they describe the actual suites run at those earlier milestones.
- Kept compatibility claims limited to self-hosted n8n 2.14.2 and retained the prohibitions on activation, external actions, production deployment, and unapproved Task 003 work.

## 2026-08-03 — Task 003 scope approval

- Selected a synthetic evaluation and portfolio-evidence baseline as Task 003 before any LLM, interface, external integration, or automation work.
- Defined a 30–50-case synthetic dataset, dependency-free runner, explicit quality and safety metrics, local Python/n8n parity, representative examples, and an implemented-system data-flow diagram.
- Required independently reviewable expected assertions, deterministic reporting, honest limitations, regression coverage, and continued human review.
- Deferred LLM integration, external systems, workflow activation, production deployment, and real-data evaluation.
- Recorded planning changes only; Task 003 implementation has not started.

## 2026-08-03 — Task 003 Phase 1

- Defined a machine-readable evaluation-case schema with independently reviewable expected status, category, urgency, security flags, missing-information assertions, and mandatory human review.
- Added 40 conspicuously synthetic cases covering all categories, all urgency values, all security flags, ambiguous and keyword-boundary probes, missing-information branches, and seven invalid-input paths.
- Included a deliberate `passwordless` keyword-boundary case whose expected label does not copy the current substring detector, allowing later metrics to expose a possible false positive.
- Added a dependency-free validator for dataset size, exact shape, JSON compatibility, unique synthetic identifiers, enums, sorted flags, rejection invariants, and required coverage.
- Added five dataset-validation tests. The full suite passed: 27 tests.
- Did not run or connect to n8n, add an LLM or dependency, change the classifier or workflow, activate anything, send a message, or deploy.
- Left Task 003 in progress; Phase 2 runner, metrics, reports, and full-dataset local parity remain next.

## 2026-08-03 — Task 003 Phase 2

- Extracted the Task 002 Code-node execution helper into a reusable local workflow-parity module without changing the workflow artifact.
- Added a dependency-free evaluation runner with category, urgency, security-flag, missing-information, safe-rejection, contract, human-review, and Python/n8n parity metrics.
- Represented each rate with numerator and denominator and used an explicit null value when a rate is undefined.
- Added deterministic JSON and Markdown rendering that reports synthetic case identifiers and structured mismatches without request text, timestamps, or machine paths.
- Added a local CLI supporting Markdown and JSON output and verified repeated JSON runs are identical.
- Measured 40/40 Python/n8n parity, 40/40 contract validity, 40/40 human-review enforcement, and 7/7 safe rejection.
- Preserved a measured keyword-boundary weakness rather than changing expected labels: `passwordless` produced one credential false positive and changed urgency from normal to high.
- Added six runner/report tests, including injected safety failure detection. The complete suite passed: 33 tests.
- Did not connect to n8n, change the workflow or classifier, add a dependency or LLM, send a message, or deploy.
- Left Task 003 in progress; Phase 3 findings review and portfolio evidence remain next.

## 2026-08-03 — Task 003 Phase 3 and completion

- Classified the measured `passwordless` mismatch as an implementation defect rather than changing its independently reviewed expected assertion.
- Replaced credential substring matching with the same bounded term pattern in Python and workflow JavaScript; kept contract version `1.0` unchanged.
- Added a focused classifier regression and updated evaluation tests to require zero failures and zero credential false positives for the committed dataset.
- Re-ran the evaluation: all expected assertions passed 40/40, Python/n8n parity passed 40/40, contract and human-review invariants passed 40/40, and safe rejection passed 7/7.
- Added a deterministic checked-in JSON result and a methodology document with the implemented data-flow diagram, representative accepted and rejected synthetic examples, reproducible commands, findings, and limitations.
- Updated architecture, security, decisions, README, portfolio evidence, status, task acceptance verification, and handoff records.
- The complete suite passed: 34 tests.
- Confirmed no n8n connection, LLM, new dependency, credential, external action, real data, message sending, activation, or deployment was introduced.
- Marked Task 003 complete and stopped before any unapproved Task 004 work.

## 2026-08-04 — Task 004 keyword boundary and negation hardening

- An external review of the completed baseline demonstrated three live defects from the Task 003 substring class: `not urgent` classified as high urgency, `update` satisfied the billing date check, and `discharged` classified as billing.
- Converted all remaining category, urgency, missing-information, and payment/identity term rules to word-bounded matching in both Python and the committed workflow Code-node JavaScript.
- Added explicit bounded variants (`charges`, `overcharged`, `invoices`, `refunds`, `refunded`, `payments`, `urgently`, `minutes`, `hours`, `application`, `problems`) to preserve intended matches that substring matching had provided implicitly.
- Treated explicitly negated urgency phrases (`not urgent`, `non-urgent`, `non urgent`) as low-urgency indicators.
- Removed the dead always-`general` category branch from the Python baseline; behavior is unchanged and the workflow JavaScript had no such branch.
- Added four focused classifier regression tests (three failed against the pre-fix baseline; one pins preserved `application` matching) and four `keyword_boundary` evaluation cases (three exposed the old workflow JavaScript through parity; one pins preserved `overcharged` matching).
- Re-ran the evaluation: 44/44 expected assertions, output-contract validity, human-review enforcement, and Python/n8n parity; safe rejection passed 7/7; zero security-flag false positives or false negatives.
- Regenerated `docs/evaluation-results.json`. The complete suite passed: 38 tests.
- Did not connect to n8n, add an LLM or dependency, add credentials or action nodes, activate anything, or deploy. The updated workflow JavaScript still requires a separately authorized native n8n retest.

## 2026-08-04 — Task 004 native n8n verification

- Connected the official n8n MCP connector to the authorized self-hosted development instance; the project owner confirmed n8n 2.14.2, the same version as the Task 002 verification.
- Created a temporary, inactive, credential-free verification workflow with the committed four-node topology and byte-identical Code-node JavaScript (the connector creates workflows from SDK code; file import is not available through it).
- Executed 16 synthetic cases manually: the committed default input, all five Task 001 fixtures, all six adverse inputs, and the four Task 004 keyword-boundary probes.
- Machine-compared every native Human Review Guard output with the Python oracle: 16/16 exact matches, including `not urgent` producing low urgency (the Task 004 lookbehind pattern works in the n8n runtime), the `update`/`date` and `discharged` boundary corrections, and structured rejections with `invalid_input` and enforced human review for every adverse input.
- Confirmed the verification workflow was never published or activated, restored its committed default input, and archived it after recording results; the older baseline workflows were not touched.
- Recorded ADR-010 for the bounded MCP-based verification approach. No credentials, URLs, or execution data entered the repository.

## 2026-08-04 — Task 005 single-source rule data

- Added `support_copilot/rules.json` as the single source for category, urgency, missing-information, and security rule data, contract enums, the synthetic-identifier pattern, and limits; every literal was extracted programmatically and cross-checked against the committed JavaScript before adoption.
- Added dependency-free structural validation for the rules file.
- Refactored the Python classifier to compile all matching structures from the shared file with an unchanged public API; all existing behavior tests and the 44-case evaluation pass unchanged.
- Moved the two Code-node JavaScript bodies into reviewable templates under `n8n/src/` with placeholder tokens and added a deterministic generator plus `scripts/build_workflow.py` with check and write modes.
- Confirmed the generated workflow JSON is byte-identical to the natively verified Task 004 artifact; a permanent drift test enforces this.
- Added six focused tests: rules validity, defect reporting, byte-identity, generated-from-data checks, Python derivation, and an end-to-end rule-edit flow-through into both implementations. The complete suite passed: 44 tests.
- Recorded ADR-011. No behavior, contract, or workflow change; no n8n connection.

## 2026-08-04 — Task 006 out-of-distribution paraphrase evaluation

- Parameterized the dataset validator with explicit coverage options (required tags, rejected-case, flag and urgency coverage); defaults preserve Task 003 behavior and all existing tests passed unchanged.
- Added `fixtures/paraphrase_cases.json`: 33 synthetic cases expressing supported intents, urgency cues, and security solicitations in phrasings that avoid the rule terms, plus four in-distribution controls; expected labels were assigned semantically and frozen before the classifier first ran on them.
- Extended `scripts/evaluate_requests.py` with an explicit `--dataset aligned|paraphrase` option.
- Measured and committed the honest result: 14/33 category, 16/33 urgency, 28/33 security-flag, 21/33 missing-information, and 5/33 full expected-assertion accuracy, with zero false positives but 0 paraphrase recall on all five paraphrased security solicitations.
- Confirmed the safety architecture held throughout: 33/33 output-contract validity, 33/33 human-review enforcement, and 33/33 Python/n8n parity despite misclassifications.
- Added seven focused tests, including a drift test on `docs/paraphrase-results.json` and an assertion that the set measures real out-of-distribution failure. The complete suite passed: 51 tests.
- Documented methodology, results, representative failures, and limitations in `docs/10-paraphrase-evaluation.md`; recorded ADR-012. No classifier, rules, or workflow change; no n8n connection.

## 2026-08-04 — Task 007 continuous verification and case-study refresh

- Added a dependency-free GitHub Actions workflow: full test suite on Python 3.10 and 3.13, workflow artifact source check, and both evaluation summaries on every push and pull request; added the README badge and recorded ADR-013.
- Brought `docs/06-portfolio-case-study.md` up to date with the Task 005 single-source evidence, the Task 006 honest out-of-distribution measurements, the engineering-honesty narrative arc, and the measured (rather than assumed) paraphrase limitation.
- No classifier, rules, workflow, or evaluation change; CI contains no secrets, deploy steps, or n8n access.

## 2026-08-04 — Task 008 LLM classifier and multi-model evaluation

- Implemented `support_copilot/llm_classifier.py`: semantic classification behind the unchanged contract, with deterministic input validation before any tokens are spent, union-only merging of deterministic security flags, templated replies, and fail-closed contract enforcement.
- Added two providers: the optional `anthropic` SDK (pinned to `claude-haiku-4-5`) and OpenRouter via the standard library (`OPENROUTER_API_KEY`, any served model), plus `--classifier`, `--provider`, and `--model` CLI options with usage reporting.
- Extended the evaluation runner with analyzer and parity options; parity is honestly reported as not measured for non-baseline analyzers.
- Added thirteen offline stub-based tests; the full suite passed: 64 tests, still key-less and network-free.
- Ran the live sweep: four models × both datasets (308 calls, ~$0.10 total) through OpenRouter. Category on paraphrases rose from the baseline's 14/33 to 31–33/33 (claude-haiku-4.5: 33/33); the five paraphrased security solicitations the baseline missed entirely were caught 4–5/5 by every model; missing-information remained a judgment-divergence domain that dominates the all-assertions metric.
- One model produced contract-nonconforming output on 10 calls; every one was rejected by the guard before reaching a caller — no unsafe output passed in any of the 308 calls.
- Committed the snapshot results and methodology (`docs/llm-evaluation-results.json`, `docs/11-llm-evaluation.md`) with explicit non-reproducibility caveats; recorded ADR-014.
