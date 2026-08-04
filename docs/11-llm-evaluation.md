# LLM Classifier Evaluation

## Purpose and claims boundary

Task 008 put an LLM classifier behind the exact contract and safety architecture the deterministic baseline uses, then measured four models on both committed datasets with the same runner as Tasks 003 and 006. The results quantify what semantic classification buys over keyword rules — and what it does not.

Unlike the deterministic evaluations, LLM outputs are **not reproducible**: these are dated snapshots (2026-08-04) of specific models behind a routing provider, with no drift test. The committed `docs/llm-evaluation-results.json` records what was measured, not what will always be measured.

## Architecture under test

`support_copilot/llm_classifier.py` replaces only the classification heuristics. Everything safety-relevant stays deterministic and provider-independent:

- Input validation runs before any tokens are spent; invalid input never reaches a model.
- The deterministic security scan always runs; model-reported flags are merged as a union — a model can add flags, never remove them.
- Replies remain fixed templates; the request text is passed as explicitly untrusted data.
- `validate_output` enforces the contract on every result; nonconforming model output raises `LLMClassifierError` (fail closed) instead of passing through. In production use, that error path falls back to the deterministic baseline.

Two providers: the `anthropic` SDK (pinned to `claude-haiku-4-5`) and OpenRouter (standard library HTTP, any served model, `OPENROUTER_API_KEY`). This sweep ran through OpenRouter with `temperature: 0` and a JSON-schema `response_format` derived from `rules.json`.

## Results — paraphrase dataset (33 semantic cases)

| Measure | Baseline | claude-haiku-4.5 | gpt-4o-mini | gemini-2.5-flash | deepseek-chat |
| --- | ---: | ---: | ---: | ---: | ---: |
| Category exact | 14/33 | **33/33** | 31/33 | 23/33¹ | 32/33 |
| Urgency exact | 16/33 | 27/33 | 24/33 | 21/33¹ | 24/33 |
| Security flags exact | 28/33 | 29/33 | 29/33 | 25/33¹ | 31/33 |
| Missing information exact | 21/33 | 7/33 | 6/33 | 11/33¹ | 8/33 |
| All expected assertions | 5/33 | 6/33 | 6/33 | 9/33¹ | 6/33 |
| Paraphrased security solicitations caught (of 5) | **0** | 4 | **5** | 4 | **5** |
| Guard-rejected or failed calls | 0 | 0 | 0 | 8¹ | 0 |
| Estimated cost (33 cases) | $0 | $0.033 | $0.003 | $0.006 | $0.004 |

¹ Gemini produced output the contract guard rejected (`LLMClassifierError`) on 8 paraphrase and 2 aligned cases; those cases count as failures on every metric. No unvalidated output passed through — the guard failed closed exactly as designed.

## Results — aligned dataset (44 implementation-aligned cases)

| Measure | Baseline | claude-haiku-4.5 | gpt-4o-mini | gemini-2.5-flash | deepseek-chat |
| --- | ---: | ---: | ---: | ---: | ---: |
| Category exact | 44/44 | 40/44 | 40/44 | 41/44 | 41/44 |
| Urgency exact | 44/44 | 34/44 | 32/44 | 31/44 | 35/44 |
| Security flags exact | 44/44 | 41/44 | 44/44 | 41/44 | 41/44 |
| Missing information exact | 44/44 | 16/44 | 14/44 | 21/44 | 17/44 |
| All expected assertions | 44/44 | 14/44 | 12/44 | 19/44 | 15/44 |

Safety invariants (output-contract validity and enforced human review) were 100% for every produced result across all 308 LLM calls; Gemini's shortfall above is entirely guard-rejected calls, not unsafe passes.

## Reading the results honestly

- **Semantic understanding is real and large.** On paraphrases the baseline recognized 14/33 categories; claude-haiku-4.5 recognized 33/33 and every model exceeded 31/33 except Gemini's error-depressed run. The five paraphrased security solicitations the baseline missed entirely (0/5) were caught 4–5/5 by every model.
- **The aligned dataset measures conformance to baseline conventions, not correctness.** Its labels intentionally encode the keyword rules' conventions (flag-driven urgency escalation, keyword-derived missing-information lists). LLMs "failing" it mostly means deviating from those conventions. The baseline's 44/44 and the models' 12–19/44 are answers to different questions.
- **Missing-information is a judgment domain, and the metric shows it.** The paraphrase labels are one author's judgment of what an operator would ask for; models make different — often defensible — judgments (e.g. asking for more context than the label, or none). This single field dominates the all-assertions metric for every model, which is why per-field reporting is the honest lens. Per ADR-012, labels were not revised after seeing model output.
- **The fail-closed guard earned its keep.** One of four models produced schema-nonconforming output on 10 of 77 cases; every one was rejected before reaching a caller. This is the architecture argument made empirical.
- **Cost is negligible at this scale.** The entire 308-call, four-model sweep cost roughly $0.10; the most expensive single model-dataset run was ~$0.04.

## Reproduction

```bash
python3 scripts/evaluate_requests.py --classifier llm --provider openrouter \
  --model anthropic/claude-haiku-4.5 --dataset paraphrase
```

Requires `OPENROUTER_API_KEY` (or `--provider anthropic` with the `anthropic` SDK and `ANTHROPIC_API_KEY`). Without a key the CLI exits with a clear error and the test suite runs fully offline on stub clients.

## Limitations

- Single snapshot per model; model versions behind these IDs change over time, and repeated runs can differ even at `temperature: 0`.
- Requests route through OpenRouter to the underlying providers; all content is conspicuously synthetic by project rule.
- The paraphrase labels' limited independence (single author) affects the missing-information and urgency comparisons most.
- No latency-optimized configuration was attempted; latency numbers in the results file are sequential wall-clock sums, not service-level claims.
- These are dataset observations, not production accuracy estimates.
