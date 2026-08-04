# Task 003: Synthetic Evaluation and Portfolio Evidence

**Status:** Complete — 2026-08-03.

## Progress

- **Phase 1 complete:** Added a validated 40-case synthetic evaluation dataset, explicit independently reviewable expected assertions, a dependency-free dataset validator, and five focused tests.
- **Phase 2 complete:** Added the dependency-free runner, explicit metrics, deterministic JSON/Markdown reports, reusable local workflow harness, and full 40-case Python/n8n parity measurement.
- **Phase 3 complete:** Reviewed and fixed the measured keyword-boundary defect, added deterministic results, methodology, representative examples, an implemented data-flow diagram, portfolio evidence, and final completion checks.

## Objective

Build a local, repeatable evaluation baseline for the deterministic support copilot using only conspicuously synthetic requests. Measure the implemented classifier's category, urgency, security-flag, contract-safety, and Python/n8n parity behavior, then turn the verified results into reviewable portfolio evidence without claiming production accuracy or business impact.

## Why this task comes next

Tasks 001 and 002 established a deterministic local reference and an inactive, manual-only n8n adapter. Before considering an LLM, operator interface, external integration, or automation, the project needs a broader evaluation set and explicit metrics that can expose weaknesses and support later comparisons against the same baseline.

## Deliverables

- A reviewed synthetic evaluation dataset containing 30–50 cases in a documented machine-readable format.
- Case coverage for every supported category, urgency level that can be produced safely, missing-information behavior, all supported security flags, rejected inputs, ambiguous wording, and conservative prompt-injection negatives.
- Expected labels or assertions that are separate from classifier-generated output and are manually reviewable.
- A dependency-free local evaluation runner using the Python standard library.
- Machine-readable evaluation results plus a concise human-readable summary generated locally.
- Separate metrics for category, urgency, security flags, safe rejection, human-review enforcement, and Python/n8n parity.
- Per-case failure details sufficient to diagnose false positives, false negatives, and contract mismatches without copying unsafe request text unnecessarily.
- Representative synthetic input/output examples suitable for the portfolio case study.
- An architecture and data-flow diagram matching the implemented Task 001 and Task 002 system.
- Updated README, evaluation methodology, portfolio case study, decisions, worklog, status, and handoff documentation as applicable.
- Automated tests for dataset validation, metric calculation, reporting, safety invariants, and repeatable execution.

## Constraints

- Use only conspicuously synthetic support requests and identities.
- Never use real Pegasus, passenger, agency, PNR, employee, email, phone, ticket, or operational data.
- Do not add an LLM, model provider, network call, telemetry service, database, web application, or third-party dependency.
- Do not connect to n8n during local implementation and do not change, activate, deploy, or add action nodes to the Task 002 workflow.
- Keep the current version `1.0` input/output contract unless a demonstrated evaluation need requires a separately reviewed contract decision.
- Do not tune rules against hidden or future evaluation expectations in a way that makes results misleading. Record rule changes and re-run the complete regression and evaluation suites.
- Treat expected labels as evaluation assertions, not verified production truth.
- Every evaluated result must remain advisory and retain `human_review_required: true`.
- Do not claim production accuracy, business impact, cost savings, latency improvement, or compatibility beyond the evidence collected.
- Do not commit generated artifacts containing timestamps, machine-specific paths, environment details, secrets, or nondeterministic ordering unless explicitly justified and sanitized.

## Evaluation design requirements

### Dataset structure

Each case must have a unique synthetic identifier, a short scenario description, one input object or deliberately malformed input, and explicit expected assertions. Expected assertions should cover only behavior a reviewer can justify from the documented rules and safety requirements.

The dataset must include:

- every allowed category;
- low, normal, high, critical, and rejected/unknown urgency paths where the classifier supports them;
- complete and incomplete requests;
- ambiguous and overlapping category language;
- each allowed security flag;
- malformed, empty, extra-field, wrong-type, invalid-identifier, and overlong inputs;
- prompt-injection variants and ordinary approval language that should not be flagged;
- cases designed to reveal keyword-boundary and false-positive weaknesses;
- at least one case for every reply template or missing-information branch.

No evaluation case may contain a real organization identifier, personal identifier, credential, secret, reachable URL, real payment value, or copied support request.

### Metrics

The runner must report at least:

- exact category match count and rate;
- exact urgency match count and rate;
- per-flag true-positive, false-positive, and false-negative counts for security flags;
- safe-rejection pass count and rate for invalid inputs;
- human-review invariant pass count and rate;
- output-contract validation pass count and rate;
- complete Python/n8n parity count and rate for cases accepted by the Task 002 input path;
- total evaluated cases and a deterministic list of failed case identifiers.

Rates must include their numerator and denominator. Undefined rates must be represented explicitly rather than converted silently to zero or one. The report must distinguish contract/safety invariants from heuristic quality observations.

### Reproducibility

- The evaluation must run locally with a documented command and no network access.
- Repeated runs against the same revision must produce deterministically ordered equivalent results.
- Generated output must be reviewable before any committed summary is updated.
- The complete existing test suite must remain green.

## Implementation plan

### Phase 1: evaluation contract and dataset

1. **Complete:** Define and document the evaluation-case schema and validation rules.
2. **Complete:** Create 30–50 independently reviewable synthetic cases covering the required matrix.
3. **Complete:** Add dataset validators that reject duplicate identifiers, unknown labels, unsafe shapes, and accidental non-synthetic identifiers.
4. **Complete:** Record expected assertions separately from current classifier output so the dataset does not merely encode existing behavior.

### Phase 2: runner and metrics

1. **Complete:** Implement a standard-library evaluation runner around the Task 001 Python API.
2. **Complete:** Calculate deterministic category, urgency, security, rejection, contract, and human-review metrics.
3. **Complete:** Extract a reusable Task 002 local JavaScript harness and evaluate Python/n8n parity without connecting to n8n.
4. **Complete:** Emit deterministic JSON and concise Markdown output without timestamps, machine paths, or request text.
5. **Complete:** Add focused unit tests for metric edge cases, undefined rates, report determinism, CLI repetition, and injected safety failures.

### Phase 3: findings and portfolio evidence

1. **Complete:** Run the full regression and evaluation suites.
2. **Complete:** Review failures and distinguish the measured implementation defect from expected-label and broader heuristic limitations.
3. **Complete:** Fix the bounded credential-term defect within contract version `1.0` and record the decision.
4. **Complete:** Add representative synthetic examples and an implemented architecture/data-flow diagram.
5. **Complete:** Update the case study with verified counts, limitations, and methodology.
6. **Complete:** Run secret, personal-data, generated-artifact, JSON, and diff checks before completion.

## Acceptance verification

1. **Pass:** `fixtures/evaluation_cases.json` contains 40 validated, conspicuously synthetic cases with unique synthetic identifiers and independently reviewable expectations.
2. **Pass:** Dataset validation enforces all required categories, urgencies, security flags, rejected inputs, ambiguity, missing-information, prompt-injection, conservative-negative, and keyword-boundary coverage.
3. **Pass:** `python3 scripts/evaluate_requests.py` runs locally with Python standard library and Node.js, without network or external-system access.
4. **Pass:** The deterministic report contains explicit numerator, denominator, and rate values for every required quality, safety, security, and parity metric.
5. **Pass:** Structured failure reporting uses synthetic case identifiers and expected/actual fields without request text; the reviewed final run has no failed cases.
6. **Pass:** Tests cover dataset validation, metric calculations, undefined rates, deterministic output, injected contract/review failures, CLI repetition, keyword-boundary regression, and committed-result drift.
7. **Pass:** All 34 tests pass and repeated evaluation output is deterministic.
8. **Pass:** All 40 cases have complete local Python/workflow JavaScript parity without connecting to or modifying an n8n instance at runtime.
9. **Pass:** `docs/09-evaluation.md` and the portfolio case study contain methodology, representative synthetic examples, the implemented data-flow diagram, measured results, and limitations.
10. **Pass:** Review and scans found no LLM, credential, secret, real personal or operational data, external integration, activation, message sending, deployment, or unsupported performance claim.

## Acceptance criteria

1. A validated dataset contains 30–50 conspicuously synthetic and independently reviewable evaluation cases.
2. Dataset coverage includes every supported category, required urgency and rejection paths, missing-information branches, every security flag, malformed inputs, ambiguous cases, prompt-injection positives, and conservative negatives.
3. A dependency-free local command evaluates the complete dataset without network or external-system access.
4. The runner reports numerator, denominator, and rate for category, urgency, security flags, safe rejection, contract validity, human-review enforcement, and Python/n8n parity as applicable.
5. Failed cases are reported deterministically by synthetic identifier with enough structured detail for diagnosis.
6. Tests verify dataset validation, metric correctness, undefined-rate handling, deterministic reporting, contract safety, and the immutable human-review requirement.
7. The existing Task 001 and Task 002 tests still pass, and the evaluation runner is repeatable on the same revision.
8. Python/n8n parity is checked locally against the committed workflow without connecting to or modifying an n8n instance.
9. Documentation includes the evaluation methodology, representative synthetic examples, an implemented-system data-flow diagram, measured results, and honest limitations.
10. No LLM, credential, secret, real personal or operational data, external integration, workflow activation, message sending, deployment, or unsupported performance claim is introduced.

## Definition of done

All acceptance criteria are demonstrably met; existing and new tests pass; evaluation output is reproducible and reviewed; documentation, decisions, worklog, status, and handoff are current; repository scans find no secret or real personal data; all results remain suggestions requiring human review; and the completed result is ready for human review without deployment.

## Explicitly deferred

- LLM or model-provider integration.
- A web or operator user interface.
- n8n activation, API/MCP management, action nodes, or external-system connections.
- Production deployment, authentication, persistence, analytics services, and real-data evaluation.
- Any comparison against an LLM until that work receives a separate approved task and uses this evaluation baseline.
