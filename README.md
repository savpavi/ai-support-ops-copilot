# AI Support Operations Copilot

AI Support Operations Copilot is a portfolio project for assisting human support operators with synthetic inbound requests. The intended system will classify a request, estimate urgency, identify missing information, draft a suggested reply, and flag possible security risks. A human must review every output before any action is taken.

## Current state

Task 001 is complete: the repository contains a dependency-free Python classifier, explicit JSON contracts, deterministic validation, synthetic fixtures, a local CLI, and automated tests. The local Task 002 artifact is also implemented as a sanitized, inactive, manual-only n8n workflow with structural and Python-parity tests. It has not been imported into or executed by an n8n instance, so development-runtime verification remains pending. Nothing has been deployed or connected to an external service. See `STATUS.md` for the authoritative status.

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
- `n8n/workflows/`: sanitized inactive Task 002 workflow artifact.
- `support_copilot/`: local classifier plus input and output validation.
- `fixtures/`: synthetic Task 001 scenarios.
- `tests/`: standard-library automated tests.
- `scripts/`: local command-line entry point.

## Local usage

Python 3.10 or newer is sufficient; there are no third-party runtime or test dependencies.

Run all tests:

```bash
python3 -m unittest discover -s tests -v
```

This runs 11 Task 001 regression tests and 8 Task 002 workflow structure/parity tests. Node.js is required only for the Task 002 tests, which execute the committed Code-node JavaScript locally and compare it with the Python reference.

Analyze one synthetic request from standard input:

```bash
printf '%s\n' '{"request_id":"SYN-DEMO-001","message":"The synthetic demo dashboard stopped working ten minutes ago."}' | python3 scripts/classify_request.py
```

Or pass a JSON file path:

```bash
python3 scripts/classify_request.py path/to/synthetic-request.json
```

The CLI returns exit code `0` for accepted input and `2` for rejected input. The contracts and allowed values are documented in `docs/07-contracts.md`.

## Limitations

The classifier uses transparent keyword rules, not an LLM. It is deterministic and useful as a contract and safety baseline, but it does not understand language semantically, measure statistical confidence, or establish production accuracy. Its suggested replies are fixed templates and must always be reviewed by a human.

The workflow artifact has not yet been verified against a real n8n version or sandbox. Follow `docs/08-n8n-manual-test.md` in an explicitly authorized development instance before claiming import or runtime compatibility. The workflow must remain inactive and must not gain credentials or action nodes.

## Safety

Never add real Pegasus, passenger, agency, PNR, employee, email, or phone data. Never commit secrets or credentials. All future outputs are advisory and require human review.

## Definition of done

The project MVP will be complete only when approved task requirements are implemented, synthetic test coverage demonstrates the required behavior, security constraints are verified, documentation reflects the implemented system, all AI output remains human-reviewed, and no secret or personal data is stored in the repository.
