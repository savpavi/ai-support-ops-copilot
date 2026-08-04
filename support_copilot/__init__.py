"""Local, deterministic support-request analysis baseline."""

from .classifier import analyze_request, validate_input, validate_output
from .evaluation import (
    assert_valid_evaluation_cases,
    evaluate_cases,
    render_json_report,
    render_markdown_report,
    validate_evaluation_cases,
)

__all__ = [
    "analyze_request",
    "assert_valid_evaluation_cases",
    "evaluate_cases",
    "render_json_report",
    "render_markdown_report",
    "validate_evaluation_cases",
    "validate_input",
    "validate_output",
]
