# Task 008 Proposal: Semantic Classification with an LLM

## Status

- **State:** proposal — owner decisions pending. No implementation is authorized by this document.
- **Motivation:** the Task 006 paraphrase evaluation quantified the keyword baseline's limit: 5/33 semantic expectations out of distribution, with zero recall on paraphrased security solicitations. The project is named "AI Support Operations Copilot" and currently contains no AI. The evaluation framework, contracts, and safety architecture built in Tasks 001–007 exist precisely to measure and constrain a semantic classifier.

## Options considered

### Option A — Claude API behind the existing contract (recommended)

A new `support_copilot` module calls the Claude API with structured outputs. The LLM replaces only the classification heuristics (category, urgency, missing information); everything else stays deterministic:

- Input validation runs first — malformed input is rejected before any tokens are spent.
- The deterministic prompt-injection and security-flag scan still runs; LLM-reported flags are merged as a union (the LLM can add flags, never remove them).
- The request text is passed to the model as untrusted data with a fixed system prompt; the model returns a JSON object constrained by a schema derived from `rules.json` enums (structured outputs guarantee schema validity).
- `validate_output` and the workflow's Human Review Guard still enforce the contract: `human_review_required: true` is forced, the reply prefix is enforced, unknown enum values are rejected. A misbehaving model cannot weaken the safety posture.
- On API error or refusal, the deterministic baseline is the fallback, so the system degrades gracefully to today's behavior.
- Suggested replies stay templated in the first phase; LLM-drafted replies are a separate later decision.

Both evaluation datasets run unchanged against the new engine via `--classifier llm`, producing the honest comparison table (baseline vs LLM, aligned vs paraphrase) that is the point of the exercise.

### Option B — Anthropic node inside the n8n workflow

Rejected for now: it would put credentials into the workflow (currently forbidden by the project's own rules and ADR-006's sanitization constraints), is much harder to test and keep in parity, and duplicates what Option A proves more cleanly. Can be revisited after Option A, with the n8n workflow remaining the deterministic-baseline path.

### Option C — Local model (e.g. Ollama)

Rejected: heavyweight setup, materially weaker quality at locally-runnable sizes, and lower portfolio value than a production-grade API integration with measured results. The offline story is already covered by the deterministic baseline.

## Model options and cost estimates

Prices are Anthropic first-party API rates (skill reference, cached 2026-06-24). Assumptions: ~2.5K input tokens per request (system prompt with contract, rules vocabulary, and a few examples, plus the message), ~0.8K output tokens including thinking, no cache hits. Estimates, not quotes.

| Model | Input $/MTok | Output $/MTok | ≈ per request | ≈ per full eval sweep (77 cases) |
| --- | ---: | ---: | ---: | ---: |
| `claude-opus-5` | $5.00 | $25.00 | ~$0.033 | ~$2.50 |
| `claude-sonnet-5` | $3.00 ($2.00 intro to 2026-08-31) | $15.00 ($10.00 intro) | ~$0.020 (intro ~$0.013) | ~$1.50 (intro ~$1.00) |
| `claude-haiku-4-5` | $1.00 | $5.00 | ~$0.007 | ~$0.55 |

Cost-relevant mechanics:

- **Prompt caching** cuts the repeated system-prompt cost by ~90% on cache hits within a sweep. Minimum cacheable prefix: 512 tokens on Opus 5, 1024 on Sonnet 5, 4096 on Haiku 4.5 — our ~2K prompt caches on Opus/Sonnet but not on Haiku.
- **Batch API** halves token prices for non-latency-sensitive runs; evaluation sweeps are a natural fit.
- At this project's scale (synthetic-only, tens of eval runs), total spend is single-digit dollars per month for any model choice. Cost is a portfolio-narrative variable here, not a budget risk.

## Recommendation

Option A, and rather than picking one model by intuition, **measure two or three** (`claude-opus-5` as the reference plus `claude-haiku-4-5` and/or `claude-sonnet-5`) on both committed datasets with the same runner, and let the resulting table pick the production default. The full three-model double-dataset sweep costs roughly $5. The deliverable becomes: baseline 5/33 vs each model's X/33 on paraphrases, with identical 100% safety invariants, plus measured latency and cost per request — a far stronger portfolio artifact than a single-model result.

## Decisions the owner must make before implementation

1. **Dependency stance.** The clean path adds the official `anthropic` Python SDK as the project's first runtime dependency (optional at import: the deterministic baseline stays dependency-free). The alternative keeps zero dependencies by calling the REST API with the standard library, at the cost of hand-rolled request/retry/typing code. Recommendation: add the SDK, scoped as an optional extra.
2. **Models to evaluate** (any subset of the table above). Recommendation: Opus 5 + Haiku 4.5 at minimum; add Sonnet 5 if the intro-pricing window matters to the narrative.
3. **Key handling.** `ANTHROPIC_API_KEY` via environment only; never in the repository; LLM tests and evaluations skip automatically when the key is absent, so CI stays deterministic and key-less. (A separately approved CI secret could later run a scheduled live sweep; not part of this proposal.)
4. **Scope confirmation.** Classification only; templated replies unchanged; no n8n changes; contract stays at version `1.0` (the engine choice is operational, not contractual).

## Safety constraints carried into any implementation

- Synthetic data only, as everywhere in this project; nothing sent to the API contains real identities.
- The request text is data, never instructions: the system prompt states this explicitly, and the deterministic injection detector plus the output contract remain the enforcement layer — the LLM is not trusted to self-police.
- `human_review_required: true` is enforced by `validate_output`, not by the model.
- All LLM results are advisory and human-reviewed, identical to the baseline's claims boundary.
- Honest reporting rules from ADR-012 apply: results are committed as measured; datasets are not tuned to the model.
