#!/usr/bin/env python3
"""Audit mixed and negative evidence for the IGRE paper.

The goal is not to make the paper look stronger by hiding failures. This audit
turns the main mixed/negative probes into explicit method-design implications:
what failed, what failure mechanism it suggests, and which IGRE change it
motivates.
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


def _load_json(rel_path: str) -> Any:
    path = ROOT / rel_path
    return json.loads(path.read_text(encoding="utf-8"))


def _get(data: Any, path: list[str], default: Any = None) -> Any:
    value = data
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    sources = {
        "model_blind_dry_run": "docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/model_blind_review_dry_run_20260603/analysis/summary.json",
        "prospective_package_summary": "docs/co_pilot_ai_scientist_v3/audits/prospective_matched_package_summary.json",
        "fml_matched_summary": "docs/co_pilot_ai_scientist_v3/audits/fml_matched_comparison_summary.json",
        "live_tfr_aggregate": "docs/co_pilot_ai_scientist_v3/experiments/live_tfr_replay_aggregate_20260603_003500/summary.json",
        "citation_frontier_probe": "docs/co_pilot_ai_scientist_v3/experiments/retrospective_frontier_citation_probe_20260602_213000/summary.json",
        "semantic_frontier_judge": "docs/co_pilot_ai_scientist_v3/experiments/semantic_frontier_judge_probe_20260602_223000/summary.json",
        "frontier_metric_disagreement": "docs/co_pilot_ai_scientist_v3/experiments/frontier_metric_disagreement_20260603_003000/summary.json",
    }
    loaded: dict[str, Any] = {}
    for key, rel_path in sources.items():
        path = ROOT / rel_path
        if not path.exists():
            errors.append(f"missing source: {rel_path}")
            continue
        loaded[key] = _load_json(rel_path)

    model_blind = loaded.get("model_blind_dry_run", {})
    prospective = loaded.get("prospective_package_summary", {})
    fml = loaded.get("fml_matched_summary", {})
    tfr = loaded.get("live_tfr_aggregate", {})
    citation = loaded.get("citation_frontier_probe", {})
    semantic = loaded.get("semantic_frontier_judge", {})
    disagreement = loaded.get("frontier_metric_disagreement", {})

    cases = [
        {
            "id": "ungated_review_text_can_hurt_blind_quality",
            "evidence": {
                "review_guided_wins": _get(model_blind, ["win_counts", "review_guided"]),
                "context_control_wins": _get(model_blind, ["win_counts", "context_control_unrelated_reviews"]),
                "ties": _get(model_blind, ["win_counts", "tie"]),
                "mean_delta": _get(model_blind, ["mean_delta", "mean"]),
                "status": model_blind.get("status"),
            },
            "failure_mechanism": "Raw review text can add noise, overfit to reviewer phrasing, or distract the generator from the original technical frame.",
            "igre_design_implication": "Route reviews into gate-specific actions before regeneration; compare against equal-context controls and blind scoring.",
        },
        {
            "id": "short_budget_fml_does_not_show_copilot_superiority",
            "evidence": {
                "status": fml.get("status"),
                "formal_pair_count": fml.get("formal_pair_count"),
                "claim_implication": fml.get("claim_implication"),
            },
            "failure_mechanism": "Tiny-budget human-gated branch choice can spend attention on plausible but under-tested continuations while autonomous search keeps a stronger local metric path.",
            "igre_design_implication": "Keep benchmark performance and manuscript quality separate; require matched multi-task reruns before claiming superiority.",
        },
        {
            "id": "prospective_packages_are_mixed",
            "evidence": {
                "package_count": prospective.get("package_count"),
                "co_pilot_wins": prospective.get("co_pilot_wins"),
                "autonomous_or_tie_wins": prospective.get("autonomous_or_tie_wins"),
                "total_active_review_minutes": prospective.get("total_active_review_minutes"),
            },
            "failure_mechanism": "Human-selected branches help on some machine-gradeable micro-problems but do not yet generalize to end-to-end AI Scientist-v2 research benchmarks.",
            "igre_design_implication": "Use human gates selectively where evaluator readiness and branch asymmetry are high; do not average controlled micro-task wins into paper-quality claims.",
        },
        {
            "id": "tfr_corrects_model_optimism_without_positive_dvrs",
            "evidence": {
                "executed_case_count": tfr.get("executed_case_count"),
                "same_model_raw_positive_count": tfr.get("same_model_raw_positive_count"),
                "strict_positive_count": tfr.get("strict_positive_count"),
                "cross_model_strict_positive_count": tfr.get("cross_model_strict_positive_count"),
            },
            "failure_mechanism": "Model judges can label guided artifacts as positive even when the preregistered delayed-value condition is not satisfied.",
            "igre_design_implication": "Use deterministic delayed-value rules and cross-model checks before treating future-frontier alignment as evidence.",
        },
        {
            "id": "citation_frontier_alignment_favors_original_context",
            "evidence": {
                "aggregate": citation.get("aggregate"),
                "claim_boundary": citation.get("claim_boundary"),
            },
            "failure_mechanism": "Lexical future-frontier scoring can reward terms already present in the original paper and miss review-induced direction changes.",
            "igre_design_implication": "Treat FAVG and citation probes as diagnostics; add semantic and human frontier judgement before declaring long-horizon alignment.",
        },
        {
            "id": "semantic_frontier_judge_still_finds_zero_delayed_value_cases",
            "evidence": {
                "aggregate": semantic.get("aggregate"),
                "claim_boundary": semantic.get("claim_boundary"),
            },
            "failure_mechanism": "Even a semantic model judge over later-citation metadata can prefer the original paper context when review guidance is generic or underspecified.",
            "igre_design_implication": "Mine and validate delayed-value candidates before expensive replay; generic reviews should not trigger high-cost frontier steering.",
        },
        {
            "id": "frontier_metrics_disagree",
            "evidence": {
                "case_count": disagreement.get("case_count"),
                "metric_win_counts": disagreement.get("metric_win_counts"),
                "disagreement_rate": disagreement.get("disagreement_rate"),
            },
            "failure_mechanism": "Internal paper quality, lexical frontier coverage, vector projection, and direct frontier cosine can reward different trajectory movements.",
            "igre_design_implication": "Do not collapse scientific taste into one scalar reward; report direct similarity, trajectory projection, and orthogonal novelty separately.",
        },
    ]

    for case in cases:
        if any(value is None for value in case["evidence"].values()):
            errors.append(f"incomplete evidence fields for {case['id']}")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "source_files": sources,
        "case_count": len(cases),
        "negative_or_mixed_case_count": len(cases),
        "cases": cases,
        "errors": errors,
        "claim_boundary": (
            "This audit supports failure-mode synthesis and method refinement. "
            "It does not convert mixed or negative evidence into superiority "
            "evidence for Co-Pilot AI Scientist v3."
        ),
    }

    json_path = AUDIT_DIR / "mixed_negative_evidence_audit.json"
    md_path = AUDIT_DIR / "mixed_negative_evidence_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Mixed And Negative Evidence Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Cases: `{audit['case_count']}`",
        "",
        "## Failure Mechanism Map",
        "",
    ]
    for case in cases:
        lines.extend(
            [
                f"### `{case['id']}`",
                "",
                f"- Evidence: `{json.dumps(case['evidence'], ensure_ascii=False)}`",
                f"- Failure mechanism: {case['failure_mechanism']}",
                f"- IGRE design implication: {case['igre_design_implication']}",
                "",
            ]
        )
    lines.extend(["## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
