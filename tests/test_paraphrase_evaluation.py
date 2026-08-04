from __future__ import annotations

import json
import unittest
from pathlib import Path

from support_copilot.evaluation import (
    PARAPHRASE_VALIDATION,
    evaluate_cases,
    validate_evaluation_cases,
)

ROOT = Path(__file__).resolve().parents[1]
PARAPHRASE_PATH = ROOT / "fixtures" / "paraphrase_cases.json"
RESULTS_PATH = ROOT / "docs" / "paraphrase-results.json"


def _synthetic_accepted_cases() -> list[dict]:
    categories = ["access_issue", "account_change", "billing", "service_disruption", "general"]
    cases = []
    for index in range(30):
        category = categories[index % len(categories)]
        cases.append(
            {
                "case_id": f"SYN-EVAL-OPT-{index:03d}",
                "description": "Synthetic validator-option case.",
                "input": {
                    "request_id": f"SYN-OPT-{index:03d}",
                    "message": "A synthetic message used only for validator option checks.",
                },
                "expected": {
                    "status": "accepted",
                    "category": category,
                    "urgency": "normal",
                    "security_flags": [],
                    "missing_information": [],
                    "human_review_required": True,
                },
                "tags": ["paraphrase"],
            }
        )
    return cases


class ValidatorOptionTests(unittest.TestCase):
    def test_default_validation_still_requires_full_coverage(self) -> None:
        errors = validate_evaluation_cases(_synthetic_accepted_cases())
        self.assertTrue(any("missing security flags" in error for error in errors))
        self.assertTrue(any("missing coverage tags" in error for error in errors))
        self.assertTrue(any("rejected-input case" in error for error in errors))

    def test_paraphrase_profile_accepts_accepted_only_dataset(self) -> None:
        errors = validate_evaluation_cases(
            _synthetic_accepted_cases(), **PARAPHRASE_VALIDATION
        )
        self.assertEqual(errors, [])

    def test_category_coverage_remains_mandatory_under_options(self) -> None:
        cases = [case for case in _synthetic_accepted_cases() if case["expected"]["category"] != "billing"]
        errors = validate_evaluation_cases(cases, **PARAPHRASE_VALIDATION)
        self.assertTrue(any("missing categories" in error for error in errors))


class ParaphraseDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads(PARAPHRASE_PATH.read_text(encoding="utf-8"))
        cls.report = evaluate_cases(cls.cases, validation=PARAPHRASE_VALIDATION)

    def test_committed_paraphrase_dataset_is_valid(self) -> None:
        self.assertEqual(
            validate_evaluation_cases(self.cases, **PARAPHRASE_VALIDATION), []
        )
        self.assertGreaterEqual(len(self.cases), 30)
        for case in self.cases:
            self.assertIn("paraphrase", case["tags"])

    def test_safety_invariants_hold_even_where_classification_fails(self) -> None:
        total = self.report["dataset_cases"]
        safety = self.report["metrics"]["safety_invariants"]
        self.assertEqual(safety["output_contract_valid"]["numerator"], total)
        self.assertEqual(safety["human_review_required"]["numerator"], total)
        self.assertEqual(self.report["metrics"]["python_n8n_parity"]["numerator"], total)

    def test_paraphrase_set_actually_measures_out_of_distribution_behavior(self) -> None:
        exact = self.report["metrics"]["heuristic_quality"]["all_expected_assertions"]
        self.assertLess(exact["numerator"], exact["denominator"])

    def test_committed_results_match_current_evaluation(self) -> None:
        committed = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(committed, self.report)


if __name__ == "__main__":
    unittest.main()
