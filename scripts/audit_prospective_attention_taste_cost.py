#!/usr/bin/env python3
"""Summarize prospective human attention and taste/insight gate costs.

The paper argues that human scientific taste should become a typed control
signal, not vague approval. This audit aggregates the prospective matched-budget
gate logs to verify that every prospective package records both attention cost
and taste/insight metadata. It deliberately keeps the claim boundary narrow:
operator-recorded cost is measurement evidence, not independent human-subject
evidence and not a proof of efficiency.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
AUDIT_DIR = DOC_DIR / "audits"
MANIFEST_PATH = DOC_DIR / "repro_manifest.json"

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


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _as_paths(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _complete_attention(gate: dict[str, Any]) -> tuple[bool, list[str]]:
    cost = gate.get("attention_cost")
    if not isinstance(cost, dict):
        return False, REQUIRED_ATTENTION_FIELDS[:]
    missing = [field for field in REQUIRED_ATTENTION_FIELDS if not _is_number(cost.get(field))]
    return not missing, missing


def _complete_taste(gate: dict[str, Any]) -> tuple[bool, list[str]]:
    taste = gate.get("taste_insight")
    if not isinstance(taste, dict):
        return False, REQUIRED_TASTE_FIELDS[:]
    missing = [field for field in REQUIRED_TASTE_FIELDS if field not in taste]
    score = taste.get("taste_insight_score")
    if not (_is_number(score) and 1 <= float(score) <= 5) and "taste_insight_score" not in missing:
        missing.append("taste_insight_score")
    if not isinstance(taste.get("qualitative_rationale"), str) or not taste.get("qualitative_rationale", "").strip():
        if "qualitative_rationale" not in missing:
            missing.append("qualitative_rationale")
    factors = taste.get("non_metric_factors")
    if not isinstance(factors, list) or not factors or not all(isinstance(item, str) for item in factors):
        if "non_metric_factors" not in missing:
            missing.append("non_metric_factors")
    return not missing, missing


def _gate_records(manifest: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    records: list[tuple[str, dict[str, Any]]] = []
    for path_value in _as_paths(manifest.get("human_gate_logs")):
        path = ROOT / path_value
        if not path.exists():
            records.append((path_value, {"missing": True}))
            continue
        data = _load_json(path)
        if isinstance(data.get("gates"), list):
            for index, gate in enumerate(data["gates"]):
                if isinstance(gate, dict):
                    records.append((f"{path_value}#gate[{index}]", gate))
        else:
            records.append((path_value, data))
    return records


def _update_manifest(output_json: Path, output_md: Path, script_path: Path, audit: dict[str, Any]) -> None:
    if not MANIFEST_PATH.exists():
        return
    manifest = _load_json(MANIFEST_PATH)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in [output_json, output_md, script_path]:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["prospective_attention_taste_cost_audit"] = {
        "status": audit["status"],
        "json": _rel(output_json),
        "markdown": _rel(output_md),
        "prospective_packages": audit["prospective_packages"],
        "gate_records": audit["gate_records"],
        "complete_attention_cost_gates": audit["complete_attention_cost_gates"],
        "complete_taste_insight_gates": audit["complete_taste_insight_gates"],
        "total_active_review_minutes": audit["attention_summary"]["total_active_review_minutes"],
        "mean_taste_insight_score": audit["taste_summary"]["mean_taste_insight_score"],
        "claim_boundary": audit["claim_boundary"],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    package_manifests = sorted(EXP_DIR.glob("*/prospective_manifest.json"))
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []
    gate_type_counts: Counter[str] = Counter()
    factor_counts: Counter[str] = Counter()
    attention_values: dict[str, list[float]] = defaultdict(list)
    taste_scores: list[float] = []

    for manifest_path in package_manifests:
        manifest = _load_json(manifest_path)
        package_id = manifest.get("package_id", manifest_path.parent.name)
        gate_records = _gate_records(manifest)
        if not gate_records:
            errors.append(f"{package_id} has no prospective human gate records")
        for source, gate in gate_records:
            if gate.get("missing") is True:
                errors.append(f"{package_id} missing gate file: {source}")
                continue
            attention_ok, attention_missing = _complete_attention(gate)
            taste_ok, taste_missing = _complete_taste(gate)
            if not attention_ok:
                errors.append(f"{source} incomplete attention cost: {attention_missing}")
            if not taste_ok:
                errors.append(f"{source} incomplete taste insight: {taste_missing}")

            attention = gate.get("attention_cost", {}) if isinstance(gate.get("attention_cost"), dict) else {}
            taste = gate.get("taste_insight", {}) if isinstance(gate.get("taste_insight"), dict) else {}
            gate_type = gate.get("gate_type", "unknown")
            gate_type_counts[str(gate_type)] += 1
            for field in REQUIRED_ATTENTION_FIELDS:
                value = attention.get(field)
                if _is_number(value):
                    attention_values[field].append(float(value))
            score = taste.get("taste_insight_score")
            if _is_number(score):
                taste_scores.append(float(score))
            for factor in taste.get("non_metric_factors", []) if isinstance(taste.get("non_metric_factors"), list) else []:
                factor_counts[str(factor)] += 1
            rows.append(
                {
                    "package_id": package_id,
                    "source": source,
                    "gate_id": gate.get("gate_id"),
                    "gate_type": gate_type,
                    "decision": gate.get("decision"),
                    "active_review_minutes": attention.get("active_review_minutes"),
                    "wall_clock_latency_minutes": attention.get("wall_clock_latency_minutes"),
                    "options_reviewed": attention.get("options_reviewed"),
                    "artifacts_reviewed_count": attention.get("artifacts_reviewed_count"),
                    "decision_count": attention.get("decision_count"),
                    "taste_insight_score": taste.get("taste_insight_score"),
                    "non_metric_factors": taste.get("non_metric_factors", []),
                    "complete_attention_cost": attention_ok,
                    "complete_taste_insight": taste_ok,
                }
            )

    complete_attention = sum(1 for row in rows if row["complete_attention_cost"])
    complete_taste = sum(1 for row in rows if row["complete_taste_insight"])
    total_active = sum(attention_values.get("active_review_minutes", []))
    total_latency = sum(attention_values.get("wall_clock_latency_minutes", []))
    total_options = sum(attention_values.get("options_reviewed", []))
    total_decisions = sum(attention_values.get("decision_count", []))
    if not rows:
        errors.append("no prospective gate rows found")

    claim_boundary = (
        "This audit supports prospective operator-recorded attention and taste/insight "
        "measurement across the matched-budget packages. It is not independent "
        "human-subject evidence, does not estimate population-level attention cost, "
        "and does not prove that human gates improve paper quality."
    )
    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "prospective_packages": len(package_manifests),
        "gate_records": len(rows),
        "complete_attention_cost_gates": complete_attention,
        "complete_taste_insight_gates": complete_taste,
        "gate_type_counts": dict(gate_type_counts),
        "attention_summary": {
            "total_active_review_minutes": total_active,
            "total_wall_clock_latency_minutes": total_latency,
            "mean_active_review_minutes": mean(attention_values["active_review_minutes"]) if attention_values["active_review_minutes"] else None,
            "median_active_review_minutes": median(attention_values["active_review_minutes"]) if attention_values["active_review_minutes"] else None,
            "total_options_reviewed": total_options,
            "total_decisions": total_decisions,
            "mean_options_per_gate": mean(attention_values["options_reviewed"]) if attention_values["options_reviewed"] else None,
        },
        "taste_summary": {
            "mean_taste_insight_score": mean(taste_scores) if taste_scores else None,
            "median_taste_insight_score": median(taste_scores) if taste_scores else None,
            "min_taste_insight_score": min(taste_scores) if taste_scores else None,
            "max_taste_insight_score": max(taste_scores) if taste_scores else None,
            "top_non_metric_factors": factor_counts.most_common(12),
        },
        "rows": rows,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": claim_boundary,
    }

    output_json = AUDIT_DIR / "prospective_attention_taste_cost_audit.json"
    output_md = AUDIT_DIR / "prospective_attention_taste_cost_audit.md"
    output_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Prospective Attention and Taste/Insight Cost Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Prospective packages: `{audit['prospective_packages']}`",
        f"- Gate records: `{audit['gate_records']}`",
        f"- Complete attention-cost gates: `{complete_attention}/{len(rows)}`",
        f"- Complete taste/insight gates: `{complete_taste}/{len(rows)}`",
        f"- Total active review minutes: `{total_active:.2f}`",
        f"- Total wall-clock latency minutes: `{total_latency:.2f}`",
        f"- Mean taste/insight score: `{audit['taste_summary']['mean_taste_insight_score']:.3f}`",
        "",
        "## Gate Types",
        "",
        "| Gate type | Count |",
        "| --- | --- |",
    ]
    for gate_type, count in sorted(gate_type_counts.items()):
        lines.append(f"| `{gate_type}` | `{count}` |")
    lines.extend(["", "## Per-Gate Records", "", "| Package | Gate | Active min | Options | Taste score | Factors |", "| --- | --- | ---: | ---: | ---: | --- |"])
    for row in rows:
        factors = ", ".join(row.get("non_metric_factors", []))
        lines.append(
            f"| `{row['package_id']}` | `{row['gate_type']}` | `{row['active_review_minutes']}` | "
            f"`{row['options_reviewed']}` | `{row['taste_insight_score']}` | {factors} |"
        )
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", claim_boundary, ""])
    output_md.write_text("\n".join(lines), encoding="utf-8")

    if args.update_manifest:
        _update_manifest(output_json, output_md, Path(__file__), audit)

    print(json.dumps({"json": _rel(output_json), "markdown": _rel(output_md), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
