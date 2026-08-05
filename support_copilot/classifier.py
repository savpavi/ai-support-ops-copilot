"""Deterministic, n8n-independent support request classifier.

Request text is always treated as untrusted data. It is matched against fixed
rules and is never evaluated as code or as instructions to this module.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from functools import lru_cache
from typing import Any

from .rules import load_rules


def _compile_flagged(entry: Mapping[str, Any]) -> re.Pattern[str]:
    return re.compile(entry["pattern"], re.IGNORECASE if "i" in entry["flags"] else 0)


def _apply_rules(rules: Mapping[str, Any]) -> None:
    """Compile the shared rule data into the module-level matching structures.

    The same `rules.json` content is injected into the committed workflow
    JavaScript by `support_copilot.workflow_build`; both implementations must
    only ever change through that shared file.
    """

    global SCHEMA_VERSION, MAX_MESSAGE_LENGTH, CATEGORIES, URGENCIES, STATUSES
    global SECURITY_FLAGS, OUTPUT_FIELDS, _SYNTHETIC_ID, _URL, _CREDENTIAL_REQUEST
    global _URGENT, _CATEGORY_RULES, _PROMPT_INJECTION_PATTERNS, _PAYMENT_TERMS
    global _IDENTITY_TERMS, _CRITICAL_TERMS, _HIGH_TERMS, _LOW_TERMS
    global _MISSING_RULES, _GENERAL_MISSING
    global REPLY_PREFIX, REPLY_MAX_LENGTH, _REPLY_LINK, _REPLY_COMMITMENTS

    SCHEMA_VERSION = rules["schema_version"]
    MAX_MESSAGE_LENGTH = rules["max_message_length"]
    CATEGORIES = set(rules["categories"])
    URGENCIES = set(rules["urgencies"])
    STATUSES = set(rules["statuses"])
    SECURITY_FLAGS = set(rules["security_flags"])
    OUTPUT_FIELDS = set(rules["output_fields"])
    _SYNTHETIC_ID = re.compile(rules["synthetic_id_pattern"])
    _CATEGORY_RULES = tuple((category, tuple(terms)) for category, terms in rules["category_rules"])

    security = rules["security"]
    _URL = _compile_flagged(security["url_pattern"])
    _CREDENTIAL_REQUEST = _compile_flagged(security["credential_pattern"])
    _PROMPT_INJECTION_PATTERNS = tuple(
        _compile_flagged(entry) for entry in security["prompt_injection_patterns"]
    )
    _PAYMENT_TERMS = tuple(security["payment_terms"])
    _IDENTITY_TERMS = tuple(security["identity_terms"])

    urgency = rules["urgency"]
    _URGENT = re.compile(urgency["urgent_pattern"])
    _CRITICAL_TERMS = tuple(urgency["critical_terms"])
    _HIGH_TERMS = tuple(urgency["high_terms"])
    _LOW_TERMS = tuple(urgency["low_terms"])

    missing = rules["missing_information"]
    _MISSING_RULES = {
        category: tuple((check["label"], tuple(check["terms"])) for check in checks)
        for category, checks in missing.items()
        if category != "general"
    }
    general = missing["general"]
    _GENERAL_MISSING = (general["label"], general["min_words"], tuple(general["terms"]))


def _apply_reply_guard(rules: Mapping[str, Any]) -> None:
    global REPLY_PREFIX, REPLY_MAX_LENGTH, _REPLY_LINK, _REPLY_COMMITMENTS

    guard = rules["reply_guard"]
    REPLY_PREFIX = guard["required_prefix"]
    REPLY_MAX_LENGTH = guard["max_length"]
    _REPLY_LINK = _compile_flagged(guard["link_pattern"])
    _REPLY_COMMITMENTS = tuple(_compile_flagged(entry) for entry in guard["commitment_patterns"])


def validate_reply(reply: Any) -> list[str]:
    """Return the reasons a suggested reply must not be used, or an empty list.

    Deterministic and shared: the rule data lives in `rules.json`, so the same
    guard can be replicated in the workflow JavaScript if generated text ever
    reaches it.

    The prefix, length, link and reflected-sensitive-content checks are exact.
    The commitment check is a term list, and Tasks 004 and 006 measured what
    term lists are worth against paraphrase: a draft that says the money will
    arrive on Thursday can pass a list built around 'we will refund'. This is a
    floor, not a semantic guarantee.
    """

    if not isinstance(reply, str):
        return ["reply must be a string"]

    errors: list[str] = []
    if not reply.startswith(REPLY_PREFIX):
        errors.append("reply must begin with the human-review prefix")
    if len(reply) > REPLY_MAX_LENGTH:
        errors.append(f"reply exceeds {REPLY_MAX_LENGTH} characters")
    if _REPLY_LINK.search(reply):
        errors.append("reply must not contain a link or destination")

    # The request-side scan, turned on the reply: a draft that reflects a card
    # number, an identity-document reference, a credential or an injection
    # attempt back at the sender is unusable regardless of how it was produced.
    reflected = _security_flags(reply)
    if reflected:
        errors.append("reply reflects sensitive content: " + ", ".join(reflected))

    for pattern in _REPLY_COMMITMENTS:
        match = pattern.search(reply)
        if match:
            errors.append(f"reply commits to an action: {match.group(0).strip()!r}")
            break

    return errors


_apply_rules(load_rules())
_apply_reply_guard(load_rules())


def validate_input(value: Any) -> list[str]:
    """Return deterministic validation errors for the public input contract."""

    if not isinstance(value, Mapping):
        return ["input must be a JSON object"]

    errors: list[str] = []
    allowed_keys = {"request_id", "message"}
    extra_keys = sorted(str(key) for key in value.keys() if key not in allowed_keys)
    if extra_keys:
        errors.append(f"unexpected fields: {', '.join(extra_keys)}")

    request_id = value.get("request_id")
    if not isinstance(request_id, str) or not _SYNTHETIC_ID.fullmatch(request_id):
        errors.append("request_id must match SYN-[A-Z0-9-] and be 7-44 characters long")

    message = value.get("message")
    if not isinstance(message, str):
        errors.append("message must be a string")
    elif not message.strip():
        errors.append("message must not be empty")
    elif len(message) > MAX_MESSAGE_LENGTH:
        errors.append(f"message must be at most {MAX_MESSAGE_LENGTH} characters")

    return errors


@lru_cache(maxsize=None)
def _term_pattern(term: str) -> re.Pattern[str]:
    return re.compile(r"\b" + re.escape(term) + r"\b")


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(_term_pattern(term).search(text) for term in terms)


def _security_flags(text: str) -> list[str]:
    flags: list[str] = []
    if any(pattern.search(text) for pattern in _PROMPT_INJECTION_PATTERNS):
        flags.append("prompt_injection")
    if _CREDENTIAL_REQUEST.search(text):
        flags.append("credential_request")
    if _contains_any(text, _PAYMENT_TERMS):
        flags.append("payment_data")
    if _contains_any(text, _IDENTITY_TERMS):
        flags.append("sensitive_identity_data")
    if _URL.search(text):
        flags.append("suspicious_link")
    return sorted(flags)


def _category(text: str) -> str:
    for category, terms in _CATEGORY_RULES:
        if _contains_any(text, terms):
            return category
    return "general"


def _urgency(text: str, flags: list[str]) -> str:
    if _contains_any(text, _CRITICAL_TERMS):
        return "critical"
    if _URGENT.search(text) or _contains_any(text, _HIGH_TERMS):
        return "high"
    if flags:
        return "high"
    if _contains_any(text, _LOW_TERMS):
        return "low"
    return "normal"


def _missing_information(category: str, text: str) -> list[str]:
    missing: list[str] = []
    if category in _MISSING_RULES:
        for label, terms in _MISSING_RULES[category]:
            if not _contains_any(text, terms):
                missing.append(label)
    else:
        label, min_words, terms = _GENERAL_MISSING
        if len(text.split()) < min_words or _contains_any(text, terms):
            missing.append(label)
    return missing


def _rationale(category: str, urgency: str, flags: list[str]) -> str:
    category_reason = {
        "access_issue": "The request describes a sign-in or access problem.",
        "account_change": "The request asks for an account or profile change.",
        "billing": "The request concerns a charge, payment, invoice, or refund.",
        "service_disruption": "The request describes unavailable or failing service.",
        "general": "The request lacks a more specific supported category.",
    }[category]
    urgency_reason = {
        "low": "It explicitly indicates that no prompt response is needed.",
        "normal": "No deterministic high-urgency indicator was found.",
        "high": "Urgent access, disruption, or security-review indicators were found.",
        "critical": "The text contains an explicit safety or medical emergency indicator.",
    }[urgency]
    if flags:
        return f"{category_reason} {urgency_reason} Security-sensitive content requires review."
    return f"{category_reason} {urgency_reason}"


def _suggested_reply(category: str, missing: list[str], flags: list[str]) -> str:
    if flags:
        opening = "Draft for human review: We received your request, but it contains content that requires a security review."
    else:
        topic = category.replace("_", " ")
        opening = f"Draft for human review: We received your {topic} request."
    if missing:
        return f"{opening} Please provide: {', '.join(missing)}. Do not include passwords, payment-card data, or identity documents."
    return f"{opening} A support operator will review the details before any action is taken."


def _security_text(value: Any) -> str:
    """Extract only known request-text fields for risk scanning, even if shape is invalid."""

    if not isinstance(value, Mapping):
        return ""
    parts = [value.get(field) for field in ("message", "request_text")]
    return "\n".join(part.strip().lower() for part in parts if isinstance(part, str))


def _rejected_result(value: Any, errors: list[str], detected_flags: list[str]) -> dict[str, Any]:
    request_id = value.get("request_id") if isinstance(value, Mapping) else None
    if not isinstance(request_id, str) or not _SYNTHETIC_ID.fullmatch(request_id):
        request_id = None
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "rejected",
        "request_id": request_id,
        "category": "unknown",
        "urgency": "unknown",
        "rationale": "Input validation failed; no classification was attempted.",
        "missing_information": [],
        "suggested_reply": "Draft for human review: The request could not be processed safely. Please provide a valid synthetic request.",
        "security_flags": sorted({"invalid_input", *detected_flags}),
        "human_review_required": True,
        "errors": errors,
    }


def analyze_request(value: Any) -> dict[str, Any]:
    """Analyze one request and always return an output-contract-shaped result."""

    errors = validate_input(value)
    if errors:
        result = _rejected_result(value, errors, _security_flags(_security_text(value)))
        validate_output(result)
        return result

    request_id = value["request_id"]
    text = value["message"].strip().lower()
    flags = _security_flags(text)
    category = _category(text)
    urgency = _urgency(text, flags)
    missing = _missing_information(category, text)
    result = {
        "schema_version": SCHEMA_VERSION,
        "status": "accepted",
        "request_id": request_id,
        "category": category,
        "urgency": urgency,
        "rationale": _rationale(category, urgency, flags),
        "missing_information": missing,
        "suggested_reply": _suggested_reply(category, missing, flags),
        "security_flags": flags,
        "human_review_required": True,
        "errors": [],
    }
    validate_output(result)
    return result


def validate_output(value: Any) -> None:
    """Raise ValueError unless value exactly satisfies the output contract."""

    if not isinstance(value, Mapping):
        raise ValueError("output must be an object")

    if set(value) != OUTPUT_FIELDS:
        raise ValueError("output fields do not match the contract")
    if not isinstance(value["schema_version"], str) or value["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported schema_version")
    if not isinstance(value["status"], str) or value["status"] not in STATUSES:
        raise ValueError("invalid status")
    if not isinstance(value["category"], str) or value["category"] not in CATEGORIES:
        raise ValueError("invalid category")
    if not isinstance(value["urgency"], str) or value["urgency"] not in URGENCIES:
        raise ValueError("invalid urgency")
    if value["human_review_required"] is not True:
        raise ValueError("human_review_required must be true")
    if value["request_id"] is not None:
        if not isinstance(value["request_id"], str) or not _SYNTHETIC_ID.fullmatch(value["request_id"]):
            raise ValueError("invalid request_id")
    if not isinstance(value["rationale"], str) or not value["rationale"]:
        raise ValueError("rationale must be a non-empty string")
    if not isinstance(value["suggested_reply"], str) or not value["suggested_reply"].startswith(
        "Draft for human review:"
    ):
        raise ValueError("suggested_reply must be a human-review draft")
    for field in ("missing_information", "security_flags", "errors"):
        if not isinstance(value[field], list) or not all(isinstance(item, str) for item in value[field]):
            raise ValueError(f"{field} must be a list of strings")
    if not set(value["security_flags"]).issubset(SECURITY_FLAGS):
        raise ValueError("invalid security flag")
    if value["status"] == "accepted" and value["errors"]:
        raise ValueError("accepted output cannot contain errors")
    if value["status"] == "rejected":
        if not value["errors"] or "invalid_input" not in value["security_flags"]:
            raise ValueError("rejected output must include errors and invalid_input")
