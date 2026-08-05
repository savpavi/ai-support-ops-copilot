# Task 010: Baseline Fallback Behind the LLM Path

## Status

- **State:** approved — 2026-08-05. Implementation authorized by the project owner.
- **Owner decisions (2026-08-05):** (1) the analyzer signature stays identical and provenance is exposed separately, so the wrapper drops into `evaluate_cases` unmodified. (2) Total time budget defaults to **20 seconds**, configurable per call. (3) A `--classifier llm-fallback` evaluation mode is added so the degraded path's accuracy can be measured.
- **Position in the approved sequence:** second of three follow-ups approved on 2026-08-05 (009 label review — complete, 010 fallback wrapper, 011 LLM-drafted replies). It runs before 011 because drafted replies inherit whatever resilience this task establishes.

## Problem

**The documented fallback does not exist.** `docs/11-llm-evaluation.md` states: *"In production use, that error path falls back to the deterministic baseline."* It does not. `LLMClassifierError` is raised in `support_copilot/llm_classifier.py` and is caught nowhere else in the repository. `scripts/evaluate_requests.py` passes `analyze_request_llm` straight to the runner, and the only thing standing between a provider failure and a dead call is `support_copilot/evaluation.py:234`, a per-case `except Exception` that records the failure so a sweep can continue. That is an evaluation boundary, not production behavior — it is why Gemini's ten guard rejections appear in the results as cases with `actual: null`.

So the project currently claims a resilience property it does not have. Under the standard this repository has applied since Task 004, an unimplemented documented behavior is a defect, and Task 009 has just finished demonstrating that claims here get checked.

**A second defect sits underneath it.** `_openrouter_transport` retries three times with `timeout=180` and exponential backoff. A provider that accepts connections and then hangs therefore takes roughly nine minutes to produce the error that a fallback would react to. A fallback that fires nine minutes late is not resilience; it converts a hard failure into a hung caller. Any wrapper worth adding has to bound total time, not just catch the exception at the end.

**A contract constraint shapes the whole design.** `validate_output` requires the output object's field set to equal the contract's exactly (`classifier.py:253`), so a result cannot carry an `engine` or `degraded` field without moving off schema version `1.0` — which would also break the byte-identical n8n workflow artifact and its parity guarantee. Provenance has to travel beside the result, not inside it.

## Approach

1. **Add a wrapper, not a branch.** A new function in `support_copilot` takes an LLM analyzer and returns a callable with the same one-argument signature, so it drops into every place an analyzer is already accepted (`evaluate_cases(analyzer=...)`, the CLI, future callers). The deterministic baseline stays the fallback target.
2. **Bound the attempt.** The wrapper enforces a total time budget across the whole LLM attempt including the transport's internal retries, and falls back when the budget is exhausted rather than waiting for the retry ladder to finish. The existing 180-second, three-attempt ladder is left in place for direct callers; the wrapper is what makes it safe to use.
3. **Fall back on failure, never on judgment.** The typed `LLMClassifierError` triggers fallback. Unexpected exceptions also trigger fallback — a resilience layer that itself raises is worthless — but they are recorded under a distinct reason so a genuine bug never hides as a routine provider blip. Input rejection is not a failure: `validate_input` runs first and a rejected input returns the deterministic rejection result on both paths, so the wrapper must not treat it as an occasion to fall back or to retry.
4. **Provenance travels beside the result.** The wrapper exposes which engine answered, and on fallback why, without touching the contract object. Contract version stays `1.0`, `validate_output` stays unchanged, and the workflow artifact is untouched.
5. **Prove the safety invariant survives degradation.** The deterministic security scan already runs on both paths and LLM flags are union-only, so a fallback result cannot carry fewer security flags than the baseline would have produced. That is currently an argument; this task makes it a test, including for the paraphrased security solicitations the baseline misses — where the honest expectation is that falling back *loses* the flags the LLM would have caught. The wrapper restores availability, not accuracy, and the tests must say so.
6. **Keep Task 008 comparable.** The existing `--classifier llm` path keeps its exact current behavior so the 2026-08-04 snapshot stays reproducible in method. The wrapper is reached through a separate option.
7. **Correct the documentation.** `docs/11-llm-evaluation.md` is amended where it asserts the fallback already exists, in the same superseded-not-overwritten style Task 009 used.

## Out of scope

- LLM-drafted replies (Task 011), which stay templated here.
- Any change to `rules.json`, the classifier's judgment, the workflow artifact, contract version `1.0`, or `_system_prompt` — the Task 009 confound is recorded, and fixing it is a separate approved task or none.
- New live model sweeps. This task is verifiable entirely offline on stubs; if a live smoke check is wanted it is a single call, decided separately.
- Caching, circuit breaking, request hedging, async, or a retry policy richer than what the transport already has. Resilience here means one bounded attempt and a safe floor.
- n8n changes. The workflow remains deterministic-baseline-only and credential-free.

## Acceptance criteria

1. A wrapper in `support_copilot` converts any LLM analyzer into one that returns a contract-valid result for every input, and never propagates `LLMClassifierError` to its caller.
2. Fallback fires on the typed error, on unexpected exceptions, and on exhaustion of a total time budget; the budget is enforced against a stubbed slow transport in a test that itself runs fast.
3. The engine that answered, and the reason for any fallback, are observable to the caller without adding a field to the contract object; `validate_output` and `SCHEMA_VERSION` are unchanged and the workflow artifact is byte-identical.
4. A rejected input produces the deterministic rejection result through the wrapper, is not counted as a fallback, and spends no tokens.
5. Fallback results carry security flags no weaker than the deterministic baseline's, proven by test; the accuracy that is lost on fallback is measured and stated rather than glossed.
6. `--classifier llm` behaves exactly as it does today; the wrapper is a separate opt-in, and both are documented.
7. New offline tests cover each failure class on stub clients; the suite grows from 64 and stays key-less, with CI unchanged.
8. `docs/11-llm-evaluation.md` no longer claims a fallback that does not exist; README, STATUS, worklog, and a new ADR record the behavior and its limits.
9. No secrets, credentials, real data, network calls in tests, or n8n contact.

## Decisions the owner must make before implementation

1. **How provenance reaches the caller.** Either the wrapper returns the contract object alone and exposes the last engine/reason through a separate accessor, or it returns a small record pairing the contract object with its provenance. The second is cleaner for a caller that must log which path answered; the first keeps the analyzer signature identical so it drops into `evaluate_cases` unmodified. Recommendation: keep the analyzer signature identical and expose provenance separately, since signature compatibility is what makes the wrapper usable everywhere.
2. **The time budget.** The current worst case before an error surfaces is roughly nine minutes. Recommendation: a default total budget in the seconds range with the value configurable per call, chosen so that a hung provider degrades to the baseline while a merely slow one still succeeds. The exact default is a judgment the owner should set, since it encodes how long a human operator should wait for a better answer.
3. **Whether the fallback path is exercised in evaluation.** Adding a `--classifier llm-fallback` mode would let a future sweep measure the degraded path's accuracy directly; leaving it out keeps the CLI surface smaller. Recommendation: add it, because criterion 5 asks what fallback costs in accuracy and the runner is how this project answers that kind of question.

## Safety constraints

- Human review stays an invariant on every path; degradation must never be a reason to weaken it.
- The deterministic security scan runs regardless of which engine answers; a fallback may lose semantic recall but must never lose a deterministic flag.
- Synthetic data only. Tests make no network request and require no key.
- The wrapper improves availability, not correctness. Nothing in this task licenses describing the LLM path as production-ready.
