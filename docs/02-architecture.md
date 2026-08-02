# Initial Architecture Proposal

## Design goal

Use the smallest architecture that cleanly separates input validation, support analysis, output validation, and future workflow integration.

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
- **n8n adapter:** deferred. A later task may map validated inputs and outputs into a workflow without moving core rules into n8n.

## Data handling

The MVP should operate in memory and avoid persistence. Logs should contain only synthetic test data and should not expose configuration or secrets. No external network connection is part of the initial implementation.

## Deferred decisions

- Programming language and exact schema library.
- Whether the analyzer is rule-based, model-backed, or hybrid.
- Model provider and configuration.
- n8n workflow shape, hosting, and credential management.

These decisions should be made only when Task 001 or a later approved task provides enough evidence.
