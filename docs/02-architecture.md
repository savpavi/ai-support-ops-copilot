# Local Baseline Architecture

## Design goal

Use the smallest architecture that cleanly separates input validation, support analysis, output validation, and future workflow integration.

## Delivery sequence

### Task 001: local baseline

Task 001 established the n8n-independent core: the machine-readable input/output contract, local classifier/analyzer, deterministic validation and policy checks, synthetic fixtures, and repeatable tests. It does not connect to n8n or create a workflow.

### Task 002: development n8n integration

Task 002 now has a sanitized local workflow artifact that is inactive and manual-only: Manual Trigger → Synthetic Request Input → Analyze and Validate → Human Review Guard. It maps one synthetic request into the established contract, preserves the same validated result and safety invariants, and is stored under `n8n/workflows/`. It does not send external messages or deploy to production. Import and execution in an authorized development n8n instance remain unverified.

The deterministic Task 001 rules are replicated in a built-in n8n Code node so the workflow remains self-contained. The Python implementation remains the canonical parity reference rather than being invoked through a shell or new local API. Workflow JSON import/export through the development UI is the intended integration mechanism; REST API and MCP access remain excluded.

## Implemented Task 001 flow

1. Accept one synthetic request through `analyze_request` or the local JSON command-line boundary.
2. Validate and normalize the input.
3. Run an analysis component that produces category, urgency, missing information, reply draft, and security flags.
4. Validate the structured result against a small explicit schema.
5. Attach and validate `human_review_required: true`.
6. Return the result locally without sending or storing it externally.

## Implemented components

- **Input contract:** exactly `request_id` and `message`, with a required `SYN-` identifier and bounded text.
- **Classifier/analyzer:** `support_copilot/classifier.py`, using fixed keyword and template rules with no external dependencies.
- **Policy checks:** deterministic input validation, output schema and enum validation, injection-risk detection, and an immutable human-review invariant.
- **Output contract:** versioned plain JSON documented in `docs/07-contracts.md`, suitable for tests and later n8n consumption.
- **Fixtures and tests:** five synthetic scenario classes plus malformed-input, contract-tampering, reply-safety, and CLI tests.
- **n8n adapter:** implemented locally as built-in Manual Trigger, Edit Fields/Set, and Code nodes. A final guard independently validates the contract and enforces human review.
- **Workflow verification:** Python tests parse and inspect the artifact, run its JavaScript in a local Node harness, and compare complete results with the Task 001 oracle. This does not emulate all n8n sandbox or import behavior.

## Data handling

The Task 001 baseline operates in memory and performs no persistence or network calls. The CLI reads one local JSON value and writes one result to standard output. Task 002 may connect only to an explicitly authorized development n8n instance; it must not send external messages or connect to production systems.

## Task 002 development boundary

The target must be a user-authorized, non-production n8n instance on a local or isolated development network. The workflow requires no n8n credential records, external network access, filesystem mounts, subprocess execution, community nodes, webhooks, schedules, or production identifiers. It must be imported and exported inactive, and retained execution data must remain synthetic and minimized.

## Deferred decisions

- The exact development instance URL, version, and access method, which must be supplied and authorized before implementation and must not be committed.
- Any future REST API or MCP management channel, which requires separate justification and approval.
- Production hosting and deployment, which remain out of scope.

Task 001 decisions must preserve a platform-independent contract. Task 002 workflow decisions should be made only after that baseline is complete and only with explicit approval.
