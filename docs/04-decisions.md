# Architecture Decision Log

## ADR-001: Synthetic data only

**Status:** Accepted — 2026-08-02

All examples, fixtures, tests, and demonstrations will use conspicuously synthetic data. Real Pegasus, passenger, agency, PNR, employee, email, and phone data are prohibited.

## ADR-002: Human review is mandatory

**Status:** Accepted — 2026-08-02

The copilot provides suggestions only. Every result will require human review, and the MVP will not send replies or take downstream actions.

## ADR-003: Simple core with deferred integration

**Status:** Accepted — 2026-08-02

Core input, analysis, policy, and output contracts will remain independent from n8n. Framework, model provider, persistence, deployment, and workflow choices are deferred until justified by an approved task.

## ADR-004: No repository secrets

**Status:** Accepted — 2026-08-02

Credentials and sensitive configuration must remain outside version control. Ignore rules provide a safety net but do not replace review.

## ADR-005: Python standard library baseline

**Status:** Accepted — 2026-08-02

Task 001 uses Python and only its standard library. Python provides JSON handling, type and value checks, a local CLI, and `unittest` without introducing dependency installation or a framework. The classifier is a deterministic rule-based baseline; model-provider selection remains outside Task 001.
