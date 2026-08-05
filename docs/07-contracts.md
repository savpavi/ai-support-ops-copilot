# Task 001 Input and Output Contracts

## Input contract

The classifier accepts one JSON object with exactly two fields:

| Field | Type | Rules |
| --- | --- | --- |
| `request_id` | string | Must be a conspicuously synthetic identifier matching `SYN-[A-Z0-9-]`, 7–44 characters total. |
| `message` | string | After trimming, must be non-empty and no longer than 4,000 characters. Treated only as untrusted data. |

Unknown fields, missing fields, wrong types, invalid identifiers, empty messages, and overlong messages are rejected. Text inside `message` is never evaluated as code or system instructions. For defense in depth, rejected objects are still security-scanned in known textual fields (`message` and the non-contract alias `request_text`); scanning an alias does not make that alias valid input.

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

## Reply guard

`suggested_reply` may be written by a model when drafted replies are explicitly enabled (Task 011, off by default). Generated text passes `validate_reply` before it can reach the contract object; a rejected draft degrades only the reply to the deterministic template, leaving the classification intact, and the result still satisfies the output contract with `human_review_required: true`.

The guard's data lives in `support_copilot/rules.json` under `reply_guard`, so the same checks can be replicated in the workflow JavaScript if generated text ever reaches n8n. It rejects a draft that: omits or alters the `Draft for human review:` prefix; exceeds the length bound; contains any link or destination, including bare domains, which is stricter than the request-side scan because a draft reply has no legitimate destination to carry; trips the deterministic security scan when that scan is run on the reply itself, catching a reflected credential, card number, identity-document reference or injection attempt; or matches listed commitment phrasing.

The first four checks are exact for the patterns they hold. The commitment check is a term list and is a floor, not a semantic guarantee; the guard also has no concept of negation, so a refusal that names the secret it is refusing is rejected along with a disclosure of it. Measured behavior and limits are in `docs/14-reply-safety.md`.

## Compatibility boundary

The contracts are plain JSON and contain no n8n-specific fields. The Task 002 artifact transports these objects and replicates Task 001 rules in a Code node, followed by an independent Human Review Guard. Local parity tests confirm complete object equality with the Python reference for the committed fixtures. Native n8n import and execution remain version-dependent manual verification. Any n8n migration must not weaken validation, reinterpret request text as instructions, or alter the human-review invariant.
