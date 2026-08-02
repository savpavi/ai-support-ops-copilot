# Requirements

## Functional requirements

Given a synthetic support request, the Task 001 baseline returns:

1. A normalized request category.
2. An urgency level with a short rationale.
3. A list of information missing from the request.
4. A suggested reply suitable for operator editing.
5. Security or privacy risk flags.
6. A clear `human_review_required` indication that is always true.

The result must use a documented, machine-readable schema and handle empty, ambiguous, and potentially unsafe input without taking an external action.

## Safety requirements

- Fixtures, examples, tests, screenshots, and logs must be synthetic.
- Real Pegasus, passenger, agency, PNR, employee, email, and phone data are prohibited.
- Secrets and credentials must never be stored in the repository or emitted in test artifacts.
- Prompt injection, credential requests, payment details, identity data, and suspicious links should be represented as risk flags rather than followed or repeated unnecessarily.
- The system must not send replies, update tickets, or trigger downstream operations.

## Quality requirements

- Prefer a small, dependency-light implementation.
- Keep business rules separate from transport or workflow adapters.
- Validate output shape and allowed values.
- Make failure modes explicit and safe.
- Provide tests for normal, urgent, incomplete, ambiguous, and security-sensitive synthetic cases.
- Document assumptions and limitations.

## Definition of done

An approved implementation task is done when all acceptance criteria pass, tests are repeatable locally, safety constraints are verified, documentation and project status are current, and a human can inspect the output before any action. Task completion does not authorize deployment or integration.
