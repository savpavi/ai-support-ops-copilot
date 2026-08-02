# Project Brief

## Purpose

Build a portfolio-quality AI Support Operations Copilot that demonstrates safe, useful assistance for human support operators using synthetic requests only.

## Problem

Support teams must quickly understand inbound messages, identify urgency and missing details, respond consistently, and avoid privacy or security mistakes. The copilot should reduce the operator's initial analysis effort without taking control away from the operator.

## Intended outcome

For each synthetic request, the system will propose a category, urgency, missing-information checklist, suggested response, and security flags in a clear structured result. Every result must state that human review is required.

## In scope

- Synthetic text requests.
- Explainable classification and urgency suggestions.
- Missing-information detection.
- Suggested reply drafting.
- Basic security and privacy risk flagging.
- Automated tests and a small set of synthetic fixtures.
- A later, explicitly authorized n8n workflow.

## Out of scope

- Real personal, operational, airline, or customer data.
- Autonomous sending, case updates, or operational decisions.
- Production connections, deployment, authentication systems, analytics platforms, or broad workflow orchestration during the MVP.
- Claims of production readiness or model accuracy unsupported by evaluation.

## Success criteria

The project is understandable to a reviewer, runs locally when implementation is authorized, produces deterministic structured output contracts around model-assisted behavior, handles representative synthetic cases, visibly enforces human review, and contains no secrets or personal data.
