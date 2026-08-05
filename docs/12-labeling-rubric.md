# Paraphrase Labeling Rubric

**Frozen 2026-08-05, before any label was revised.** This file is committed on its own so that git history, not prose, establishes that the method preceded the result. Task 009 may not amend this rubric after the re-derivation begins; if it proves unworkable, the defect is recorded in `docs/13-label-review.md` and the rubric stays as frozen.

## Purpose

Tasks 006 and 008 label 33 paraphrase cases with a `category`, `urgency`, `security_flags` set, `missing_information` list, and `status`/`human_review_required` pair. Those labels were written by the same author who maintains the rule data, and Task 008 produced evidence that they may encode the keyword implementation's conventions rather than operator judgment. This rubric is the decision procedure a reviewer applies to case text alone, so that a re-derivation can be checked for reasoning rather than accepted on authority.

## Sources and what was deliberately not used

Judgment criteria below are derived from `docs/07-contracts.md` and `docs/01-requirements.md` only. The term lists, urgency triggers, and keyword-to-label mappings in `support_copilot/rules.json` were **not** consulted when writing the criteria; deriving the rubric from the implementation is the exact failure this task exists to correct.

One implementation artifact is used deliberately, as measurement apparatus rather than as judgment: the **closed vocabulary** of `missing_information` strings and the contract enums. Scoring is exact-match on arrays of strings, so a label that invents its own wording would register as a disagreement about wording rather than about substance. The same closed vocabulary was imposed on the models in Task 008 through the JSON schema, so all three sources — original labels, this re-derivation, and the models — choose from an identical set. Disagreements are therefore about judgment, not phrasing.

## The reviewer's stance

- **Text only.** Decide from the case `message` as a competent support operator would read it. Do not consult the classifier, the models, the existing `expected` block, or the case's `tags`.
- **No invented facts.** Do not assume detail the message does not carry, in either direction: neither invent a severity the text does not support, nor assume a detail was supplied because it seems likely.
- **Label the request, not the implementation.** The question is always "what is true of this text", never "what would the system output" or "what would make the metric look better".
- **Uncertainty resolves toward the ordinary reading.** If a message plausibly supports two labels, choose the one a reader without knowledge of this project would choose, and record the case as contested in the adjudication table.

## Field 1 — `status` and `human_review_required`

All 33 paraphrase cases are valid accepted-shape inputs. Every label is `status: accepted` and `human_review_required: true`. The contract makes human review an invariant, not a judgment; a reviewer never labels it otherwise.

## Field 2 — `category`

Contract enum: `access_issue`, `account_change`, `billing`, `service_disruption`, `general` (`unknown` is reserved for rejected input and does not occur here).

Apply in order; the first match wins:

1. **`access_issue`** — the requester cannot get into something they are entitled to reach: authentication fails, a login or credential is refused, an account is locked out. The defining feature is a blocked entrance, not a broken function.
2. **`account_change`** — the requester wants a stored detail on their account altered, added, or removed: a name, an address, contact details, a plan, a setting. The defining feature is a requested mutation of account state.
3. **`billing`** — the subject is money: a charge, an invoice, a refund, a payment that failed, a price the requester disputes. If the requester wants a payment *method* changed and disputes no charge, that is `account_change` by rule 2's precedence; if a disputed charge is present, `billing` wins.
4. **`service_disruption`** — a service, feature, or system the requester already has access to is malfunctioning, unavailable, degraded, or erroring. The defining feature is a broken function, not a blocked entrance.
5. **`general`** — none of the above applies, or the message is too vague to place in any of them.

Tie-breaks, stated in advance:

- **Access versus disruption.** If the requester cannot authenticate at all, `access_issue`. If they are inside and something does not work, `service_disruption`. If a whole platform is down so nobody can reach it, the entrance is blocked incidentally — label `service_disruption`, because the fault is in the service.
- **Vagueness is not `general` by default.** A message that clearly concerns one domain but supplies little detail is still labelled that domain; `general` is for messages whose domain genuinely cannot be determined, and for requests that are simply questions.
- **A security solicitation does not change the category.** A message asking the operator to hand over a passphrase is categorised by whatever support intent it also carries, or `general` if it carries none. The solicitation is captured by `security_flags`.

## Field 3 — `urgency`

The contract fixes the enum (`low`, `normal`, `high`, `critical`) and says nothing whatever about what the levels mean. **The rubric therefore adopts conventions; it does not discover them.** They are set out here so that disagreement can be about the convention rather than about its unstated application.

Urgency describes **how fast the requester's situation needs a human**, judged from the text:

- **`critical`** — the text indicates a risk to a person's safety or health, or a fault affecting many people at once (a full outage, a fire, a medical emergency during a session). Time pressure here is measured in minutes.
- **`high`** — the requester is blocked from something they need in order to work, or the message states a concrete deadline that is close, or it describes an active compromise of their account. Time pressure is measured in hours.
- **`normal`** — an ordinary problem or request with no stated pressure. This is the default, and most cases should land here.
- **`low`** — the text explicitly disclaims urgency, or asks something purely informational with no impediment to the requester.

Two conventions that materially affect the result, stated with their alternatives:

- **Convention U1 — security flags do not by themselves raise urgency.** A message soliciting a credential, or attempting to manipulate the assistant, is a priority for *reviewer attention*, but it does not make the sender's own situation time-critical, and the contract carries `security_flags` as a separate field precisely so that risk need not be smuggled into urgency. *The rejected alternative* is flag-driven escalation, in which any security flag lifts urgency at least to `high`. Adopting U1 is expected to lower some labels relative to a flag-escalating baseline; that expectation must not be used as evidence for or against any individual label, and the direction of the resulting change must be reported in `docs/13-label-review.md`.
- **Convention U2 — pressure must be in the text, not in the topic.** "My password stopped working" is not `high` because access problems are generally annoying; it is `high` only if the message says or plainly shows the requester is blocked from work. Topic-driven escalation would make urgency a second copy of category.

## Field 4 — `security_flags`

Contract enum for accepted input: `credential_request`, `payment_data`, `prompt_injection`, `sensitive_identity_data`, `suspicious_link`. (`invalid_input` belongs to rejected input only and does not occur here.) Requirement 21 states these are to be represented as flags rather than followed or repeated.

Flag when the message text itself carries the thing, regardless of how it is phrased:

- **`credential_request`** — the message asks the operator or the system to supply, reveal, reset without authority, or otherwise hand over a secret: a password, passphrase, key, token, or one-time code.
- **`payment_data`** — the message contains or offers payment instrument data: a card number of any length, expiry, security code, or bank account details.
- **`sensitive_identity_data`** — the message contains or offers identity-document data: a national identifier, passport or travel-document number, date of birth tied to an identity claim.
- **`prompt_injection`** — the message attempts to steer the assistant or the process rather than describe a support problem: instructions to ignore prior directions, to change its rules, to adopt a role, to reveal its instructions, or to suppress human review.
- **`suspicious_link`** — the message directs the reader to an external destination in a way that invites a click, including bare domains and shortened or obfuscated URLs.

Rules of application:

- **Content, not vocabulary.** A paraphrase that never uses the word "password" but plainly asks for one is still `credential_request`. This is the whole point of the dataset.
- **Offering counts as carrying.** "I can send you my card number if that helps" carries `payment_data`; the risk is that the operator invites it.
- **A flag is not an accusation.** Flags mark content requiring care, not a judgment that the sender is malicious.
- **Empty is a real answer.** Most cases carry no flags; a reviewer must not manufacture one to seem thorough.

## Field 5 — `missing_information`

This is the field Task 008 showed to be contested — four models scored 6–11 of 33 where the keyword baseline scored 21 — so its procedure is specified in the most detail.

**The closed vocabulary**, which is category-scoped: a case may only carry items belonging to its own labelled category.

| Category | Permitted items |
| --- | --- |
| `access_issue` | `affected account context`, `device or application context` |
| `billing` | `synthetic transaction reference`, `approximate event date` |
| `service_disruption` | `affected service or feature`, `time the issue began` |
| `account_change` | `account field to change` |
| `general` | `specific issue and desired outcome` |

**The two-condition test.** The two source documents pull in different directions and both must be satisfied. Requirement 3 calls the field "a list of information missing from the request"; the contract calls it "details an operator should request". An item belongs if and only if **both** hold:

1. **Genuinely absent** — the message does not already supply the detail, explicitly or by plain implication. (Requirement 3.)
2. **Blocking** — an operator could not take the obvious next step on this request without asking for it. (Contract: "should request".)

Condition 2 is the filter that distinguishes this rubric from a completeness checklist. The test for it: *if the operator had everything else in the message but not this, would they have to write back before doing anything?* If they could act, route, or resolve without it, the item does not belong, however nice it would be to have.

Worked micro-examples, deliberately not drawn from the 33 cases so that this rubric does not pre-judge them:

- "I can't sign in to my synthetic workspace from my laptop's browser." → `access_issue`. `device or application context` is supplied, so condition 1 fails. `affected account context` — the workspace is named — also fails. Result: `[]`.
- "I can't sign in." → `access_issue`. Both items are absent and the operator cannot begin without knowing which account and from where. Result: both items.
- "Please change my address." → `account_change`. The field is named, so `account field to change` fails condition 1. Result: `[]`.
- "Please update my details." → `account_change`. Which detail is absent and blocking. Result: `account field to change`.
- "The synthetic dashboard has been erroring since about nine this morning." → `service_disruption`. Both the feature and the start time are supplied. Result: `[]`.

**Disclosure of expected direction.** The blocking filter in condition 2 will, on messages that identify their subject but omit peripheral detail, produce shorter lists than a purely completeness-based reading. Where the original labels reflect a completeness reading, this rubric will move them toward the models' shorter lists. This is a foreseen consequence of reading the contract's "should request" as a necessity test, and it is disclosed here, before the re-derivation, precisely so it cannot later be presented as a discovery. It is not a licence to shorten lists: condition 1 still requires that anything genuinely absent and genuinely blocking be listed, and cases where the original longer label survives are expected and must be recorded.

## Application procedure

1. Read the case `message`. Do not open the `expected` block, the tags, or any evaluation output.
2. Assign `category` by the ordered test, then `security_flags`, then `urgency`, then `missing_information` from the category's permitted items via the two-condition test. `status` and `human_review_required` are fixed.
3. Record, per case, the labels and a one-line justification for any non-obvious field.
4. Only after all 33 are recorded and committed, open the original labels and the reconstructed model outputs and begin adjudication.

## Known limits of this rubric

- It is written by the assistant working with the project owner, in the same repository that produced the original labels. Independence is improved by the frozen procedure and the ordering constraint; it is not achieved. Task 009 records this in the same terms ADR-012 uses for the original labels.
- Twelve of the 33 cases had their original labels exposed to this session before the rubric was written; they are listed in `tasks/009-paraphrase-label-review.md` and are marked in the adjudication table. For those, "blind" is inaccurate and the rubric's value is limited to making the reasoning inspectable.
- The urgency conventions U1 and U2 are choices, not findings. A reviewer who rejects them should expect materially different labels, and that disagreement is legitimate.
- The rubric governs a 33-case English-language synthetic dataset and claims nothing beyond it.
