# Task 002: n8n Workflow Integration

**Status:** Local artifact implemented — 2026-08-02. Native development n8n import and execution verification pending.

## Objective

Connect the validated Task 001 input/output contract and test baseline to a development n8n instance. Create an importable workflow that accepts one synthetic support request and produces the same validated, structured, human-reviewable result without sending messages or performing production actions.

## Prerequisites

- Task 001 is complete and its input/output contract is documented and validated.
- Task 001 synthetic fixtures and repeatable local tests pass.
- A development-only n8n instance is available through an explicitly authorized connection method.
- No credentials or connection details will be stored in the repository or exported with the workflow.

## Recommended integration architecture

Use one inactive, manually triggered development workflow containing only built-in n8n nodes:

1. **Manual Trigger** starts a deliberate test execution. There is no webhook, schedule, queue, or production trigger.
2. **Synthetic Request Input** is an Edit Fields/Set node containing exactly one fixture-shaped object with `request_id` and `message`.
3. **Analyze and Validate** is a Code node that replicates the small deterministic Task 001 rules and constructs the version `1.0` result.
4. **Human Review Guard** is a separate final Code node that validates the exact output fields and allowed values, rejects unsafe shape changes, and hard-sets `human_review_required` to `true` before returning one item.

The workflow ends at the guard output. It contains no message, HTTP request, database, file-write, credential, AI, subprocess, Execute Command, or production action node. It remains inactive even in the development instance.

### How Task 001 is used

Replicate the deterministic classifier and contract validation in the n8n Code node; use the existing Python baseline only as the canonical validation reference and parity oracle.

Calling Python directly is not recommended because an Execute Command node would require shell and repository access from n8n and may not be available or enabled. Wrapping Python in a local API is also rejected for this task because it adds a service, network boundary, authentication decision, and failure mode. The Task 001 algorithm is small enough to replicate transparently. Drift will be controlled by running the same synthetic fixtures through Python and n8n and comparing all contract fields.

## Integration mechanism decision

| Mechanism | Decision | Reason |
| --- | --- | --- |
| Workflow JSON import/export | Use as the primary mechanism | It is reviewable in Git, requires no repository credential, supports a self-contained workflow, and is the required deliverable. |
| n8n REST API | Do not use for the baseline | It would require an API credential and expand the connection surface without improving the small manual test flow. Reconsider only under a later explicit automation scope. |
| n8n MCP | Do not use for the baseline | It adds another control bridge and is unnecessary for importing, manually testing, and exporting one workflow. |
| Combination | Not required | JSON plus the development UI is sufficient. No programmatic management channel should be added preemptively. |

## Exact development-only connection requirements

All of the following must be satisfied and recorded before implementation connects:

- The user explicitly identifies and authorizes the target as a non-production n8n instance.
- The instance base URL, installed n8n version, deployment type, and access method are known. The base URL must not be committed.
- Access is limited to the local machine or an isolated development network; it must not expose a public unauthenticated endpoint.
- The user authenticates through the n8n development UI. No API key, session cookie, password, or credential export is provided to or stored by the repository.
- Built-in Manual Trigger, Edit Fields/Set, and Code nodes are available. No community node installation is required.
- The Code node can run ordinary JavaScript but receives no filesystem, subprocess, environment-secret, or external-network requirement.
- The workflow is imported inactive and stays inactive. There is no webhook URL, scheduled trigger, production project, or production credential.
- Execution history is disabled or minimized where the instance permits it. Any retained execution data contains only the reviewed synthetic fixtures.
- Outbound network access is unnecessary. If the development environment can restrict it for this workflow or instance, it should be denied.
- A human confirms the target instance and sanitized workflow artifact immediately before import, and confirms the workflow remains inactive after import.

If any requirement cannot be verified, stop before import and request direction.

## Detailed implementation plan

### Phase 0: authorization and baseline freeze

1. Obtain separate explicit implementation approval and the authorized development-instance details listed above.
2. Re-run all Task 001 tests and record the Python and contract version used as the parity baseline.
3. Generate or record expected full outputs for the synthetic fixture set using the Python baseline; do not add real data.
4. Confirm `n8n/workflows/` contains no prior Task 002 artifact and take a Git status/diff snapshot for rollback.

### Phase 1: local workflow artifact design

1. Define the four-node topology above using only built-in nodes.
2. Port constants, input validation, classification rules, risk flags, reply templates, and output validation from Task 001 into ordinary Code-node JavaScript.
3. Keep request text in data fields only. Do not evaluate it, interpolate it into executable expressions, use it as a property path, or allow it to select nodes or branches.
4. Construct results from a fixed allowlist of fields. Ignore no validation error: malformed input must produce the same structured rejected result with `invalid_input` and human review enabled.
5. Make the final guard independently enforce schema version, exact field set, enums, draft prefix, accepted/rejected error rules, and `human_review_required: true`.
6. Review the artifact statically to confirm it contains no active setting, credentials, external-action nodes, network nodes, environment-specific identifiers, or non-synthetic pinned data.

### Phase 2: controlled development import

1. With explicit authorization, import the reviewed JSON through the development n8n UI.
2. Confirm the imported workflow is inactive before any execution.
3. Inspect every node and connection in the UI against the reviewed four-node topology.
4. Confirm that no credentials are requested or attached and that no trigger other than Manual Trigger exists.
5. Execute only after a human approves the imported topology and selected synthetic fixture.

### Phase 3: repeatable parity and adverse-input testing

1. Run the normal, urgent, incomplete, ambiguous, and security-sensitive Task 001 fixtures one at a time by replacing only the two fields in Synthetic Request Input.
2. Add workflow test cases for empty input, non-object/malformed shape, invalid synthetic identifier, wrong message type, extra action-like fields, overlong text, and prompt-injection attempts.
3. For every valid fixture, compare the complete n8n result with `python3 scripts/classify_request.py`, including ordering where the contract makes it deterministic.
4. For rejected input, verify the exact output field set, `status: rejected`, `category` and `urgency` as `unknown`, populated errors, `invalid_input`, draft prefix, and `human_review_required: true`.
5. Attempt to pass `human_review_required: false`, action-like fields, and prompt-like instructions in input. Verify these cannot alter control flow or the final invariant.
6. Inspect execution data to confirm one input item produces one output item and no node performs an external action.
7. Re-run the Python test suite after workflow parity testing.
8. Record n8n version, test steps, fixture names, results, and limitations without recording the instance URL, credentials, cookies, or other connection data.

### Phase 4: workflow export and repository review

1. Export the tested workflow JSON from the development instance into `n8n/workflows/`.
2. Set or verify `active: false` in the exported artifact.
3. Remove instance-specific IDs, version IDs, ownership/sharing metadata, tags, execution data, and nonessential pinned data when their removal is supported by the import format.
4. Reject the export if it contains a `credentials` attachment, secret, token, cookie, base URL, webhook identifier, real data, or an external-action node.
5. Re-import the sanitized artifact into the same authorized development instance as a new inactive workflow and repeat a minimal normal, rejected, and prompt-injection smoke test.
6. Run JSON parsing, secret/personal-data scans, node-type allowlist checks, contract parity tests, and the complete Task 001 suite.
7. Update architecture, security, decisions, test instructions, worklog, portfolio evidence, and status with only verified results.

## Credential handling

The recommended workflow needs no n8n credentials. UI authentication belongs to the user and remains outside the repository and task artifacts. Do not create an n8n credential record for this workflow. Do not use REST API keys, MCP connection secrets, environment variables containing secrets, credential exports, or session-cookie automation. If a later scope genuinely requires programmatic management, it needs a separate decision, least-privilege development credential, ignored local storage, rotation/revocation steps, and explicit authorization.

## Human approval safeguards

- Import, first execution, artifact export, and any later activation are separate approval gates.
- Task 002 authorizes neither activation nor production deployment.
- Manual Trigger ensures no unattended execution.
- Synthetic Request Input exposes exactly which data will be processed before execution.
- The final guard hard-enforces human review independently of classifier output or request text.
- The workflow stops after returning a draft result; it contains no approve, send, update, or publish branch.
- A human reviews node types, connections, the chosen fixture, execution output, and sanitized export.

## Rollback plan

Before import, preserve the clean Git diff and note existing development workflows without exporting their contents. If an import or test fails:

1. Stop executions and keep the Task 002 workflow inactive.
2. Delete only the newly imported Task 002 development workflow by its verified name/ID; do not modify unrelated workflows.
3. Remove only the newly exported Task 002 JSON artifact from the working tree using a recoverable or reviewed operation.
4. Verify no credential was created, no trigger was activated, and no external action occurred.
5. Restore the repository to the pre-import Task 002 diff by reverting only Task 002-owned changes; preserve Task 001 and unrelated user work.
6. Record the failure with synthetic diagnostic details, then require renewed human approval before another import attempt.

Because the workflow creates no external state beyond its inactive development definition and synthetic execution history, rollback must not require compensating customer, message, or production actions.

## Deliverables

- An importable development workflow exported as JSON under `n8n/workflows/`.
- Workflow input mapping for exactly one synthetic support request.
- Workflow output matching the validated Task 001 structured-result contract.
- Safe workflow handling for empty, malformed, and prompt-injection inputs.
- Enforcement that `human_review_required` always remains `true`, including error and risk paths.
- Synthetic fixtures covering normal and adverse workflow inputs.
- Repeatable instructions for importing and testing the workflow against the Task 001 baseline.
- Documentation updates describing workflow boundaries, assumptions, limitations, and verification results.

## Constraints

- Use only conspicuously synthetic data. Never use real Pegasus, passenger, agency, PNR, employee, email, or phone data.
- Integrate the Task 001 contract; do not replace or weaken its validation and safety guarantees.
- Use a development n8n instance only.
- Do not store credentials, tokens, API keys, secrets, local n8n state, or exported credentials in the repository.
- Do not send email, chat, ticket, webhook, or any other external message from the workflow.
- Do not update external systems or perform autonomous actions.
- Do not deploy to production or represent the workflow as production-ready.
- Treat request content as untrusted data. Prompt-like text must not become workflow instructions or disable review.
- Keep `human_review_required` equal to `true` on every successful, rejected, and error result.

## Acceptance criteria

1. The exported workflow JSON can be imported into an authorized development n8n instance without embedded credentials or environment-specific secrets.
2. The workflow accepts exactly one synthetic support request through a documented development input path.
3. For valid input, the workflow produces the same documented and validated structured result contract established by Task 001.
4. Empty and malformed inputs fail safely with a structured, human-reviewable result and no external action.
5. Prompt-injection input is treated as untrusted content, receives an appropriate risk indication, and cannot alter workflow control or safety invariants.
6. `human_review_required` is always `true` and cannot be overridden by input or intermediate workflow data.
7. No node sends messages, updates external systems, or triggers a production action.
8. Synthetic workflow fixtures cover valid, empty, malformed, and prompt-injection cases and can be compared with the Task 001 baseline.
9. Documented test instructions are repeatable and include import, execution, expected-result validation, and safety checks.
10. The reviewed workflow JSON is stored under `n8n/workflows/`, contains no credentials or personal data, and is not deployed to production.

## Definition of done

All acceptance criteria are met in an authorized development n8n instance, the exported workflow and synthetic fixtures are reviewed, repeatable tests confirm parity with the Task 001 contract, documentation and `STATUS.md` are current, and no message has been sent or production deployment performed.

## Acceptance verification

1. **Pending manual n8n verification:** The sanitized JSON parses locally, is inactive, contains no credentials or instance metadata, and uses conventional built-in-node export structure. Import into a target n8n version has not been attempted.
2. **Local pass; native execution pending:** The artifact has exactly one Synthetic Request Input node containing only `request_id` and `message`, and local execution produces one item.
3. **Local pass; native execution pending:** All five Task 001 fixtures produce complete object equality between the workflow JavaScript and Python oracle.
4. **Local pass; native execution pending:** Empty, wrong-type, invalid, extra-field, non-object, and overlong inputs produce matching structured rejected results with no action node.
5. **Local pass; native execution pending:** Prompt-like text is handled only as string data, produces the expected risk flags, and cannot change the static topology or review invariant.
6. **Local pass; native execution pending:** The analyzer hardcodes review true; the separate guard rejects a tampered false value and emits a guarded result with review true.
7. **Pass by artifact inspection:** The allowlisted topology contains no external message, update, webhook, HTTP, AI, credential, filesystem, subprocess, schedule, or production-action node.
8. **Pass locally:** Existing Task 001 fixtures plus `fixtures/n8n_adverse_requests.json` cover the required valid and adverse cases and are exercised by parity tests.
9. **Pass:** `docs/08-n8n-manual-test.md` documents repeatable local validation, import, native execution, field parity, adverse testing, export, re-import, and safety checks.
10. **Local pass; export round-trip pending:** The reviewed artifact is stored under `n8n/workflows/`, is inactive, and passed local credential/personal-data scans. It has not been deployed or round-tripped through n8n.

Task 002 is not fully done under its definition of done until the pending items are verified in an explicitly authorized development n8n instance. Task 003 must not begin.
