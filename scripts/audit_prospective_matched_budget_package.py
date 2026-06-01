#!/usr/bin/env python3
"""Audit prospective matched-budget Co-Pilot AI Scientist v3 packages.

The top-conference claim requires more than archived module probes. A qualifying
package must contain a prospective co-pilot trajectory, a matched autonomous
baseline, complete human taste/insight and attention-cost records for every
human gate, a final claim audit, and a manuscript artifact produced from the
same run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_MANIFEST_FIELDS = [
    "package_id",
    "status",
    "co_pilot_trajectory",
    "autonomous_baseline",
    "human_gate_logs",
    "claim_audit",
    "manuscript",
    "matched_budget",
]

REQUIRED_ATTENTION_FIELDS = [
    "active_review_minutes",
    "wall_clock_latency_minutes",
    "options_reviewed",
    "artifacts_reviewed_count",
    "decision_count",
]

REQUIRED_TASTE_FIELDS = [
    "rubric_version",
    "scores",
    "taste_insight_score",
    "qualitative_rationale",
    "non_metric_factors",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _as_paths(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _exists(path_value: str) -> bool:
    return (ROOT / path_value).exists()


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _complete_attention(gate: dict[str, Any]) -> tuple[bool, list[str]]:
    cost = gate.get("attention_cost")
    missing: list[str] = []
    if not isinstance(cost, dict):
        return False, REQUIRED_ATTENTION_FIELDS[:]
    for field in REQUIRED_ATTENTION_FIELDS:
        if not _is_number(cost.get(field)):
            missing.append(field)
    return not missing, missing


def _complete_taste(gate: dict[str, Any]) -> tuple[bool, list[str]]:
    taste = gate.get("taste_insight")
    missing: list[str] = []
    if not isinstance(taste, dict):
        return False, REQUIRED_TASTE_FIELDS[:]
    for field in REQUIRED_TASTE_FIELDS:
        if field not in taste:
            missing.append(field)
    score = taste.get("taste_insight_score")
    if not (_is_number(score) and 1 <= float(score) <= 5):
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
    return not missing, missing


def _load_gate(path_value: str) -> dict[str, Any] | None:
    path = ROOT / path_value
    if not path.exists():
        return None
    data = _load_json(path)
    if "gates" in data and isinstance(data["gates"], list):
        return {"embedded_gates": data["gates"], "path": path_value}
    return data


def _gate_records(manifest: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    records: list[tuple[str, dict[str, Any]]] = []
    for path_value in _as_paths(manifest.get("human_gate_logs")):
        loaded = _load_gate(path_value)
        if not loaded:
            continue
        if "embedded_gates" in loaded:
            for index, gate in enumerate(loaded["embedded_gates"]):
                if isinstance(gate, dict):
                    records.append((f"{path_value}#gate[{index}]", gate))
        else:
            records.append((path_value, loaded))
    return records


def audit_manifest(path: Path) -> dict[str, Any]:
    manifest = _load_json(path)
    errors: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            errors.append(f"missing manifest field: {field}")

    for field in ["co_pilot_trajectory", "autonomous_baseline", "claim_audit", "manuscript"]:
        for path_value in _as_paths(manifest.get(field)):
            if not _exists(path_value):
                errors.append(f"missing artifact for {field}: {path_value}")

    human_gate_paths = _as_paths(manifest.get("human_gate_logs"))
    if not human_gate_paths:
        errors.append("human_gate_logs must list at least one gate log or trajectory")
    for path_value in human_gate_paths:
        if not _exists(path_value):
            errors.append(f"missing human gate artifact: {path_value}")

    budget = manifest.get("matched_budget")
    if not isinstance(budget, dict):
        errors.append("matched_budget must be an object")
    else:
        for field in ["same_task", "same_model_family", "same_step_budget", "same_tool_access"]:
            if budget.get(field) is not True:
                errors.append(f"matched_budget.{field} must be true")

    gates = []
    for source, gate in _gate_records(manifest):
        attention_ok, attention_missing = _complete_attention(gate)
        taste_ok, taste_missing = _complete_taste(gate)
        gates.append(
            {
                "source": source,
                "gate_id": gate.get("gate_id"),
                "gate_type": gate.get("gate_type"),
                "complete_attention_cost": attention_ok,
                "missing_attention_cost_fields": attention_missing,
                "complete_taste_insight": taste_ok,
                "missing_taste_insight_fields": taste_missing,
            }
        )
        if not attention_ok:
            errors.append(f"{source} lacks complete attention_cost: {', '.join(attention_missing)}")
        if not taste_ok:
            errors.append(f"{source} lacks complete taste_insight: {', '.join(taste_missing)}")

    if manifest.get("status") not in {"prospective_complete", "prospective_pilot"}:
        warnings.append("manifest status is not a completed prospective status")

    return {
        "manifest": _rel(path),
        "package_id": manifest.get("package_id"),
        "overall_status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "gate_records_checked": len(gates),
        "complete_attention_cost_gates": sum(1 for gate in gates if gate["complete_attention_cost"]),
        "complete_taste_insight_gates": sum(1 for gate in gates if gate["complete_taste_insight"]),
        "gates": gates,
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Prospective Matched-Budget Package Audit",
        "",
        "This audit checks whether the repository contains a prospective matched-budget",
        "run that can support stronger Co-Pilot AI Scientist v3 claims. It is stricter",
        "than the artifact manifest: synthetic smoke logs and retrospective replays do",
        "not count as qualifying performance evidence.",
        "",
        "## Summary",
        "",
        f"- Overall status: `{summary['overall_status']}`",
        f"- Manifest files checked: {summary['manifest_files_checked']}",
        f"- Passing packages: {summary['passing_packages']}",
        f"- Failing packages: {summary['failing_packages']}",
        "",
    ]
    if not summary["packages"]:
        lines.extend(
            [
                "No prospective matched-budget package manifests were found.",
                "",
                "A qualifying package must provide:",
                "",
                "1. A co-pilot trajectory generated prospectively.",
                "2. A matched autonomous baseline on the same task/model/tool budget.",
                "3. Complete `attention_cost` records for every human gate.",
                "4. Complete `taste_insight` records for every human gate.",
                "5. A final claim audit and manuscript generated from the same run.",
                "",
            ]
        )
    for package in summary["packages"]:
        lines.extend(
            [
                f"## `{package['package_id'] or package['manifest']}`",
                "",
                f"- Status: `{package['overall_status']}`",
                f"- Gate records checked: {package['gate_records_checked']}",
                f"- Complete attention-cost gates: {package['complete_attention_cost_gates']}",
                f"- Complete taste/insight gates: {package['complete_taste_insight_gates']}",
                f"- Errors: {len(package['errors'])}",
                "",
            ]
        )
        for error in package["errors"]:
            lines.append(f"- {error}")
        lines.append("")
    lines.extend(["## Interpretation", ""])
    if summary["passing_packages"]:
        lines.extend(
            [
                "At least one non-synthetic package now satisfies the minimum",
                "prospective matched-budget evidence shape. This permits the paper to",
                "state that the evaluation package can be produced and audited, but it",
                "does not by itself prove top-conference-level performance. Strong",
                "claims about paper quality, human-attention efficiency, or superiority",
                "over autonomous AI Scientist-v2 still require larger tasks, more seeds,",
                "and independent paper-quality evaluation.",
            ]
        )
    else:
        lines.extend(
            [
                "Until this audit passes on at least one non-synthetic package, the",
                "paper should not claim that IGRE improves paper quality,",
                "human-attention efficiency, or autonomous AI Scientist-v2 performance.",
                "Passing this audit would not by itself prove top-conference-level",
                "results, but it is the minimum evidence shape needed before those",
                "claims can be evaluated.",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest-glob",
        action="append",
        default=["docs/co_pilot_ai_scientist_v3/experiments/prospective_matched_*/prospective_manifest.json"],
    )
    parser.add_argument(
        "--output-json",
        default="docs/co_pilot_ai_scientist_v3/audits/prospective_matched_budget_package_audit.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/co_pilot_ai_scientist_v3/audits/prospective_matched_budget_package_audit.md",
    )
    args = parser.parse_args()

    manifests = sorted({path for pattern in args.manifest_glob for path in ROOT.glob(pattern)})
    packages = [audit_manifest(path) for path in manifests]
    passing = [package for package in packages if package["overall_status"] == "pass"]
    summary = {
        "overall_status": "pass" if passing else "fail_no_passing_prospective_package",
        "manifest_files_checked": len(manifests),
        "passing_packages": len(passing),
        "failing_packages": len(packages) - len(passing),
        "required_manifest_fields": REQUIRED_MANIFEST_FIELDS,
        "required_attention_fields": REQUIRED_ATTENTION_FIELDS,
        "required_taste_fields": REQUIRED_TASTE_FIELDS,
        "packages": packages,
    }

    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
