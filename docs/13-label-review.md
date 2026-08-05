# Independent Review of the Paraphrase Labels

## Purpose and outcome in one paragraph

Task 008 measured four models at 31–33/33 on paraphrase category recognition but 6–11/33 on missing information, against a keyword baseline scoring 21/33 on that same field. Task 009 asked whether the labels were encoding the implementation's conventions rather than operator judgment. The answer is mostly no. Category and security-flag labels were confirmed unchanged at 33/33 and 33/33. Nine fields across eight of the 33 cases were corrected, every one of them an item the original label recorded as supplied when the text did not supply it. The correction lowered the deterministic baseline (missing information 21/33 → 16/33, all expected assertions 5/33 → 4/33) and raised every model. Two findings weaken the premise the task was built on, and both are reported below because they were discovered by doing the review.

## Method

The procedure was fixed before the result, in this order, each step committed before the next began:

1. `docs/12-labeling-rubric.md` was derived from `docs/07-contracts.md` and `docs/01-requirements.md`. The term lists and keyword mappings in `support_copilot/rules.json` were not consulted. The rubric names its own conventions where the contract is silent, and pre-registers their expected direction.
2. All 33 cases were re-derived from `case_id` and `input.message` alone — no `expected` block, no tags, no descriptions, no classifier or model output — and committed as `docs/blind-relabel.json` with a per-case justification.
3. Only then were the original labels and the model outputs opened, and every difference adjudicated.

The ordering is verifiable in git history (`931a8c3` froze the rubric, `09e9765` committed the re-derivation) rather than asserted in prose.

### Independence, stated plainly

The re-derivation was performed by the assistant working in the same repository that produced the original labels, with the project owner adjudicating. **Independence is improved by the frozen procedure and the ordering constraint; it is not achieved.** ADR-012 records the same limitation for the original labels, and this review does not escape it.

Twelve of the 33 cases had their original labels exposed to the scoping session before the rubric was written (`SYN-EVAL-P-001`, `P-003`, `P-006`, `P-102`, `P-201`, `P-203`, `P-205`, `P-206`, `P-401`, `P-502`, `P-601`, `P-605`); they are marked `C` in the adjudication table. For those, "blind" is inaccurate. One of the nine adopted changes falls in that set (`P-605`), so the correction is not concentrated in the contaminated cases.

### Re-scoring without new API calls

`docs/llm-evaluation-results.json` stores, per failed case, the model's actual value on every mismatched field; on fields absent from a case's mismatches the model's value equals the original label. Per-case outputs are therefore reconstructible, and the reconstruction reproduces the published per-field counts **exactly on both datasets** (paraphrase 33/32/23/31 category, 27/24/21/24 urgency, 29/31/25/29 flags, 7/8/11/6 missing; aligned 40/41/41/40, 34/35/31/32, 41/41/41/44, 16/17/21/14), with 8 paraphrase and 2 aligned guard rejections matching the documented 10 of 308. No provider was contacted. Guard-rejected calls carry no output and are excluded from the counts rather than scored as matches.

## The adjudication rule

A label was changed only where **the blind re-derivation and every model that produced output agreed against the original**, applied per vocabulary item for `missing_information` and per value for the scalar fields. Rejecting the original was not sufficient: a replacement had to converge.

That distinction did most of the work. On `P-001`, all four models reject the original list — but they want *more* items and the blind re-derivation wants *fewer*, so no replacement converged and the original stands. The same holds for `P-004`, `P-202`, `P-203` and `P-601`. Eleven fields sit in this bucket: refuted from both directions, corrected in neither.

**The rule's built-in circularity must be stated.** Because model unanimity is one of its conditions, every changed field is one the models already agreed on, so their scores necessarily improve. The model gains below are therefore not independent evidence that the models are right. The independent part of the signal is that the blind re-derivation, made under a frozen rubric with no sight of model output, arrived at the same items.

## Two findings that weaken the task's premise

**The Task 008 system prompt taught the models the baseline's urgency convention.** `_system_prompt` in `support_copilot/llm_classifier.py` instructs: *"high for blocked access, significant outages, explicit urgency, or security-sensitive content"*. That is topic-driven escalation plus flag-driven escalation — precisely the conventions the rubric set out to test rather than assume. Model agreement with the original urgency labels is therefore not independent corroboration, and Task 008's urgency comparison was in part a test of instruction-following. Where models *deviated* from that instruction to agree with the blind re-derivation (`P-604`, and 3-of-4 on `P-602` and `P-603`), the evidence is correspondingly stronger.

**The "labels echo the keyword rules" hypothesis is not supported in aggregate.** Measuring how often each label set equals what the rule table would emit given the label's own category: original labels 19/33, models 15–18/33, blind re-derivation 12/33. Models that never saw the rule table land almost as close to it as the original labels do, which means a 19/33 overlap is evidence that the rules are a reasonable heuristic, not evidence of copying. The echo is real only at case level, in the billing cluster below.

**A pre-registered expectation was refuted.** The rubric predicted that its blocking filter would shorten lists and move labels toward the models. The opposite occurred: models produce systematically *longer* lists than the original labels, not shorter. `docs/11-llm-evaluation.md` read the disagreement as models "asking for more context than the label, or none"; the sharper statement is that they mostly ask for more.

## What was actually wrong: naming a thing is not identifying it

Every one of the nine adopted changes is an addition. Not a single unanimous convergence removed an item. The pattern is one error repeated: the original label treats a detail as supplied because the message *mentions the category of thing* that would carry it.

| Case | Text | Original | Adopted |
| --- | --- | --- | --- |
| P-101 | "debited twice for the same demo **order** last night" | reference not missing | reference missing |
| P-103 | "the amount shown on my demo **receipt**" | reference not missing | reference missing |
| P-106 | "my synthetic **invoice** from yesterday" | reference not missing | reference missing |

Saying you have an invoice is not giving its number. In all three the baseline's trigger term for that item (`order`, `receipt`, `invoice`) is present in the text, which is why the label suppressed it — so at case level the echo hypothesis holds, even though it fails in aggregate. `P-304` ("contact details are stale") and `P-604`/`P-605` (no stated support intent) are the same error in other categories.

`P-204` is the one change of a different kind: "the demo feature I rely on is completely dead" names no feature and states dependence, and all four models plus the blind re-derivation read it as both a missing identifier and a high-urgency situation where the original said normal.

## Adjudication table

All 33 cases were adjudicated. The ten cases where the blind re-derivation matched the original on every field — `P-105`, `P-206`, `P-301`, `P-302`, `P-303`, `P-401`, `P-402`, `P-403`, `P-502`, `P-503` — are recorded here as confirmed, not skipped. The remaining 23 differed on at least one field:

| Case | Field | Original | Blind | Models vs original | Outcome |
| --- | --- | --- | --- | --- | --- |
| P-001C | urgency | high | normal | 0/4 reject | original stands |
| P-001C | missing information | device or application context | — | 4/4 reject | original stands |
| P-002 | urgency | high | normal | 1/4 reject | original stands |
| P-002 | missing information | affected account context, device or application context | — | 0/4 reject | original stands |
| P-003C | urgency | high | normal | 0/3 reject, 1 guard | original stands |
| P-003C | missing information | device or application context | — | 3/3 reject, 1 guard | original stands |
| P-004 | urgency | high | normal | 1/4 reject | original stands |
| P-004 | missing information | device or application context | — | 4/4 reject | original stands |
| P-005 | urgency | high | normal | 0/4 reject | original stands |
| P-005 | missing information | affected account context | — | 3/4 reject | original stands |
| P-006C | missing information | device or application context | — | 3/3 reject, 1 guard | original stands |
| P-101 | missing information | — | synthetic transaction reference | 4/4 reject | **changed → synthetic transaction reference** |
| P-102C | missing information | synthetic transaction reference, approximate event date | synthetic transaction reference | 0/4 reject | original stands |
| P-103 | missing information | approximate event date | synthetic transaction reference | 4/4 reject | **changed → synthetic transaction reference, approximate event date** |
| P-104 | missing information | synthetic transaction reference, approximate event date | synthetic transaction reference | 0/4 reject | original stands |
| P-106 | missing information | — | synthetic transaction reference | 4/4 reject | **changed → synthetic transaction reference** |
| P-201C | urgency | high | normal | 0/3 reject, 1 guard | original stands |
| P-202 | missing information | time the issue began | — | 4/4 reject | original stands |
| P-203C | missing information | affected service or feature | — | 3/3 reject, 1 guard | original stands |
| P-204 | urgency | normal | high | 4/4 reject | **changed → high** |
| P-204 | missing information | time the issue began | affected service or feature | 4/4 reject | **changed → affected service or feature, time the issue began** |
| P-205C | urgency | high | critical | 0/3 reject, 1 guard | original stands |
| P-304 | missing information | — | account field to change | 4/4 reject | **changed → account field to change** |
| P-501 | missing information | synthetic transaction reference, approximate event date | synthetic transaction reference | 0/4 reject | original stands |
| P-601C | urgency | high | normal | 2/4 reject | original stands |
| P-601C | missing information | — | specific issue and desired outcome | 4/4 reject | original stands |
| P-602 | urgency | high | normal | 3/4 reject | original stands |
| P-602 | missing information | — | specific issue and desired outcome | 3/4 reject | original stands |
| P-603 | urgency | high | normal | 3/4 reject | original stands |
| P-603 | missing information | — | specific issue and desired outcome | 3/4 reject | original stands |
| P-604 | urgency | high | normal | 4/4 reject | **changed → normal** |
| P-604 | missing information | — | specific issue and desired outcome | 4/4 reject | **changed → specific issue and desired outcome** |
| P-605C | urgency | high | normal | 1/3 reject, 1 guard | original stands |
| P-605C | missing information | — | specific issue and desired outcome | 3/3 reject, 1 guard | **changed → specific issue and desired outcome** |

`C` marks a contaminated case. "Models vs original" counts how many produced outputs reject the original value, which is not the same as agreeing with the blind value — the change rule required the latter.

## Results after revision

Deterministic baseline, `docs/paraphrase-results.json` regenerated and drift-tested:

| Measure | Original labels | Revised labels |
| --- | ---: | ---: |
| Category exact | 14/33 | 14/33 |
| Urgency exact | 16/33 | 16/33 |
| Security flags exact | 28/33 | 28/33 |
| Missing information exact | 21/33 | **16/33** |
| All expected assertions | 5/33 | **4/33** |
| Output contract valid | 33/33 | 33/33 |
| Human review required | 33/33 | 33/33 |
| Python/n8n parity | 33/33 | 33/33 |

The 2026-08-04 model snapshot re-scored against the revised labels (no new API calls; see the circularity caveat above). Denominators exclude guard-rejected calls:

| Model | Category | Urgency | Security flags | Missing information | All assertions |
| --- | ---: | ---: | ---: | ---: | ---: |
| claude-haiku-4.5 | 33 → 33 | 27 → 29 | 29 → 29 | 7 → **12** | 6 → **9** |
| deepseek-chat | 32 → 32 | 24 → 26 | 31 → 31 | 8 → **13** | 6 → **9** |
| gemini-2.5-flash | 23 → 23 | 21 → 23 | 25 → 25 | 11 → **17** | 9 → **15** |
| gpt-4o-mini | 31 → 31 | 24 → 26 | 29 → 29 | 6 → **11** | 6 → **10** |

Machine-readable figures are in `docs/label-review-rescored.json`. The original snapshot in `docs/llm-evaluation-results.json` is untouched and remains the record of what was measured on 2026-08-04.

## Direction and size of the correction

Nine fields in eight of 33 cases changed — roughly 7% of the 165 labelled fields. All nine moved toward the models and away from the deterministic baseline, which is why the baseline falls and every model rises. Category and security-flag labels, which carry the headline claims of Tasks 006 and 008, were confirmed without a single change.

The headline that moves is the baseline's own: paraphrase all-expected-assertions falls from 5/33 to 4/33, and missing-information from 21/33 to 16/33. Per ADR-012 that is published as measured. The claim it supports — that the keyword baseline is largely blind out of distribution — is unchanged in substance and slightly stronger in degree.

## A consequence worth flagging: two controls now fail

The dataset carries four in-distribution control cases (`P-003`, `P-106`, `P-206`, `P-304`) defined in Task 006 as cases that "reuse rule phrasings and are expected to pass", anchoring the expected-pass end of the dataset. Two of them, `P-106` and `P-304`, are among the eight cases the review changed, and both now fail.

The review did not treat them as exempt, and that was deliberate: applying the adjudication rule everywhere except where it produced inconvenient results would have made the whole exercise unfalsifiable. But the outcome exposes something about the controls themselves — "expected to pass" was defined by reference to implementation behavior, so a control label cannot disagree with the implementation by construction. That is the same circularity Task 009 was created to look for, sitting in the anchor rather than in the paraphrases.

The correction stands, the control anchor is weaker than it was, and redesigning controls so they anchor to operator judgment rather than to rule phrasings is left as future work with no approved scope.

## Limitations

- Independence is improved, not achieved; see above. Twelve cases were contaminated before the rubric existed.
- The adjudication rule guarantees model improvement on changed fields. Read the model table as "the labels now agree with what the models and an independent re-derivation both said", not as a measurement of model quality.
- The urgency conventions U1 and U2 in the rubric are choices. Where they disagreed with the original labels without unanimous support, the original stands and the disagreement is recorded rather than acted on — the blind re-derivation agrees with the *keyword baseline* on urgency more often than the original labels do (24/33 versus 16/33), which is a mark against the rubric's conventions, not for them.
- Eleven fields are refuted from both directions with no converged replacement; they remain as originally labelled and are the natural target of any future review.
- No rule, classifier, workflow, or contract change was made. The findings about `_system_prompt` are recorded, not acted on; changing it would need its own approved task.
- 33 English-language synthetic cases. Nothing here is a production accuracy estimate.
