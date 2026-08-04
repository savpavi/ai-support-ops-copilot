from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from typing import Any

from support_copilot import analyze_request, validate_output
from support_copilot.workflow_parity import analyze_workflow_request, run_code_node

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "n8n" / "workflows" / "ai-support-operations-copilot.json"
WORKFLOW = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
TASK_001_FIXTURES = json.loads((ROOT / "fixtures" / "support_requests.json").read_text(encoding="utf-8"))
ADVERSE_FIXTURES = json.loads((ROOT / "fixtures" / "n8n_adverse_requests.json").read_text(encoding="utf-8"))
NODES = {node["name"]: node for node in WORKFLOW["nodes"]}


def _run_workflow_code(input_value: Any) -> dict[str, Any]:
    return analyze_workflow_request(input_value)


def _find_keys(value: Any, target: str) -> list[Any]:
    matches: list[Any] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == target:
                matches.append(child)
            matches.extend(_find_keys(child, target))
    elif isinstance(value, list):
        for child in value:
            matches.extend(_find_keys(child, target))
    return matches


class WorkflowStructureTests(unittest.TestCase):
    def test_workflow_is_sanitized_inactive_and_manual_only(self) -> None:
        self.assertFalse(WORKFLOW["active"])
        self.assertEqual(
            set(WORKFLOW),
            {"name", "nodes", "connections", "active", "settings"},
        )
        self.assertEqual(_find_keys(WORKFLOW, "credentials"), [])
        self.assertNotIn("pinData", WORKFLOW)
        self.assertNotIn("id", WORKFLOW)
        self.assertNotIn("versionId", WORKFLOW)

    def test_exact_approved_node_topology(self) -> None:
        expected_types = {
            "Manual Trigger": "n8n-nodes-base.manualTrigger",
            "Synthetic Request Input": "n8n-nodes-base.set",
            "Analyze and Validate": "n8n-nodes-base.code",
            "Human Review Guard": "n8n-nodes-base.code",
        }
        self.assertEqual({name: node["type"] for name, node in NODES.items()}, expected_types)
        self.assertEqual(
            WORKFLOW["connections"],
            {
                "Manual Trigger": {
                    "main": [[{"node": "Synthetic Request Input", "type": "main", "index": 0}]]
                },
                "Synthetic Request Input": {
                    "main": [[{"node": "Analyze and Validate", "type": "main", "index": 0}]]
                },
                "Analyze and Validate": {
                    "main": [[{"node": "Human Review Guard", "type": "main", "index": 0}]]
                },
            },
        )

    def test_code_nodes_have_no_external_capability_calls(self) -> None:
        forbidden_fragments = (
            "fetch(",
            "$http",
            "http.request",
            "child_process",
            "process.env",
            "$env",
            "$credentials",
            "executecommand",
        )
        for name in ("Analyze and Validate", "Human Review Guard"):
            code = NODES[name]["parameters"]["jsCode"].lower()
            with self.subTest(node=name):
                for fragment in forbidden_fragments:
                    self.assertNotIn(fragment, code)

    def test_default_input_is_exactly_one_synthetic_request(self) -> None:
        assignments = NODES["Synthetic Request Input"]["parameters"]["assignments"]["assignments"]
        input_value = {assignment["name"]: assignment["value"] for assignment in assignments}
        self.assertEqual(set(input_value), {"request_id", "message"})
        self.assertTrue(input_value["request_id"].startswith("SYN-"))
        self.assertIn("synthetic", input_value["message"].lower())
        self.assertEqual(_run_workflow_code(input_value), analyze_request(input_value))


class WorkflowParityTests(unittest.TestCase):
    def test_task_001_fixtures_match_python_exactly(self) -> None:
        for case in TASK_001_FIXTURES:
            with self.subTest(case=case["name"]):
                result = _run_workflow_code(case["input"])
                self.assertEqual(result, analyze_request(case["input"]))
                validate_output(result)

    def test_adverse_fixtures_match_python_and_fail_safely(self) -> None:
        for case in ADVERSE_FIXTURES:
            with self.subTest(case=case["name"]):
                result = _run_workflow_code(case["input"])
                self.assertEqual(result, analyze_request(case["input"]))
                self.assertEqual(result["status"], "rejected")
                self.assertTrue(result["human_review_required"])
                validate_output(result)
                for field, expected in case.get("expected", {}).items():
                    self.assertEqual(result[field], expected)

    def test_exact_native_prompt_injection_regression_is_flagged_in_parity_evaluation(self) -> None:
        case = next(case for case in ADVERSE_FIXTURES if case["name"] == "native-prompt-injection-regression")
        python_result = analyze_request(case["input"])
        workflow_result = _run_workflow_code(case["input"])
        self.assertEqual(workflow_result, python_result)
        self.assertIn("prompt_injection", python_result["security_flags"])
        self.assertIn("prompt_injection", workflow_result["security_flags"])
        self.assertTrue(workflow_result["human_review_required"])

        normalized = {
            "request_id": case["input"]["request_id"],
            "message": case["input"]["request_text"],
        }
        normalized_python = analyze_request(normalized)
        normalized_workflow = _run_workflow_code(normalized)
        self.assertEqual(normalized_workflow, normalized_python)
        self.assertEqual(normalized_workflow["status"], "accepted")
        self.assertIn("prompt_injection", normalized_workflow["security_flags"])
        self.assertTrue(normalized_workflow["human_review_required"])

    def test_overlong_and_non_object_inputs_match_python(self) -> None:
        values: list[Any] = [None, [], {"request_id": "SYN-N8N-LONG-001", "message": "x" * 4_001}]
        for value in values:
            with self.subTest(value_type=type(value).__name__):
                self.assertEqual(_run_workflow_code(value), analyze_request(value))

    def test_guard_rejects_tampering_and_restores_review_invariant(self) -> None:
        valid = analyze_request(TASK_001_FIXTURES[0]["input"])
        tampered = copy.deepcopy(valid)
        tampered["human_review_required"] = False
        guarded = run_code_node(NODES["Human Review Guard"]["parameters"]["jsCode"], [tampered])
        self.assertEqual(len(guarded), 1)
        result = guarded[0]["json"]
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["security_flags"], ["invalid_input"])
        self.assertTrue(result["human_review_required"])
        validate_output(result)


if __name__ == "__main__":
    unittest.main()
