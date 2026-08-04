"""Single-source rule data shared by the Python baseline and the workflow JavaScript.

`rules.json` holds the term lists and regular-expression patterns that Tasks 003
and 004 showed to be the drift-prone part of the duplicated implementations.
Patterns are stored in a portable form (for example `[\\s\\S]` instead of an
engine-specific DOTALL flag) so both `re` and JavaScript `RegExp` compile the
same string.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

RULES_PATH = Path(__file__).with_name("rules.json")

_TOP_LEVEL_KEYS = {
    "rules_version",
    "schema_version",
    "max_message_length",
    "synthetic_id_pattern",
    "output_fields",
    "categories",
    "urgencies",
    "statuses",
    "security_flags",
    "category_rules",
    "urgency",
    "missing_information",
    "security",
}
_ALLOWED_FLAGS = {"", "i"}


def load_rules() -> dict[str, Any]:
    """Load the committed rule data file."""

    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def _is_term_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(term, str) and term for term in value)
    )


def _check_pattern(errors: list[str], name: str, value: Any) -> None:
    if not isinstance(value, Mapping) or set(value) != {"pattern", "flags"}:
        errors.append(f"{name} must be an object with pattern and flags")
        return
    if value["flags"] not in _ALLOWED_FLAGS:
        errors.append(f"{name} flags must be one of {sorted(_ALLOWED_FLAGS)}")
    if not isinstance(value["pattern"], str) or not value["pattern"]:
        errors.append(f"{name} pattern must be a non-empty string")
        return
    try:
        re.compile(value["pattern"])
    except re.error:
        errors.append(f"{name} pattern must be a valid regular expression")


def validate_rules(value: Any) -> list[str]:
    """Return deterministic structural errors without consulting the classifier."""

    if not isinstance(value, Mapping):
        return ["rules must be a JSON object"]

    errors: list[str] = []
    if set(value) != _TOP_LEVEL_KEYS:
        errors.append(f"rules keys must be exactly {sorted(_TOP_LEVEL_KEYS)}")
        return errors

    if not isinstance(value["max_message_length"], int) or value["max_message_length"] <= 0:
        errors.append("max_message_length must be a positive integer")
    for key in ("rules_version", "schema_version"):
        if not isinstance(value[key], str) or not value[key]:
            errors.append(f"{key} must be a non-empty string")
    for key in ("output_fields", "categories", "urgencies", "statuses", "security_flags"):
        if not _is_term_list(value[key]) or len(set(value[key])) != len(value[key]):
            errors.append(f"{key} must be a non-empty list of unique strings")
    if _is_term_list(value["output_fields"]) and value["output_fields"] != sorted(value["output_fields"]):
        errors.append("output_fields must be sorted")

    try:
        re.compile(value["synthetic_id_pattern"])
    except (TypeError, re.error):
        errors.append("synthetic_id_pattern must be a valid regular expression")

    category_rules = value["category_rules"]
    if not isinstance(category_rules, list) or not category_rules:
        errors.append("category_rules must be a non-empty list")
    else:
        for index, entry in enumerate(category_rules):
            if (
                not isinstance(entry, list)
                or len(entry) != 2
                or not isinstance(entry[0], str)
                or not _is_term_list(entry[1])
            ):
                errors.append(f"category_rules[{index}] must be [category, non-empty terms]")

    urgency = value["urgency"]
    if not isinstance(urgency, Mapping) or set(urgency) != {
        "critical_terms",
        "urgent_pattern",
        "high_terms",
        "low_terms",
    }:
        errors.append("urgency must define critical_terms, urgent_pattern, high_terms, low_terms")
    else:
        for key in ("critical_terms", "high_terms", "low_terms"):
            if not _is_term_list(urgency[key]):
                errors.append(f"urgency.{key} must be a non-empty list of terms")
        try:
            re.compile(urgency["urgent_pattern"])
        except (TypeError, re.error):
            errors.append("urgency.urgent_pattern must be a valid regular expression")

    missing = value["missing_information"]
    if not isinstance(missing, Mapping) or "general" not in missing:
        errors.append("missing_information must be an object with a general entry")
    else:
        for category, checks in missing.items():
            if category == "general":
                continue
            if not isinstance(checks, list) or not checks:
                errors.append(f"missing_information.{category} must be a non-empty list")
                continue
            for index, check in enumerate(checks):
                if (
                    not isinstance(check, Mapping)
                    or set(check) != {"label", "terms"}
                    or not isinstance(check["label"], str)
                    or not check["label"]
                    or not _is_term_list(check["terms"])
                ):
                    errors.append(
                        f"missing_information.{category}[{index}] must define label and non-empty terms"
                    )
        general = missing["general"]
        if (
            not isinstance(general, Mapping)
            or set(general) != {"label", "min_words", "terms"}
            or not isinstance(general.get("label"), str)
            or not general.get("label")
            or not isinstance(general.get("min_words"), int)
            or general.get("min_words", 0) <= 0
            or not _is_term_list(general.get("terms"))
        ):
            errors.append("missing_information.general must define label, positive min_words, and terms")

    security = value["security"]
    if not isinstance(security, Mapping) or set(security) != {
        "credential_pattern",
        "url_pattern",
        "payment_terms",
        "identity_terms",
        "prompt_injection_patterns",
    }:
        errors.append(
            "security must define credential_pattern, url_pattern, payment_terms, "
            "identity_terms, prompt_injection_patterns"
        )
    else:
        _check_pattern(errors, "security.credential_pattern", security["credential_pattern"])
        _check_pattern(errors, "security.url_pattern", security["url_pattern"])
        for key in ("payment_terms", "identity_terms"):
            if not _is_term_list(security[key]):
                errors.append(f"security.{key} must be a non-empty list of terms")
        patterns = security["prompt_injection_patterns"]
        if not isinstance(patterns, list) or not patterns:
            errors.append("security.prompt_injection_patterns must be a non-empty list")
        else:
            for index, pattern in enumerate(patterns):
                _check_pattern(errors, f"security.prompt_injection_patterns[{index}]", pattern)

    return errors
