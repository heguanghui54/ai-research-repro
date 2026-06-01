#!/usr/bin/env python3
"""Audit human-gate logs for scientific taste/insight coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TASTE_FIELDS = [
    "rubric_version",
    "scores",
    "taste_insight_score",
    "qualitative_rationale",
    "non_metric_factors",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _load_dimensions(path: Path) -> list[str]:
    rubric = _load_json(path)
    dimensions = rubric.get("dimensions", [])
    names = [item.get("name") for item in dimensions if isinstance(item, dict)]
    return [name for name in names if isinstance(name, str) and name]


def _valid_score(value: Any) -> bool:
    return _is_number(value) and 1 <= float(value) <= 5


def audit_gate(
    path: Path,
    data: dict[str, Any],
    *,
    source: str,
    required_dimensions: list[str],
) -> dict[str, Any]:
    taste = data.get("taste_insight")
    missing: list[str] = []
    scores: dict[str, float] = {}

    if not isinstance(taste, dict):
        missing = REQUIRED_TASTE_FIELDS[:] + [f"scores.{name}" for name in required_dimensions]
    else:
        for field in REQUIRED_TASTE_FIELDS:
            if field not in taste:
                missing.append(field)

        score_map = taste.get("scores")
        if isinstance(score_map, dict):
            for dimension in required_dimensions:
                value = score_map.get(dimension)
                if _valid_score(value):
                    scores[dimension] = float(value)
                else:
                    missing.append(f"scores.{dimension}")
        else:
            for dimension in required_dimensions:
                missing.append(f"scores.{dimension}")

        if not _valid_score(taste.get("taste_insight_score")):
            if "taste_insight_score" not in missing:
                missing.append("taste_insight_score")

        rationale = taste.get("qualitative_rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            if "qualitative_rationale" not in missing:
                missing.append("qualitative_rationale")

        factors = taste.get("non_metric_factors")
        if (
            not isinstance(factors, list)
            or not factors
            or not all(isinstance(item, str) and item.strip() for item in factors)
        ):
            if "non_metric_factors" not in missing:
                missing.append("non_metric_factors")

    return {
        "path": str(path.relative_to(ROOT)),
        "source": source,
        "gate_id": data.get("gate_id"),
        "gate_type": data.get("gate_type"),
        "research_task_id": data.get("research_task_id"),
        "has_taste_insight": isinstance(taste, dict),
        "missing_taste_insight_fields": missing,
        "complete_taste_insight": not missing,
        "numeric_scores": scores,
        "taste_insight_score": taste.get("taste_insight_score") if isinstance(taste, dict) else None,
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Scientific Taste/Insight Coverage Audit",
        "",
        "This audit checks whether human gate logs contain enough structured",
        "information to evaluate scientific taste and insight as a logged search",
        "prior. Missing values are reported as missing rather than estimated.",
        "",
        "## Summary",
        "",
        f"- Gate records audited: {summary['gate_records_audited']}",
        f"- Standalone gate log files audited: {summary['standalone_gate_logs_audited']}",
        f"- Trajectory files audited: {summary['trajectory_files_audited']}",
        f"- Logs containing any taste/insight object: {summary['records_with_taste_insight']}",
        f"- Logs with complete taste/insight records: {summary['complete_taste_insight_records']}",
        f"- Logs missing one or more required taste/insight fields: {summary['incomplete_taste_insight_records']}",
    ]
    if summary["aggregate_taste_insight"]:
        agg = summary["aggregate_taste_insight"]
        lines.append(f"- Mean taste/insight score among complete records: {agg['mean_taste_insight_score']:.3f}")
    else:
        lines.append("- Aggregate taste/insight score: unavailable because no complete gate log has the required fields.")

    lines.extend(
        [
            "",
            "## Required Rubric Dimensions",
            "",
            ", ".join(f"`{name}`" for name in summary["required_rubric_dimensions"]),
            "",
            "## Per-Gate Coverage",
            "",
            "| Gate | Source | Type | Has taste record | Complete | Missing fields |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for gate in summary["gates"]:
        missing = ", ".join(gate["missing_taste_insight_fields"]) or "-"
        has_record = "yes" if gate["has_taste_insight"] else "no"
        complete = "yes" if gate["complete_taste_insight"] else "no"
        lines.append(
            f"| `{gate['gate_id']}` | `{gate['source']}` | `{gate['gate_type']}` | {has_record} | {complete} | {missing} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The package now defines a rubric for logging human scientific taste and",
            "insight. Complete records show where taste was logged prospectively or",
            "as an explicit author decision; incomplete records show older gates or",
            "gates where the field was not captured. Coverage alone does not support",
            "a claim that taste-gated search improves the upper tail of research",
            "outcomes.",
            "",
            "Future prospective matched-budget runs must fill `taste_insight` at each",
            "human gate and compare downstream trajectories against autonomous",
            "baselines. This audit is therefore a measurement-readiness artifact, not a",
            "performance result.",
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
        "--rubric-json",
        default="docs/co_pilot_ai_scientist_v3/taste_insight_rubric.json",
    )
    parser.add_argument(
        "--output-json",
        default="docs/co_pilot_ai_scientist_v3/audits/taste_insight_coverage_audit.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/co_pilot_ai_scientist_v3/audits/taste_insight_coverage_audit.md",
    )
    args = parser.parse_args()

    logs_dir = ROOT / args.logs_dir
    dimensions = _load_dimensions(ROOT / args.rubric_json)
    gates = [
        audit_gate(
            path,
            _load_json(path),
            source="human_gate_log",
            required_dimensions=dimensions,
        )
        for path in sorted(logs_dir.glob("*.json"))
    ]
    for pattern in args.trajectory_glob:
        for path in sorted(ROOT.glob(pattern)):
            trajectory = _load_json(path)
            for index, gate in enumerate(trajectory.get("gates", [])):
                if isinstance(gate, dict):
                    gates.append(
                        audit_gate(
                            path,
                            gate,
                            source=f"trajectory_gate[{index}]",
                            required_dimensions=dimensions,
                        )
                    )

    complete = [gate for gate in gates if gate["complete_taste_insight"]]
    complete_scores = [
        float(gate["taste_insight_score"])
        for gate in complete
        if _valid_score(gate["taste_insight_score"])
    ]

    aggregate = None
    if complete_scores:
        aggregate = {"mean_taste_insight_score": mean(complete_scores)}

    summary = {
        "gate_records_audited": len(gates),
        "standalone_gate_logs_audited": len(list(logs_dir.glob("*.json"))),
        "trajectory_files_audited": sum(1 for pattern in args.trajectory_glob for _ in ROOT.glob(pattern)),
        "records_with_taste_insight": sum(1 for gate in gates if gate["has_taste_insight"]),
        "complete_taste_insight_records": len(complete),
        "incomplete_taste_insight_records": len(gates) - len(complete),
        "required_taste_fields": REQUIRED_TASTE_FIELDS,
        "required_rubric_dimensions": dimensions,
        "aggregate_taste_insight": aggregate,
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
