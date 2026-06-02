#!/usr/bin/env python3
"""Audit the Human Revision vs AI Scientist Revision protocol."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
MANIFEST_PATH = DOC_DIR / "repro_manifest.json"


REQUIRED_METADATA = [
    "forum_id",
    "note_id",
    "cdate",
    "tcdate",
    "ddate",
    "invitation",
    "revision",
]

REQUIRED_CHAIN = ["P0", "R", "PH", "PAI", "PAI-6G", "Pcontrol"]
REQUIRED_ARMS = [
    "P0-only",
    "raw-review-guided",
    "six-gate-guided",
    "shuffled-review-control",
    "human-author-revision",
]
REQUIRED_METRICS = [
    "review_coverage",
    "revision_alignment",
    "scientific_delta",
    "human_unique_gain",
    "ai_unique_gain",
    "six_gate_gain",
    "frontier_alignment",
    "claim_calibration",
    "leakage_flags",
]
REQUIRED_GATES = [
    "scientific_taste_prior",
    "evaluator_stress_test",
    "frontier_direction_router",
    "verifiable_micro_evolution",
    "structured_feedback",
    "claim_calibration",
]
REQUIRED_MD_TERMS = [
    "Human Revision vs AI Scientist Revision Protocol",
    "forum_id",
    "note_id",
    "cdate",
    "tcdate",
    "ddate",
    "invitation",
    "revision",
    "P0",
    "PH",
    "PAI-6G",
    "shuffled-review-control",
    "PH must never be visible",
    "time-capped",
    "review_coverage",
    "frontier_alignment",
    "leakage_flags",
    "six-gate",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _update_manifest(paths: list[Path], audit: dict[str, Any]) -> None:
    if not MANIFEST_PATH.exists():
        return
    manifest = _load_json(MANIFEST_PATH)
    current = manifest.setdefault("current_artifacts", [])
    for path in paths:
        rel = _rel(path)
        if rel not in current:
            current.append(rel)
    manifest["human_revision_vs_ai_revision_protocol"] = {
        "status": audit["status"],
        "json": _rel(AUDIT_DIR / "human_revision_vs_ai_revision_protocol_audit.json"),
        "markdown": _rel(AUDIT_DIR / "human_revision_vs_ai_revision_protocol_audit.md"),
        "protocol_markdown": _rel(DOC_DIR / "human_revision_vs_ai_revision_protocol.md"),
        "protocol_json": _rel(DOC_DIR / "human_revision_vs_ai_revision_protocol.json"),
        "claim_boundary": audit["claim_boundary"],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = DOC_DIR / "human_revision_vs_ai_revision_protocol.md"
    json_path = DOC_DIR / "human_revision_vs_ai_revision_protocol.json"
    md_text = md_path.read_text(encoding="utf-8")
    protocol = _load_json(json_path)

    errors: list[str] = []
    metadata_presence = {term: term in protocol.get("required_metadata", []) or term in md_text for term in REQUIRED_METADATA}
    for term, present in metadata_presence.items():
        if not present:
            errors.append(f"missing required metadata term: {term}")

    chain = protocol.get("version_chain", {})
    chain_presence = {term: term in chain and term in md_text for term in REQUIRED_CHAIN}
    for term, present in chain_presence.items():
        if not present:
            errors.append(f"missing version-chain artifact: {term}")

    arm_presence = {term: term in protocol.get("generation_arms", []) and term in md_text for term in REQUIRED_ARMS}
    for term, present in arm_presence.items():
        if not present:
            errors.append(f"missing generation arm: {term}")

    metric_presence = {term: term in protocol.get("metrics", []) and term in md_text for term in REQUIRED_METRICS}
    for term, present in metric_presence.items():
        if not present:
            errors.append(f"missing metric: {term}")

    gate_presence = {term: term in protocol.get("six_gates_tested", []) and term in md_text for term in REQUIRED_GATES}
    for term, present in gate_presence.items():
        if not present:
            errors.append(f"missing IGRE gate: {term}")

    md_term_presence = {term: term in md_text for term in REQUIRED_MD_TERMS}
    for term, present in md_term_presence.items():
        if not present:
            errors.append(f"markdown missing required term: {term}")

    eligibility_blob = " ".join(protocol.get("eligibility_rules", []))
    leakage_protection = all(
        term in eligibility_blob
        for term in ["PH must never be visible", "time-capped", "retrospective replay"]
    )
    if not leakage_protection:
        errors.append("eligibility rules do not fully encode PH leakage and time-cap safeguards")

    if protocol.get("status") != "protocol_not_yet_empirical_result":
        errors.append("protocol status should preserve that this is not yet empirical evidence")
    if "not current evidence" not in protocol.get("claim_boundary", ""):
        errors.append("claim boundary does not explicitly prevent empirical overclaim")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "protocol_markdown": _rel(md_path),
        "protocol_json": _rel(json_path),
        "metadata_presence": metadata_presence,
        "version_chain_presence": chain_presence,
        "generation_arm_presence": arm_presence,
        "metric_presence": metric_presence,
        "gate_presence": gate_presence,
        "markdown_term_presence": md_term_presence,
        "leakage_protection_present": leakage_protection,
        "errors": errors,
        "claim_boundary": (
            "This audit verifies that the protocol is complete enough to guide "
            "future version-chain experiments. It does not certify that any "
            "OpenReview case has been empirically run or that AI/IGRE revision "
            "outperforms human author revision."
        ),
    }

    audit_json = AUDIT_DIR / "human_revision_vs_ai_revision_protocol_audit.json"
    audit_md = AUDIT_DIR / "human_revision_vs_ai_revision_protocol_audit.md"
    audit_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Human Revision vs AI Scientist Revision Protocol Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Protocol markdown: `{audit['protocol_markdown']}`",
        f"- Protocol JSON: `{audit['protocol_json']}`",
        f"- Leakage protection present: `{audit['leakage_protection_present']}`",
        "",
        "## Checks",
        "",
        f"- Metadata fields: `{sum(metadata_presence.values())}/{len(metadata_presence)}`",
        f"- Version-chain artifacts: `{sum(chain_presence.values())}/{len(chain_presence)}`",
        f"- Generation arms: `{sum(arm_presence.values())}/{len(arm_presence)}`",
        f"- Metrics: `{sum(metric_presence.values())}/{len(metric_presence)}`",
        f"- IGRE gates: `{sum(gate_presence.values())}/{len(gate_presence)}`",
        "",
        "## Claim Boundary",
        "",
        audit["claim_boundary"],
    ]
    if errors:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in errors)
    audit_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    _update_manifest([md_path, json_path, audit_json, audit_md], audit)
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
