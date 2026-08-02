# Task 001 Input and Output Contracts

## Input contract

The classifier accepts one JSON object with exactly two fields:

| Field | Type | Rules |
| --- | --- | --- |
| `request_id` | string | Must be a conspicuously synthetic identifier matching `SYN-[A-Z0-9-]`, 7–44 characters total. |
| `message` | string | After trimming, must be non-empty and no longer than 4,000 characters. Treated only as untrusted data. |

Unknown fields, missing fields, wrong types, invalid identifiers, empty messages, and overlong messages are rejected. Text inside `message` is never evaluated as code or system instructions.

Example synthetic input:

```json
{
  "request_id": "SYN-EXAMPLE-01",
  "message": "The synthetic demo dashboard stopped working ten minutes ago."
}
```

## Output contract

Every call returns one JSON object with exactly these fields:

| Field | Type | Rules |
| --- | --- | --- |
| `schema_version` | string | Currently `1.0`. |
| `status` | string | `accepted` or `rejected`. |
| `request_id` | string or null | Validated synthetic identifier, or `null` when it cannot be trusted. |
| `category` | string | `access_issue`, `account_change`, `billing`, `service_disruption`, `general`, or `unknown`. |
| `urgency` | string | `low`, `normal`, `high`, `critical`, or `unknown`. |
| `rationale` | string | Concise deterministic explanation. |
| `missing_information` | array of strings | Details an operator should request; never invented facts. |
| `suggested_reply` | string | Always begins `Draft for human review:`. |
| `security_flags` | array of strings | Zero or more validated risk codes. |
| `human_review_required` | boolean | Always and only `true`. |
| `errors` | array of strings | Empty for accepted input; populated for rejected input. |

Allowed security flags are `credential_request`, `invalid_input`, `payment_data`, `prompt_injection`, `sensitive_identity_data`, and `suspicious_link`.

Rejected inputs use `category: unknown` and `urgency: unknown`, include `invalid_input`, and still produce a reviewable draft with `human_review_required: true`. Output validation rejects missing or extra fields, invalid enum values, an unmarked reply draft, or any attempt to set human review to false.

## Compatibility boundary

The contracts are plain JSON and contain no n8n-specific fields. The Task 002 artifact transports these objects and replicates Task 001 rules in a Code node, followed by an independent Human Review Guard. Local parity tests confirm complete object equality with the Python reference for the committed fixtures. Native n8n import and execution remain version-dependent manual verification. Any n8n migration must not weaken validation, reinterpret request text as instructions, or alter the human-review invariant.
