#!/usr/bin/env python3
"""Build a triage package for expensive delayed-value deep replay cases."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
RUN_ID = "delayed_value_deep_case_triage_20260602_232000"
OUT_DIR = EXP_DIR / RUN_ID

MINING_RUN = EXP_DIR / "delayed_value_review_candidate_mining_20260603_001500"
VALIDATION_RUN = EXP_DIR / "delayed_value_candidate_frontier_validation_20260603_011500"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _norm(value: float | int | None, scale: float) -> float:
    if value is None or scale <= 0:
        return 0.0
    return max(0.0, min(float(value) / scale, 1.0))


def _case_score(item: dict[str, Any], mined: dict[str, Any] | None) -> tuple[float, dict[str, float]]:
    review_signal = item.get("review_signal") or {}
    label = item.get("candidate_label")
    gates = set(item.get("primary_gates") or (mined or {}).get("primary_gates") or [])
    long_groups = set(_groups(mined, "long_horizon"))
    friction_groups = set(_groups(mined, "short_term_friction"))
    matched_frontier = review_signal.get("matched_frontier_terms") or []
    matched_actionability = review_signal.get("matched_actionability_terms") or []

    title_overlap = float(item.get("title_token_overlap") or 0.0)
    cited_by = float(item.get("openalex_cited_by_count") or 0.0)
    review_minus_title = float(item.get("review_minus_title_score") or 0.0)
    review_score = float(review_signal.get("score") or 0.0)
    delayed_score = float(item.get("delayed_candidate_score") or (mined or {}).get("delayed_candidate_score") or 0.0)
    long_score = float((mined or {}).get("long_horizon_score") or 0.0)
    asymmetry = float((mined or {}).get("temporal_asymmetry_score") or 0.0)

    components = {
        "label_priority": {
            "delayed_value_replay_candidate": 1.0,
            "long_horizon_positive_candidate": 0.85,
            "generic_or_unrouted": 0.35,
            "short_term_repair_signal": 0.2,
        }.get(str(label), 0.0),
        "frontier_validation": _norm(review_score, 0.5),
        "review_over_title": max(0.0, min(review_minus_title / 0.28, 1.0)),
        "mining_strength": _norm(delayed_score, 6.0),
        "long_horizon_density": _norm(long_score, 3.0),
        "temporal_asymmetry": _norm(asymmetry, 2.5),
        "gate_coverage": min(len(gates & {"scientific_taste_prior", "evaluator_stress_test", "frontier_steering", "claim_calibration"}) / 3.0, 1.0),
        "frontier_term_count": min(len(matched_frontier) / 5.0, 1.0),
        "actionability_terms": min(len(matched_actionability) / 2.0, 1.0),
        "openalex_match": 1.0 if title_overlap >= 0.8 else 0.0,
        "citation_trace": min(cited_by / 10.0, 1.0),
        "productive_friction": min(len(friction_groups & {"weak_immediate_evidence", "missing_evaluation", "presentation_or_claim_friction"}) / 2.0, 1.0),
        "mechanism_or_frontier_group": 1.0 if long_groups & {"mechanism_depth", "frontier_direction", "generalization_scaling"} else 0.0,
    }
    weights = {
        "label_priority": 1.4,
        "frontier_validation": 1.2,
        "review_over_title": 1.4,
        "mining_strength": 1.0,
        "long_horizon_density": 0.8,
        "temporal_asymmetry": 0.6,
        "gate_coverage": 0.9,
        "frontier_term_count": 0.7,
        "actionability_terms": 0.7,
        "openalex_match": 0.9,
        "citation_trace": 0.4,
        "productive_friction": 0.4,
        "mechanism_or_frontier_group": 0.6,
    }
    raw = sum(components[key] * weights[key] for key in weights)
    match_penalty = 0.0 if title_overlap >= 0.8 else 1.75
    if item.get("status") != "scored":
        match_penalty += 1.0
    score = raw - match_penalty
    return round(score, 4), {key: round(value, 4) for key, value in components.items()}


def _why_selected(item: dict[str, Any], mined: dict[str, Any] | None) -> list[str]:
    reasons: list[str] = []
    review_signal = item.get("review_signal") or {}
    if item.get("candidate_label") in {"delayed_value_replay_candidate", "long_horizon_positive_candidate"}:
        reasons.append(f"screened as {item.get('candidate_label')}")
    if float(item.get("review_minus_title_score") or 0.0) > 0:
        reasons.append(
            f"review adds frontier signal over title/context by {float(item.get('review_minus_title_score') or 0.0):.2f}"
        )
    if review_signal.get("matched_frontier_terms"):
        terms = ", ".join(review_signal["matched_frontier_terms"][:6])
        reasons.append(f"matches future-frontier terms: {terms}")
    if review_signal.get("matched_actionability_terms"):
        terms = ", ".join(review_signal["matched_actionability_terms"][:4])
        reasons.append(f"contains actionability terms: {terms}")
    long_groups = _groups(mined, "long_horizon")
    friction_groups = _groups(mined, "short_term_friction")
    if long_groups:
        reasons.append("long-horizon groups: " + ", ".join(long_groups))
    if friction_groups:
        reasons.append("productive short-term friction: " + ", ".join(friction_groups))
    if float(item.get("title_token_overlap") or 0.0) >= 0.8:
        reasons.append("OpenAlex title match is exact or near-exact")
    return reasons


def _groups(item: dict[str, Any] | None, kind: str) -> list[str]:
    if not item:
        return []
    if kind == "long_horizon":
        explicit = item.get("long_horizon_groups")
        hits = item.get("long_horizon_hits")
    else:
        explicit = item.get("friction_groups")
        hits = item.get("short_term_friction_hits")
    if explicit:
        return list(explicit)
    if isinstance(hits, dict):
        return [key for key, values in hits.items() if values]
    return []


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mined_reviews = _load_json(MINING_RUN / "candidate_reviews.json")
    validation_items = _load_json(VALIDATION_RUN / "per_item.json")
    mining_summary = _load_json(MINING_RUN / "summary.json")
    validation_summary = _load_json(VALIDATION_RUN / "summary.json")

    mined_by_id = {item["review_id"]: item for item in mined_reviews}
    ranked = []
    for item in validation_items:
        mined = mined_by_id.get(item.get("review_id"))
        score, components = _case_score(item, mined)
        record = {
            "rank": None,
            "triage_score": score,
            "score_components": components,
            "review_id": item.get("review_id"),
            "paper_index": item.get("paper_index"),
            "title": item.get("title"),
            "candidate_label": item.get("candidate_label"),
            "status": item.get("status"),
            "decision": item.get("decision"),
            "mean_score": item.get("mean_score"),
            "delayed_candidate_score": item.get("delayed_candidate_score") or (mined or {}).get("delayed_candidate_score"),
            "long_horizon_score": (mined or {}).get("long_horizon_score"),
            "temporal_asymmetry_score": (mined or {}).get("temporal_asymmetry_score"),
            "openalex_id": item.get("openalex_id"),
            "openalex_year": item.get("openalex_year"),
            "openalex_cited_by_count": item.get("openalex_cited_by_count"),
            "title_token_overlap": item.get("title_token_overlap"),
            "review_signal": item.get("review_signal"),
            "title_signal": item.get("title_signal"),
            "review_minus_title_score": item.get("review_minus_title_score"),
            "primary_gates": item.get("primary_gates") or (mined or {}).get("primary_gates"),
            "actionable_categories": (mined or {}).get("actionable_categories"),
            "long_horizon_groups": _groups(mined, "long_horizon"),
            "friction_groups": _groups(mined, "short_term_friction"),
            "excerpt": (mined or {}).get("excerpt"),
            "selection_reasons": _why_selected(item, mined),
        }
        ranked.append(record)

    ranked.sort(key=lambda x: (x["triage_score"], float(x.get("review_minus_title_score") or 0.0)), reverse=True)
    for i, item in enumerate(ranked, start=1):
        item["rank"] = i

    selected = ranked[:3]
    deferred = ranked[3:]
    label_counts: dict[str, int] = {}
    for item in selected:
        label = str(item.get("candidate_label"))
        label_counts[label] = label_counts.get(label, 0) + 1

    summary = {
        "run_id": RUN_ID,
        "timestamp_utc": _utc_now(),
        "status": "deep_case_triage_only",
        "candidate_source": _rel(MINING_RUN / "candidate_reviews.json"),
        "frontier_validation_source": _rel(VALIDATION_RUN / "per_item.json"),
        "input_review_count": mining_summary.get("aggregate", {}).get("review_count"),
        "input_paper_count": mining_summary.get("aggregate", {}).get("paper_count"),
        "validated_candidate_count": len(validation_items),
        "ranked_candidate_count": len(ranked),
        "selected_case_count": len(selected),
        "selected_label_counts": label_counts,
        "mean_selected_triage_score": round(sum(item["triage_score"] for item in selected) / len(selected), 4),
        "mean_selected_review_minus_title_score": round(
            sum(float(item.get("review_minus_title_score") or 0.0) for item in selected) / len(selected), 4
        ),
        "selected_cases": [
            {
                "rank": item["rank"],
                "review_id": item["review_id"],
                "title": item["title"],
                "candidate_label": item["candidate_label"],
                "triage_score": item["triage_score"],
                "review_minus_title_score": item["review_minus_title_score"],
                "openalex_cited_by_count": item["openalex_cited_by_count"],
                "primary_gates": item["primary_gates"],
                "long_horizon_groups": item["long_horizon_groups"],
                "friction_groups": item["friction_groups"],
                "selection_reasons": item["selection_reasons"],
            }
            for item in selected
        ],
        "source_aggregate": {
            "candidate_mining": mining_summary.get("aggregate", {}),
            "frontier_validation": validation_summary.get("aggregate", {}),
        },
        "ranking_rule": {
            "positive_terms": [
                "delayed or long-horizon candidate label",
                "review frontier signal stronger than title-only signal",
                "frontier/actionability terms in the review",
                "scientific taste, evaluator stress, frontier, or claim-calibration gate coverage",
                "exact or near-exact OpenAlex match",
                "productive short-term friction coupled to long-horizon groups",
            ],
            "penalties": [
                "possible OpenAlex match drift",
                "unscored candidate",
            ],
        },
        "claim_boundary": (
            "This artifact selects the next expensive deep replay cases. It does not claim that "
            "the reviews caused future progress or that review-guided regeneration improves the "
            "original papers. Each selected case still requires paper-only, raw-review-guided, "
            "six-gate-hybrid-guided, and shuffled-review-control regeneration plus short-term "
            "and future-frontier judging."
        ),
    }

    (OUT_DIR / "selected_cases.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "ranked_candidates.json").write_text(json.dumps(ranked, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "deferred_candidates.json").write_text(json.dumps(deferred, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Delayed-Value Deep Case Triage",
        "",
        f"- Run ID: `{RUN_ID}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Candidate source: `{summary['candidate_source']}`",
        f"- Frontier validation source: `{summary['frontier_validation_source']}`",
        f"- Ranked candidates: `{summary['ranked_candidate_count']}`",
        f"- Selected cases: `{summary['selected_case_count']}`",
        f"- Mean selected triage score: `{summary['mean_selected_triage_score']}`",
        f"- Mean selected review-title delta: `{summary['mean_selected_review_minus_title_score']}`",
        "",
        "## Why This Artifact Exists",
        "",
        "The paper argues that human taste and insight often matter most when they redirect a research trajectory, not when they merely optimize the next local score. Existing probes already mine delayed-value review candidates and compare their review text with later frontier terms. This triage package turns those probes into an explicit queue for expensive Temporal Frontier Replay.",
        "",
        "## Selected Deep Replay Cases",
        "",
        "| Rank | Review ID | Label | Triage | Review-title delta | Citations | Title |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for item in selected:
        lines.append(
            f"| {item['rank']} | `{item['review_id']}` | `{item['candidate_label']}` | "
            f"{item['triage_score']} | {item.get('review_minus_title_score')} | "
            f"{item.get('openalex_cited_by_count')} | {item['title']} |"
        )
    lines.extend(["", "## Case Rationales", ""])
    for item in selected:
        lines.append(f"### {item['rank']}. {item['title']}")
        lines.append("")
        lines.append(f"- Review ID: `{item['review_id']}`")
        lines.append(f"- Primary gates: `{', '.join(item.get('primary_gates') or [])}`")
        lines.append(f"- Long-horizon groups: `{', '.join(item.get('long_horizon_groups') or [])}`")
        lines.append(f"- Productive friction: `{', '.join(item.get('friction_groups') or [])}`")
        lines.append("- Selection reasons:")
        for reason in item["selection_reasons"]:
            lines.append(f"  - {reason}")
        lines.append("")
        lines.append("Excerpt:")
        lines.append("")
        lines.append(f"> {(item.get('excerpt') or '')[:700]}")
        lines.append("")
    lines.extend(
        [
            "## Ranking Rule",
            "",
            "The ranking combines candidate-mining strength, review-over-title frontier signal, gate coverage, long-horizon density, OpenAlex match quality, citation trace, and productive short-term friction. It penalizes possible bibliographic match drift and unscored candidates.",
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
            "",
        ]
    )
    (OUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({"run_id": RUN_ID, "summary": _rel(OUT_DIR / "summary.json"), "selected": len(selected)}, indent=2))


if __name__ == "__main__":
    main()
