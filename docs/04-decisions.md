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

## ADR-006: Self-contained workflow JSON with Python parity reference

**Status:** Accepted — 2026-08-02; verified on self-hosted n8n 2.14.2.

Task 002 uses an inactive manual-only workflow made from built-in n8n nodes and transported by reviewed workflow JSON. The small deterministic Task 001 algorithm is replicated in a Code node, with a separate final contract guard. The Python baseline and fixtures remain the canonical parity reference. Direct Python execution is rejected because it requires shell/repository access; a Python API is rejected because it adds a service and network boundary. REST API and n8n MCP management are excluded unless a later need justifies their credentials and additional control surface.

The sanitized artifact was manually imported, executed, exported, and re-imported in an authorized self-hosted n8n 2.14.2 development instance. This verification does not establish compatibility with newer n8n versions or authorize activation, external actions, or production deployment.

## ADR-007: Independent synthetic expectations and local evaluation reports

**Status:** Accepted — 2026-08-03.

Task 003 stores manually reviewable synthetic expectations separately from classifier output. A Python standard-library runner evaluates the local baseline and executes the committed n8n Code-node JavaScript through a reusable local Node harness. Reports are deterministic, contain no timestamps or machine paths, identify failures by synthetic case ID without echoing request text, and separate heuristic observations from contract and human-review invariants. This creates a comparison baseline without adding a model provider, service, network boundary, or n8n connection.

## ADR-008: Bound credential terms to avoid substring false positives

**Status:** Accepted — 2026-08-03.

The first Task 003 evaluation showed that substring matching classified `passwordless` as a credential request and raised its urgency. Because the synthetic text does not request a credential, the expected assertion was retained and the implementation was corrected. Python and workflow JavaScript now use the same case-insensitive, word-bounded credential-term pattern. This narrow change preserves the version `1.0` contract and existing positive detections while preventing the measured false positive.

## ADR-009: Word-bounded term rules with explicit negation handling

**Status:** Accepted — 2026-08-04.

Task 003 bounded only the credential terms after the `passwordless` false positive. An external review of the completed baseline demonstrated the same substring defect class in the remaining rules: `urgent` matched inside `not urgent`, `date` matched inside `update`, and `charge` matched inside `discharged`. Task 004 converts every category, urgency, missing-information, and payment/identity term rule in both Python and the committed workflow JavaScript to word-bounded matching, preserves previously implicit matches through explicit variants (for example `charges`, `overcharged`, `urgently`, `minutes`, `application`), and treats explicitly negated urgency (`not urgent`, `non-urgent`, `non urgent`) as a low-urgency indicator instead of a high-urgency match. A dead always-`general` branch in the Python category rule was removed with no behavior change; the workflow JavaScript had no such branch. The version `1.0` contract is unchanged. Deterministic keyword rules still cannot understand paraphrases or arbitrary negation; this decision only removes in-word false matches and the three demonstrated defects.

## ADR-010: Native verification through the official n8n MCP connector

**Status:** Accepted — 2026-08-04.

ADR-006 excluded REST and MCP management of n8n while there was no demonstrated need. The Task 004 revision required a native retest, and the project owner connected the official n8n MCP connector to the authorized self-hosted development instance (owner-confirmed n8n 2.14.2, the same version as the Task 002 verification) for this session. Because the connector creates workflows from SDK code rather than importing files, verification used a temporary equivalent workflow with the identical four-node topology, identical parameters, and byte-identical Code-node JavaScript taken from the committed artifact. Sixteen synthetic cases — the committed default input, the five Task 001 fixtures, the six adverse inputs, and the four Task 004 boundary probes — were executed manually, and every Human Review Guard output equaled the Python oracle exactly. The temporary workflow remained inactive and credential-free and was archived after the results were recorded. No credentials, instance URLs, or execution data enter the repository. This decision authorizes MCP use only for development-instance verification of committed artifacts; it does not authorize activation, credentials, external actions, or production management.

## ADR-011: Single-source rule data with a byte-identical workflow generator

**Status:** Accepted — 2026-08-04.

Tasks 003 and 004 fixed the same defect class twice because rule data existed separately in Python and in the workflow JavaScript. `support_copilot/rules.json` is now the only place term lists, shared regular-expression patterns, contract enums, the synthetic-identifier pattern, and limits are written. The Python baseline compiles its matching structures from that file at import time. The Code-node JavaScript lives as reviewable templates under `n8n/src/` whose rule literals are placeholder tokens; `scripts/build_workflow.py` deterministically renders them into the committed workflow JSON and offers a check mode. The generator's first output is byte-identical to the natively verified Task 004 artifact, proving the extraction changed nothing, and a permanent drift test fails whenever the committed artifact differs from its sources. Shared patterns are stored in a portable form (`[\s\S]` instead of an engine-specific DOTALL flag, with explicit flag strings) so both engines compile the same strings. Behavioral parity tests remain as the backstop for the small amount of still-duplicated logic.

## ADR-012: Semantic out-of-distribution assertions reported honestly

**Status:** Accepted — 2026-08-04.

The aligned Task 003 dataset demonstrates contract discipline, and its full score says nothing about language understanding. Task 006 adds a second dataset whose expected labels are semantic judgments made from the case text alone, frozen before the classifier first ran on those inputs, with four in-distribution control cases as anchors. The measured result — 5/33 expected assertions, zero paraphrase recall on security solicitations, and 100% contract, human-review, and parity invariants — is committed verbatim in `docs/paraphrase-results.json` and protected by a drift test that does not require assertion success. The dataset validator gained explicit coverage options (defaults unchanged) so both dataset purposes share one runner and report format. Rule changes chasing this dataset are rejected: relabeling or patching terms to pass would turn it back into an aligned dataset and destroy its value as a measurement. The labels' limited independence (same session authors rules and labels) is recorded in the methodology.
