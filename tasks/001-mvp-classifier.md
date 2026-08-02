# Task 001: MVP Classifier

**Status:** Not started. Do not implement without explicit approval.

## Objective

Build the smallest local classifier/analyzer that turns one synthetic support request into a validated, structured, human-reviewable recommendation.

## Deliverables

- A documented input and output contract.
- A local classifier/analyzer implementation.
- Category and urgency suggestions with concise rationales.
- Missing-information detection.
- A suggested reply draft.
- Security and privacy risk flags.
- An invariant that human review is always required.
- Synthetic fixtures and automated tests.
- Updates to architecture, decisions, worklog, README, and status as needed.

## Constraints

- Use synthetic data only; never use real Pegasus, passenger, agency, PNR, employee, email, or phone data.
- Do not store secrets, credentials, or sensitive configuration.
- Do not connect to n8n, create an n8n workflow, deploy, send messages, or call production systems.
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

## Definition of done

All acceptance criteria are demonstrably met, tests pass locally, documentation and `STATUS.md` are updated, and a final review confirms that all data is synthetic and every result requires human approval.
