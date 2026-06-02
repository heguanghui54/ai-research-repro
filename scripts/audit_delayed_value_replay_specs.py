#!/usr/bin/env python3
"""Audit delayed-value replay specification package."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
AUDIT_DIR = DOC_DIR / "audits"
RUN_DIR = EXP_DIR / "delayed_value_replay_specs_20260602_234500"
REQUIRED_CONDITIONS = {
    "paper_only",
    "raw_review_guided",
    "six_gate_hybrid_guided",
    "shuffled_review_control",
}


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
    if not _file_ok(summary_path):
        errors.append(f"missing summary: {_rel(summary_path)}")
        summary: dict[str, Any] = {}
    else:
        summary = _load_json(summary_path)
    if not _file_ok(readme_path):
        errors.append(f"missing README: {_rel(readme_path)}")

    cases = summary.get("cases", [])
    if summary.get("status") != "preregistered_replay_specs_only":
        errors.append("summary status must be preregistered_replay_specs_only")
    if len(cases) != 3:
        errors.append(f"expected 3 replay spec cases, found {len(cases)}")
    if set(summary.get("conditions", [])) != REQUIRED_CONDITIONS:
        errors.append("summary conditions do not match required TFR condition set")

    case_checks = []
    for case in cases:
        case_dir = ROOT / case["case_dir"]
        missing = []
        spec_path = case_dir / "replay_spec.json"
        spec_md_path = case_dir / "replay_spec.md"
        if not _file_ok(spec_path):
            missing.append(_rel(spec_path))
            spec = {}
        else:
            spec = _load_json(spec_path)
        if not _file_ok(spec_md_path):
            missing.append(_rel(spec_md_path))
        for condition in REQUIRED_CONDITIONS:
            prompt_path = case_dir / f"{condition}_prompt.txt"
            if not _file_ok(prompt_path, min_bytes=200):
                missing.append(_rel(prompt_path))
        if set(spec.get("required_conditions", [])) != REQUIRED_CONDITIONS:
            errors.append(f"{case.get('review_id')} spec missing required conditions")
        if "not an executed replay" not in spec.get("claim_boundary", ""):
            errors.append(f"{case.get('review_id')} spec missing execution boundary")
        if len(spec.get("positive_delayed_value_rule", [])) < 5:
            errors.append(f"{case.get('review_id')} spec has incomplete delayed-value rule")
        if missing:
            errors.append(f"{case.get('review_id')} missing files: {missing}")
        case_checks.append(
            {
                "review_id": case.get("review_id"),
                "case_dir": case.get("case_dir"),
                "missing_files": missing,
                "condition_count": len(spec.get("required_conditions", [])) if spec else 0,
                "domain": spec.get("domain") if spec else case.get("domain"),
            }
        )

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "run_dir": _rel(RUN_DIR),
        "case_count": len(cases),
        "conditions": sorted(REQUIRED_CONDITIONS),
        "case_checks": case_checks,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "A pass means the next delayed-value replay cases are preregistered and "
            "executable as specs. It does not mean any replay has been executed or "
            "that delayed-value evidence has been found."
        ),
    }

    json_path = AUDIT_DIR / "delayed_value_replay_specs_audit.json"
    md_path = AUDIT_DIR / "delayed_value_replay_specs_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Delayed-Value Replay Specs Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Run dir: `{audit['run_dir']}`",
        f"- Case count: `{audit['case_count']}`",
        f"- Conditions: `{', '.join(audit['conditions'])}`",
        "",
        "## Case Checks",
        "",
    ]
    for check in case_checks:
        lines.append(
            f"- `{check['review_id']}` domain `{check['domain']}` conditions `{check['condition_count']}` missing `{check['missing_files']}`"
        )
    lines.extend(["", "## Errors", ""])
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
