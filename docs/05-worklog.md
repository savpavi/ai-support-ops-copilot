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
