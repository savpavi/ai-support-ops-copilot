# Task 007: Continuous Verification and Case-Study Refresh

## Status

- **State:** complete — 2026-08-04.
- **Approved scope:** add public continuous verification (GitHub Actions) and bring the portfolio case study up to date with Tasks 004–006 evidence. Approved by the project owner on 2026-08-04. No behavior change.

## Delivered

1. `.github/workflows/ci.yml`: full test suite on Python 3.10 and 3.13, `scripts/build_workflow.py` check, and both evaluation summaries on every push and pull request; no secrets, deploy steps, or n8n access (ADR-013).
2. README CI badge.
3. `docs/06-portfolio-case-study.md`: Task 005 single-source evidence, Task 006 honest out-of-distribution evidence, continuous-verification section, and measured limitations.

## Acceptance

The first CI run on GitHub must pass; the case study must describe only built and verified capabilities.
