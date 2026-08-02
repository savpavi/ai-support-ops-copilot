# Initial Architecture Proposal

## Design goal

Use the smallest architecture that cleanly separates input validation, support analysis, output validation, and future workflow integration.

## Delivery sequence

### Task 001: local baseline

Task 001 establishes the n8n-independent core: the machine-readable input/output contract, local classifier/analyzer, deterministic validation and policy checks, synthetic fixtures, and repeatable tests. It does not connect to n8n or create a workflow.

### Task 002: development n8n integration

Only after Task 001 is complete, Task 002 connects that validated baseline to an authorized development n8n instance. It maps one synthetic request into the established contract, preserves the same validated result and safety invariants, adds workflow-level adverse-input tests, and exports an importable workflow JSON under `n8n/workflows/`. It does not send external messages or deploy to production.

## Proposed flow

1. Accept one synthetic request through a local function or command-line boundary.
2. Validate and normalize the input.
3. Run an analysis component that produces category, urgency, missing information, reply draft, and security flags.
4. Validate the structured result against a small explicit schema.
5. attach or enforce `human_review_required: true`.
6. Return the result locally without sending or storing it externally.

## Proposed components

- **Input contract:** request identifier and message text, with identifiers explicitly synthetic.
- **Classifier/analyzer:** a narrow module behind a stable interface. Its first implementation should avoid committing to a large framework.
- **Policy checks:** deterministic checks for required fields, allowed enum values, human review, and obvious risk indicators.
- **Output contract:** structured JSON suitable for tests and later n8n consumption.
- **Fixtures and tests:** synthetic cases covering expected and adverse inputs.
- **n8n adapter:** deferred to Task 002. It will map the validated Task 001 inputs and outputs into a development workflow without moving or weakening core validation rules.

## Data handling

The Task 001 baseline should operate in memory and avoid persistence. Logs should contain only synthetic test data and should not expose configuration or secrets. No external network connection is part of Task 001. Task 002 may connect only to an explicitly authorized development n8n instance; it must not send external messages or connect to production systems.

## Deferred decisions

- Programming language and exact schema library.
- Whether the analyzer is rule-based, model-backed, or hybrid.
- Model provider and configuration.
- Exact n8n workflow shape and development connection method, deferred to Task 002 after Task 001 validation.
- Production hosting and deployment, which remain out of scope.

Task 001 decisions must preserve a platform-independent contract. Task 002 workflow decisions should be made only after that baseline is complete and only with explicit approval.
