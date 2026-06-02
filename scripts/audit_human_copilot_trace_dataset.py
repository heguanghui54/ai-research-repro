#!/usr/bin/env python3
"""Audit the derived Human Co-Pilot Trace Dataset before release.

This checks the dataset as a process-evidence artifact. It does not certify
human-subject compliance or population-level validity; it only verifies that
the released file is a derived metadata layer with explicit claim boundaries.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
DATASET_JSON = DOC_DIR / "human_copilot_trace_dataset.json"
OUT_JSON = DOC_DIR / "audits" / "human_copilot_trace_dataset_audit.json"
OUT_MD = DOC_DIR / "audits" / "human_copilot_trace_dataset_audit.md"

REQUIRED_TOP_LEVEL = [
    "status",
    "public_dataset_survey",
    "primary_dataset_positioning",
    "current_snapshot",
    "gate_records",
    "prospective_packages",
    "commit_index",
    "claim_scope",
]

REQUIRED_GATE_FIELDS = [
    "source",
    "gate_id",
    "gate_type",
    "research_task_id",
    "option_count",
    "has_attention_cost",
    "has_taste_insight",
    "human_decision",
]

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_.-]{12,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9_.-]{12,}"),
]

RAW_LOG_MARKERS = [
    "messages",
    "chat_log",
    "raw_transcript",
    "conversation",
    "prompt_text",
    "response_text",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _walk(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = [(prefix, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_walk(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(_walk(child, f"{prefix}[{index}]"))
    return rows


def audit_dataset(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_TOP_LEVEL:
        if field not in data:
            errors.append(f"missing top-level field: {field}")

    if data.get("primary_dataset_positioning") != "single_author_longitudinal_codex_copilot_trace_corpus":
        errors.append("primary_dataset_positioning must identify single-author longitudinal scope")

    survey = data.get("public_dataset_survey")
    if not isinstance(survey, list) or len(survey) < 3:
        errors.append("public_dataset_survey must list at least three adjacent public datasets")

    snapshot = data.get("current_snapshot", {})
    if not isinstance(snapshot, dict):
        errors.append("current_snapshot must be an object")
        snapshot = {}
    for field in ["gate_record_count", "attention_cost_records", "taste_insight_records", "prospective_package_count", "commit_count"]:
        value = snapshot.get(field)
        if not isinstance(value, int) or value < 0:
            errors.append(f"current_snapshot.{field} must be a non-negative integer")

    gates = data.get("gate_records")
    if not isinstance(gates, list) or not gates:
        errors.append("gate_records must be a non-empty list")
        gates = []
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            errors.append(f"gate_records[{index}] must be an object")
            continue
        for field in REQUIRED_GATE_FIELDS:
            if field not in gate:
                errors.append(f"gate_records[{index}] missing {field}")

    packages = data.get("prospective_packages")
    if not isinstance(packages, list):
        errors.append("prospective_packages must be a list")
        packages = []

    claim_scope = data.get("claim_scope", {})
    supports = claim_scope.get("supports") if isinstance(claim_scope, dict) else None
    unsupported = claim_scope.get("does_not_support_alone") if isinstance(claim_scope, dict) else None
    if not isinstance(supports, list) or not supports:
        errors.append("claim_scope.supports must be a non-empty list")
    if not isinstance(unsupported, list) or not unsupported:
        errors.append("claim_scope.does_not_support_alone must be a non-empty list")
    if isinstance(unsupported, list) and not any("population" in item for item in unsupported):
        errors.append("claim scope must explicitly reject population-level conclusions")

    serialized = json.dumps(data, ensure_ascii=False)
    secret_hits = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(serialized):
            secret_hits.append(pattern.pattern)
    if secret_hits:
        errors.append("possible secret-like strings found in dataset JSON")

    raw_markers = []
    for path, value in _walk(data):
        key = path.split(".")[-1].split("[")[0]
        if key in RAW_LOG_MARKERS:
            raw_markers.append(path)
        if isinstance(value, str) and len(value) > 2000:
            warnings.append(f"long string may be raw content: {path}")
    if raw_markers:
        errors.append(f"raw-log-like fields present: {', '.join(raw_markers[:10])}")

    commit_count = len(data.get("commit_index", [])) if isinstance(data.get("commit_index"), list) else 0
    if commit_count != snapshot.get("commit_count"):
        warnings.append("commit_index length differs from current_snapshot.commit_count")
    if len(gates) != snapshot.get("gate_record_count"):
        warnings.append("gate_records length differs from current_snapshot.gate_record_count")
    if len(packages) != snapshot.get("prospective_package_count"):
        warnings.append("prospective_packages length differs from current_snapshot.prospective_package_count")

    return {
        "status": "pass" if not errors else "fail",
        "dataset": _rel(DATASET_JSON),
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "public_dataset_survey_entries": len(survey) if isinstance(survey, list) else 0,
            "gate_records": len(gates),
            "prospective_packages": len(packages),
            "commit_index_entries": commit_count,
            "secret_pattern_hits": len(secret_hits),
            "raw_log_marker_hits": len(raw_markers),
        },
        "release_positioning": {
            "can_release_as": "derived_metadata_case_study" if not errors else "do_not_release_until_fixed",
            "not_certified_for": [
                "raw_chat_log_release",
                "population_level_human_subject_claims",
                "attention_efficiency_claims_without_independent_timing",
            ],
        },
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Human Co-Pilot Trace Dataset Audit",
        "",
        f"- Status: `{summary['status']}`",
        f"- Dataset: `{summary['dataset']}`",
        f"- Gate records: {summary['counts']['gate_records']}",
        f"- Prospective packages: {summary['counts']['prospective_packages']}",
        f"- Commit index entries: {summary['counts']['commit_index_entries']}",
        f"- Secret-pattern hits: {summary['counts']['secret_pattern_hits']}",
        f"- Raw-log marker hits: {summary['counts']['raw_log_marker_hits']}",
        "",
        "## Errors",
        "",
    ]
    if summary["errors"]:
        lines.extend(f"- {error}" for error in summary["errors"])
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    if summary["warnings"]:
        lines.extend(f"- {warning}" for warning in summary["warnings"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A passing audit means the public artifact is a derived metadata layer",
            "rather than raw Codex chat logs. It can support process and case-study",
            "claims about IGRE, but it does not certify population-level human-subject",
            "claims or attention-efficiency claims.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    data = _load_json(DATASET_JSON)
    summary = audit_dataset(data)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
