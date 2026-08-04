from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from support_copilot import analyze_request, evaluate_cases, render_json_report, render_markdown_report
from support_copilot.evaluation import make_rate

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "fixtures" / "evaluation_cases.json").read_text(encoding="utf-8"))
COMMITTED_RESULTS = json.loads((ROOT / "docs" / "evaluation-results.json").read_text(encoding="utf-8"))


class EvaluationMetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = evaluate_cases(CASES)

    def test_full_dataset_metrics_and_local_parity(self) -> None:
        self.assertEqual(self.report["dataset_cases"], 44)
        self.assertEqual(
            self.report["metrics"]["python_n8n_parity"],
            {"numerator": 44, "denominator": 44, "rate": 1.0},
        )
        self.assertEqual(
            self.report["metrics"]["safety_invariants"],
            {
                "safe_rejection": {"numerator": 7, "denominator": 7, "rate": 1.0},
                "output_contract_valid": {"numerator": 44, "denominator": 44, "rate": 1.0},
                "human_review_required": {"numerator": 44, "denominator": 44, "rate": 1.0},
            },
        )

    def test_keyword_boundary_regression_is_fixed(self) -> None:
        self.assertEqual(self.report["failed_case_ids"], [])
        self.assertEqual(self.report["failures"], [])
        credential = self.report["metrics"]["security_flags"]["credential_request"]
        self.assertEqual(credential["false_positive"], 0)
        self.assertEqual(credential["false_negative"], 0)

    def test_rate_represents_undefined_explicitly(self) -> None:
        self.assertEqual(make_rate(0, 0), {"numerator": 0, "denominator": 0, "rate": None})
        with self.assertRaises(ValueError):
            make_rate(2, 1)

    def test_report_detects_contract_and_human_review_failure(self) -> None:
        baseline = [analyze_request(case["input"]) for case in CASES]
        unsafe = copy.deepcopy(baseline[0])
        unsafe["human_review_required"] = False

        def fake_analyze(value: object) -> dict[str, object]:
            if value == CASES[0]["input"]:
                return unsafe
            return analyze_request(value)

        with patch("support_copilot.evaluation.analyze_request", side_effect=fake_analyze):
            report = evaluate_cases(CASES, workflow_results=baseline)
        safety = report["metrics"]["safety_invariants"]
        self.assertEqual(safety["human_review_required"]["numerator"], 43)
        self.assertEqual(safety["output_contract_valid"]["numerator"], 43)
        first = next(item for item in report["failures"] if item["case_id"] == CASES[0]["case_id"])
        self.assertIn("human_review", first["checks"])
        self.assertIn("output_contract", first["checks"])
        self.assertIn("python_n8n_parity", first["checks"])


class EvaluationReportingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = evaluate_cases(CASES)

    def test_json_and_markdown_are_deterministic_and_do_not_echo_requests(self) -> None:
        first_json = render_json_report(self.report)
        second_json = render_json_report(self.report)
        self.assertEqual(first_json, second_json)
        self.assertEqual(json.loads(first_json), self.report)
        self.assertNotIn("passwordless login option", first_json)

        first_markdown = render_markdown_report(self.report)
        self.assertEqual(first_markdown, render_markdown_report(self.report))
        self.assertIn("Heuristic quality observations", first_markdown)
        self.assertIn("Safety and contract invariants", first_markdown)
        self.assertIn("## Failed cases\n\n- None", first_markdown)
        self.assertNotIn("passwordless login option", first_markdown)

    def test_committed_machine_readable_result_matches_current_evaluation(self) -> None:
        self.assertEqual(COMMITTED_RESULTS, self.report)

    def test_cli_emits_repeatable_json_and_markdown(self) -> None:
        json_runs = []
        for _ in range(2):
            completed = subprocess.run(
                [sys.executable, "scripts/evaluate_requests.py", "--format", "json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            json_runs.append(completed.stdout)
        self.assertEqual(json_runs[0], json_runs[1])

        completed = subprocess.run(
            [sys.executable, "scripts/evaluate_requests.py", "--format", "markdown"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(completed.stdout.startswith("# Synthetic Evaluation Summary\n"))


if __name__ == "__main__":
    unittest.main()
