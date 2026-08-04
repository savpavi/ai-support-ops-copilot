from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from support_copilot import analyze_request
from support_copilot import classifier
from support_copilot.rules import load_rules, validate_rules
from support_copilot.workflow_build import (
    generate_workflow_text,
    render_analyze_jscode,
    render_guard_jscode,
)

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "n8n" / "workflows" / "ai-support-operations-copilot.json"


class RulesFileTests(unittest.TestCase):
    def test_rules_file_is_valid_and_complete(self) -> None:
        rules = load_rules()
        self.assertEqual(validate_rules(rules), [])

    def test_rules_validation_reports_structural_defects(self) -> None:
        rules = copy.deepcopy(load_rules())
        rules["category_rules"][0][1] = []
        del rules["urgency"]["urgent_pattern"]
        rules["security"]["prompt_injection_patterns"][0]["pattern"] = "("
        errors = validate_rules(rules)
        self.assertTrue(any("category_rules" in error for error in errors))
        self.assertTrue(any("urgent_pattern" in error for error in errors))
        self.assertTrue(any("prompt_injection_patterns" in error for error in errors))


class GeneratedArtifactTests(unittest.TestCase):
    def test_committed_workflow_is_byte_identical_to_generated_output(self) -> None:
        self.assertEqual(
            generate_workflow_text(),
            WORKFLOW_PATH.read_text(encoding="utf-8"),
        )

    def test_generated_code_nodes_come_from_rules_data(self) -> None:
        rules = load_rules()
        analyze = render_analyze_jscode(rules)
        guard = render_guard_jscode(rules)
        for term in ("overcharged", "not urgent", "application"):
            self.assertIn(f"'{term}'", analyze)
        self.assertIn(rules["urgency"]["urgent_pattern"], analyze)
        self.assertIn(rules["synthetic_id_pattern"], guard)
        for flag in rules["security_flags"]:
            self.assertIn(f"'{flag}'", guard)


class PythonDerivationTests(unittest.TestCase):
    def test_python_classifier_derives_rule_structures_from_rules_file(self) -> None:
        rules = load_rules()
        self.assertEqual(classifier.SCHEMA_VERSION, rules["schema_version"])
        self.assertEqual(classifier.MAX_MESSAGE_LENGTH, rules["max_message_length"])
        self.assertEqual(classifier.CATEGORIES, set(rules["categories"]))
        self.assertEqual(classifier.URGENCIES, set(rules["urgencies"]))
        self.assertEqual(classifier.STATUSES, set(rules["statuses"]))
        self.assertEqual(classifier.SECURITY_FLAGS, set(rules["security_flags"]))
        self.assertEqual(classifier._SYNTHETIC_ID.pattern, rules["synthetic_id_pattern"])
        self.assertEqual(classifier._URGENT.pattern, rules["urgency"]["urgent_pattern"])
        self.assertEqual(
            [(category, tuple(terms)) for category, terms in rules["category_rules"]],
            list(classifier._CATEGORY_RULES),
        )
        self.assertEqual(
            [pattern["pattern"] for pattern in rules["security"]["prompt_injection_patterns"]],
            [pattern.pattern for pattern in classifier._PROMPT_INJECTION_PATTERNS],
        )

    def test_rule_edit_flows_to_python_and_generated_javascript(self) -> None:
        edited = copy.deepcopy(load_rules())
        edited["urgency"]["high_terms"] = [*edited["urgency"]["high_terms"], "synthetic meltdown"]

        self.assertIn("'synthetic meltdown'", render_analyze_jscode(edited))

        probe = {
            "request_id": "SYN-RULES-001",
            "message": "A synthetic meltdown occurred in the demo environment.",
        }
        classifier._apply_rules(edited)
        try:
            self.assertEqual(analyze_request(probe)["urgency"], "high")
        finally:
            classifier._apply_rules(load_rules())
        self.assertEqual(analyze_request(probe)["urgency"], "normal")


if __name__ == "__main__":
    unittest.main()
