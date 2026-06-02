#!/usr/bin/env python3
"""Render deep-regeneration case mini-paper artifacts as PDFs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from build_copilot_v3_pdfs import build_pdf


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
BUILD_DIR = DOC_DIR / "build" / "deep_regeneration_cases"
DEEP_RUN = EXP_DIR / "deep_regeneration_cases_20260602_203000"
HYBRID_RUN = EXP_DIR / "six_gate_hybrid_review_cases_20260602_211500"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_md(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _slug(text: str) -> str:
    keep = []
    for char in text.lower():
        if char.isalnum():
            keep.append(char)
        elif keep and keep[-1] != "_":
            keep.append("_")
    return "".join(keep).strip("_")[:80]


def _review_guided_markdown(case_dir: Path, out_md: Path) -> None:
    original = _load_json(case_dir / "original_paper.json")
    reviews = _load_json(case_dir / "human_reviews.json")
    regen = _load_json(case_dir / "regenerated_artifacts.json")
    scores = _load_json(case_dir / "short_term_scores.json")
    frontier = _load_json(case_dir / "future_frontier_evidence.json")
    guided = regen.get("review_guided_regeneration", {})
    baseline = regen.get("baseline_regeneration", {})

    lines = [
        f"# Review-Guided Mini-Paper: {original.get('title')}",
        "",
        "## Source Paper",
        "",
        f"- Paper ID: `{original.get('paper_id')}`",
        f"- Venue/source: `{original.get('venue')}`",
        f"- arXiv: `{original.get('arxiv_id') or 'not available'}`",
        f"- Original mean score: `{original.get('mean_score')}`",
        "",
        "## Human Review Guidance Used",
        "",
    ]
    for insight in guided.get("review_insights_used", []):
        lines.append(f"- {insight}")
    lines.extend(["", "## Review Evidence Excerpts", ""])
    for index, review in enumerate(reviews.get("reviews", [])[:3], start=1):
        summary = review.get("paper_summary") or review.get("raw", "")
        lines.extend([f"### Review {index}", "", summary[:1200], ""])
    lines.extend(
        [
            "## Paper-Only Baseline Artifact",
            "",
            f"**Core contribution:** {baseline.get('core_contribution')}",
            "",
            f"**Experiment plan:** {baseline.get('experiment_plan')}",
            "",
            baseline.get("mini_paper_artifact") or "",
            "",
            "## Human-Review-Guided Artifact",
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
            "",
            "## Short-Term Review Scores",
            "",
        ]
    )
    for row in scores.get("reviews", []):
        model = row.get("model")
        row_scores = row.get("scores", {})
        lines.extend(
            [
                f"### {model}",
                "",
                f"- Winner: `{row.get('winner')}`",
                f"- Context-control overall: `{row_scores.get('context_control', {}).get('overall')}`",
                f"- Review-guided overall: `{row_scores.get('review_guided', {}).get('overall')}`",
                f"- Specific review value: {row.get('specific_review_value')}",
                "",
            ]
        )
    citation = frontier.get("citation_frontier") or {}
    temporal = citation.get("temporal_diagnostic", {})
    semantic = frontier.get("semantic_frontier") or {}
    judgement = semantic.get("judgement", {})
    lines.extend(
        [
            "## Later-Frontier Evidence",
            "",
            f"- Citation-frontier winner: `{citation.get('winner')}`",
            f"- Citation temporal pattern: `{temporal.get('pattern')}`",
            f"- Semantic-frontier winner: `{judgement.get('winner')}`",
            f"- Latent delayed-value candidate: `{judgement.get('latent_delayed_value_candidate')}`",
            f"- Frontier terms: `{', '.join(citation.get('frontier_terms', []))}`",
            "",
            "## Evidence Boundary",
            "",
            "This PDF displays a concrete human-review-guided mini-paper artifact from the current pilot. It is not yet a full benchmark-executed deep reproduction.",
        ]
    )
    _write_md(out_md, lines)


def _gate_optimized_markdown(hybrid_case_dir: Path, source_case_dir: Path, out_md: Path) -> None:
    original = _load_json(source_case_dir / "original_paper.json")
    optimized = _load_json(hybrid_case_dir / "gate_optimized_regeneration.json")
    hybrid = _load_json(hybrid_case_dir / "optimized_hybrid_review.json")
    comparison = _load_json(hybrid_case_dir / "case_comparison.json")

    lines = [
        f"# Six-Gate Hybrid-Review Mini-Paper: {original.get('title')}",
        "",
        "## Source Paper",
        "",
        f"- Paper ID: `{original.get('paper_id')}`",
        f"- Venue/source: `{original.get('venue')}`",
        f"- arXiv: `{original.get('arxiv_id') or 'not available'}`",
        "",
        "## Six-Gate Optimized Hybrid Review",
        "",
    ]
    for gate in hybrid.get("six_gate_review", []):
        lines.extend(
            [
                f"### {gate.get('label')}",
                "",
                f"- Evidence count: `{gate.get('evidence_count')}`",
                f"- Optimized action: {gate.get('action')}",
                "",
            ]
        )
    lines.extend(
        [
            "## Gate-Optimized Mini-Paper Artifact",
            "",
            optimized.get("mini_paper_artifact", ""),
            "",
            "## Proxy Metrics",
            "",
        ]
    )
    for key, value in optimized.get("proxy_metrics", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    source = comparison.get("source_case_summary", {})
    lines.extend(
        [
            "",
            "## Case-Level Comparison",
            "",
            f"- Source case type: `{source.get('case_type')}`",
            f"- Citation temporal pattern: `{source.get('citation_temporal_pattern')}`",
            f"- Semantic frontier winner: `{source.get('semantic_frontier_winner')}`",
            "",
            "## Evidence Boundary",
            "",
            optimized.get("claim_boundary", ""),
        ]
    )
    _write_md(out_md, lines)


def main() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    deep_summary = _load_json(DEEP_RUN / "summary.json")
    pdfs = []
    for case in deep_summary.get("cases", []):
        source_case_dir = ROOT / case["case_dir"]
        hybrid_case_dir = HYBRID_RUN / Path(case["case_dir"]).name
        slug = _slug(case["paper_id"] + "_" + case["case_label"])

        raw_md = BUILD_DIR / f"{slug}_review_guided.md"
        raw_pdf = BUILD_DIR / f"{slug}_review_guided.pdf"
        _review_guided_markdown(source_case_dir, raw_md)
        build_pdf(raw_md, raw_pdf, "en")

        hybrid_md = BUILD_DIR / f"{slug}_six_gate_hybrid.md"
        hybrid_pdf = BUILD_DIR / f"{slug}_six_gate_hybrid.pdf"
        _gate_optimized_markdown(hybrid_case_dir, source_case_dir, hybrid_md)
        build_pdf(hybrid_md, hybrid_pdf, "en")

        pdfs.append(
            {
                "paper_id": case["paper_id"],
                "title": case["title"],
                "review_guided_markdown": str(raw_md.relative_to(ROOT)),
                "review_guided_pdf": str(raw_pdf.relative_to(ROOT)),
                "six_gate_hybrid_markdown": str(hybrid_md.relative_to(ROOT)),
                "six_gate_hybrid_pdf": str(hybrid_pdf.relative_to(ROOT)),
                "review_guided_pdf_bytes": raw_pdf.stat().st_size,
                "six_gate_hybrid_pdf_bytes": hybrid_pdf.stat().st_size,
            }
        )

    summary = {
        "status": "deep_case_pdfs_built",
        "pdf_count": len(pdfs) * 2,
        "cases": pdfs,
        "claim_boundary": (
            "These PDFs display pilot mini-paper artifacts generated from raw human-review "
            "guidance and six-gate optimized hybrid-review guidance. They are concrete "
            "viewable artifacts, not completed full experimental reproductions."
        ),
    }
    (BUILD_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": str((BUILD_DIR / "summary.json").relative_to(ROOT)), "pdf_count": summary["pdf_count"]}, indent=2))


if __name__ == "__main__":
    main()
