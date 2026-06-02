#!/usr/bin/env python3
"""Audit the prepared human-expert blind review packet.

This verifies packet readiness and preserves the boundary that no independent
human expert ratings have been collected yet.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
PACKET_DIR = DOC_DIR / "experiments" / "human_expert_blind_review_packet_20260602_143000"

REQUIRED_SCORE_COLUMNS = [
    "reviewer_id",
    "pair_id",
    "winner",
    "A_problem_framing",
    "A_method_specificity",
    "A_experiment_design",
    "A_limitation_honesty",
    "A_claim_calibration",
    "A_overall_quality",
    "B_problem_framing",
    "B_method_specificity",
    "B_experiment_design",
    "B_limitation_honesty",
    "B_claim_calibration",
    "B_overall_quality",
    "rationale",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _exists(path: Path, *, min_bytes: int = 1) -> dict[str, Any]:
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    return {
        "path": _rel(path),
        "exists": exists,
        "bytes": size,
        "ok": exists and size >= min_bytes,
    }


def _csv_columns(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or []


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = PACKET_DIR / "summary.json"
    pairs_path = PACKET_DIR / "pairs.json"
    condition_key_path = PACKET_DIR / "condition_key.json"
    score_template_path = PACKET_DIR / "score_sheet_template.csv"
    prereg_json_path = PACKET_DIR / "preregistration_analysis_plan.json"

    summary = _load_json(summary_path)
    pairs = _load_json(pairs_path)
    condition_key = _load_json(condition_key_path)
    prereg = _load_json(prereg_json_path)

    errors: list[str] = []
    warnings: list[str] = []

    required_files = [
        PACKET_DIR / "README.md",
        PACKET_DIR / "reviewer_index.md",
        PACKET_DIR / "instructions.md",
        PACKET_DIR / "consent_privacy_note.md",
        PACKET_DIR / "recruitment_email.md",
        PACKET_DIR / "collection_protocol.md",
        score_template_path,
        pairs_path,
        condition_key_path,
        PACKET_DIR / "preregistration_analysis_plan.md",
        prereg_json_path,
        PACKET_DIR / "template_summary_smoke" / "summary.json",
        PACKET_DIR / "template_summary_smoke" / "summary.md",
    ]
    required_files.extend(PACKET_DIR / "pairs" / f"pair_{idx:02d}.md" for idx in range(1, 7))
    file_status = {str(path.relative_to(PACKET_DIR)): _exists(path, min_bytes=20) for path in required_files}
    for rel, status in file_status.items():
        if not status["ok"]:
            errors.append(f"missing or too small required packet file: {rel}")

    pair_items = pairs if isinstance(pairs, list) else pairs.get("pairs", [])
    pair_count = len(pair_items)
    if pair_count != 6:
        errors.append(f"expected 6 pairs, found {pair_count}")

    mapping = condition_key.get("mapping", {})
    if len(mapping) != 6:
        errors.append(f"condition key should map 6 pairs, found {len(mapping)}")
    expected_pair_ids = {f"pair_{idx:02d}" for idx in range(1, 7)}
    mapped_pair_ids = set(mapping)
    if mapped_pair_ids != expected_pair_ids:
        errors.append(f"condition key pair ids mismatch: {sorted(mapped_pair_ids)}")

    reviewer_visible = set(summary.get("reviewer_visible_files", []))
    hidden = set(summary.get("hidden_files", []))
    hidden_required = {
        _rel(condition_key_path),
        _rel(prereg_json_path),
        _rel(PACKET_DIR / "preregistration_analysis_plan.md"),
    }
    if not hidden_required.issubset(hidden):
        errors.append("hidden files do not include condition key and preregistration plan")
    if reviewer_visible & hidden:
        errors.append(f"reviewer-visible files overlap hidden files: {sorted(reviewer_visible & hidden)}")
    if _rel(condition_key_path) in reviewer_visible:
        errors.append("condition key is reviewer-visible")

    reviewer_index_text = _read(PACKET_DIR / "reviewer_index.md")
    if "condition_key.json" in reviewer_index_text and "not included" not in reviewer_index_text:
        errors.append("reviewer index mentions condition_key.json without hiding warning")
    instructions_text = _read(PACKET_DIR / "instructions.md")
    for term in ["winner", "A", "B", "tie"]:
        if term not in instructions_text:
            errors.append(f"instructions missing scoring term: {term}")

    columns = _csv_columns(score_template_path)
    missing_columns = [col for col in REQUIRED_SCORE_COLUMNS if col not in columns]
    if missing_columns:
        errors.append(f"score sheet template missing columns: {missing_columns}")

    smoke_path = PACKET_DIR / "template_summary_smoke" / "summary.json"
    smoke = _load_json(smoke_path)
    if smoke.get("inter_rater_agreement", {}).get("status") != "not_enough_valid_votes":
        errors.append("template summary smoke should report not_enough_valid_votes")
    if smoke.get("claim_boundary") != (
        "This summary is valid only if the CSV contains independent human expert ratings collected under the packet instructions."
    ):
        warnings.append("template summary smoke claim boundary changed; verify wording")

    planned_minimum_raters = prereg.get("design", {}).get("planned_raters", {}).get("minimum")
    planned_minimum_valid_rows = prereg.get("design", {}).get("planned_minimum_valid_rows")
    if planned_minimum_raters != 3:
        errors.append("preregistration planned_minimum_raters should be 3")
    if planned_minimum_valid_rows != 18:
        errors.append("preregistration planned_minimum_valid_rows should be 18")
    required_tests = {
        "bootstrap_confidence_interval_for_review_guided_minus_comparator_mean_delta",
        "two_sided_exact_binomial_test_for_review_guided_wins_excluding_ties",
        "fleiss_kappa_for_A_B_tie_when_enough_balanced_votes_exist",
    }
    if not required_tests.issubset(set(prereg.get("statistical_tests", []))):
        errors.append("preregistration missing required statistical tests")

    if summary.get("status") != "preregistered_packet_prepared_no_human_ratings_yet":
        warnings.append("packet summary status changed; verify whether human ratings exist")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass_prepared_no_human_ratings" if not errors else "fail",
        "packet_dir": _rel(PACKET_DIR),
        "pair_count": pair_count,
        "required_files_checked": len(required_files),
        "file_status": file_status,
        "score_template_columns_present": {col: col in columns for col in REQUIRED_SCORE_COLUMNS},
        "reviewer_visible_file_count": len(reviewer_visible),
        "hidden_file_count": len(hidden),
        "condition_key_hidden": _rel(condition_key_path) in hidden and _rel(condition_key_path) not in reviewer_visible,
        "preregistration": {
            "planned_minimum_raters": planned_minimum_raters,
            "planned_minimum_valid_rows": planned_minimum_valid_rows,
            "statistical_tests": prereg.get("statistical_tests", []),
        },
        "template_summary_smoke_status": smoke.get("inter_rater_agreement", {}).get("status"),
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "This audit verifies that the blind review packet is ready to collect "
            "independent human ratings. It is not human-rating evidence."
        ),
    }

    json_path = AUDIT_DIR / "human_expert_blind_review_packet_audit.json"
    md_path = AUDIT_DIR / "human_expert_blind_review_packet_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Human Expert Blind Review Packet Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Packet: `{audit['packet_dir']}`",
        f"- Pair count: `{audit['pair_count']}`",
        f"- Required files checked: `{audit['required_files_checked']}`",
        f"- Condition key hidden: `{audit['condition_key_hidden']}`",
        f"- Template summary smoke status: `{audit['template_summary_smoke_status']}`",
        "",
        "## Preregistration",
        "",
        f"- Planned minimum raters: `{audit['preregistration']['planned_minimum_raters']}`",
        f"- Planned minimum valid rows: `{audit['preregistration']['planned_minimum_valid_rows']}`",
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
