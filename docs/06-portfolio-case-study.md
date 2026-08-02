# Portfolio Case Study

## Working title

Designing a Human-in-the-Loop AI Copilot for Support Operations

## Case-study intent

This document will capture the problem framing, design decisions, implementation evidence, evaluation results, limitations, and lessons learned. It must describe only capabilities that have actually been built and verified.

## Current narrative

The project begins from a safety-first premise: automated analysis can accelerate support triage and drafting, but a human operator remains accountable for interpretation and action. Task 001 implements a deliberately modest baseline: transparent Python rules classify synthetic requests, produce templated draft replies, flag security-sensitive text, and validate a plain-JSON result. The output contract rejects any attempt to disable human review. Keeping this core independent from workflow tooling creates a reproducible reference for later integration.

## Task 001 evidence

- Five conspicuously synthetic fixture classes: normal, urgent, incomplete, ambiguous, and security-sensitive.
- Eleven repeatable standard-library tests covering valid behavior, rejected input, contract tampering, prompt injection, draft safety, and CLI parity.
- A versioned input/output contract with deterministic allowed values and error behavior.
- No runtime dependencies, persistence, network services, LLM calls, message sending, or deployment.

## Current limitations

Keyword rules can miss paraphrases and can produce false positives. Urgency is based on explicit phrases rather than operational context. Missing-information checks are illustrative, and reply drafts are intentionally generic. The test suite demonstrates contract and safety behavior, not production accuracy or business impact.

## Task 002 local integration evidence

- A reviewable inactive workflow artifact with exactly four built-in nodes and no credentials or external-action nodes.
- A separate Human Review Guard that converts malformed or tampered intermediate output into a structured rejected result with review still required.
- Eight local tests that inspect workflow structure and compare the embedded JavaScript against the Python oracle for Task 001 and adverse fixtures.
- A manual import, fixture parity, export, and re-import guide for an authorized development n8n instance.

This evidence supports artifact structure and deterministic parity outside n8n. It does not yet support a claim that a particular n8n version imports or executes the artifact correctly; that remains a manual verification step.

## Evidence to collect later

- Architecture and data-flow diagram matching the implemented system.
- Representative synthetic input/output examples.
- Test and evaluation methodology with measurable results.
- Examples of ambiguous, incomplete, urgent, and adversarial requests.
- Tradeoffs behind classification categories, urgency rules, and model choices.
- Screenshots only after checking that they contain no real data or secrets.

## Claims policy

Do not claim production readiness, business impact, accuracy, latency, or cost improvements until supported by reproducible evidence. Clearly distinguish implemented behavior from proposed future work.
