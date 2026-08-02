# Task 002: n8n Workflow Integration

**Status:** Not started. Blocked until Task 001 is complete and explicitly approved for integration work.

## Objective

Connect the validated Task 001 input/output contract and test baseline to a development n8n instance. Create an importable workflow that accepts one synthetic support request and produces the same validated, structured, human-reviewable result without sending messages or performing production actions.

## Prerequisites

- Task 001 is complete and its input/output contract is documented and validated.
- Task 001 synthetic fixtures and repeatable local tests pass.
- A development-only n8n instance is available through an explicitly authorized connection method.
- No credentials or connection details will be stored in the repository or exported with the workflow.

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
