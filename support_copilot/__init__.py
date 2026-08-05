"""Local, deterministic support-request analysis baseline."""

from .classifier import analyze_request, validate_input, validate_output
from .evaluation import (
    assert_valid_evaluation_cases,
    evaluate_cases,
    render_json_report,
    render_markdown_report,
    validate_evaluation_cases,
)
from .fallback import (
    DEFAULT_BUDGET_SECONDS,
    PROVENANCE,
    last_provenance,
    reset_provenance,
    with_baseline_fallback,
)

__all__ = [
    "DEFAULT_BUDGET_SECONDS",
    "PROVENANCE",
    "analyze_request",
    "assert_valid_evaluation_cases",
    "evaluate_cases",
    "last_provenance",
    "render_json_report",
    "render_markdown_report",
    "reset_provenance",
    "validate_evaluation_cases",
    "validate_input",
    "validate_output",
    "with_baseline_fallback",
]
