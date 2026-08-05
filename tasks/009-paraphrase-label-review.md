# Task 009: Independent Review of the Paraphrase Labels

## Status

- **State:** complete — 2026-08-05. All acceptance criteria met: rubric frozen in its own commit before any revision, all 33 cases blind re-derived and committed before the originals were opened, nine fields in eight cases adjudicated and changed, model snapshot re-scored with no new API call, 64 tests passing offline. Results in `docs/13-label-review.md`.
- **Owner decisions (2026-08-05):** (1) the practical option — assistant re-derivation under the frozen rubric, owner adjudicates differences; independence is improved, not achieved, and the write-up must say so. (2) Model outputs enter adjudication only after the blind re-derivation is committed. (3) Whatever the review measures is published, including a fallen headline number.
- **Artifacts:** the rubric is `docs/12-labeling-rubric.md`, committed on its own before any label is revised so the ordering is auditable in git history; the review is `docs/13-label-review.md`.
- **Position in the approved sequence:** first of three approved follow-ups (009 label review, 010 baseline-fallback wrapper, 011 LLM-drafted replies). It runs first because it defines the ground truth the other two are measured against.
- **Motivation:** `docs/10-paraphrase-evaluation.md` and ADR-012 both record that the paraphrase labels were authored in the same session that maintains the rule data, which bounds their independence. Task 008 turned that caveat into evidence: four independent models scored 33/33, 32/33, 31/33 and 23/33 on category but only 7, 8, 6 and 11 of 33 on missing information, against a baseline that scores 21/33 on the same field. A single field now dominates the all-assertions metric for every model. Either the labels encode baseline conventions rather than operator judgment, or four models are independently wrong in the same direction. The project currently cannot say which.

## Problem

The paraphrase dataset is the project's only measurement of language understanding, and every comparison in Tasks 006 and 008 is stated relative to its labels. If those labels are partly a restatement of the keyword rules, then:

- the baseline's 21/33 on missing information is inflated by construction, and
- every model's 6–11/33 is a penalty for disagreeing with the implementation rather than for being wrong.

ADR-012 forbids the obvious failure mode — revising labels until results improve — and that prohibition stays in force. What is missing is the sanctioned alternative it names: resolving disputes **by review, recorded**, rather than by rerunning. This task performs that review once, under a method fixed in advance.

## Approach

1. **Write the labeling rubric first, from the contract, not from the code.** Derive from `docs/07-contracts.md` and `docs/01-requirements.md` an explicit decision procedure for each labelled field, above all `missing_information` (what must an operator ask for before acting, versus what is merely nice to have?) and `urgency` (what evidence in text alone justifies each level?). Commit `docs/12-labeling-rubric.md` on its own, before any label is revised, so the ordering is verifiable in git history rather than asserted in prose. Where the contract is genuinely silent, the rubric states the convention it adopts and why.
2. **Re-derive all 33 labels blind.** Working from the case text and the frozen rubric only — not from the existing `expected` blocks, not from baseline output, not from model output — produce an independent label set for every case. All 33, not only the disputed ones: reviewing only the cases the models challenged would bias the outcome toward whatever the models preferred.
3. **Three-way diff and adjudication.** Compare, per case and per field: the original 2026-08-04 label, the blind re-derivation, and the reconstructed model outputs (see step 4). Every difference is adjudicated against the rubric with a written justification, and every adjudication is recorded — including the ones where the original label survives, which are the evidence that the review was not a rewrite.
4. **Re-score the existing model snapshot without new API calls.** `docs/llm-evaluation-results.json` records, for each failed case, the model's actual value on every mismatched field; on fields absent from a case's mismatches the model's value equals the original label. The four models' per-case outputs are therefore reconstructible for all labelled fields, and the 2026-08-04 snapshot can be re-scored against revised labels without contacting any provider.

   The reconstruction rule was verified against the published tables while this task was written: replaying it over the paraphrase runs reproduces `docs/11-llm-evaluation.md` exactly for all four models (category 33/32/23/31, urgency 27/24/21/24, security flags 29/31/25/29, missing information 7/8/11/6). Guard-rejected calls are identifiable because every field carries `actual: null` and all four checks fail together; they have no output to re-score and must be excluded from re-scored per-field denominators rather than silently counted as matches. Implementation must re-verify the same replay on the aligned runs before relying on it.
5. **Regenerate the deterministic results and republish honestly.** Re-run the baseline paraphrase evaluation, regenerate `docs/paraphrase-results.json`, and update its drift test. The superseded 2026-08-04 figures stay in the record as superseded, with the revision and its reason stated; they are not overwritten as if they had never been measured.
6. **Report the direction of the correction.** State plainly whether the review moved the labels toward the baseline, toward the models, or neither, and how many labels changed. A review that changed nothing is a publishable result; so is one that invalidates a headline number.

## Out of scope

- Any change to `rules.json`, the classifier, the workflow artifact, or contract version `1.0`. If the review shows the baseline is right and the models are wrong, that is a finding, not a licence to edit rules.
- The aligned dataset (`fixtures/evaluation_cases.json`). Its labels deliberately encode baseline conventions and `docs/11-llm-evaluation.md` already says so; reviewing it would be a different task with a different purpose.
- Adding, removing, or rewording paraphrase **cases**. Only the `expected` blocks are under review; changing the inputs would break comparability with both prior evaluations.
- New live LLM calls, LLM-drafted replies, the fallback wrapper, n8n changes, activation, or deployment.

## Acceptance criteria

1. `docs/12-labeling-rubric.md` is committed in its own commit, before any label is revised, so the ordering is verifiable in git history; it covers all five labelled fields and states its adopted conventions where the contract is silent.
2. All 33 cases have a blind re-derivation recorded, produced from case text and rubric alone, and the twelve pre-contaminated cases listed below are marked as such per case rather than presented as blind.
3. Every per-field difference among original label, blind re-derivation, and reconstructed model output is adjudicated with a written justification; unchanged labels are recorded as adjudicated, not as skipped.
4. The reconstruction of the four models' per-case outputs from `docs/llm-evaluation-results.json` reproduces the originally reported per-field counts exactly on both datasets, and guard-rejected calls (all-`null` actuals) are excluded from re-scored denominators rather than treated as matches.
5. No new API call is made; `docs/llm-evaluation-results.json` keeps its 2026-08-04 snapshot as measured, with re-scored figures published separately and clearly marked as re-scored against revised labels.
6. `fixtures/paraphrase_cases.json` validates unchanged under `PARAPHRASE_VALIDATION`; case inputs, identifiers, tags, and count are byte-identical apart from adjudicated `expected` blocks.
7. `docs/paraphrase-results.json` matches the regenerated evaluation output exactly and its drift test passes; the full suite (currently 64 tests) passes offline and key-less.
8. `docs/13-label-review.md` documents the method, the per-case adjudication table, before/after metrics for baseline and all four models, the direction and size of the correction, and the contamination disclosure below.
9. `docs/10-paraphrase-evaluation.md` and `docs/11-llm-evaluation.md` carry the revised figures with the superseded ones retained and marked; README, `docs/06-portfolio-case-study.md`, STATUS, worklog, and a new ADR-015 reflect the outcome.
10. No secrets, credentials, or real data; every case remains conspicuously synthetic.

## Known contamination of the blind re-derivation

The scoping session that produced this task read published evidence that exposes original labels for twelve of the 33 cases, before the re-derivation begins. Concealing that would defeat the purpose of the task, so it is recorded here and must be carried into `docs/13-label-review.md` and the limitations of `docs/10-paraphrase-evaluation.md`:

- from the representative-failures table in `docs/10-paraphrase-evaluation.md`: `SYN-EVAL-P-001`, `P-102`, `P-502`, `P-601`, `P-605`;
- from the first record of `fixtures/paraphrase_cases.json`, read while inspecting the file shape: `SYN-EVAL-P-001`;
- from the Gemini failure entries of `docs/llm-evaluation-results.json`, read while verifying reconstructability: `SYN-EVAL-P-003`, `P-006`, `P-201`, `P-203`, `P-205`, `P-206`, `P-401`, `P-605`.

Twelve distinct cases are affected; the remaining twenty-one are re-derived without prior sight of their labels. Contaminated cases are re-derived and adjudicated like the rest but are marked in the adjudication table, and any label change among them carries less evidential weight than a change among the twenty-one. If the correction turns out to be concentrated in the contaminated twelve, that fact is itself a result and must be reported.

## Owner decisions (resolved 2026-08-05)

1. **Who performs the blind re-derivation.** The strongest option was the owner labeling the 33 cases personally from the rubric, the only genuinely independent human judgment available to this project; the practical option was an assistant re-derivation under the frozen rubric with the owner adjudicating differences. **Decided: the practical option.** The residual dependence is stated in the limitations exactly as ADR-012 states the current one — independence here is improved, not achieved, and the write-up must say so.
2. **Whether model outputs enter the adjudication.** **Decided: yes, but only after the blind re-derivation is committed,** so the anchoring risk is bounded by ordering rather than by intention.
3. **What happens if a headline number falls.** The published baseline figure of 5/33 all-assertions and the models' 31–33/33 category results may both move. **Decided: publish whatever is measured,** per ADR-012; a fallen number is the deliverable, not a problem to fix in this task.

## Safety constraints

- Synthetic data only; no network access is required or permitted for this task.
- No rule or classifier change may be introduced under the description of a label correction.
- Results are advisory measurements of a 33-case dataset, not production accuracy estimates; the claims boundary of Tasks 006 and 008 carries over unchanged.
