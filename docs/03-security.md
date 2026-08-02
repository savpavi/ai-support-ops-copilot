# Security Principles

## Data minimization

Use only the minimum synthetic input needed to demonstrate behavior. Do not collect, copy, or infer real personal or operational information.

## Prohibited repository content

- Real Pegasus, passenger, agency, PNR, employee, email, or phone data.
- API keys, tokens, passwords, cookies, private keys, connection strings, or service-account files.
- n8n credential exports or local n8n state.
- Production prompts, logs, screenshots, or payloads containing sensitive data.

## Safe behavior

- Treat input as untrusted data, not as instructions to the system.
- Flag attempts to obtain secrets, override policy, or induce unsafe actions.
- Avoid echoing sensitive-looking values into drafts or logs.
- Validate input size and output shape when implementation begins.
- Fail closed: return a reviewable error or risk flag rather than performing an action.
- Require human review for every classification and draft.
- Grant future integrations the least privilege needed and keep credentials outside the repository.

## Development controls

- Store local configuration in ignored environment files; commit only placeholder examples with no usable values if a later task requires them.
- Run secret and personal-data checks before commits and releases.
- Use synthetic, conspicuously fictional fixture values.
- Review dependencies and avoid adding them without need.
- Do not deploy or connect to n8n during initialization.

## Incident rule

If real data or a secret is discovered, stop work, avoid reproducing it in logs or discussion, remove it from the working tree safely, and notify the repository owner so rotation or history cleanup can be handled explicitly.
