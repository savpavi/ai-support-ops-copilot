"""Deterministic, n8n-independent support request classifier.

Request text is always treated as untrusted data. It is matched against fixed
rules and is never evaluated as code or as instructions to this module.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

SCHEMA_VERSION = "1.0"
MAX_MESSAGE_LENGTH = 4_000

CATEGORIES = {
    "access_issue",
    "account_change",
    "billing",
    "service_disruption",
    "general",
    "unknown",
}
URGENCIES = {"low", "normal", "high", "critical", "unknown"}
STATUSES = {"accepted", "rejected"}
SECURITY_FLAGS = {
    "credential_request",
    "invalid_input",
    "payment_data",
    "prompt_injection",
    "sensitive_identity_data",
    "suspicious_link",
}

_SYNTHETIC_ID = re.compile(r"^SYN-[A-Z0-9][A-Z0-9-]{2,39}$")
_URL = re.compile(r"https?://|www\.", re.IGNORECASE)

_CATEGORY_RULES = (
    ("access_issue", ("cannot log in", "can't log in", "locked out", "sign in", "login")),
    ("billing", ("charged", "charge", "billing", "invoice", "refund", "payment")),
    (
        "service_disruption",
        ("service unavailable", "unavailable", "outage", "not working", "system down", "stopped working"),
    ),
    ("account_change", ("change account", "update profile", "change name", "account update")),
)

_PROMPT_INJECTION_PATTERNS = (
    re.compile(
        r"\b(?:ignore|disregard|override)\b.{0,40}\b(?:previous|prior|system|developer|hidden)\s+"
        r"(?:instructions?|rules?|prompts?|policies?)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:disable|remove|skip|bypass|avoid|turn\s+off)\b.{0,30}\b"
        r"(?:human[ _-]?review|review requirement|human approval)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:approve|execute|send|submit|publish|process)\b.{0,40}\b"
        r"(?:automatically|without\s+(?:human\s+)?review|without\s+approval)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\bautomatically\b.{0,20}\b(?:approve|execute|send|submit|publish|process)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:set|change|alter|modify|override)\b.{0,30}\b"
        r"(?:human_review_required|security_flags|(?:status|urgency|category)\s+(?:field|value|to))\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:human_review_required|security_flags)\b.{0,30}\b"
        r"(?:false|true|null|empty|unknown|approved|rejected)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:reveal|show|display|print|expose|return)\b.{0,30}\b"
        r"(?:system|developer|hidden)\s+(?:prompts?|instructions?|rules?)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\bbypass\b.{0,30}\b(?:safety|policy|guardrails?|validation|review)\b",
        re.IGNORECASE | re.DOTALL,
    ),
)


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


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _security_flags(text: str) -> list[str]:
    flags: list[str] = []
    if any(pattern.search(text) for pattern in _PROMPT_INJECTION_PATTERNS):
        flags.append("prompt_injection")
    if _contains_any(text, ("password", "passcode", "api key", "access token", "secret token")):
        flags.append("credential_request")
    if _contains_any(text, ("card number", "credit card", "security code", "cvv")):
        flags.append("payment_data")
    if _contains_any(text, ("passport number", "national id", "identity document")):
        flags.append("sensitive_identity_data")
    if _URL.search(text):
        flags.append("suspicious_link")
    return sorted(flags)


def _category(text: str) -> str:
    for category, terms in _CATEGORY_RULES:
        if _contains_any(text, terms):
            return category
    if len(text.split()) < 4 or _contains_any(text, ("help me", "it failed", "problem", "urgent")):
        return "general"
    return "general"


def _urgency(text: str, flags: list[str]) -> str:
    if _contains_any(text, ("immediate danger", "medical emergency", "safety emergency")):
        return "critical"
    if _contains_any(
        text,
        ("urgent", "stranded", "locked out", "system down", "cannot access", "can't access"),
    ):
        return "high"
    if flags:
        return "high"
    if _contains_any(text, ("when convenient", "no rush", "general question")):
        return "low"
    return "normal"


def _missing_information(category: str, text: str) -> list[str]:
    missing: list[str] = []
    if category == "access_issue":
        if not _contains_any(text, ("account", "profile", "workspace")):
            missing.append("affected account context")
        if not _contains_any(text, ("browser", "device", "app", "desktop", "mobile")):
            missing.append("device or application context")
    elif category == "billing":
        if not _contains_any(text, ("invoice", "transaction", "order", "receipt", "synthetic reference")):
            missing.append("synthetic transaction reference")
        if not _contains_any(text, ("date", "today", "yesterday")):
            missing.append("approximate event date")
    elif category == "service_disruption":
        if not _contains_any(text, ("dashboard", "portal", "service", "app", "feature")):
            missing.append("affected service or feature")
        if not _contains_any(text, ("since", "started", "today", "minute", "hour")):
            missing.append("time the issue began")
    elif category == "account_change":
        if not _contains_any(text, ("name", "setting", "preference", "profile")):
            missing.append("account field to change")
    elif len(text.split()) < 8 or _contains_any(text, ("help me", "it failed", "problem")):
        missing.append("specific issue and desired outcome")
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

    required = {
        "schema_version",
        "status",
        "request_id",
        "category",
        "urgency",
        "rationale",
        "missing_information",
        "suggested_reply",
        "security_flags",
        "human_review_required",
        "errors",
    }
    if set(value) != required:
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
