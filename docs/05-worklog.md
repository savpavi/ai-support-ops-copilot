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
