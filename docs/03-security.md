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

## Task 002 controls

- Use a user-authorized development n8n instance on a local or isolated network only.
- Import an inactive workflow through the authenticated development UI; keep UI credentials and connection details outside the repository.
- Use only built-in Manual Trigger, Edit Fields/Set, and Code nodes. Do not use webhooks, schedules, HTTP requests, AI nodes, Execute Command, filesystem writes, databases, or message/action nodes.
- Give Code nodes no secrets, credentials, filesystem dependency, subprocess access requirement, or external-network requirement.
- Treat request text only as a string value; never evaluate it or use it to choose expressions, property paths, nodes, or control flow.
- Keep a separate final guard that validates the exact output contract and forces `human_review_required: true`.
- Minimize or disable execution retention where supported and use only reviewed synthetic fixtures.
- Before committing an export, verify it is inactive and scan for credential attachments, tokens, cookies, instance URLs and IDs, webhook data, personal data, and unexpected node types.
- Require human approval before import, first execution, export, re-import verification, activation, or any production use. Task 002 does not authorize the last two actions.

The committed workflow currently satisfies the local static controls: it is inactive, contains only the four allowlisted built-in nodes, carries no credential attachment or instance metadata, uses synthetic default input, and ends at the Human Review Guard. These controls must be rechecked after native n8n import/export because the target instance can add metadata or apply version-specific migrations.

Prompt-injection detection uses bounded deterministic patterns for explicit control manipulation: overriding prior/system instructions, disabling review, automatic approval/execution, protected-output-field changes, hidden-prompt disclosure, and safety bypass. Rejected objects are also risk-scanned in known text fields so malformed shape cannot suppress a prompt-injection flag. Ordinary requests mentioning approval remain unflagged unless they include a clear control or autonomy-bypass instruction.

Credential-request detection uses bounded credential terms so ordinary synthetic words such as `passwordless` are not treated as credential requests. Python and workflow JavaScript carry the same rule and are checked for complete parity.

## Task 003 evaluation controls

- Run evaluation locally without network access or an n8n connection.
- Keep expected labels separate from classifier-generated output and treat them as review assertions, not production truth.
- Emit only synthetic case identifiers, structured mismatch fields, counts, and rates; do not echo request text into reports.
- Represent undefined metric rates explicitly as `null` or `undefined` rather than hiding missing evidence.
- Preserve the mandatory human-review and output-contract checks as safety metrics distinct from heuristic quality observations.

## Incident rule

If real data or a secret is discovered, stop work, avoid reproducing it in logs or discussion, remove it from the working tree safely, and notify the repository owner so rotation or history cleanup can be handled explicitly.
