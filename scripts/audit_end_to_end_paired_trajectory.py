#!/usr/bin/env python3
"""Audit same-run end-to-end paired trajectory evidence.

This audit separates workflow completion from performance superiority. A pass
means the package contains a continuous co-pilot trajectory, generated
co-pilot/autonomous manuscripts, and a same-run autonomous comparator; it does
not mean the co-pilot condition is empirically better.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
TRAJ_DIR = DOC_DIR / "experiments" / "online_full_gate_smoke_20260602_010521"
ONLINE_DIR = TRAJ_DIR / "online_manuscript"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _exists(path: Path, min_bytes: int = 1) -> dict[str, Any]:
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    return {"path": _rel(path), "exists": exists, "bytes": size, "ok": exists and size >= min_bytes}


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = DOC_DIR / "repro_manifest.json"

    trajectory_path = TRAJ_DIR / "trajectory.json"
    autonomous_summary_path = TRAJ_DIR / "autonomous_baseline_summary.json"
    co_pilot_manuscript_path = ONLINE_DIR / "co_pilot_online_full_gate_manuscript.md"
    autonomous_manuscript_path = ONLINE_DIR / "autonomous_online_comparator_manuscript.md"
    online_summary_path = ONLINE_DIR / "summary.json"
    online_summary_md_path = ONLINE_DIR / "summary.md"
    comparison_path = ONLINE_DIR / "matched_budget_comparison_summary.json"
    comparison_md_path = ONLINE_DIR / "matched_budget_comparison_summary.md"
    paper_quality_path = ONLINE_DIR / "paper_quality" / "summary.json"
    paper_quality_md_path = ONLINE_DIR / "paper_quality" / "summary.md"

    trajectory = _load_json(trajectory_path)
    comparison = _load_json(comparison_path)
    online_summary = _load_json(online_summary_path)
    paper_quality = _load_json(paper_quality_path)

    gates = trajectory.get("gates", [])
    gate_types = {gate.get("gate_type") for gate in gates}
    required_gate_types = {
        "idea_selection",
        "evaluator_approval",
        "branch_selection",
        "program_search_escalation",
        "claim_audit",
    }

    co_metric = comparison.get("co_pilot_metric")
    auto_metric = comparison.get("autonomous_metric")
    lower_is_better = bool(comparison.get("lower_is_better"))
    if co_metric is None or auto_metric is None:
        metric_winner = "unscored"
    elif lower_is_better:
        metric_winner = "co_pilot" if co_metric < auto_metric else "autonomous" if auto_metric < co_metric else "tie"
    else:
        metric_winner = "co_pilot" if co_metric > auto_metric else "autonomous" if auto_metric > co_metric else "tie"

    co_score = comparison.get("co_pilot_scores", {}).get("overall")
    auto_score = comparison.get("autonomous_scores", {}).get("overall")
    if co_score is None or auto_score is None:
        manuscript_score_winner = "unscored"
    else:
        manuscript_score_winner = "co_pilot" if co_score > auto_score else "autonomous" if auto_score > co_score else "tie"

    artifact_status = {
        "trajectory": _exists(trajectory_path),
        "autonomous_summary": _exists(autonomous_summary_path),
        "co_pilot_manuscript": _exists(co_pilot_manuscript_path, 1000),
        "autonomous_manuscript": _exists(autonomous_manuscript_path, 1000),
        "online_summary_json": _exists(online_summary_path),
        "online_summary_md": _exists(online_summary_md_path),
        "comparison_json": _exists(comparison_path),
        "comparison_md": _exists(comparison_md_path),
        "paper_quality_json": _exists(paper_quality_path),
        "paper_quality_md": _exists(paper_quality_md_path),
    }

    errors: list[str] = []
    if not all(item["ok"] for item in artifact_status.values()):
        errors.append("one or more required paired-trajectory artifacts are missing or too small")
    if not trajectory.get("is_single_online_smoke_run"):
        errors.append("trajectory is not marked as a single online smoke run")
    if not comparison.get("matched_continuous_trajectory"):
        errors.append("autonomous comparator is not marked as same-continuous-trajectory")
    missing_gates = sorted(required_gate_types - gate_types)
    if missing_gates:
        errors.append(f"missing required gate types: {missing_gates}")
    if not online_summary.get("matched_autonomous_manuscript"):
        errors.append("online manuscript summary does not mark matched autonomous manuscript")

    superiority_supported = metric_winner == "co_pilot" and manuscript_score_winner == "co_pilot"
    model_review_successful = int(paper_quality.get("successful_reviews", 0) or 0)
    model_review_count = int(paper_quality.get("review_count", 0) or 0)
    model_review_winner = (
        "co_pilot"
        if paper_quality.get("co_pilot_wins", 0) > paper_quality.get("autonomous_wins", 0)
        else "autonomous"
        if paper_quality.get("autonomous_wins", 0) > paper_quality.get("co_pilot_wins", 0)
        else "tie"
    )
    audit = {
        "audit_date": _utc_now(),
        "status": "pass_same_run_smoke_pair" if not errors else "fail",
        "evidence_level": "same_run_smoke_pair",
        "artifacts": artifact_status,
        "trajectory_id": trajectory.get("trajectory_id"),
        "gate_count": len(gates),
        "gate_types": sorted(gate_types),
        "matched_continuous_trajectory": bool(comparison.get("matched_continuous_trajectory")),
        "fresh_online_smoke": bool(online_summary.get("fresh_online_smoke")),
        "co_pilot_metric": co_metric,
        "autonomous_metric": auto_metric,
        "lower_is_better": lower_is_better,
        "metric_winner": metric_winner,
        "co_pilot_manuscript_internal_score": co_score,
        "autonomous_manuscript_internal_score": auto_score,
        "manuscript_score_winner": manuscript_score_winner,
        "model_review": {
            "status": paper_quality.get("status"),
            "successful_reviews": model_review_successful,
            "review_count": model_review_count,
            "co_pilot_wins": paper_quality.get("co_pilot_wins"),
            "autonomous_wins": paper_quality.get("autonomous_wins"),
            "ties": paper_quality.get("ties"),
            "winner": model_review_winner,
            "scope_note": paper_quality.get("scope_note"),
        },
        "superiority_supported": superiority_supported,
        "errors": errors,
        "claim_boundary": (
            "This is a same-run smoke pair from gate orchestration to manuscript "
            "production. In this pair the autonomous baseline wins the benchmark "
            "metric while the co-pilot manuscript wins the internal manuscript "
            "structure/claim-calibration score and a two-model manuscript-quality "
            "probe. The model review is an audit aid, not human expert peer "
            "review. The result supports workflow completion and comparison "
            "readiness, not empirical superiority over autonomous AI Scientist-v2."
        ),
    }

    json_path = AUDIT_DIR / "end_to_end_paired_trajectory_audit.json"
    md_path = AUDIT_DIR / "end_to_end_paired_trajectory_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# End-to-End Paired Trajectory Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Evidence level: `{audit['evidence_level']}`",
        f"- Trajectory: `{artifact_status['trajectory']['path']}`",
        f"- Co-pilot manuscript: `{artifact_status['co_pilot_manuscript']['path']}`",
        f"- Autonomous manuscript: `{artifact_status['autonomous_manuscript']['path']}`",
        f"- Matched continuous trajectory: `{audit['matched_continuous_trajectory']}`",
        f"- Gate count: `{audit['gate_count']}`",
        f"- Metric winner: `{audit['metric_winner']}`",
        f"- Manuscript internal-score winner: `{audit['manuscript_score_winner']}`",
        f"- Model-review winner: `{audit['model_review']['winner']}`",
        f"- Superiority supported: `{audit['superiority_supported']}`",
        "",
        "## Metrics",
        "",
        f"- Co-pilot benchmark metric: `{audit['co_pilot_metric']}`",
        f"- Autonomous benchmark metric: `{audit['autonomous_metric']}`",
        f"- Lower is better: `{audit['lower_is_better']}`",
        f"- Co-pilot manuscript internal score: `{audit['co_pilot_manuscript_internal_score']}`",
        f"- Autonomous manuscript internal score: `{audit['autonomous_manuscript_internal_score']}`",
        f"- Model reviewer calls: `{model_review_successful}/{model_review_count}`",
        f"- Model review co-pilot wins: `{paper_quality.get('co_pilot_wins')}`",
        f"- Model review autonomous wins: `{paper_quality.get('autonomous_wins')}`",
        f"- Model review ties: `{paper_quality.get('ties')}`",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    manifest = _load_json(manifest_path)
    manifest["end_to_end_paired_trajectory_audit"] = {
        "status": audit["status"],
        "json": _rel(json_path),
        "markdown": _rel(md_path),
        "metric_winner": metric_winner,
        "manuscript_score_winner": manuscript_score_winner,
        "superiority_supported": superiority_supported,
    }
    for path in [
        Path(__file__),
        json_path,
        md_path,
        co_pilot_manuscript_path,
        autonomous_manuscript_path,
        online_summary_path,
        online_summary_md_path,
        comparison_path,
        comparison_md_path,
        paper_quality_path,
        paper_quality_md_path,
    ]:
        rel = _rel(path)
        if rel not in manifest["current_artifacts"]:
            manifest["current_artifacts"].append(rel)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
