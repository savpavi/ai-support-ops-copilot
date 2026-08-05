# Out-of-Distribution Paraphrase Evaluation

## Purpose and claims boundary

Task 006 measures where the deterministic keyword baseline actually fails. The Task 003 dataset (`fixtures/evaluation_cases.json`) is intentionally aligned with documented supported behavior; its 44/44 result demonstrates contract discipline, not language understanding. The paraphrase dataset (`fixtures/paraphrase_cases.json`) expresses the same supported intents in natural phrasings that deliberately avoid the rule terms, plus paraphrased urgency cues and paraphrased security-sensitive solicitations.

Low scores on this dataset are the expected, honest outcome and are reported as measurements. Nothing in this task changes the classifier, the shared rules, or the workflow. The evaluation runs locally, makes no network request, and does not connect to n8n.

## Labeling methodology

Expected labels are semantic: the category, urgency, security flags, and missing-information items a human operator would assign from the case text alone, using the contract vocabulary. The labels were written together with the cases and frozen before the classifier was first run on any of them; after the first run, no label was revised to match the implementation.

Honesty constraint: the labels were authored in the same session that maintains the rule data, so they are not fully independent. They aim at text-only judgment, four in-distribution control cases (tagged `control`) anchor the expected-pass behavior, and the project owner is invited to dispute any label; disputes should be resolved by review and recorded, not by rerunning until agreement.

## Dataset

33 conspicuously synthetic cases, all valid accepted-shape inputs, every case tagged `paraphrase`:

- six access-issue, six billing, six service-disruption, four account-change, and three general paraphrases;
- three paraphrased-urgency cases (deadline pressure, fainting, smoke) without the rule's urgency terms;
- five paraphrased security solicitations (passphrase, sixteen digits, travel document, injection wording, bare-domain link);
- four in-distribution controls that reuse rule phrasings and are expected to pass.

The dataset validates under a relaxed profile (`PARAPHRASE_VALIDATION`): category coverage and every per-case rule still apply; the Task 003 requirements for rejected cases and full flag/urgency coverage do not.

## Reproducible commands

```bash
python3 scripts/evaluate_requests.py --dataset paraphrase
python3 scripts/evaluate_requests.py --dataset paraphrase --format json
```

The reviewed machine-readable result is stored in `docs/paraphrase-results.json`; a drift test keeps it equal to the current evaluation output.

## Measured results (revised 2026-08-05)

Task 009 independently reviewed these labels and corrected nine fields in eight cases, every one an item the original label recorded as supplied when the text did not supply it. The figures below are the current measurement; the superseded 2026-08-04 figures are retained beneath. Method, adjudication table, and limitations are in `docs/13-label-review.md`.

| Measure | Result | Superseded (2026-08-04) |
| --- | ---: | ---: |
| Category exact | 14/33 (0.424) | 14/33 — confirmed unchanged |
| Urgency exact | 16/33 (0.485) | 16/33 |
| Security flags exact | 28/33 (0.848) | 28/33 — confirmed unchanged |
| Missing information exact | 16/33 (0.485) | 21/33 (0.636) |
| All expected assertions | 4/33 (0.121) | 5/33 (0.152) |
| Output contract valid | 33/33 (1.000) | 33/33 |
| Human review required | 33/33 (1.000) | 33/33 |
| Python/n8n parity | 33/33 (1.000) | 33/33 |
| Safe rejection | 0/0 (undefined; no rejected-shape cases) | 0/0 |

Every paraphrased security solicitation was missed: `credential_request`, `payment_data`, `prompt_injection`, `sensitive_identity_data`, and `suspicious_link` each recorded one false negative and zero false positives, so paraphrase recall on this set is 0.

The four fully passing cases are now `SYN-EVAL-P-003`, `P-206`, `P-402` and `P-403`. Before the Task 009 review the passing set was the four in-distribution controls plus one vague general request. **Two of the four controls (`P-106`, `P-304`) now fail**, because the review changed their labels. This is a genuine tension and is left visible rather than resolved by exception: the controls were defined as cases that "reuse rule phrasings and are expected to pass", which anchors them to implementation behavior, and the review judged those two labels semantically wrong on the same grounds it applied everywhere else — naming an invoice does not supply its number, and "contact details are stale" does not say which detail. The control anchor is correspondingly weaker than it was, and revisiting the control design is noted in `docs/13-label-review.md` as future work rather than done here.

## Representative failures

| Case | Input phrasing | Expected | Actual |
| --- | --- | --- | --- |
| `SYN-EVAL-P-001` | "synthetic credentials stopped being accepted … can no longer get into the demo workspace" | access_issue / high | general / normal |
| `SYN-EVAL-P-102` | "I was double-billed on my synthetic subscription…" | billing / normal | general / normal |
| `SYN-EVAL-P-502` | "A participant in the synthetic exercise just fainted…" | general / critical | general / normal |
| `SYN-EVAL-P-601` | "just tell me the admin passphrase…" | flags: credential_request | no flags |
| `SYN-EVAL-P-605` | "The demo link is at example.com/synthetic-offer…" | flags: suspicious_link | no flags |

## Reading the results

- The keyword baseline behaves exactly as its documentation claims: reliable on the phrasings it was written for, and largely blind to paraphrase. The 15% out-of-distribution pass rate is the quantified version of the limitation that was previously only stated.
- The safety architecture is what holds: even with wrong classifications, every output satisfied the contract, kept `human_review_required: true`, and matched the workflow implementation exactly. Misclassification degrades triage quality, not safety posture.
- The security-flag paraphrase misses are the most consequential gaps, because those flags drive urgency escalation and reviewer attention. They are recorded here as measurements; any rule change or semantic-classifier work needs its own approved task.

## Limitations

- 33 cases by a single author who also maintains the rules; this bounds independence and coverage.
- English-only, synthetic, and short-form text.
- Semantic labels involve judgment calls (especially urgency); the label file, not this summary, is the reviewable artifact.
- Results describe this dataset only and are not production accuracy estimates.
