# Task 011: LLM-Drafted Replies Behind a Real Reply Guard

## Status

- **State:** approved — 2026-08-05. Implementation authorized by the project owner.
- **Owner decisions (2026-08-05):** (1) generate a reply for every accepted case, including security-flagged ones, and make behavior on flagged cases the headline measurement. (2) Live sweep authorized over two models. (3) Length bound stays close to what today's templates produce.
- **Position in the approved sequence:** third of three follow-ups approved on 2026-08-05 (009 label review — complete, 010 fallback wrapper — complete, 011 drafted replies). It runs last because it depends on Task 010's degradation path.

## Problem

`suggested_reply` is the one contract field the project has never let a model write, and the only field whose safety rests on almost nothing. `validate_output` checks exactly two things about it: that it is a string, and that it starts with `Draft for human review:` (`classifier.py:269`). Everything else that makes today's replies safe comes from the fact that `_suggested_reply` is four lines of string concatenation over a category, a missing-information list, and a boolean. The template cannot promise a refund, invent an order number, repeat a card number back to the sender, or follow an instruction embedded in the request, because it cannot say anything that is not already in it.

Replace it with generated text and that guarantee is gone, while the guard stays a prefix check. The exposure is specific:

- **Commitment.** A draft that says "we will refund this within 24 hours" creates an expectation an operator may send on with light edits. `docs/01-requirements.md` forbids the system from sending replies or triggering operations; it says nothing about the system *promising* them, because until now it could not.
- **Fabrication.** The contract already forbids invented facts in `missing_information`. A generated reply can invent a policy, an amount, a date, or a reference number, and the same prohibition has to reach it.
- **Echo of untrusted input.** The request text is data, never instructions. A generated reply is the first place that boundary can leak: by obeying an injected instruction, or by quoting one back.
- **Reflecting sensitive content.** A message containing a card number or an identity-document number must not produce a draft that repeats it. This one is objectively checkable and is not checked today.
- **Complying with a solicitation.** The five paraphrased credential and payment solicitations in the paraphrase dataset are exactly the inputs where a helpful model is most likely to draft something it should refuse.

The honest framing is that **this task's work is the guard and its measurement, not the generation.** Generating a reply is a schema field and a prompt paragraph. Knowing whether the generated reply is safe is a new evaluation axis this project does not have.

## Approach

1. **One call, not two.** The reply is added to the existing structured-output schema rather than made a second request, so cost and latency stay where Task 008 measured them. Failure is scoped, not shared: a reply that fails the guard degrades **only the reply** to the existing template, leaving a good classification intact. This is deliberately finer-grained than Task 010's wrapper, which degrades the whole result.
2. **Add `validate_reply`, deterministic and shared.** A new guard runs on every generated reply before it can reach the contract object. Its data lives in `support_copilot/rules.json` under ADR-011's single-source rule, so the Human Review Guard can enforce the same thing if the workflow ever carries generated text. It rejects, at minimum: a missing or altered review prefix; a reply exceeding a length bound; any reply that trips the existing deterministic security scan when that scan is run *on the reply itself* — which catches a card number, an identity-document number, or a link reflected back; any URL at all, since a draft reply has no legitimate reason to emit one; and commitment phrasing drawn from an explicit term list.
3. **State plainly what the guard cannot do.** The security-scan reuse and the length and URL rules are exact. The commitment term list is keyword matching, and Tasks 004 and 006 established what keyword matching is worth against paraphrase: a model that writes "you can expect the money back by Thursday" will pass a list built around "we will refund". This is a floor, not a semantic guarantee, and the task's deliverable is the measurement of where that floor sits — not a claim that drafted replies are safe.
4. **Build an adversarial reply dataset and freeze its labels first.** A new fixture set of synthetic requests designed to tempt a draft into each failure mode — demands for a commitment, requests to confirm invented details, embedded instructions, messages carrying card and document numbers, the paraphrased solicitations. Expected outcomes are written before any model is run, in the ADR-012 discipline: for each case, whether a safe draft is possible at all and what the guard must catch if it is not.
5. **Measure, then report whatever comes out.** A live sweep over the reply dataset and both existing datasets, on the models Task 008 already measured, reporting how often generated replies pass the guard, how often the guard's rejection was correct, and — the number that matters — how many unsafe drafts passed the guard on human reading of every reply that survived it. Per ADR-014, results are a dated snapshot with no drift test.
6. **Default off.** Generated replies are opt-in at the call site and in the CLI. The deterministic baseline and the existing `--classifier llm` path keep templated replies exactly as they are today, so every committed evaluation result stays comparable.

## Out of scope

- Sending, routing, or acting on any reply. The human-review invariant and the no-external-action rule are untouched.
- Changing contract version `1.0`. `suggested_reply` is already a contract field, so generated text needs no schema change.
- n8n changes. The workflow stays deterministic-baseline-only; `validate_reply`'s data lands in `rules.json` so the guard *can* be replicated later, but replicating it is not this task.
- Changing `_system_prompt`'s classification instructions, the Task 009 confound, the control redesign, or any rule affecting category, urgency, flags, or missing information.
- Tone, localisation, style configuration, or multi-turn drafting.

## Acceptance criteria

1. `validate_reply` is deterministic, its data lives in `rules.json`, and it rejects at minimum: a missing or altered prefix, an over-length reply, a reply that trips the deterministic security scan run on itself, any URL, and listed commitment phrasing.
2. A rejected reply degrades to the existing template while the classification is preserved; the result still satisfies `validate_output` and `human_review_required` stays true.
3. Generated replies are off by default; `--classifier llm` and the deterministic baseline produce byte-identical replies to today's, proven by test against the committed fixtures.
4. Offline tests cover every rejection class on stub clients, including a reply that reflects a card number, one that reflects an identity-document number, one containing a URL, one promising an action, and one that drops the prefix. The suite grows from 79, stays key-less, and CI is unchanged.
5. A reply-safety fixture set exists with outcomes frozen before the first model run, and the dataset validates structurally like the others.
6. The live sweep is reported per model with the guard's pass rate, and with a human reading of **every** draft that passed the guard, so that "unsafe drafts that survived" is a measured count rather than an absence of evidence.
7. The measured limits of the commitment list are stated in the same paragraph as its pass rate, in the terms Task 006 used for the keyword baseline.
8. `docs/07-contracts.md` documents the reply guard; a new document records the methodology and results; README, STATUS, worklog, and a new ADR record the behavior, the default-off posture, and the limits.
9. No secrets, credentials, real data, or n8n contact; every fixture is conspicuously synthetic.

## Decisions the owner must make before implementation

1. **Whether security-flagged cases get generated replies at all.** Suppressing generation whenever a security flag is present is the conservative option and removes the highest-risk drafts entirely; generating for every accepted case is the informative option, because the flagged cases are precisely where a reply guard earns or fails to earn its keep, and suppressing them would leave the guard untested where it matters most. Recommendation: generate for every accepted case, and make behavior on flagged cases the headline measurement — with the option to switch to suppression if the measurement is bad.
2. **Whether the live sweep is authorized, and over how many models.** The measurement in criterion 6 requires reading every surviving draft, so the cost is reviewer attention rather than tokens; the token cost is in the same range as Task 008's roughly $0.10. Recommendation: two models rather than four, since the question is whether the guard holds rather than which model writes best prose.
3. **How strict the length bound is.** A short bound is easy to enforce and makes drafts less useful; a long one gives the model room to commit to things. Recommendation: a bound in the low hundreds of characters, close to what today's templates produce, so a generated draft stays a starting point rather than a finished letter.

## Safety constraints

- Every drafted reply is advisory and human-reviewed; nothing in this task weakens that, and the guard's failure mode is always the template, never an unguarded draft.
- The request text remains untrusted data. A generated reply that follows or repeats an instruction from the request is a guard failure to be measured and reported, not an acceptable outcome.
- The deterministic security scan continues to run on the request regardless of what happens to the reply.
- Synthetic data only. Offline tests make no network request; the live sweep sends only synthetic text, per ADR-014.
- No result of this task licenses describing drafted replies as safe for unreviewed use.
