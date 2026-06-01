#!/usr/bin/env python3
"""Audit human-gate logs for measurable attention-cost fields."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_COST_FIELDS = [
    "active_review_minutes",
    "wall_clock_latency_minutes",
    "options_reviewed",
    "artifacts_reviewed_count",
    "decision_count",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def audit_gate(path: Path, data: dict[str, Any], *, source: str) -> dict[str, Any]:
    cost = data.get("attention_cost")
    missing: list[str] = []
    numeric: dict[str, float] = {}

    if not isinstance(cost, dict):
        missing = REQUIRED_COST_FIELDS[:]
    else:
        for field in REQUIRED_COST_FIELDS:
            value = cost.get(field)
            if _is_number(value):
                numeric[field] = float(value)
            else:
                missing.append(field)

    return {
        "path": str(path.relative_to(ROOT)),
        "source": source,
        "gate_id": data.get("gate_id"),
        "gate_type": data.get("gate_type"),
        "research_task_id": data.get("research_task_id"),
        "has_attention_cost": isinstance(cost, dict),
        "missing_attention_cost_fields": missing,
        "complete_attention_cost": not missing,
        "numeric_attention_cost": numeric,
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Human Gate Attention-Cost Audit",
        "",
        "This audit checks whether human gate logs contain enough information to measure",
        "human attention cost in matched-budget experiments. Missing values are reported",
        "as missing rather than estimated.",
        "",
        "## Summary",
        "",
        f"- Gate records audited: {summary['gate_records_audited']}",
        f"- Standalone gate log files audited: {summary['standalone_gate_logs_audited']}",
        f"- Trajectory files audited: {summary['trajectory_files_audited']}",
        f"- Logs with complete attention-cost records: {summary['complete_attention_cost_logs']}",
        f"- Logs missing one or more required attention-cost fields: {summary['incomplete_attention_cost_logs']}",
    ]
    if summary["aggregate_measured_cost"]:
        agg = summary["aggregate_measured_cost"]
        lines.extend(
            [
                f"- Total active review minutes: {agg['total_active_review_minutes']:.3f}",
                f"- Mean active review minutes per measured gate: {agg['mean_active_review_minutes']:.3f}",
                f"- Total decision count: {agg['total_decision_count']:.0f}",
            ]
        )
    else:
        lines.append("- Aggregate attention cost: unavailable because no complete gate log has measured minutes.")

    lines.extend(
        [
            "",
            "## Per-Gate Coverage",
            "",
            "| Gate | Source | Type | Complete | Missing fields |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for gate in summary["gates"]:
        missing = ", ".join(gate["missing_attention_cost_fields"]) or "-"
        complete = "yes" if gate["complete_attention_cost"] else "no"
        lines.append(
            f"| `{gate['gate_id']}` | `{gate['source']}` | `{gate['gate_type']}` | {complete} | {missing} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The current retrospective and smoke-run gate logs support auditable decision",
            "provenance, but they do not yet support the paper's attention-efficiency",
            "claim. Future prospective matched-budget runs must fill `attention_cost`",
            "for every human gate, including active review minutes, wall-clock latency,",
            "options reviewed, artifacts reviewed, and decision count.",
            "",
            "This is a negative measurement-readiness result, not a performance result.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--logs-dir",
        default="docs/co_pilot_ai_scientist_v3/human_gate_logs",
    )
    parser.add_argument(
        "--trajectory-glob",
        action="append",
        default=[
            "docs/co_pilot_ai_scientist_v3/experiments/full_gate_executable_trace/trajectory.json",
            "docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_*/trajectory.json",
        ],
        help="Trajectory JSON glob(s) whose embedded gates should be audited.",
    )
    parser.add_argument(
        "--output-json",
        default="docs/co_pilot_ai_scientist_v3/audits/human_gate_attention_cost_audit.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/co_pilot_ai_scientist_v3/audits/human_gate_attention_cost_audit.md",
    )
    args = parser.parse_args()

    logs_dir = ROOT / args.logs_dir
    gates = [
        audit_gate(path, _load_json(path), source="human_gate_log")
        for path in sorted(logs_dir.glob("*.json"))
    ]
    for pattern in args.trajectory_glob:
        for path in sorted(ROOT.glob(pattern)):
            trajectory = _load_json(path)
            for index, gate in enumerate(trajectory.get("gates", [])):
                if isinstance(gate, dict):
                    source = f"trajectory_gate[{index}]"
                    gates.append(audit_gate(path, gate, source=source))
    complete = [gate for gate in gates if gate["complete_attention_cost"]]

    aggregate = None
    if complete:
        active = [gate["numeric_attention_cost"]["active_review_minutes"] for gate in complete]
        decisions = [gate["numeric_attention_cost"]["decision_count"] for gate in complete]
        aggregate = {
            "total_active_review_minutes": sum(active),
            "mean_active_review_minutes": mean(active),
            "total_decision_count": sum(decisions),
        }

    summary = {
        "gate_records_audited": len(gates),
        "gate_logs_audited": len(gates),
        "standalone_gate_logs_audited": len(list(logs_dir.glob("*.json"))),
        "trajectory_files_audited": sum(1 for pattern in args.trajectory_glob for _ in ROOT.glob(pattern)),
        "complete_attention_cost_logs": len(complete),
        "incomplete_attention_cost_logs": len(gates) - len(complete),
        "required_attention_cost_fields": REQUIRED_COST_FIELDS,
        "aggregate_measured_cost": aggregate,
        "gates": gates,
    }

    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
