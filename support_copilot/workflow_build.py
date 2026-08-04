"""Deterministic generator for the committed workflow Code-node JavaScript.

The JavaScript logic lives as reviewable templates under `n8n/src/`; every rule
literal in them is a `__TOKEN__` placeholder filled from `rules.json`. The
committed workflow artifact must always equal the generated output byte for
byte, which the test suite and `scripts/build_workflow.py --check` enforce.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .rules import load_rules

ROOT = Path(__file__).resolve().parents[1]
ANALYZE_TEMPLATE_PATH = ROOT / "n8n" / "src" / "analyze-and-validate.js"
GUARD_TEMPLATE_PATH = ROOT / "n8n" / "src" / "human-review-guard.js"
WORKFLOW_PATH = ROOT / "n8n" / "workflows" / "ai-support-operations-copilot.json"

_LEFTOVER_TOKEN = re.compile(r"__[A-Z0-9_]+__")


def _js_string(value: str) -> str:
    if "'" in value and '"' in value:
        raise ValueError(f"term may not contain both quote styles: {value!r}")
    return f'"{value}"' if "'" in value else f"'{value}'"


def _js_terms(terms: list[str]) -> str:
    return "[" + ", ".join(_js_string(term) for term in terms) + "]"


def _js_regex(entry: Mapping[str, str]) -> str:
    return f"/{entry['pattern']}/{entry['flags']}"


def _js_lines(header: str, values: list[str]) -> str:
    lines = [f"const {header} = ["]
    lines.extend(f"  {value}," for value in values)
    lines.append("];")
    return "\n".join(lines)


def _replacements(rules: Mapping[str, Any]) -> dict[str, str]:
    security = rules["security"]
    urgency = rules["urgency"]
    replacements = {
        "__SCHEMA_VERSION__": _js_string(rules["schema_version"]),
        "__MAX_MESSAGE_LENGTH__": str(rules["max_message_length"]),
        "__SYNTHETIC_ID__": f"/{rules['synthetic_id_pattern']}/",
        "__URL_PATTERN__": _js_regex(security["url_pattern"]),
        "__CREDENTIAL_PATTERN__": _js_regex(security["credential_pattern"]),
        "__URGENT_PATTERN__": f"/{urgency['urgent_pattern']}/",
        "__CATEGORY_RULES__": _js_lines(
            "CATEGORY_RULES",
            [
                f"[{_js_string(category)}, {_js_terms(terms)}]"
                for category, terms in rules["category_rules"]
            ],
        ),
        "__PROMPT_INJECTION_PATTERNS__": _js_lines(
            "PROMPT_INJECTION_PATTERNS",
            [_js_regex(entry) for entry in security["prompt_injection_patterns"]],
        ),
        "__PAYMENT_TERMS__": _js_terms(security["payment_terms"]),
        "__IDENTITY_TERMS__": _js_terms(security["identity_terms"]),
        "__CRITICAL_TERMS__": _js_terms(urgency["critical_terms"]),
        "__HIGH_TERMS__": _js_terms(urgency["high_terms"]),
        "__LOW_TERMS__": _js_terms(urgency["low_terms"]),
        "__OUTPUT_FIELDS__": _js_lines(
            "REQUIRED_FIELDS", [_js_string(field) for field in rules["output_fields"]]
        ),
        "__CATEGORIES__": _js_terms(rules["categories"]),
        "__URGENCIES__": _js_terms(rules["urgencies"]),
        "__STATUSES__": _js_terms(rules["statuses"]),
        "__SECURITY_FLAGS__": _js_terms(rules["security_flags"]),
    }
    for category, checks in rules["missing_information"].items():
        if category == "general":
            replacements["__MI_GENERAL_LABEL__"] = _js_string(checks["label"])
            replacements["__MI_GENERAL_MIN_WORDS__"] = str(checks["min_words"])
            replacements["__MI_GENERAL_TERMS__"] = _js_terms(checks["terms"])
        else:
            for index, check in enumerate(checks):
                replacements[f"__MI_{category}_{index}_LABEL__"] = _js_string(check["label"])
                replacements[f"__MI_{category}_{index}_TERMS__"] = _js_terms(check["terms"])
    return replacements


def _render(template: str, rules: Mapping[str, Any]) -> str:
    rendered = template
    for token, value in _replacements(rules).items():
        rendered = rendered.replace(token, value)
    leftover = _LEFTOVER_TOKEN.search(rendered)
    if leftover:
        raise ValueError(f"unfilled template token: {leftover.group(0)}")
    return rendered


def render_analyze_jscode(rules: Mapping[str, Any] | None = None) -> str:
    return _render(ANALYZE_TEMPLATE_PATH.read_text(encoding="utf-8"), rules or load_rules())


def render_guard_jscode(rules: Mapping[str, Any] | None = None) -> str:
    return _render(GUARD_TEMPLATE_PATH.read_text(encoding="utf-8"), rules or load_rules())


def generate_workflow_text(rules: Mapping[str, Any] | None = None) -> str:
    """Return the workflow JSON with both Code-node bodies regenerated from source."""

    workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}
    nodes["Analyze and Validate"]["parameters"]["jsCode"] = render_analyze_jscode(rules)
    nodes["Human Review Guard"]["parameters"]["jsCode"] = render_guard_jscode(rules)
    return json.dumps(workflow, indent=2) + "\n"
