#!/usr/bin/env python3
"""Audit the aggregate live Temporal Frontier Replay summary."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
RUN_DIR = DOC_DIR / "experiments" / "live_tfr_replay_aggregate_20260603_003500"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_ok(path: Path, min_bytes: int = 20) -> bool:
    return path.exists() and path.stat().st_size >= min_bytes


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    warnings: list[str] = []
    summary_path = RUN_DIR / "summary.json"
    readme_path = RUN_DIR / "README.md"
    if not _file_ok(summary_path, min_bytes=100):
        errors.append(f"missing summary: {_rel(summary_path)}")
        summary: dict[str, Any] = {}
    else:
        summary = _load_json(summary_path)
    if not _file_ok(readme_path, min_bytes=100):
        errors.append(f"missing README: {_rel(readme_path)}")

    expected = {
        "executed_case_count": 2,
        "same_model_raw_positive_count": 2,
        "strict_positive_count": 0,
        "cross_model_successful_judge_count": 2,
        "cross_model_strict_positive_count": 0,
    }
    observed = {key: summary.get(key) for key in expected}
    for key, value in expected.items():
        if observed.get(key) != value:
            errors.append(f"{key} expected {value}, observed {observed.get(key)}")

    case_rows = summary.get("case_rows", [])
    cross_rows = summary.get("cross_model_rows", [])
    if len(case_rows) != 2:
        errors.append("case_rows does not contain two executed cases")
    if len(cross_rows) != 2:
        errors.append("cross_model_rows does not contain two cross-model runs")
    if any(row.get("strict_label") == "positive" for row in case_rows):
        warnings.append("at least one same-model strict positive case appears in aggregate")
    if any(
        row.get("aggregate", {}).get("strict_label_counts", {}).get("positive", 0) > 0
        for row in cross_rows
    ):
        warnings.append("at least one cross-model strict positive case appears in aggregate")
    if "not as evidence that delayed-value review signals have already been found" not in summary.get("interpretation", ""):
        errors.append("interpretation does not preserve negative delayed-value boundary")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "run_dir": _rel(RUN_DIR),
        "summary": _rel(summary_path),
        "observed": observed,
        "expected": expected,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "A pass means the aggregate live TFR replay summary is internally "
            "consistent with the archived two-case replay evidence. It does not "
            "mean delayed-value evidence, benchmark reruns, or human ratings exist."
        ),
    }
    json_path = AUDIT_DIR / "live_tfr_replay_summary_audit.json"
    md_path = AUDIT_DIR / "live_tfr_replay_summary_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Live TFR Replay Summary Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Run dir: `{audit['run_dir']}`",
        f"- Observed: `{audit['observed']}`",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
