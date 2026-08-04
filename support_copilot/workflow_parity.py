"""Local execution helpers for the committed n8n Code-node JavaScript."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "n8n" / "workflows" / "ai-support-operations-copilot.json"


def _workflow_nodes() -> dict[str, dict[str, Any]]:
    workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    return {node["name"]: node for node in workflow["nodes"]}


def _require_node() -> None:
    if shutil.which("node") is None:
        raise RuntimeError("Node.js is required to validate n8n Code-node parity")


def run_code_node(code: str, input_values: list[Any]) -> list[dict[str, Any]]:
    """Execute one Code-node invocation with all values in one n8n-style input."""

    _require_node()
    wrapper = f"""
const payload = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const $input = {{
  first: () => payload[0],
  all: () => payload,
}};
const execute = () => {{
{code}
}};
const result = execute();
process.stdout.write(JSON.stringify(result));
"""
    payload = [{"json": value} for value in input_values]
    completed = subprocess.run(
        ["node", "-e", wrapper],
        cwd=ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "Code-node execution failed")
    result = json.loads(completed.stdout)
    if not isinstance(result, list):
        raise RuntimeError("Code node must return an item list")
    return result


def _run_code_node_for_each(code: str, input_values: list[Any]) -> list[list[dict[str, Any]]]:
    """Run the same Code node once per value inside a single local Node process."""

    _require_node()
    wrapper = f"""
const values = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const execute = (payload) => {{
  const $input = {{
    first: () => payload[0],
    all: () => payload,
  }};
{code}
}};
const results = values.map((value) => execute([{{json: value}}]));
process.stdout.write(JSON.stringify(results));
"""
    completed = subprocess.run(
        ["node", "-e", wrapper],
        cwd=ROOT,
        input=json.dumps(input_values),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "Code-node batch execution failed")
    result = json.loads(completed.stdout)
    if not isinstance(result, list) or len(result) != len(input_values):
        raise RuntimeError("Code-node batch result count does not match input count")
    return result


def analyze_workflow_requests(input_values: list[Any]) -> list[dict[str, Any]]:
    """Run each value through Analyze and Validate, then Human Review Guard locally."""

    nodes = _workflow_nodes()
    analyzed_runs = _run_code_node_for_each(
        nodes["Analyze and Validate"]["parameters"]["jsCode"], input_values
    )
    analyzed_values: list[Any] = []
    for result in analyzed_runs:
        if len(result) != 1 or not isinstance(result[0], dict) or "json" not in result[0]:
            raise RuntimeError("Analyze and Validate must produce exactly one item per request")
        analyzed_values.append(result[0]["json"])

    guarded_runs = _run_code_node_for_each(
        nodes["Human Review Guard"]["parameters"]["jsCode"], analyzed_values
    )
    guarded_values: list[dict[str, Any]] = []
    for result in guarded_runs:
        if len(result) != 1 or not isinstance(result[0], dict) or "json" not in result[0]:
            raise RuntimeError("Human Review Guard must produce exactly one item per request")
        guarded = result[0]["json"]
        if not isinstance(guarded, dict):
            raise RuntimeError("Human Review Guard output must be an object")
        guarded_values.append(guarded)
    return guarded_values


def analyze_workflow_request(input_value: Any) -> dict[str, Any]:
    """Run one value through the committed local workflow JavaScript."""

    return analyze_workflow_requests([input_value])[0]
