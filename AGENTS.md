# Working Rules for Codex

## Project boundary

This repository is for a portfolio-quality AI Support Operations Copilot. Work must remain simple, reviewable, and aligned with the documented requirements and decisions.

## Mandatory rules

- Use only clearly synthetic support requests and identities.
- Never use real Pegasus, passenger, agency, PNR, employee, email, or phone data.
- Never commit credentials, tokens, API keys, secrets, environment files, or exported connection data.
- Deployment requires explicit approval. Local code and inactive workflow preparation within the requested task do not require additional approval. Connecting to or modifying an external n8n instance or other external system requires authorization covering that system and operation; honor authorization already given for the same scope.
- Treat every AI result as a suggestion requiring human review; never represent it as an autonomous decision.
- Keep the architecture small and avoid frameworks or services without a demonstrated need.
- Read `STATUS.md`, the relevant task file, and applicable documentation before making changes.
- Work on the task the user requested. Use `STATUS.md` and the relevant task document for current progress and acceptance criteria; do not infer the active task from a fixed number in these instructions or start an unrelated backlog task.
- Record material architecture or security choices in `docs/04-decisions.md` and meaningful progress in `docs/05-worklog.md`.
- For behavior changes, add or update relevant tests and synthetic fixtures. Documentation-only edits require document and diff checks, not implementation tests.
- Preserve unrelated user changes and report verification performed.

## Definition of done

A task is done only when its acceptance criteria are met, relevant tests pass, documentation and status are updated, no secrets or personal data are present, and the result is ready for human review. Deployment is never implied by task completion.
