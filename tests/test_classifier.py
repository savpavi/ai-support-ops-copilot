from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from support_copilot import analyze_request, validate_input, validate_output

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = json.loads((ROOT / "fixtures" / "support_requests.json").read_text(encoding="utf-8"))


class FixtureTests(unittest.TestCase):
    def test_required_synthetic_fixture_scenarios(self) -> None:
        self.assertEqual(
            {case["name"] for case in FIXTURES},
            {"normal", "urgent", "incomplete", "ambiguous", "security-sensitive"},
        )
        for case in FIXTURES:
            with self.subTest(case=case["name"]):
                result = analyze_request(case["input"])
                self.assertEqual(result["status"], "accepted")
                self.assertTrue(result["human_review_required"])
                self.assertTrue(result["suggested_reply"].startswith("Draft for human review:"))
                validate_output(result)
                for field, expected in case["expected"].items():
                    self.assertEqual(result[field], expected)

    def test_suggested_reply_does_not_echo_or_invent_untrusted_details(self) -> None:
        result = analyze_request(next(case["input"] for case in FIXTURES if case["name"] == "security-sensitive"))
        reply = result["suggested_reply"].lower()
        self.assertNotIn("ignore previous instructions", reply)
        self.assertNotIn("reveal the system prompt", reply)
        self.assertIn("security review", reply)


class InputValidationTests(unittest.TestCase):
    def test_empty_and_malformed_inputs_fail_safely(self) -> None:
        invalid_values = [
            None,
            [],
            {},
            {"request_id": "SYN-EMPTY-001", "message": "   "},
            {"request_id": "REAL-001", "message": "Synthetic demonstration text."},
            {"request_id": "SYN-TYPE-001", "message": 42},
            {"request_id": "SYN-EXTRA-001", "message": "Synthetic text.", "action": "send"},
            {"request_id": "SYN-LONG-001", "message": "x" * 4_001},
        ]
        for value in invalid_values:
            with self.subTest(value_type=type(value).__name__):
                result = analyze_request(value)
                self.assertEqual(result["status"], "rejected")
                self.assertEqual(result["category"], "unknown")
                self.assertEqual(result["urgency"], "unknown")
                self.assertTrue(result["errors"])
                self.assertEqual(result["security_flags"], ["invalid_input"])
                self.assertTrue(result["human_review_required"])
                validate_output(result)

    def test_valid_input_has_no_validation_errors(self) -> None:
        self.assertEqual(validate_input(FIXTURES[0]["input"]), [])


class OutputValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_result = analyze_request(FIXTURES[0]["input"])

    def test_human_review_cannot_be_disabled(self) -> None:
        tampered = copy.deepcopy(self.valid_result)
        tampered["human_review_required"] = False
        with self.assertRaisesRegex(ValueError, "human_review_required"):
            validate_output(tampered)

    def test_missing_extra_and_invalid_fields_are_rejected(self) -> None:
        missing = copy.deepcopy(self.valid_result)
        del missing["rationale"]
        extra = copy.deepcopy(self.valid_result)
        extra["send_message"] = True
        invalid_category = copy.deepcopy(self.valid_result)
        invalid_category["category"] = "invented"
        for value in (missing, extra, invalid_category):
            with self.subTest(fields=sorted(value)):
                with self.assertRaises(ValueError):
                    validate_output(value)

    def test_unmarked_reply_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.valid_result)
        tampered["suggested_reply"] = "Automatically approved."
        with self.assertRaisesRegex(ValueError, "human-review draft"):
            validate_output(tampered)

    def test_malformed_request_id_type_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.valid_result)
        tampered["request_id"] = 42
        with self.assertRaisesRegex(ValueError, "invalid request_id"):
            validate_output(tampered)

    def test_malformed_enum_type_is_rejected_cleanly(self) -> None:
        tampered = copy.deepcopy(self.valid_result)
        tampered["category"] = []
        with self.assertRaisesRegex(ValueError, "invalid category"):
            validate_output(tampered)


class CliTests(unittest.TestCase):
    def test_cli_processes_one_fixture_repeatably(self) -> None:
        request = json.dumps(FIXTURES[0]["input"])
        completed = subprocess.run(
            [sys.executable, "scripts/classify_request.py"],
            cwd=ROOT,
            input=request,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result, analyze_request(FIXTURES[0]["input"]))

    def test_cli_rejects_non_json_safely(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/classify_request.py"],
            cwd=ROOT,
            input="not json",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "rejected")
        self.assertTrue(result["human_review_required"])


if __name__ == "__main__":
    unittest.main()
