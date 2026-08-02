# AI Support Operations Copilot

AI Support Operations Copilot is a portfolio project for assisting human support operators with synthetic inbound requests. The intended system will classify a request, estimate urgency, identify missing information, draft a suggested reply, and flag possible security risks. A human must review every output before any action is taken.

## Current state

Project initialization is complete. No application, classifier, n8n workflow, integration, or deployment has been implemented. See `STATUS.md` for the authoritative status.

## Scope

The MVP is expected to accept synthetic support text and produce a structured recommendation containing:

- request category and confidence or rationale;
- urgency level and rationale;
- missing information needed for safe handling;
- a draft response clearly marked as suggested text;
- security and privacy risk flags;
- an explicit human-review requirement.

Out of scope for the initial phase are real customer data, production integrations, autonomous replies or actions, deployment, and unnecessary platform complexity.

## Repository map

- `docs/`: brief, requirements, architecture, security, decisions, worklog, and case-study notes.
- `tasks/`: bounded implementation task specifications.
- `n8n/workflows/`: reserved for later workflow artifacts; currently empty.
- `fixtures/`: reserved for synthetic examples; currently empty.
- `tests/`: reserved for automated verification; currently empty.
- `scripts/`: reserved for small project utilities; currently empty.

## Safety

Never add real Pegasus, passenger, agency, PNR, employee, email, or phone data. Never commit secrets or credentials. All future outputs are advisory and require human review.

## Definition of done

The project MVP will be complete only when approved task requirements are implemented, synthetic test coverage demonstrates the required behavior, security constraints are verified, documentation reflects the implemented system, all AI output remains human-reviewed, and no secret or personal data is stored in the repository.
