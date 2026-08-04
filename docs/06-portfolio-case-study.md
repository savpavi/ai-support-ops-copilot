# Portfolio Case Study

## Working title

Designing a Human-in-the-Loop AI Copilot for Support Operations

## Case-study intent

This document will capture the problem framing, design decisions, implementation evidence, evaluation results, limitations, and lessons learned. It must describe only capabilities that have actually been built and verified.

## Current narrative

The project begins from a safety-first premise: automated analysis can accelerate support triage and drafting, but a human operator remains accountable for interpretation and action. Task 001 implements a deliberately modest baseline: transparent Python rules classify synthetic requests, produce templated draft replies, flag security-sensitive text, and validate a plain-JSON result. The output contract rejects any attempt to disable human review. Keeping this core independent from workflow tooling creates a reproducible reference for later integration.

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
- Thirty-eight passing automated tests across the classifier, workflow structure/parity, dataset validation, metrics, safety-failure detection, CLI determinism, and result-file drift prevention.

These measurements demonstrate behavior against the committed synthetic assertions. They do not establish production accuracy, generalization, business impact, or real-world security effectiveness.

The Task 003 credential-boundary correction and the Task 004 word-boundary hardening changed the committed workflow after Task 002's native n8n run. The updated JavaScript was natively re-verified on 2026-08-04 against the same self-hosted n8n 2.14.2 instance: a 16-case sweep (default input, five fixtures, six adverse inputs, four boundary probes) produced exact output parity with the Python oracle through an MCP-created workflow with byte-identical Code-node JavaScript (ADR-010).

## Current limitations

Keyword rules can miss paraphrases and can produce false positives outside the evaluated cases. Urgency is based on explicit phrases rather than operational context. Missing-information checks are illustrative, and reply drafts are intentionally generic. Full Python/n8n parity can reproduce a shared defect, so independent expected assertions remain necessary. The evaluation demonstrates contract and safety behavior within a small synthetic dataset, not production accuracy or business impact.

## Evidence that remains optional or future work

- Screenshots only after checking that they contain no real data or secrets.
- A separately approved comparison against a future alternative implementation using the same evaluation baseline.

## Claims policy

Do not claim production readiness, business impact, accuracy, latency, or cost improvements until supported by reproducible evidence. Clearly distinguish implemented behavior from proposed future work.
