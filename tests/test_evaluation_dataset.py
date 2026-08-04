from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from support_copilot import assert_valid_evaluation_cases, validate_evaluation_cases

ROOT = Path(__file__).resolve().parents[1]
EVALUATION_CASES = json.loads(
    (ROOT / "fixtures" / "evaluation_cases.json").read_text(encoding="utf-8")
)


class EvaluationDatasetTests(unittest.TestCase):
    def test_committed_dataset_is_valid(self) -> None:
        self.assertEqual(validate_evaluation_cases(EVALUATION_CASES), [])
        assert_valid_evaluation_cases(EVALUATION_CASES)

    def test_dataset_has_independently_reviewable_expected_assertions(self) -> None:
        self.assertGreaterEqual(len(EVALUATION_CASES), 30)
        self.assertLessEqual(len(EVALUATION_CASES), 50)
        for case in EVALUATION_CASES:
            with self.subTest(case=case["case_id"]):
                self.assertEqual(
                    set(case["expected"]),
                    {
                        "status",
                        "category",
                        "urgency",
                        "security_flags",
                        "missing_information",
                        "human_review_required",
                    },
                )
                self.assertTrue(case["expected"]["human_review_required"])

    def test_duplicate_ids_and_invalid_expectations_fail(self) -> None:
        invalid = copy.deepcopy(EVALUATION_CASES)
        invalid[1]["case_id"] = invalid[0]["case_id"]
        invalid[2]["expected"]["category"] = "invented"
        invalid[3]["expected"]["human_review_required"] = False
        errors = validate_evaluation_cases(invalid)
        self.assertTrue(any("must be unique" in error for error in errors))
        self.assertTrue(any("category is invalid" in error for error in errors))
        self.assertTrue(any("human_review_required must be true" in error for error in errors))

    def test_wrong_shape_and_incomplete_coverage_fail(self) -> None:
        self.assertEqual(
            validate_evaluation_cases({}),
            ["evaluation dataset must be a JSON array"],
        )
        errors = validate_evaluation_cases(EVALUATION_CASES[:1])
        self.assertTrue(any("must contain 30-50 cases" in error for error in errors))
        self.assertTrue(any("missing categories" in error for error in errors))
        self.assertTrue(any("missing security flags" in error for error in errors))

    def test_non_json_input_and_unsorted_flags_fail(self) -> None:
        invalid = copy.deepcopy(EVALUATION_CASES)
        invalid[0]["input"] = {"not_json": {1, 2}}
        invalid[1]["expected"]["security_flags"] = ["prompt_injection", "credential_request"]
        errors = validate_evaluation_cases(invalid)
        self.assertTrue(any("input must be JSON-compatible" in error for error in errors))
        self.assertTrue(any("security_flags must be sorted and unique" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
