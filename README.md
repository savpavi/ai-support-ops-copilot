# AI Support Operations Copilot

[![CI](https://github.com/savpavi/ai-support-ops-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/savpavi/ai-support-ops-copilot/actions/workflows/ci.yml)

AI Support Operations Copilot is a portfolio project for assisting human support operators with synthetic inbound requests. The intended system will classify a request, estimate urgency, identify missing information, draft a suggested reply, and flag possible security risks. A human must review every output before any action is taken.

## Current state

Tasks 001 through 004 are complete. The repository contains a dependency-free Python classifier, explicit JSON contracts, deterministic validation, synthetic fixtures, a local CLI, automated tests, and a reviewed 44-case synthetic evaluation. It also contains a sanitized, inactive, manual-only n8n workflow with structural and Python-parity tests. The Task 002 workflow revision was manually verified on an authorized self-hosted n8n 2.14.2 development instance, including import, execution, guarded adverse inputs, export, and re-import; the later Task 003 and Task 004 keyword corrections were natively re-verified on the same instance on 2026-08-04 with a 16-case sweep and exact output parity. Compatibility with newer n8n versions is unverified. Nothing has been deployed or connected to a production or external action system. See `STATUS.md` for the authoritative status.

## Scope

The MVP is expected to accept synthetic support text and produce a structured recommendation containing:

- request category and confidence or rationale;
- urgency level and rationale;
- missing information needed for safe handling;
- a draft response clearly marked as suggested text;
- security and privacy risk flags;
- an explicit human-review requirement.

Out of scope for the initial phase are real customer data, production integrations, autonomous replies or actions, deployment, and unnecessary platform complexity.

## Repository map

- `docs/`: brief, requirements, architecture, security, decisions, worklog, and case-study notes.
- `tasks/`: bounded implementation task specifications.
- `n8n/workflows/`: sanitized inactive workflow artifact, generated from `n8n/src/` and `support_copilot/rules.json`.
- `n8n/src/`: reviewable Code-node JavaScript templates whose rule literals are placeholders.
- `support_copilot/`: local classifier, input/output validation, shared rule data (`rules.json`), evaluation, and the workflow generator.
- `fixtures/`: synthetic scenarios and the reviewed evaluation dataset.
- `tests/`: standard-library automated tests.
- `scripts/`: local command-line entry points.

## Local usage

Python 3.10 or newer is sufficient; there are no third-party runtime or test dependencies.

Run all tests:

```bash
python3 -m unittest discover -s tests -v
```

This currently runs 64 tests: 17 classifier regression tests (Tasks 001 and 004), 9 Task 002 workflow structure/parity tests, 12 dataset/evaluation tests (Tasks 003 and 004), 6 rule-source and generator tests (Task 005), 7 paraphrase-evaluation tests (Task 006), and 13 offline LLM-classifier tests (Task 008). The suite needs no API key and makes no network requests. Node.js is required for workflow parity tests and the evaluation, which execute the committed Code-node JavaScript locally and compare it with the Python reference.

All rule data (term lists, shared patterns, enums, limits) lives in `support_copilot/rules.json`; the committed workflow JavaScript is generated from `n8n/src/` templates. Verify that the committed artifact matches its sources:

```bash
python3 scripts/build_workflow.py
```

After editing `rules.json` or a template, regenerate the artifact with `--write`. A regenerated workflow revision requires a new native n8n verification before runtime claims are repeated.

Run the 44-case aligned synthetic evaluation and print a concise Markdown summary:

```bash
python3 scripts/evaluate_requests.py
```

Run the 33-case out-of-distribution paraphrase evaluation, whose low scores are the honest, expected outcome (see `docs/10-paraphrase-evaluation.md`):

```bash
python3 scripts/evaluate_requests.py --dataset paraphrase
```

Run either dataset against the optional LLM classifier (same contract, same safety guards; requires `OPENROUTER_API_KEY`, or the `anthropic` SDK plus `ANTHROPIC_API_KEY` with `--provider anthropic`; see `docs/11-llm-evaluation.md` for measured results):

```bash
python3 scripts/evaluate_requests.py --dataset paraphrase --classifier llm \
  --provider openrouter --model anthropic/claude-haiku-4.5
```

Print the deterministic machine-readable report instead:

```bash
python3 scripts/evaluate_requests.py --format json
```

The command performs no network access and does not connect to n8n. Reports contain synthetic case identifiers and structured mismatches, not request text. Expected labels are reviewable evaluation assertions rather than production truth.

Analyze one synthetic request from standard input:

```bash
printf '%s\n' '{"request_id":"SYN-DEMO-001","message":"The synthetic demo dashboard stopped working ten minutes ago."}' | python3 scripts/classify_request.py
```

Or pass a JSON file path:

```bash
python3 scripts/classify_request.py path/to/synthetic-request.json
```

The CLI returns exit code `0` for accepted input and `2` for rejected input. The contracts and allowed values are documented in `docs/07-contracts.md`.

## Limitations

The classifier uses transparent keyword rules, not an LLM. It is deterministic and useful as a contract and safety baseline, but it does not understand language semantically, measure statistical confidence, or establish production accuracy. The Task 006 paraphrase evaluation quantifies this honestly: on 33 out-of-distribution phrasings it meets only 4/33 semantic expectations and misses every paraphrased security solicitation, while the output contract, human-review enforcement, and Python/n8n parity hold at 100%. Those labels were themselves independently reviewed in Task 009, which confirmed the category and security-flag labels unchanged, corrected nine fields in eight cases, and published the resulting drop from 5/33 rather than keeping the better number (`docs/13-label-review.md`). The optional Task 008 LLM classifier closes most of that semantic gap behind the same contract — paraphrase category recognition reached 31–33/33 across four measured models, and the guard rejected all nonconforming model output fail-closed (`docs/11-llm-evaluation.md`). Its suggested replies are fixed templates and must always be reviewed by a human.

The Task 002 workflow revision was verified on self-hosted n8n 2.14.2. Tasks 003 and 004 later made bounded keyword corrections in the committed Code-node JavaScript and verified them locally with 44/44 Python parity; the current revision was then natively verified on the same self-hosted n8n 2.14.2 instance on 2026-08-04 through a 16-case sweep with exact output parity (see `docs/08-n8n-manual-test.md` and ADR-010). Compatibility with newer n8n versions remains unverified. The workflow must remain inactive and must not gain credentials or action nodes.

The first Task 003 evaluation exposed a keyword-boundary weakness: `passwordless` matched the baseline's original `password` substring rule. The credential detector was corrected in both Python and workflow JavaScript and a regression test was added. Task 004 then applied the same word-boundary hardening to every remaining term rule after an external review demonstrated the same defect class elsewhere (`not urgent` raised urgency to high, `date` matched inside `update`, and `charge` matched inside `discharged`), and added explicit negated-urgency handling plus four regression evaluation cases. The reviewed 44-case result has no expected-assertion failures. This remains synthetic dataset evidence, not a production accuracy estimate. See `docs/09-evaluation.md`.

## Safety

Never add real Pegasus, passenger, agency, PNR, employee, email, or phone data. Never commit secrets or credentials. All future outputs are advisory and require human review.

## Definition of done

The project MVP will be complete only when approved task requirements are implemented, synthetic test coverage demonstrates the required behavior, security constraints are verified, documentation reflects the implemented system, all AI output remains human-reviewed, and no secret or personal data is stored in the repository.
