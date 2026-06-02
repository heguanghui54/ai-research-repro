#!/usr/bin/env python3
"""Audit the Temporal Frontier Replay protocol and archived probe outputs."""

from __future__ import annotations

import json
import math
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


def _binomial_two_sided(successes: int, trials: int, p: float = 0.5) -> float | None:
    if trials <= 0:
        return None
    observed = math.comb(trials, successes) * (p**successes) * ((1 - p) ** (trials - successes))
    total = 0.0
    for k in range(trials + 1):
        prob = math.comb(trials, k) * (p**k) * ((1 - p) ** (trials - k))
        if prob <= observed + 1e-15:
            total += prob
    return min(1.0, total)


def _winner_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        winner = str(item.get("winner", "missing"))
        counts[winner] = counts.get(winner, 0) + 1
    return counts


def _pattern_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        pattern = str((item.get("temporal_diagnostic") or {}).get("pattern", "missing"))
        counts[pattern] = counts.get(pattern, 0) + 1
    return counts


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    spec_path = DOC_DIR / "temporal_frontier_replay_spec.json"
    protocol_path = DOC_DIR / "retrospective_frontier_alignment_protocol.json"
    smoke_path = DOC_DIR / "experiments" / "retrospective_frontier_alignment_smoke_20260602_160000" / "summary.json"
    citation_path = DOC_DIR / "experiments" / "retrospective_frontier_citation_probe_20260602_213000" / "summary.json"
    review_signal_path = DOC_DIR / "experiments" / "review_frontier_signal_probe_20260602_214500" / "summary.json"
    semantic_path = DOC_DIR / "experiments" / "semantic_frontier_judge_probe_20260602_223000" / "summary.json"
    candidate_path = (
        DOC_DIR
        / "experiments"
        / "delayed_value_review_candidate_mining_20260603_001500"
        / "summary.json"
    )
    validation_path = (
        DOC_DIR
        / "experiments"
        / "delayed_value_candidate_frontier_validation_20260603_011500"
        / "summary.json"
    )
    triage_path = (
        DOC_DIR
        / "experiments"
        / "delayed_value_deep_case_triage_20260602_232000"
        / "summary.json"
    )

    errors: list[str] = []
    warnings: list[str] = []

    required_paths = [
        spec_path,
        protocol_path,
        smoke_path,
        citation_path,
        review_signal_path,
        semantic_path,
        candidate_path,
        validation_path,
        triage_path,
    ]
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing required artifact: {_rel(path)}")

    if errors:
        audit = {
            "audit_date": _utc_now(),
            "status": "fail",
            "errors": errors,
            "warnings": warnings,
        }
    else:
        spec = _load_json(spec_path)
        protocol = _load_json(protocol_path)
        smoke = _load_json(smoke_path)
        citation = _load_json(citation_path)
        review_signal = _load_json(review_signal_path)
        semantic = _load_json(semantic_path)
        candidate_mining = _load_json(candidate_path)
        candidate_validation = _load_json(validation_path)
        deep_case_triage = _load_json(triage_path)

        for condition in ["paper_only", "review_guided", "shuffled_review_control"]:
            if condition not in spec.get("required_conditions", []):
                errors.append(f"spec missing required condition: {condition}")
            if condition not in protocol.get("conditions", []):
                errors.append(f"protocol missing required condition: {condition}")

        delayed_def = spec.get("delayed_value_review_signal", {})
        for key in [
            "short_term_condition",
            "frontier_condition",
            "control_condition",
            "review_condition",
            "validity_condition",
        ]:
            if key not in delayed_def:
                errors.append(f"delayed-value definition missing: {key}")

        smoke_items = smoke.get("per_paper", [])
        smoke_winners = _winner_counts(smoke_items)
        smoke_patterns = _pattern_counts(smoke_items)
        smoke_agg = smoke.get("aggregate", smoke)
        citation_agg = citation.get("aggregate", citation)
        review_agg = review_signal.get("aggregate", review_signal)
        semantic_agg = semantic.get("aggregate", semantic)

        citation_wins = citation_agg.get("winner_counts", {})
        review_guided_wins = int(citation_wins.get("review_guided", 0))
        paper_only_wins = int(citation_wins.get("paper_only", 0))
        shuffled_wins = int(citation_wins.get("shuffled_review_control", 0))
        non_tie_paper_only_trials = review_guided_wins + paper_only_wins
        non_tie_control_trials = review_guided_wins + shuffled_wins

        delayed_cases = int(citation_agg.get("delayed_value_case_count", 0))
        semantic_delayed_cases = int(semantic_agg.get("latent_delayed_value_candidate_count", 0))
        review_delayed_cases = int(review_agg.get("latent_delayed_value_candidate_count", 0))

        if delayed_cases == 0 and semantic_delayed_cases == 0 and review_delayed_cases == 0:
            warnings.append("No delayed-value review signal is found in the current archived TFR probes.")

        if int(citation_agg.get("citation_count_after_relevance_filter", 0)) < 50:
            warnings.append("Citation-backed future-frontier evidence is still thin for strong claims.")

        status = "fail" if errors else "pass_with_negative_delayed_value_evidence"
        audit = {
            "audit_date": _utc_now(),
            "status": status,
            "spec": _rel(spec_path),
            "protocol": _rel(protocol_path),
            "inputs_present": {
                "deterministic_smoke": _rel(smoke_path),
                "citation_backed_probe": _rel(citation_path),
                "review_frontier_signal_probe": _rel(review_signal_path),
                "semantic_frontier_judge_probe": _rel(semantic_path),
                "delayed_value_candidate_mining": _rel(candidate_path),
                "delayed_value_candidate_frontier_validation": _rel(validation_path),
                "delayed_value_deep_case_triage": _rel(triage_path),
            },
            "required_conditions_present": not errors,
            "delayed_value_definition_complete": not any(
                error.startswith("delayed-value definition missing") for error in errors
            ),
            "deterministic_smoke": {
                "paper_count": smoke_agg.get("paper_count", len(smoke_items)),
                "winner_counts": smoke_agg.get("winner_counts", smoke_winners),
                "review_guided_wins": smoke_agg.get("review_guided_wins", smoke_winners.get("review_guided", 0)),
                "shuffled_control_wins": smoke_agg.get(
                    "shuffled_control_wins", smoke_winners.get("shuffled_review_control", 0)
                ),
                "delayed_value_case_count": smoke_agg.get(
                    "delayed_value_case_count", smoke_patterns.get("delayed_value_candidate", 0)
                ),
                "short_term_positive_long_term_negative_count": smoke_agg.get(
                    "short_term_positive_long_term_negative_count",
                    smoke_patterns.get("short_term_positive_long_term_negative", 0),
                ),
            },
            "citation_backed_probe": {
                "paper_count": citation_agg.get("paper_count"),
                "papers_with_retrieved_citations": citation_agg.get("papers_with_retrieved_citations"),
                "relevance_filtered_citations": citation_agg.get("citation_count_after_relevance_filter"),
                "possible_match_drift_papers": citation_agg.get("possible_match_drift_papers"),
                "winner_counts": citation_wins,
                "delayed_value_case_count": delayed_cases,
                "short_term_positive_long_term_negative_count": citation_agg.get(
                    "short_term_positive_long_term_negative_count"
                ),
                "review_guided_vs_paper_only_exact_sign_test_p": _binomial_two_sided(
                    review_guided_wins, non_tie_paper_only_trials
                ),
                "review_guided_vs_shuffled_control_exact_sign_test_p": _binomial_two_sided(
                    review_guided_wins, non_tie_control_trials
                ),
            },
            "review_frontier_signal_probe": {
                "review_snippet_count": review_agg.get("review_snippet_count"),
                "review_beats_paper_context_count": review_agg.get("review_beats_paper_context_count"),
                "latent_delayed_value_candidate_count": review_delayed_cases,
            },
            "semantic_frontier_judge_probe": {
                "successful_judgements": semantic_agg.get("successful_judgements"),
                "winner_counts": semantic_agg.get("winner_counts"),
                "latent_delayed_value_candidate_count": semantic_delayed_cases,
                "mean_scores": semantic_agg.get("mean_scores"),
            },
            "delayed_value_candidate_mining": {
                "review_count": candidate_mining.get("aggregate", {}).get("review_count"),
                "paper_count": candidate_mining.get("aggregate", {}).get("paper_count"),
                "delayed_value_replay_candidate_count": candidate_mining.get("aggregate", {}).get(
                    "delayed_value_replay_candidate_count"
                ),
                "candidate_rate": candidate_mining.get("aggregate", {}).get("candidate_rate"),
                "long_horizon_positive_candidate_count": candidate_mining.get("aggregate", {}).get(
                    "long_horizon_positive_candidate_count"
                ),
                "short_term_repair_signal_count": candidate_mining.get("aggregate", {}).get(
                    "short_term_repair_signal_count"
                ),
                "claim_boundary": candidate_mining.get("claim_boundary"),
            },
            "delayed_value_candidate_frontier_validation": {
                "attempted_count": candidate_validation.get("aggregate", {}).get("attempted_count"),
                "scored_count": candidate_validation.get("aggregate", {}).get("scored_count"),
                "not_scored_count": candidate_validation.get("aggregate", {}).get("not_scored_count"),
                "delayed_candidate_mean_review_signal_score": candidate_validation.get("aggregate", {}).get(
                    "delayed_candidate_mean_review_signal_score"
                ),
                "control_mean_review_signal_score": candidate_validation.get("aggregate", {}).get(
                    "control_mean_review_signal_score"
                ),
                "delayed_minus_control_mean_score": candidate_validation.get("aggregate", {}).get(
                    "delayed_minus_control_mean_score"
                ),
                "claim_boundary": candidate_validation.get("claim_boundary"),
            },
            "delayed_value_deep_case_triage": {
                "selected_case_count": deep_case_triage.get("selected_case_count"),
                "mean_selected_triage_score": deep_case_triage.get("mean_selected_triage_score"),
                "mean_selected_review_minus_title_score": deep_case_triage.get(
                    "mean_selected_review_minus_title_score"
                ),
                "selected_cases": deep_case_triage.get("selected_cases", []),
                "claim_boundary": deep_case_triage.get("claim_boundary"),
            },
            "claim_boundary": (
                "TFR is operationalized and auditable, but the archived probes are negative for "
                "delayed-value human-review evidence. Candidate mining can prioritize which "
                "historical comments should enter expensive replay, a small OpenAlex validation "
                "shows weak positive candidate-vs-control frontier alignment, and the deep-case "
                "triage queue now selects three concrete cases for future expensive replay. These "
                "candidates are still not positive delayed-value cases until paper-only, "
                "raw-review-guided, six-gate-hybrid-guided, and shuffled controls are judged "
                "against later frontier evidence."
            ),
            "errors": errors,
            "warnings": warnings,
        }

    json_path = AUDIT_DIR / "temporal_frontier_replay_audit.json"
    md_path = AUDIT_DIR / "temporal_frontier_replay_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Temporal Frontier Replay Audit",
        "",
        f"Audit date: `{audit['audit_date']}`",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Summary",
        "",
        f"- Spec: `{audit.get('spec', 'missing')}`",
        f"- Protocol: `{audit.get('protocol', 'missing')}`",
        f"- Required replay conditions present: `{audit.get('required_conditions_present', False)}`",
        f"- Delayed-value definition complete: `{audit.get('delayed_value_definition_complete', False)}`",
    ]
    if "citation_backed_probe" in audit:
        citation = audit["citation_backed_probe"]
        semantic = audit["semantic_frontier_judge_probe"]
        review = audit["review_frontier_signal_probe"]
        candidates = audit["delayed_value_candidate_mining"]
        validation = audit["delayed_value_candidate_frontier_validation"]
        triage = audit["delayed_value_deep_case_triage"]
        lines.extend(
            [
                "",
                "## Archived Probe Results",
                "",
                f"- Citation-backed papers: `{citation['paper_count']}`",
                f"- Relevance-filtered later citations: `{citation['relevance_filtered_citations']}`",
                f"- Citation delayed-value cases: `{citation['delayed_value_case_count']}`",
                f"- Citation short-term-positive/long-term-negative cases: `{citation['short_term_positive_long_term_negative_count']}`",
                f"- Review snippets scored: `{review['review_snippet_count']}`",
                f"- Review snippets beating paper context: `{review['review_beats_paper_context_count']}`",
                f"- Semantic successful judgements: `{semantic['successful_judgements']}`",
                f"- Semantic winner counts: `{semantic['winner_counts']}`",
                f"- Semantic delayed-value candidates: `{semantic['latent_delayed_value_candidate_count']}`",
                "",
                "## Candidate Mining",
                "",
                f"- Reviews screened: `{candidates['review_count']}`",
                f"- Papers screened: `{candidates['paper_count']}`",
                f"- Delayed-value replay candidates: `{candidates['delayed_value_replay_candidate_count']}`",
                f"- Candidate rate: `{candidates['candidate_rate']}`",
                f"- Long-horizon positive candidates: `{candidates['long_horizon_positive_candidate_count']}`",
                f"- Short-term repair signals: `{candidates['short_term_repair_signal_count']}`",
                "",
                "## Candidate Frontier Validation",
                "",
                f"- Attempted reviews: `{validation['attempted_count']}`",
                f"- Scored reviews: `{validation['scored_count']}`",
                f"- Not scored after match-drift guard: `{validation['not_scored_count']}`",
                f"- Delayed-candidate mean review signal: `{validation['delayed_candidate_mean_review_signal_score']}`",
                f"- Control mean review signal: `{validation['control_mean_review_signal_score']}`",
                f"- Delayed minus control mean score: `{validation['delayed_minus_control_mean_score']}`",
                "",
                "## Deep Case Triage",
                "",
                f"- Selected cases: `{triage['selected_case_count']}`",
                f"- Mean selected triage score: `{triage['mean_selected_triage_score']}`",
                f"- Mean selected review-title delta: `{triage['mean_selected_review_minus_title_score']}`",
            ]
        )
        for case in triage.get("selected_cases", []):
            lines.append(
                f"- `{case['review_id']}` `{case['candidate_label']}` triage `{case['triage_score']}`: {case['title']}"
            )
        lines.extend(
            [
                "",
                "## Claim Boundary",
                "",
                audit["claim_boundary"],
            ]
        )
    if audit.get("warnings"):
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in audit["warnings"])
    if audit.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in audit["errors"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))


if __name__ == "__main__":
    main()
