# Working Rules for Codex

## Project boundary

This repository is for a portfolio-quality AI Support Operations Copilot. Work must remain simple, reviewable, and aligned with the documented requirements and decisions.

## Mandatory rules

- Use only clearly synthetic support requests and identities.
- Never use real Pegasus, passenger, agency, PNR, employee, email, or phone data.
- Never commit credentials, tokens, API keys, secrets, environment files, or exported connection data.
- Do not deploy or connect to external systems unless a later task explicitly authorizes it.
- Do not connect to n8n or create an n8n workflow during project initialization.
- Treat every AI result as a suggestion requiring human review; never represent it as an autonomous decision.
- Keep the initial architecture small and avoid frameworks or services without a demonstrated need.
- Read `STATUS.md`, the relevant task file, and applicable documentation before making changes.
- Work on one approved task at a time. Do not begin Task 001 until explicitly instructed.
- Record material architecture or security choices in `docs/04-decisions.md` and meaningful progress in `docs/05-worklog.md`.
- Add or update tests and synthetic fixtures when implementation begins.
- Preserve unrelated user changes and report verification performed.

## Definition of done for future tasks

A task is done only when its acceptance criteria are met, relevant tests pass, documentation and status are updated, no secrets or personal data are present, and the result is ready for human review. Deployment is never implied by task completion.
