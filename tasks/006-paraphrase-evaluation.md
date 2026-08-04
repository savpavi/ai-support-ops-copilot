# Task 006: Out-of-Distribution Paraphrase Evaluation

## Status

- **State:** complete — 2026-08-04. All acceptance criteria verified: 51 tests pass, the paraphrase evaluation is deterministic with committed results (5/33 expected assertions, 100% safety invariants), and no behavior or artifact changed.
- **Approved scope:** measure the keyword baseline against paraphrased synthetic requests whose expected labels are assigned semantically, not aligned to the implementation. Approved by the project owner on 2026-08-04 as the second follow-up from the external review.

## Problem

The Task 003 dataset is intentionally aligned with documented supported behavior, so its 44/44 result demonstrates contract discipline, not language understanding. The honest limits of the keyword rules — missed paraphrases, missed urgency cues, missed security solicitations phrased without the trigger terms — are currently undocumented claims rather than measurements.

## Approach

1. Parameterize the existing dataset validator so coverage requirements (required tags, rejected-case requirement, flag/urgency coverage) are arguments with defaults that preserve current behavior, and let the evaluation runner accept the same options.
2. Add `fixtures/paraphrase_cases.json`: 30+ synthetic cases that express supported intents in natural phrasings that deliberately do not copy the rule terms, plus paraphrased security-sensitive content and paraphrased urgency cues.
3. Expected labels are semantic: the category, urgency, flags, and missing-information a human operator would assign from the text alone. Labels are written before running the classifier on these inputs and must not be revised to match the implementation; label disputes are resolved by review, not by rerunning.
4. Evaluate with the existing runner (quality metrics, safety invariants, parity, per-flag counts) and commit the honest machine-readable result as `docs/paraphrase-results.json` with methodology and analysis in `docs/10-paraphrase-evaluation.md`.
5. Extend `scripts/evaluate_requests.py` with a `--dataset` option selecting the aligned or paraphrase dataset.
6. Failures are measurements. No rule changes in this task; systematic defects discovered here become candidates for a separately approved task.

## Out of scope

- Changing classifier or workflow behavior, `rules.json`, or the committed workflow artifact.
- Any LLM, n8n connection, integration, activation, or deployment.
- Real customer text or identities; every case remains conspicuously synthetic.

## Acceptance criteria

1. The dataset validator accepts explicit coverage options with unchanged default behavior, and all existing tests pass unchanged.
2. `fixtures/paraphrase_cases.json` validates under the paraphrase profile: 30+ unique synthetic cases, every non-unknown category represented, every case tagged `paraphrase`.
3. The paraphrase evaluation runs deterministically; safety invariants (output-contract validity, human-review enforcement, Python/n8n parity) hold at 100% even where classification is wrong.
4. The committed `docs/paraphrase-results.json` matches the current evaluation output exactly, enforced by a drift test that does not require expected-assertion success.
5. `docs/10-paraphrase-evaluation.md` documents methodology, honest per-metric and per-flag results, representative failures, and limitations.
6. README, STATUS, worklog, and the decision record reflect the new evaluation and its claims boundary.
