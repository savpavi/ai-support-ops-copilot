# Local Baseline Architecture

## Design goal

Use the smallest architecture that cleanly separates input validation, support analysis, output validation, and future workflow integration.

## Delivery sequence

### Task 001: local baseline

Task 001 established the n8n-independent core: the machine-readable input/output contract, local classifier/analyzer, deterministic validation and policy checks, synthetic fixtures, and repeatable tests. It does not connect to n8n or create a workflow.

### Task 002: development n8n integration

Only after Task 001 is complete, Task 002 connects that validated baseline to an authorized development n8n instance. It maps one synthetic request into the established contract, preserves the same validated result and safety invariants, adds workflow-level adverse-input tests, and exports an importable workflow JSON under `n8n/workflows/`. It does not send external messages or deploy to production.

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
- **n8n adapter:** deferred to Task 002. It will map the validated Task 001 inputs and outputs into a development workflow without moving or weakening core validation rules.

## Data handling

The Task 001 baseline operates in memory and performs no persistence or network calls. The CLI reads one local JSON value and writes one result to standard output. Task 002 may connect only to an explicitly authorized development n8n instance; it must not send external messages or connect to production systems.

## Deferred decisions

- Exact n8n workflow shape and development connection method, deferred to Task 002 after Task 001 validation.
- Production hosting and deployment, which remain out of scope.

Task 001 decisions must preserve a platform-independent contract. Task 002 workflow decisions should be made only after that baseline is complete and only with explicit approval.
