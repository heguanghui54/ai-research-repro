#!/usr/bin/env python3
"""Audit the Long-Horizon Taste Gate and DVRS evidence boundary.

This audit ties the LHTG/DVRS method language to existing Temporal Frontier
Replay probes. It is intentionally conservative: it can pass while reporting
zero positive delayed-value review signals.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _contains_all(path: Path, needles: list[str]) -> dict[str, bool]:
    text = path.read_text(encoding="utf-8")
    return {needle: needle in text for needle in needles}


def _add_manifest_artifacts(paths: list[Path], audit: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["lhtg_dvrs_audit"] = {
        "status": audit["status"],
        "json": _rel(AUDIT_DIR / "lhtg_dvrs_audit.json"),
        "markdown": _rel(AUDIT_DIR / "lhtg_dvrs_audit.md"),
        "method_terms_present": audit["method_terms_present"],
        "reusable_workflow_terms_present": audit["reusable_workflow_terms_present"],
        "delayed_value_positive_cases": audit["delayed_value_positive_cases"],
        "candidate_queue_size": audit["candidate_queue"]["delayed_value_replay_candidates"],
        "candidate_frontier_delta": audit["candidate_frontier_validation"]["delayed_minus_control_mean_score"],
        "executed_multicase_replay_cases": audit["executed_multicase_replay"]["case_count"],
        "executed_multicase_strict_positive_cases": audit["executed_multicase_replay"][
            "strict_positive_cases"
        ],
        "claim_boundary": audit["claim_boundary"],
    }
    current_counts = manifest.setdefault("current_counts", {})
    current_counts["lhtg_dvrs_audit_runs"] = 1
    current_counts["lhtg_delayed_value_positive_cases"] = audit["delayed_value_positive_cases"]
    current_counts["lhtg_candidate_queue_size"] = audit["candidate_queue"]["delayed_value_replay_candidates"]
    current_counts["lhtg_candidate_frontier_delta"] = audit["candidate_frontier_validation"][
        "delayed_minus_control_mean_score"
    ]
    current_counts["lhtg_executed_multicase_replay_cases"] = audit["executed_multicase_replay"]["case_count"]
    current_counts["lhtg_executed_multicase_strict_positive_cases"] = audit["executed_multicase_replay"][
        "strict_positive_cases"
    ]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    architecture = DOC_DIR / "architecture.md"
    paper_en = DOC_DIR / "paper_en_focused.md"
    paper_zh = DOC_DIR / "paper_zh_focused.md"
    tfr_spec_md = DOC_DIR / "temporal_frontier_replay_spec.md"
    tfr_spec_json = DOC_DIR / "temporal_frontier_replay_spec.json"
    skill_md = ROOT / "skills" / "co-pilot-ai-scientist-v3" / "SKILL.md"
    task_template = ROOT / "skills" / "co-pilot-ai-scientist-v3" / "templates" / "task_spec_template.md"
    gate_template = ROOT / "skills" / "co-pilot-ai-scientist-v3" / "templates" / "human_gate_log_template.json"
    usage_en = DOC_DIR / "usage_en.md"
    usage_zh = DOC_DIR / "usage_zh.md"
    runbook_en = DOC_DIR / "RUNBOOK_EN.md"
    runbook_zh = DOC_DIR / "RUNBOOK_ZH.md"
    tfr_audit_path = AUDIT_DIR / "temporal_frontier_replay_audit.json"
    mining_path = DOC_DIR / "experiments" / "delayed_value_review_candidate_mining_20260603_001500" / "summary.json"
    validation_path = (
        DOC_DIR / "experiments" / "delayed_value_candidate_frontier_validation_20260603_011500" / "summary.json"
    )
    citation_path = DOC_DIR / "experiments" / "retrospective_frontier_citation_probe_20260602_213000" / "summary.json"
    review_signal_path = DOC_DIR / "experiments" / "review_frontier_signal_probe_20260602_214500" / "summary.json"
    semantic_path = DOC_DIR / "experiments" / "semantic_frontier_judge_probe_20260602_223000" / "summary.json"
    multicase_replay_path = AUDIT_DIR / "delayed_value_replay_multicase_audit.json"

    tfr_spec = _load_json(tfr_spec_json)
    tfr_audit = _load_json(tfr_audit_path)
    mining = _load_json(mining_path)
    validation = _load_json(validation_path)
    citation = _load_json(citation_path)
    review_signal = _load_json(review_signal_path)
    semantic = _load_json(semantic_path)
    multicase_replay = _load_json(multicase_replay_path)

    method_checks = {
        _rel(architecture): _contains_all(architecture, ["Long-Horizon Taste Gate", "LHTG", "DVRS"]),
        _rel(paper_en): _contains_all(paper_en, ["Long-Horizon Taste Gate", "LHTG", "DVRS"]),
        _rel(paper_zh): _contains_all(paper_zh, ["长期科研品味门控", "LHTG", "DVRS"]),
        _rel(tfr_spec_md): _contains_all(tfr_spec_md, ["Long-Horizon Taste Gate", "LHTG Routing Rule", "DVRS"]),
    }
    reusable_workflow_checks = {
        _rel(skill_md): _contains_all(
            skill_md,
            [
                "Long-Horizon Taste Gate",
                "scripts/run_delayed_value_review_candidate_mining.py",
                "scripts/audit_long_horizon_taste_gate.py",
            ],
        ),
        _rel(task_template): _contains_all(
            task_template,
            ["long_horizon_taste_gate", "Delayed-Value Review Signal", "shuffled-review-control"],
        ),
        _rel(gate_template): _contains_all(
            gate_template,
            ["long_horizon_taste_gate", "is_lhtg_candidate", "delayed_value_label"],
        ),
        _rel(usage_en): _contains_all(
            usage_en,
            ["LHTG/DVRS", "scripts/audit_long_horizon_taste_gate.py", "0` positive delayed-value cases"],
        ),
        _rel(usage_zh): _contains_all(
            usage_zh,
            ["LHTG/DVRS", "scripts/audit_long_horizon_taste_gate.py", "正向 delayed-value cases"],
        ),
        _rel(runbook_en): _contains_all(
            runbook_en,
            ["Long-Horizon Taste Gate / DVRS Audit", "positive delayed-value cases: `0`"],
        ),
        _rel(runbook_zh): _contains_all(
            runbook_zh,
            ["长期科研品味门控 / DVRS 审计", "positive delayed-value cases：`0`"],
        ),
    }

    missing_terms = []
    for path, checks in method_checks.items():
        for term, present in checks.items():
            if not present:
                missing_terms.append(f"{path}: {term}")
    missing_workflow_terms = []
    for path, checks in reusable_workflow_checks.items():
        for term, present in checks.items():
            if not present:
                missing_workflow_terms.append(f"{path}: {term}")

    mining_agg = mining["aggregate"]
    validation_agg = validation["aggregate"]
    citation_agg = citation["aggregate"]
    review_agg = review_signal["aggregate"]
    semantic_agg = semantic["aggregate"]

    delayed_positive_cases = int(citation_agg.get("delayed_value_case_count", 0))
    latent_review_cases = int(review_agg.get("latent_delayed_value_candidate_count", 0))
    latent_semantic_cases = int(semantic_agg.get("latent_delayed_value_candidate_count", 0))
    total_positive_cases = delayed_positive_cases + latent_review_cases + latent_semantic_cases

    errors: list[str] = []
    warnings: list[str] = []
    if missing_terms:
        errors.append(f"missing LHTG/DVRS method terms: {missing_terms}")
    if missing_workflow_terms:
        errors.append(f"missing LHTG/DVRS reusable workflow terms: {missing_workflow_terms}")
    if tfr_audit.get("status") != "pass_with_negative_delayed_value_evidence":
        errors.append("TFR audit status changed unexpectedly")
    if not tfr_spec.get("delayed_value_label_conditions"):
        errors.append("TFR spec JSON lacks delayed-value label conditions")
    if total_positive_cases == 0:
        warnings.append("No positive delayed-value review signal has been validated yet")
    if validation_agg.get("delayed_minus_control_mean_score", 0) <= 0:
        warnings.append("Candidate-frontier validation does not show a positive replay-prioritization delta")
    if multicase_replay.get("strict_positive_cases", 0) == 0:
        warnings.append("Multicase live replay found no strict positive DVRS case")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass_with_no_positive_dvrs" if not errors else "fail",
        "method_terms_present": not missing_terms,
        "reusable_workflow_terms_present": not missing_workflow_terms,
        "method_checks": method_checks,
        "reusable_workflow_checks": reusable_workflow_checks,
        "tfr_status": tfr_audit.get("status"),
        "candidate_queue": {
            "reviews_screened": mining_agg.get("review_count"),
            "papers_screened": mining_agg.get("paper_count"),
            "delayed_value_replay_candidates": mining_agg.get("delayed_value_replay_candidate_count"),
            "candidate_rate": mining_agg.get("candidate_rate"),
            "long_horizon_positive_candidates": mining_agg.get("long_horizon_positive_candidate_count"),
            "short_term_repair_signals": mining_agg.get("short_term_repair_signal_count"),
        },
        "candidate_frontier_validation": {
            "attempted_count": validation_agg.get("attempted_count"),
            "scored_count": validation_agg.get("scored_count"),
            "delayed_candidate_mean_review_signal_score": validation_agg.get(
                "delayed_candidate_mean_review_signal_score"
            ),
            "control_mean_review_signal_score": validation_agg.get("control_mean_review_signal_score"),
            "delayed_minus_control_mean_score": validation_agg.get("delayed_minus_control_mean_score"),
        },
        "validated_negative_evidence": {
            "citation_delayed_value_cases": delayed_positive_cases,
            "citation_short_term_positive_long_term_negative_cases": citation_agg.get(
                "short_term_positive_long_term_negative_count"
            ),
            "review_frontier_latent_delayed_value_candidates": latent_review_cases,
            "semantic_latent_delayed_value_candidates": latent_semantic_cases,
            "semantic_winner_counts": semantic_agg.get("winner_counts"),
        },
        "executed_multicase_replay": {
            "status": multicase_replay.get("status"),
            "case_count": multicase_replay.get("case_count"),
            "same_model_positive_cases": multicase_replay.get("same_model_positive_cases"),
            "strict_positive_cases": multicase_replay.get("strict_positive_cases"),
            "cross_model_strict_positive_cases": multicase_replay.get(
                "cross_model_strict_positive_cases"
            ),
            "cross_model_frontier_winner_counts": multicase_replay.get(
                "cross_model_frontier_winner_counts"
            ),
            "path": _rel(multicase_replay_path),
        },
        "delayed_value_positive_cases": total_positive_cases,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "LHTG/DVRS is operationalized as a routing and replay policy, but the current "
            "archived evidence validates only candidate prioritization and negative/weak TFR "
            "boundaries. It does not prove that human reviews improve long-horizon discovery."
        ),
    }

    json_path = AUDIT_DIR / "lhtg_dvrs_audit.json"
    md_path = AUDIT_DIR / "lhtg_dvrs_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Long-Horizon Taste Gate / DVRS Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Method terms present: `{audit['method_terms_present']}`",
        f"- Reusable workflow terms present: `{audit['reusable_workflow_terms_present']}`",
        f"- TFR status: `{audit['tfr_status']}`",
        f"- Delayed-value positive cases: `{audit['delayed_value_positive_cases']}`",
        "",
        "## Reusable Workflow Checks",
        "",
    ]
    for path, checks in audit["reusable_workflow_checks"].items():
        missing = [term for term, present in checks.items() if not present]
        lines.append(f"- `{path}`: `{'pass' if not missing else 'fail'}`")
        if missing:
            lines.append(f"  - missing: `{missing}`")
    lines.extend([
        "",
        "## Candidate Queue",
        "",
        f"- Reviews screened: `{audit['candidate_queue']['reviews_screened']}`",
        f"- Papers screened: `{audit['candidate_queue']['papers_screened']}`",
        f"- Delayed-value replay candidates: `{audit['candidate_queue']['delayed_value_replay_candidates']}`",
        f"- Candidate rate: `{audit['candidate_queue']['candidate_rate']}`",
        f"- Long-horizon positive candidates: `{audit['candidate_queue']['long_horizon_positive_candidates']}`",
        f"- Short-term repair signals: `{audit['candidate_queue']['short_term_repair_signals']}`",
        "",
        "## Candidate Frontier Validation",
        "",
        f"- Attempted reviews: `{audit['candidate_frontier_validation']['attempted_count']}`",
        f"- Scored reviews: `{audit['candidate_frontier_validation']['scored_count']}`",
        "- Delayed-candidate mean review signal: "
        f"`{audit['candidate_frontier_validation']['delayed_candidate_mean_review_signal_score']}`",
        f"- Control mean review signal: `{audit['candidate_frontier_validation']['control_mean_review_signal_score']}`",
        f"- Delayed minus control mean score: `{audit['candidate_frontier_validation']['delayed_minus_control_mean_score']}`",
        "",
        "## Validated Negative Evidence",
        "",
        f"- Citation delayed-value cases: `{audit['validated_negative_evidence']['citation_delayed_value_cases']}`",
        "- Citation short-term-positive/long-term-negative cases: "
        f"`{audit['validated_negative_evidence']['citation_short_term_positive_long_term_negative_cases']}`",
        "- Review-frontier latent delayed-value candidates: "
        f"`{audit['validated_negative_evidence']['review_frontier_latent_delayed_value_candidates']}`",
        "- Semantic latent delayed-value candidates: "
        f"`{audit['validated_negative_evidence']['semantic_latent_delayed_value_candidates']}`",
        f"- Semantic winner counts: `{audit['validated_negative_evidence']['semantic_winner_counts']}`",
        "",
        "## Executed Multicase Replay",
        "",
        f"- Replay audit status: `{audit['executed_multicase_replay']['status']}`",
        f"- Replay cases: `{audit['executed_multicase_replay']['case_count']}`",
        f"- Same-model positive labels: `{audit['executed_multicase_replay']['same_model_positive_cases']}`",
        f"- Strict positive DVRS cases: `{audit['executed_multicase_replay']['strict_positive_cases']}`",
        "- Cross-model strict positive labels: "
        f"`{audit['executed_multicase_replay']['cross_model_strict_positive_cases']}`",
        "- Cross-model frontier winner counts: "
        f"`{audit['executed_multicase_replay']['cross_model_frontier_winner_counts']}`",
        "",
        "## Errors",
        "",
    ])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    _add_manifest_artifacts(
        [
            json_path,
            md_path,
            Path(__file__),
            skill_md,
            task_template,
            gate_template,
            usage_en,
            usage_zh,
            runbook_en,
            runbook_zh,
            multicase_replay_path,
        ],
        audit,
    )

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
