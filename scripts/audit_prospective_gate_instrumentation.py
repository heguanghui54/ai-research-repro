#!/usr/bin/env python3
"""Audit prospective human-gate instrumentation readiness.

The existing historical gate logs are intentionally incomplete. This audit asks
a different question: does the reusable workflow now contain enough hard
preflight machinery to prevent future matched-budget claims from being made
without measured attention cost and scientific taste/insight records?
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
SKILL_DIR = ROOT / "skills" / "co-pilot-ai-scientist-v3"


ATTENTION_FIELDS = [
    "active_review_minutes",
    "wall_clock_latency_minutes",
    "options_reviewed",
    "artifacts_reviewed_count",
    "decision_count",
]

TASTE_FIELDS = [
    "rubric_version",
    "scores",
    "taste_insight_score",
    "qualitative_rationale",
    "non_metric_factors",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _contains(path: Path, needles: list[str]) -> dict[str, bool]:
    text = path.read_text(encoding="utf-8")
    return {needle: needle in text for needle in needles}


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = DOC_DIR / "repro_manifest.json"
    skill_path = SKILL_DIR / "SKILL.md"
    task_template_path = SKILL_DIR / "templates" / "task_spec_template.md"
    gate_template_path = SKILL_DIR / "templates" / "human_gate_log_template.json"
    create_log_path = ROOT / "scripts" / "create_human_gate_log.py"
    protocol_path = DOC_DIR / "prospective_matched_budget_protocol.md"
    schema_path = DOC_DIR / "human_gate_schema.json"
    attention_audit_path = AUDIT_DIR / "human_gate_attention_cost_audit.json"
    taste_audit_path = AUDIT_DIR / "taste_insight_coverage_audit.json"

    checks = {
        _rel(skill_path): _contains(
            skill_path,
            [
                "--require-complete-attention",
                "--require-complete-taste",
                "matched-budget",
                "attention_cost",
                "taste_insight",
            ],
        ),
        _rel(task_template_path): _contains(
            task_template_path,
            [
                "Prospective Gate Instrumentation",
                "--require-complete-attention",
                "--require-complete-taste",
                *ATTENTION_FIELDS,
                *TASTE_FIELDS,
            ],
        ),
        _rel(create_log_path): _contains(
            create_log_path,
            [
                "REQUIRED_ATTENTION_FIELDS",
                "REQUIRED_TASTE_FIELDS",
                "require_complete_attention",
                "require_complete_taste",
                *ATTENTION_FIELDS,
                *TASTE_FIELDS,
            ],
        ),
        _rel(protocol_path): _contains(
            protocol_path,
            [
                "audit_prospective_gate_instrumentation.py",
                "--require-complete-attention",
                "--require-complete-taste",
                *ATTENTION_FIELDS,
                *TASTE_FIELDS,
            ],
        ),
    }

    gate_template = _load_json(gate_template_path)
    schema = _load_json(schema_path)
    attention_audit = _load_json(attention_audit_path)
    taste_audit = _load_json(taste_audit_path)

    schema_attention_props = schema.get("properties", {}).get("attention_cost", {}).get("properties", {})
    schema_taste_props = schema.get("properties", {}).get("taste_insight", {}).get("properties", {})
    template_attention = gate_template.get("attention_cost", {})
    template_taste = gate_template.get("taste_insight", {})

    structural_checks = {
        "schema_has_attention_fields": {field: field in schema_attention_props for field in ATTENTION_FIELDS},
        "schema_has_taste_fields": {field: field in schema_taste_props for field in TASTE_FIELDS},
        "template_has_attention_fields": {field: field in template_attention for field in ATTENTION_FIELDS},
        "template_has_taste_fields": {field: field in template_taste for field in TASTE_FIELDS},
        "historical_attention_gap_is_explicit": attention_audit.get("complete_attention_cost_logs", 0)
        < attention_audit.get("gate_records_audited", 0),
        "historical_taste_gap_is_explicit": taste_audit.get("complete_taste_insight_records", 0)
        < taste_audit.get("gate_records_audited", 0),
    }

    errors: list[str] = []
    for path, path_checks in checks.items():
        missing = [needle for needle, present in path_checks.items() if not present]
        if missing:
            errors.append(f"{path} missing instrumentation tokens: {missing}")
    for name, value in structural_checks.items():
        if isinstance(value, dict):
            missing = [field for field, present in value.items() if not present]
            if missing:
                errors.append(f"{name} missing fields: {missing}")
        elif value is not True:
            errors.append(f"{name} is not true")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass_with_known_historical_gaps" if not errors else "fail",
        "checks": checks,
        "structural_checks": structural_checks,
        "historical_attention_coverage": {
            "gate_records_audited": attention_audit.get("gate_records_audited"),
            "complete_attention_cost_logs": attention_audit.get("complete_attention_cost_logs"),
            "incomplete_attention_cost_logs": attention_audit.get("incomplete_attention_cost_logs"),
        },
        "historical_taste_coverage": {
            "gate_records_audited": taste_audit.get("gate_records_audited"),
            "complete_taste_insight_records": taste_audit.get("complete_taste_insight_records"),
            "incomplete_taste_insight_records": taste_audit.get("incomplete_taste_insight_records"),
        },
        "errors": errors,
        "claim_boundary": (
            "A pass means future prospective matched-budget runs have a documented "
            "preflight path for complete attention-cost and taste/insight capture. "
            "It does not repair missing historical fields and does not provide "
            "performance evidence."
        ),
    }

    json_path = AUDIT_DIR / "prospective_gate_instrumentation_audit.json"
    md_path = AUDIT_DIR / "prospective_gate_instrumentation_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Prospective Gate Instrumentation Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Historical complete attention logs: `{audit['historical_attention_coverage']['complete_attention_cost_logs']}/{audit['historical_attention_coverage']['gate_records_audited']}`",
        f"- Historical complete taste logs: `{audit['historical_taste_coverage']['complete_taste_insight_records']}/{audit['historical_taste_coverage']['gate_records_audited']}`",
        "",
        "## Required Attention Fields",
        "",
    ]
    lines.extend(f"- `{field}`" for field in ATTENTION_FIELDS)
    lines.extend(["", "## Required Taste/Insight Fields", ""])
    lines.extend(f"- `{field}`" for field in TASTE_FIELDS)
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    manifest = _load_json(manifest_path)
    manifest["prospective_gate_instrumentation_audit"] = {
        "status": audit["status"],
        "json": _rel(json_path),
        "markdown": _rel(md_path),
        "claim_boundary": audit["claim_boundary"],
    }
    for path in [Path(__file__), json_path, md_path, task_template_path, protocol_path]:
        rel = _rel(path)
        if rel not in manifest["current_artifacts"]:
            manifest["current_artifacts"].append(rel)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
