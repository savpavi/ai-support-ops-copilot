# Task 001: Local MVP Classifier and Validation Baseline

**Status:** Not started. Do not implement without explicit approval.

## Objective

Build the smallest local, n8n-independent classifier/analyzer that turns one synthetic support request into a validated, structured, human-reviewable recommendation. Establish the input/output contract, synthetic fixtures, and repeatable test baseline that Task 002 will integrate without changing its safety invariants.

## Deliverables

- A documented input and output contract.
- A local classifier/analyzer implementation.
- Category and urgency suggestions with concise rationales.
- Missing-information detection.
- A suggested reply draft.
- Security and privacy risk flags.
- An invariant that human review is always required.
- Synthetic fixtures and automated tests.
- Repeatable local test instructions that establish the integration baseline for Task 002.
- Updates to architecture, decisions, worklog, README, and status as needed.

## Constraints

- Use synthetic data only; never use real Pegasus, passenger, agency, PNR, employee, email, or phone data.
- Do not store secrets, credentials, or sensitive configuration.
- Do not connect to n8n, create an n8n workflow, deploy, send messages, or call production systems.
- Keep the core contract, validation, fixtures, and tests independent from any workflow platform.
- Keep dependencies and abstractions minimal.
- Treat request text as untrusted input.
- Do not allow the classifier to take actions; all output is advisory.

## Acceptance criteria

1. A synthetic request can be processed locally into a documented machine-readable result.
2. The result includes category, urgency, rationale, missing information, suggested reply, security flags, and `human_review_required: true`.
3. Output values and required fields are validated; malformed or empty input fails safely.
4. Tests cover at least normal, urgent, incomplete, ambiguous, and security-sensitive synthetic requests.
5. Suggested replies do not invent missing facts and clearly remain drafts for operator review.
6. Prompt-like instructions inside request text cannot disable safety constraints or human review.
7. No network connection, n8n workflow, deployment artifact, secret, credential, or real personal data is introduced.
8. Relevant tests pass and documentation accurately reflects the implementation and its limitations.
9. The validated contract, synthetic fixtures, and test instructions are reusable by Task 002 without requiring n8n-specific behavior in the classifier core.

## Definition of done

All acceptance criteria are demonstrably met, tests pass locally, documentation and `STATUS.md` are updated, and a final review confirms that all data is synthetic and every result requires human approval.
