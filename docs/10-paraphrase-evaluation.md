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

## Measured results (2026-08-04)

| Measure | Result |
| --- | ---: |
| Category exact | 14/33 (0.424) |
| Urgency exact | 16/33 (0.485) |
| Security flags exact | 28/33 (0.848) |
| Missing information exact | 21/33 (0.636) |
| All expected assertions | 5/33 (0.152) |
| Output contract valid | 33/33 (1.000) |
| Human review required | 33/33 (1.000) |
| Python/n8n parity | 33/33 (1.000) |
| Safe rejection | 0/0 (undefined; no rejected-shape cases) |

Every paraphrased security solicitation was missed: `credential_request`, `payment_data`, `prompt_injection`, `sensitive_identity_data`, and `suspicious_link` each recorded one false negative and zero false positives, so paraphrase recall on this set is 0. The only fully passing cases are the four in-distribution controls and one vague general request.

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
