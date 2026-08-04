"""Validation for the independently reviewed synthetic evaluation dataset."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from .classifier import CATEGORIES, SECURITY_FLAGS, STATUSES, URGENCIES
from .classifier import analyze_request, validate_output
from .workflow_parity import analyze_workflow_requests

MIN_EVALUATION_CASES = 30
MAX_EVALUATION_CASES = 50

_CASE_ID = re.compile(r"^SYN-EVAL-[A-Z0-9][A-Z0-9-]{2,30}$")
_CASE_FIELDS = {"case_id", "description", "input", "expected", "tags"}
_EXPECTED_FIELDS = {
    "status",
    "category",
    "urgency",
    "security_flags",
    "missing_information",
    "human_review_required",
}
_REQUIRED_TAGS = {
    "ambiguous",
    "keyword_boundary",
    "prompt_injection_negative",
    "reply_branch",
}


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def _json_compatible(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def validate_evaluation_cases(value: Any) -> list[str]:
    """Return deterministic errors without running or consulting the classifier."""

    if not isinstance(value, list):
        return ["evaluation dataset must be a JSON array"]

    errors: list[str] = []
    if not MIN_EVALUATION_CASES <= len(value) <= MAX_EVALUATION_CASES:
        errors.append(
            f"evaluation dataset must contain {MIN_EVALUATION_CASES}-{MAX_EVALUATION_CASES} cases"
        )

    seen_ids: set[str] = set()
    covered_categories: set[str] = set()
    covered_urgencies: set[str] = set()
    covered_flags: set[str] = set()
    covered_tags: set[str] = set()
    has_rejected = False

    for index, case in enumerate(value):
        prefix = f"case[{index}]"
        if not isinstance(case, Mapping):
            errors.append(f"{prefix} must be an object")
            continue

        if set(case) != _CASE_FIELDS:
            errors.append(f"{prefix} fields must be exactly {sorted(_CASE_FIELDS)}")

        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not _CASE_ID.fullmatch(case_id):
            errors.append(f"{prefix}.case_id must match SYN-EVAL-[A-Z0-9-]")
        elif case_id in seen_ids:
            errors.append(f"{prefix}.case_id must be unique: {case_id}")
        else:
            seen_ids.add(case_id)

        description = case.get("description")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{prefix}.description must be a non-empty string")

        if not _json_compatible(case.get("input")):
            errors.append(f"{prefix}.input must be JSON-compatible")

        tags = case.get("tags")
        if not _is_string_list(tags):
            errors.append(f"{prefix}.tags must be a non-empty list of strings")
        else:
            if len(tags) != len(set(tags)):
                errors.append(f"{prefix}.tags must not contain duplicates")
            covered_tags.update(tags)

        expected = case.get("expected")
        if not isinstance(expected, Mapping):
            errors.append(f"{prefix}.expected must be an object")
            continue
        if set(expected) != _EXPECTED_FIELDS:
            errors.append(f"{prefix}.expected fields must be exactly {sorted(_EXPECTED_FIELDS)}")

        status = expected.get("status")
        category = expected.get("category")
        urgency = expected.get("urgency")
        flags = expected.get("security_flags")
        missing = expected.get("missing_information")

        if status not in STATUSES:
            errors.append(f"{prefix}.expected.status is invalid")
        else:
            has_rejected = has_rejected or status == "rejected"
        if category not in CATEGORIES:
            errors.append(f"{prefix}.expected.category is invalid")
        else:
            covered_categories.add(category)
        if urgency not in URGENCIES:
            errors.append(f"{prefix}.expected.urgency is invalid")
        else:
            covered_urgencies.add(urgency)
        if not isinstance(flags, list) or not all(isinstance(flag, str) for flag in flags):
            errors.append(f"{prefix}.expected.security_flags must be a list of strings")
        elif flags != sorted(set(flags)):
            errors.append(f"{prefix}.expected.security_flags must be sorted and unique")
        elif not set(flags).issubset(SECURITY_FLAGS):
            errors.append(f"{prefix}.expected.security_flags contains an unknown flag")
        else:
            covered_flags.update(flags)
        if not isinstance(missing, list) or not all(isinstance(item, str) for item in missing):
            errors.append(f"{prefix}.expected.missing_information must be a list of strings")
        if expected.get("human_review_required") is not True:
            errors.append(f"{prefix}.expected.human_review_required must be true")

        if status == "accepted" and (category == "unknown" or urgency == "unknown"):
            errors.append(f"{prefix} accepted expectations cannot use unknown classification values")
        if status == "rejected":
            if category != "unknown" or urgency != "unknown":
                errors.append(f"{prefix} rejected expectations must use unknown category and urgency")
            if isinstance(flags, list) and "invalid_input" not in flags:
                errors.append(f"{prefix} rejected expectations must include invalid_input")
            if missing != []:
                errors.append(f"{prefix} rejected expectations must have no missing-information items")

    required_categories = CATEGORIES - {"unknown"}
    if not required_categories.issubset(covered_categories):
        errors.append(f"dataset is missing categories: {sorted(required_categories - covered_categories)}")
    required_urgencies = URGENCIES - {"unknown"}
    if not required_urgencies.issubset(covered_urgencies):
        errors.append(f"dataset is missing urgencies: {sorted(required_urgencies - covered_urgencies)}")
    if not SECURITY_FLAGS.issubset(covered_flags):
        errors.append(f"dataset is missing security flags: {sorted(SECURITY_FLAGS - covered_flags)}")
    if not _REQUIRED_TAGS.issubset(covered_tags):
        errors.append(f"dataset is missing coverage tags: {sorted(_REQUIRED_TAGS - covered_tags)}")
    if not has_rejected:
        errors.append("dataset must include at least one rejected-input case")

    return errors


def assert_valid_evaluation_cases(value: Any) -> None:
    """Raise a single review-friendly exception when dataset validation fails."""

    errors = validate_evaluation_cases(value)
    if errors:
        raise ValueError("invalid evaluation dataset:\n- " + "\n- ".join(errors))


def make_rate(numerator: int, denominator: int) -> dict[str, int | float | None]:
    """Return an explicit, JSON-safe rate with undefined represented as null."""

    if numerator < 0 or denominator < 0 or numerator > denominator:
        raise ValueError("rate counts must satisfy 0 <= numerator <= denominator")
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": None if denominator == 0 else numerator / denominator,
    }


def _expected_matches(expected: Mapping[str, Any], actual: Any, field: str) -> bool:
    return isinstance(actual, Mapping) and actual.get(field) == expected[field]


def evaluate_cases(
    cases: Any,
    *,
    workflow_results: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate Python behavior, safety assertions, and local workflow parity."""

    assert_valid_evaluation_cases(cases)
    typed_cases: list[Mapping[str, Any]] = list(cases)
    python_results: list[dict[str, Any] | None] = []
    python_errors: list[str | None] = []
    for case in typed_cases:
        try:
            python_results.append(analyze_request(case["input"]))
            python_errors.append(None)
        except Exception as error:  # Defensive evaluation boundary; details stay synthetic.
            python_results.append(None)
            python_errors.append(type(error).__name__)

    if workflow_results is None:
        workflow_values = analyze_workflow_requests([case["input"] for case in typed_cases])
    else:
        workflow_values = list(workflow_results)
    if len(workflow_values) != len(typed_cases):
        raise ValueError("workflow result count must match evaluation case count")

    quality_fields = ("category", "urgency", "security_flags", "missing_information")
    expected_fields = ("status", *quality_fields, "human_review_required")
    quality_counts = {field: 0 for field in quality_fields}
    exact_assertion_count = 0
    contract_count = 0
    review_count = 0
    parity_count = 0
    rejected_total = 0
    safe_rejection_count = 0
    failures: list[dict[str, Any]] = []
    flag_counts = {flag: {"true_positive": 0, "false_positive": 0, "false_negative": 0} for flag in sorted(SECURITY_FLAGS)}

    for index, case in enumerate(typed_cases):
        expected = case["expected"]
        actual = python_results[index]
        workflow = workflow_values[index]
        mismatches: dict[str, dict[str, Any]] = {}
        checks: list[str] = []

        for field in expected_fields:
            if not _expected_matches(expected, actual, field):
                mismatches[field] = {
                    "expected": expected[field],
                    "actual": actual.get(field) if isinstance(actual, Mapping) else None,
                }
        if not mismatches:
            exact_assertion_count += 1
        for field in quality_fields:
            if field not in mismatches:
                quality_counts[field] += 1

        contract_valid = False
        if isinstance(actual, Mapping):
            try:
                validate_output(actual)
                contract_valid = True
            except ValueError:
                pass
        if contract_valid:
            contract_count += 1
        else:
            checks.append("output_contract")

        review_valid = isinstance(actual, Mapping) and actual.get("human_review_required") is True
        if review_valid:
            review_count += 1
        else:
            checks.append("human_review")

        if expected["status"] == "rejected":
            rejected_total += 1
            safe_rejection = (
                isinstance(actual, Mapping)
                and actual.get("status") == "rejected"
                and "invalid_input" in actual.get("security_flags", [])
                and actual.get("human_review_required") is True
            )
            if safe_rejection:
                safe_rejection_count += 1
            else:
                checks.append("safe_rejection")

        parity = isinstance(actual, Mapping) and dict(actual) == dict(workflow)
        if parity:
            parity_count += 1
        else:
            checks.append("python_n8n_parity")

        expected_flags = set(expected["security_flags"])
        actual_flags = set(actual.get("security_flags", [])) if isinstance(actual, Mapping) else set()
        for flag in sorted(SECURITY_FLAGS):
            if flag in expected_flags and flag in actual_flags:
                flag_counts[flag]["true_positive"] += 1
            elif flag not in expected_flags and flag in actual_flags:
                flag_counts[flag]["false_positive"] += 1
            elif flag in expected_flags and flag not in actual_flags:
                flag_counts[flag]["false_negative"] += 1

        if mismatches:
            checks.append("expected_assertions")
        if python_errors[index] is not None:
            checks.append("python_execution")
        if checks:
            failure: dict[str, Any] = {
                "case_id": case["case_id"],
                "checks": sorted(set(checks)),
            }
            if mismatches:
                failure["mismatches"] = {key: mismatches[key] for key in sorted(mismatches)}
            if python_errors[index] is not None:
                failure["python_error_type"] = python_errors[index]
            failures.append(failure)

    per_flag: dict[str, Any] = {}
    for flag in sorted(flag_counts):
        counts = flag_counts[flag]
        tp = counts["true_positive"]
        fp = counts["false_positive"]
        fn = counts["false_negative"]
        per_flag[flag] = {
            **counts,
            "precision": make_rate(tp, tp + fp),
            "recall": make_rate(tp, tp + fn),
        }

    total = len(typed_cases)
    return {
        "report_version": "1.0",
        "dataset_cases": total,
        "metrics": {
            "heuristic_quality": {
                "category_exact": make_rate(quality_counts["category"], total),
                "urgency_exact": make_rate(quality_counts["urgency"], total),
                "security_flags_exact": make_rate(quality_counts["security_flags"], total),
                "missing_information_exact": make_rate(quality_counts["missing_information"], total),
                "all_expected_assertions": make_rate(exact_assertion_count, total),
            },
            "safety_invariants": {
                "safe_rejection": make_rate(safe_rejection_count, rejected_total),
                "output_contract_valid": make_rate(contract_count, total),
                "human_review_required": make_rate(review_count, total),
            },
            "python_n8n_parity": make_rate(parity_count, total),
            "security_flags": per_flag,
        },
        "failed_case_ids": [failure["case_id"] for failure in failures],
        "failures": failures,
    }


def render_json_report(report: Mapping[str, Any]) -> str:
    """Render stable machine-readable output without timestamps or environment data."""

    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def _format_rate(metric: Mapping[str, Any]) -> str:
    rate = metric["rate"]
    rendered = "undefined" if rate is None else f"{rate:.3f}"
    return f"{metric['numerator']}/{metric['denominator']} ({rendered})"


def render_markdown_report(report: Mapping[str, Any]) -> str:
    """Render a concise deterministic summary that distinguishes quality and safety."""

    quality = report["metrics"]["heuristic_quality"]
    safety = report["metrics"]["safety_invariants"]
    lines = [
        "# Synthetic Evaluation Summary",
        "",
        f"Evaluated cases: {report['dataset_cases']}",
        "",
        "## Heuristic quality observations",
        "",
        f"- Category exact: {_format_rate(quality['category_exact'])}",
        f"- Urgency exact: {_format_rate(quality['urgency_exact'])}",
        f"- Security flags exact: {_format_rate(quality['security_flags_exact'])}",
        f"- Missing information exact: {_format_rate(quality['missing_information_exact'])}",
        f"- All expected assertions: {_format_rate(quality['all_expected_assertions'])}",
        "",
        "## Safety and contract invariants",
        "",
        f"- Safe rejection: {_format_rate(safety['safe_rejection'])}",
        f"- Output contract valid: {_format_rate(safety['output_contract_valid'])}",
        f"- Human review required: {_format_rate(safety['human_review_required'])}",
        f"- Python/n8n parity: {_format_rate(report['metrics']['python_n8n_parity'])}",
        "",
        "## Security flags",
        "",
        "| Flag | TP | FP | FN | Precision | Recall |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for flag, metric in report["metrics"]["security_flags"].items():
        lines.append(
            f"| {flag} | {metric['true_positive']} | {metric['false_positive']} | "
            f"{metric['false_negative']} | {_format_rate(metric['precision'])} | "
            f"{_format_rate(metric['recall'])} |"
        )
    lines.extend(["", "## Failed cases", ""])
    if report["failed_case_ids"]:
        lines.extend(f"- `{case_id}`" for case_id in report["failed_case_ids"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "Expected labels are synthetic evaluation assertions, not production truth. All outputs require human review.",
            "",
        ]
    )
    return "\n".join(lines)
