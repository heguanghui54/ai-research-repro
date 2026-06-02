#!/usr/bin/env python3
"""Build inspectable deep-regeneration case folders from OpenReview probes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
RUN_ID = "deep_regeneration_cases_20260602_203000"
OUT_DIR = EXP_DIR / RUN_ID

SELECTED_IDS = ["openreview_sample_1", "openreview_sample_2", "openreview_sample_17"]

CASE_NOTES = {
    "openreview_sample_1": {
        "case_label": "LLM refusal and reliability",
        "case_type": "mixed_short_term_positive_long_term_negative",
        "why_selected": (
            "Review guidance sharpens the refusal-training mechanism and broadens "
            "evaluation, but current frontier evidence does not show later alignment."
        ),
        "deep_rerun_focus": [
            "Add non-arithmetic refusal benchmarks.",
            "Measure accuracy, rejection precision, rejection recall, calibration, and over-refusal.",
            "Compare with later refusal-policy and user-facing safety evaluation work.",
        ],
    },
    "openreview_sample_2": {
        "case_label": "Conditional graph generation and molecular design",
        "case_type": "frontier_reconstruction_boundary",
        "why_selected": (
            "Review guidance improves motivation and comparison framing, while the "
            "current citation-frontier probe fails to recover a reliable later frontier."
        ),
        "deep_rerun_focus": [
            "Use a low-cost molecular graph benchmark with public evaluators.",
            "Require the review-guided condition to test assumptions and baselines.",
            "Report validity, uniqueness, novelty, property satisfaction, and baseline comparisons.",
        ],
    },
    "openreview_sample_17": {
        "case_label": "Knowledge unlearning and privacy risk",
        "case_type": "strong_frontier_route_candidate",
        "why_selected": (
            "Review guidance surfaces baselines, metrics, and the breaking-point "
            "question for scaling unlearning, which is a concrete later-field route."
        ),
        "deep_rerun_focus": [
            "Run a small unlearning setup with increasing unlearning-set sizes.",
            "Measure forget quality, privacy leakage, retained utility, and baseline gaps.",
            "Compare the generated experiment design with later machine-unlearning and LLM-unlearning benchmarks.",
        ],
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["paper_id"]: item for item in items if item.get("paper_id")}


def _parse_review_snippet(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
    review = parsed.get("review", {})
    compact = {
        "score_fields": {k: v for k, v in parsed.items() if k != "review" and v is not None},
        "paper_summary": review.get("paper_summary"),
        "main_review": review.get("main_review"),
        "limitations": review.get("limitations"),
        "raw": raw,
    }
    return compact


def _short_term_reviews(equal_summary: dict[str, Any], paper_id: str) -> list[dict[str, Any]]:
    rows = []
    for review in equal_summary.get("reviews", []):
        model = review.get("model")
        for item in review.get("per_paper", []):
            if item.get("paper_id") == paper_id:
                rows.append({"model": model, **item})
    return rows


def _frontier_item(frontier_summary: dict[str, Any], paper_id: str) -> dict[str, Any] | None:
    for item in frontier_summary.get("per_paper", []):
        if item.get("paper_id") == paper_id:
            return item
    return None


def _semantic_item(semantic_summary: dict[str, Any], paper_id: str) -> dict[str, Any] | None:
    for item in semantic_summary.get("per_paper", []):
        if item.get("paper_id") == paper_id:
            return item
    return None


def _scores_summary(short_term: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {}
    for row in short_term:
        scores = row.get("scores", {})
        summary[row["model"]] = {
            "winner": row.get("winner"),
            "context_control_overall": scores.get("context_control", {}).get("overall"),
            "review_guided_overall": scores.get("review_guided", {}).get("overall"),
            "specific_review_value": row.get("specific_review_value"),
            "remaining_confounds": row.get("remaining_confounds"),
        }
    return summary


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    selected = _by_id(
        _load_json(EXP_DIR / "openreview_guided_regeneration_probe_20260602_073500" / "selected_papers.json")
    )
    regenerated = _by_id(
        _load_json(EXP_DIR / "openreview_guided_regeneration_probe_20260602_073500" / "regenerated_artifacts.json")[
            "papers"
        ]
    )
    equal_summary = _load_json(EXP_DIR / "openreview_equal_context_ablation_20260602_142000" / "summary.json")
    frontier_summary = _load_json(EXP_DIR / "retrospective_frontier_citation_probe_20260602_213000" / "summary.json")
    semantic_summary = _load_json(EXP_DIR / "semantic_frontier_judge_probe_20260602_223000" / "summary.json")

    cases = []
    for index, paper_id in enumerate(SELECTED_IDS, start=1):
        paper = selected[paper_id]
        regen = regenerated[paper_id]
        short_term = _short_term_reviews(equal_summary, paper_id)
        frontier = _frontier_item(frontier_summary, paper_id)
        semantic = _semantic_item(semantic_summary, paper_id)
        notes = CASE_NOTES[paper_id]

        case_dir = OUT_DIR / f"case_{index:02d}_{paper_id}"
        case_dir.mkdir(parents=True, exist_ok=True)

        parsed_reviews = [_parse_review_snippet(raw) for raw in paper.get("review_snippets", [])]
        original = {
            "paper_id": paper_id,
            "title": paper.get("title"),
            "venue": paper.get("venue"),
            "arxiv_id": paper.get("arxiv_id"),
            "decision": paper.get("decision"),
            "mean_score": paper.get("mean_score"),
            "mean_novelty": paper.get("mean_novelty"),
            "mean_correctness": paper.get("mean_correctness"),
            "mean_clarity": paper.get("mean_clarity"),
            "mean_impact": paper.get("mean_impact"),
            "abstract_excerpt": paper.get("abstract_excerpt"),
            "decision_text_excerpt": paper.get("decision_text_excerpt"),
        }
        _write_json(case_dir / "original_paper.json", original)
        _write_json(case_dir / "human_reviews.json", {"paper_id": paper_id, "reviews": parsed_reviews})
        _write_json(case_dir / "regenerated_artifacts.json", regen)
        _write_json(case_dir / "short_term_scores.json", {"paper_id": paper_id, "reviews": short_term})
        _write_json(
            case_dir / "future_frontier_evidence.json",
            {"paper_id": paper_id, "citation_frontier": frontier, "semantic_frontier": semantic},
        )

        _write_md(
            case_dir / "original_paper.md",
            [
                f"# Original Paper: {paper.get('title')}",
                "",
                f"- Paper ID: `{paper_id}`",
                f"- Venue/source: `{paper.get('venue')}`",
                f"- arXiv: `{paper.get('arxiv_id') or 'not available'}`",
                f"- Decision: `{paper.get('decision')}`",
                f"- Mean score: `{paper.get('mean_score')}`",
                "",
                "## Abstract Excerpt",
                "",
                paper.get("abstract_excerpt") or "",
                "",
                "## Decision Excerpt",
                "",
                paper.get("decision_text_excerpt") or "",
            ],
        )

        review_lines = [f"# Human Reviews: {paper.get('title')}", ""]
        for review_index, parsed in enumerate(parsed_reviews, start=1):
            review_lines.extend(
                [
                    f"## Review {review_index}",
                    "",
                    f"- Score fields: `{json.dumps(parsed.get('score_fields', {}), ensure_ascii=False)}`",
                    "",
                    "### Paper Summary",
                    "",
                    parsed.get("paper_summary") or "(not available)",
                    "",
                    "### Main Review",
                    "",
                    parsed.get("main_review") or "(not available in compact extract)",
                    "",
                    "### Limitations",
                    "",
                    parsed.get("limitations") or "(not available in compact extract)",
                    "",
                ]
            )
        _write_md(case_dir / "human_reviews.md", review_lines)

        baseline = regen.get("baseline_regeneration", {})
        guided = regen.get("review_guided_regeneration", {})
        _write_md(
            case_dir / "regenerated_artifacts.md",
            [
                f"# Regenerated Artifacts: {paper.get('title')}",
                "",
                "## Paper-Only / Baseline Artifact",
                "",
                f"**Core contribution:** {baseline.get('core_contribution')}",
                "",
                f"**Method sketch:** {baseline.get('method_sketch')}",
                "",
                f"**Experiment plan:** {baseline.get('experiment_plan')}",
                "",
                f"**Limitations:** {baseline.get('limitations')}",
                "",
                f"**Claim boundary:** {baseline.get('claim_boundary')}",
                "",
                baseline.get("mini_paper_artifact") or "",
                "",
                "## Review-Guided Artifact",
                "",
                "Review insights used:",
                "",
                *[f"- {insight}" for insight in guided.get("review_insights_used", [])],
                "",
                f"**Core contribution:** {guided.get('core_contribution')}",
                "",
                f"**Method sketch:** {guided.get('method_sketch')}",
                "",
                f"**Experiment plan:** {guided.get('experiment_plan')}",
                "",
                f"**Limitations:** {guided.get('limitations')}",
                "",
                f"**Claim boundary:** {guided.get('claim_boundary')}",
                "",
                guided.get("mini_paper_artifact") or "",
            ],
        )

        score_summary = _scores_summary(short_term)
        score_lines = [f"# Short-Term Scores: {paper.get('title')}", ""]
        for model, row in score_summary.items():
            score_lines.extend(
                [
                    f"## {model}",
                    "",
                    f"- Winner: `{row.get('winner')}`",
                    f"- Context-control overall: `{row.get('context_control_overall')}`",
                    f"- Review-guided overall: `{row.get('review_guided_overall')}`",
                    f"- Specific review value: {row.get('specific_review_value')}",
                    f"- Remaining confounds: {row.get('remaining_confounds')}",
                    "",
                ]
            )
        _write_md(case_dir / "short_term_scores.md", score_lines)

        frontier = frontier or {}
        temporal = frontier.get("temporal_diagnostic", {})
        semantic_judgement = (semantic or {}).get("judgement", {})
        _write_md(
            case_dir / "future_frontier_evidence.md",
            [
                f"# Future Frontier Evidence: {paper.get('title')}",
                "",
                "## Citation / Lexical Frontier Probe",
                "",
                f"- Winner: `{frontier.get('winner')}`",
                f"- Frontier quality: `{frontier.get('frontier_quality')}`",
                f"- Citation count used: `{frontier.get('citation_count_used')}`",
                f"- Frontier terms: `{', '.join(frontier.get('frontier_terms', []))}`",
                f"- Temporal pattern: `{temporal.get('pattern')}`",
                f"- Short-term review-guided minus paper-only: `{temporal.get('short_term_review_guided_minus_paper_only')}`",
                f"- Long-term frontier review-guided minus paper-only: `{temporal.get('long_term_frontier_review_guided_minus_paper_only')}`",
                "",
                "## Semantic Frontier Judge",
                "",
                f"- Status: `{(semantic or {}).get('status')}`",
                f"- Winner: `{semantic_judgement.get('winner')}`",
                f"- Latent delayed-value candidate: `{semantic_judgement.get('latent_delayed_value_candidate')}`",
                f"- Derived temporal pattern: `{(semantic or {}).get('derived_temporal_pattern')}`",
                f"- Reason: {semantic_judgement.get('reason')}",
            ],
        )

        case_summary = {
            "paper_id": paper_id,
            "case_label": notes["case_label"],
            "case_type": notes["case_type"],
            "title": paper.get("title"),
            "short_term_scores": score_summary,
            "citation_frontier_winner": frontier.get("winner"),
            "citation_temporal_pattern": temporal.get("pattern"),
            "semantic_frontier_winner": semantic_judgement.get("winner"),
            "latent_delayed_value_candidate": semantic_judgement.get("latent_delayed_value_candidate"),
            "why_selected": notes["why_selected"],
            "deep_rerun_focus": notes["deep_rerun_focus"],
        }
        _write_json(case_dir / "case_summary.json", case_summary)
        _write_md(
            case_dir / "case_analysis.md",
            [
                f"# Case Analysis: {notes['case_label']}",
                "",
                f"- Paper ID: `{paper_id}`",
                f"- Case type: `{notes['case_type']}`",
                f"- Title: {paper.get('title')}",
                "",
                "## Why This Case Was Selected",
                "",
                notes["why_selected"],
                "",
                "## Current Evidence Boundary",
                "",
                "This folder is an inspectable pilot replay case. It does not prove a full deep rerun, "
                "does not reproduce the original paper's full experiments, and does not establish a "
                "validated delayed-value positive case unless the explicit frontier evidence says so.",
                "",
                "## Deep Rerun Focus",
                "",
                *[f"- {item}" for item in notes["deep_rerun_focus"]],
            ],
        )
        cases.append({"case_dir": _rel(case_dir), **case_summary})

    summary = {
        "run_id": RUN_ID,
        "created_at": _utc_now(),
        "status": "pilot_deep_case_package_built_from_existing_openreview_probes",
        "case_count": len(cases),
        "cases": cases,
        "source_artifacts": [
            _rel(EXP_DIR / "openreview_guided_regeneration_probe_20260602_073500" / "selected_papers.json"),
            _rel(EXP_DIR / "openreview_guided_regeneration_probe_20260602_073500" / "regenerated_artifacts.json"),
            _rel(EXP_DIR / "openreview_equal_context_ablation_20260602_142000" / "summary.json"),
            _rel(EXP_DIR / "retrospective_frontier_citation_probe_20260602_213000" / "summary.json"),
            _rel(EXP_DIR / "semantic_frontier_judge_probe_20260602_223000" / "summary.json"),
        ],
        "claim_boundary": (
            "The package exposes three concrete replay candidates with original papers, "
            "review guidance, regenerated artifacts, short-term scores, and frontier evidence. "
            "It is a deep-case scaffold, not completed large-scale historical reproduction."
        ),
    }
    _write_json(OUT_DIR / "summary.json", summary)
    lines = [
        "# Deep Regeneration Cases",
        "",
        f"- Run ID: `{RUN_ID}`",
        f"- Status: `{summary['status']}`",
        f"- Case count: `{len(cases)}`",
        "",
        "## Cases",
        "",
    ]
    for case in cases:
        lines.extend(
            [
                f"### {case['case_label']}",
                "",
                f"- Paper ID: `{case['paper_id']}`",
                f"- Title: {case['title']}",
                f"- Case type: `{case['case_type']}`",
                f"- Case folder: `{case['case_dir']}`",
                f"- Citation temporal pattern: `{case.get('citation_temporal_pattern')}`",
                f"- Semantic frontier winner: `{case.get('semantic_frontier_winner')}`",
                "",
            ]
        )
    lines.extend(["## Claim Boundary", "", summary["claim_boundary"], ""])
    _write_md(OUT_DIR / "README.md", lines)

    print(json.dumps({"run_id": RUN_ID, "summary": _rel(OUT_DIR / "summary.json"), "cases": len(cases)}, indent=2))


if __name__ == "__main__":
    main()
