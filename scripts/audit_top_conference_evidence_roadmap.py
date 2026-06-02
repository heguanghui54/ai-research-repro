#!/usr/bin/env python3
"""Audit the top-conference evidence roadmap.

This checks whether the roadmap converts each remaining strong-venue blocker
into a concrete experiment with a claim, minimum design, upgrade condition, and
fallback. It does not judge whether the milestones have been completed.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"


REQUIRED_MILESTONES = {
    "blind_human_expert_review": [
        "qualified reviewers",
        "anonymized pairs",
        "majority",
    ],
    "matched_autonomous_vs_human_gated_runs": [
        "At least 3 tasks",
        "5 matched pairs",
        "same model family",
    ],
    "lhtg_dvrs_replay": [
        "30 delayed-value candidates",
        "30 matched controls",
        "positive delayed-value case",
    ],
    "three_deep_regeneration_case_studies": [
        "three selected cases",
        "human review excerpts",
        "runnable experiment code or logs",
        "later-frontier evidence",
    ],
    "live_multi_researcher_copilot_trace_data": [
        "20 prospective gates",
        "5 researchers",
        "attention_cost",
        "taste_insight",
    ],
    "non_fml_official_benchmark_check": [
        "non-FML",
        "matched package",
        "evaluator-safety",
    ],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    roadmap_json_path = DOC_DIR / "top_conference_evidence_roadmap.json"
    roadmap_md_path = DOC_DIR / "top_conference_evidence_roadmap.md"
    roadmap = _load_json(roadmap_json_path)
    md_text = roadmap_md_path.read_text(encoding="utf-8")

    errors: list[str] = []
    warnings: list[str] = []
    milestones = {item.get("id"): item for item in roadmap.get("milestones", [])}

    milestone_checks: dict[str, dict[str, Any]] = {}
    for milestone_id, required_terms in REQUIRED_MILESTONES.items():
        item = milestones.get(milestone_id)
        if not item:
            errors.append(f"missing milestone: {milestone_id}")
            milestone_checks[milestone_id] = {"exists": False}
            continue
        field_presence = {
            field: bool(item.get(field))
            for field in ["claim_tested", "minimum_design", "upgrade_condition", "fallback_if_failed"]
        }
        missing_fields = [field for field, present in field_presence.items() if not present]
        for field in missing_fields:
            errors.append(f"{milestone_id} missing required field: {field}")

        joined = json.dumps(item, ensure_ascii=False)
        term_presence = {term: term in joined for term in required_terms}
        missing_terms = [term for term, present in term_presence.items() if not present]
        for term in missing_terms:
            errors.append(f"{milestone_id} missing design term: {term}")

        milestone_checks[milestone_id] = {
            "exists": True,
            "field_presence": field_presence,
            "term_presence": term_presence,
            "ok": not missing_fields and not missing_terms,
        }

    decision_rule = roadmap.get("submission_decision_rule", {})
    if not decision_rule.get("pilot_or_system_paper"):
        errors.append("submission decision rule missing pilot_or_system_paper")
    if not decision_rule.get("top_conference_empirical_paper"):
        errors.append("submission decision rule missing top_conference_empirical_paper")
    if "not empirical superiority over autonomous AI Scientist-v2" not in roadmap.get("claim_boundary", ""):
        errors.append("claim boundary does not preserve non-superiority statement")

    required_md_terms = [
        "Milestone 1: Blind Human Expert Review",
        "Milestone 2: Matched Autonomous Versus Human-Gated Runs",
        "Milestone 3: Long-Horizon Taste Gate / DVRS Replay",
        "Milestone 4: Three Deep Regeneration Case Studies",
        "Milestone 5: Live Multi-Researcher Co-Pilot Trace Data",
        "Milestone 6: Non-FML Official Benchmark Check",
        "Decision Rule For The Paper",
        "not empirical superiority over autonomous AI Scientist-v2",
    ]
    md_term_presence = {term: term in md_text for term in required_md_terms}
    for term, present in md_term_presence.items():
        if not present:
            errors.append(f"roadmap markdown missing term: {term}")

    if roadmap.get("status") != "roadmap_not_completed":
        warnings.append("roadmap status changed; verify whether milestone evidence actually completed")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "roadmap_json": _rel(roadmap_json_path),
        "roadmap_markdown": _rel(roadmap_md_path),
        "milestone_count": len(roadmap.get("milestones", [])),
        "required_milestone_count": len(REQUIRED_MILESTONES),
        "milestone_checks": milestone_checks,
        "submission_decision_rule_present": bool(decision_rule),
        "md_term_presence": md_term_presence,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "A pass means the roadmap is actionable and preserves the current "
            "evidence boundary. It does not mean the top-conference evidence "
            "milestones have been completed."
        ),
    }

    json_path = AUDIT_DIR / "top_conference_evidence_roadmap_audit.json"
    md_path = AUDIT_DIR / "top_conference_evidence_roadmap_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Top-Conference Evidence Roadmap Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Roadmap JSON: `{audit['roadmap_json']}`",
        f"- Roadmap Markdown: `{audit['roadmap_markdown']}`",
        f"- Milestones: `{audit['milestone_count']}/{audit['required_milestone_count']}`",
        "",
        "## Milestone Checks",
        "",
    ]
    for milestone_id, check in milestone_checks.items():
        lines.append(f"- `{milestone_id}`: `{'pass' if check.get('ok') else 'fail'}`")
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
