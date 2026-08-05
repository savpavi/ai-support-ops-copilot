# Portfolio Case Study

## Working title

Designing a Human-in-the-Loop AI Copilot for Support Operations

## Case-study intent

This document will capture the problem framing, design decisions, implementation evidence, evaluation results, limitations, and lessons learned. It must describe only capabilities that have actually been built and verified.

## Current narrative

The project begins from a safety-first premise: automated analysis can accelerate support triage and drafting, but a human operator remains accountable for interpretation and action. Task 001 implements a deliberately modest baseline: transparent Python rules classify synthetic requests, produce templated draft replies, flag security-sensitive text, and validate a plain-JSON result. The output contract rejects any attempt to disable human review. Keeping this core independent from workflow tooling creates a reproducible reference for later integration.

The later arc of the project is about engineering honesty: an external review found a systematic defect class, the fix was applied systematically and natively re-verified, the drift-prone rule data was reduced to a single provable source, and finally the baseline was measured against paraphrases it was never written for — and the low score was published rather than patched away.

## Task 001 evidence

- Five conspicuously synthetic fixture classes: normal, urgent, incomplete, ambiguous, and security-sensitive.
- Thirteen repeatable standard-library tests covering valid behavior, rejected input, contract tampering, prompt injection, draft safety, and CLI parity.
- A versioned input/output contract with deterministic allowed values and error behavior.
- No runtime dependencies, persistence, network services, LLM calls, message sending, or deployment.

## Task 002 integration evidence

- A reviewable inactive workflow artifact with exactly four built-in nodes and no credentials or external-action nodes.
- A separate Human Review Guard that converts malformed or tampered intermediate output into a structured rejected result with review still required.
- Nine local tests that inspect workflow structure and compare the embedded JavaScript against the Python oracle for Task 001 and adverse fixtures.
- A manual import, fixture parity, export, and re-import guide for an authorized development n8n instance.
- Native verification on self-hosted n8n 2.14.2: successful import, inactive manual-only execution, normal and urgent results, guarded normalized and malformed prompt-injection results, and successful export/re-import execution.
- Native confirmation that no credentials, external APIs, LLMs, webhooks, messaging, or production systems were used.

This evidence supports artifact structure, deterministic Python/JavaScript parity, and development compatibility with self-hosted n8n 2.14.2. Compatibility with newer n8n versions is not yet verified, and no upgrade recommendation is part of Task 002.

## Task 003 evaluation evidence

- Forty-four reviewed synthetic evaluation cases spanning all supported categories, urgency values, security flags, missing-information branches, malformed inputs, ambiguous cases, and conservative negatives.
- A dependency-free runner that emits deterministic machine-readable JSON and human-readable Markdown without request text, timestamps, machine paths, network access, or an n8n connection.
- Explicit separation between heuristic observations and safety invariants, with numerator and denominator retained for every rate.
- Final measurements of 44/44 category, urgency, security-flag, missing-information, expected-assertion, output-contract, human-review, and Python/n8n parity checks; safe rejection passed 7/7.
- Per-security-flag results with zero false positives and zero false negatives within the committed dataset.
- A keyword-boundary regression discovered by the first run: `passwordless` was incorrectly treated as a credential request. The expected label was preserved, both implementations were corrected, and a focused regression test was added before the final run.
- A Task 004 hardening pass after an external review demonstrated the same substring defect class in the remaining rules (`not urgent` raised urgency, `date` matched inside `update`, `charge` matched inside `discharged`): every term rule became word-bounded in both implementations, explicitly negated urgency became a low-urgency indicator, and four regression evaluation cases were added.
- A checked-in deterministic result, methodology, implemented data-flow diagram, and representative accepted and rejected synthetic examples in `docs/09-evaluation.md` and `docs/evaluation-results.json`.
- Thirty-eight passing automated tests at Task 003/004 completion across the classifier, workflow structure/parity, dataset validation, metrics, safety-failure detection, CLI determinism, and result-file drift prevention; the suite has since grown to fifty-one.

These measurements demonstrate behavior against the committed synthetic assertions. They do not establish production accuracy, generalization, business impact, or real-world security effectiveness.

The Task 003 credential-boundary correction and the Task 004 word-boundary hardening changed the committed workflow after Task 002's native n8n run. The updated JavaScript was natively re-verified on 2026-08-04 against the same self-hosted n8n 2.14.2 instance: a 16-case sweep (default input, five fixtures, six adverse inputs, four boundary probes) produced exact output parity with the Python oracle through an MCP-created workflow with byte-identical Code-node JavaScript (ADR-010).

## Task 005 single-source evidence

- `support_copilot/rules.json` is the only place rule data (term lists, shared portable regular expressions, contract enums, limits) is written; the Python classifier compiles from it at import.
- The workflow Code-node JavaScript lives as reviewable templates under `n8n/src/`; a deterministic generator (`scripts/build_workflow.py`) renders them into the committed artifact.
- The generator's first output was byte-identical to the natively verified Task 004 artifact, proving the extraction changed nothing, and a permanent drift test plus a check mode prevent the artifact from diverging from its sources.
- A flow-through test edits one rule in memory and observes the change in both the Python classifier and the generated JavaScript.

## Task 006 honest out-of-distribution evidence

- Thirty-three paraphrase cases whose expected labels are semantic judgments frozen before the classifier first ran on them, with four in-distribution controls.
- The committed, unretouched result: 4/33 full expected assertions (category 14/33, urgency 16/33, security flags 28/33, missing information 16/33), with zero false positives and zero paraphrase recall on all five paraphrased security solicitations. The figures were 5/33 and 21/33 until Task 009 independently reviewed the labels themselves and corrected nine fields; the lower number is published because it is the measured one.
- The safety architecture held everywhere classification failed: output-contract validity, human-review enforcement, and Python/n8n parity were 33/33.
- A decision record (ADR-012) forbids chasing this dataset with rule patches, preserving it as a measurement instead of another aligned score.
- Fifty-one passing automated tests overall, including a drift test that pins the committed paraphrase results without requiring assertion success.

## Continuous verification

Since 2026-08-04, GitHub Actions runs the full test suite on Python 3.10 and 3.13, verifies that the committed workflow artifact matches its generated sources, and prints both evaluation summaries on every push and pull request.

## Current limitations

Keyword rules miss paraphrases, and this is now measured rather than assumed: 4/33 semantic expectations on the out-of-distribution set, with every paraphrased security solicitation missed (`docs/10-paraphrase-evaluation.md`). The measurement's own labels were then audited under a rubric frozen in advance, which corrected nine fields and lowered the published score (`docs/13-label-review.md`). Urgency is based on explicit phrases rather than operational context. Missing-information checks are illustrative, and reply drafts are intentionally generic. Full Python/n8n parity can reproduce a shared defect, so independent expected assertions remain necessary. The evaluation demonstrates contract and safety behavior within a small synthetic dataset, not production accuracy or business impact.

## Evidence that remains optional or future work

- Screenshots only after checking that they contain no real data or secrets.
- A separately approved comparison against a future alternative implementation using the same evaluation baseline.

## Claims policy

Do not claim production readiness, business impact, accuracy, latency, or cost improvements until supported by reproducible evidence. Clearly distinguish implemented behavior from proposed future work.
