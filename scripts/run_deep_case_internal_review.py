#!/usr/bin/env python3
"""Deterministic internal review for deep regeneration cases.

This closes the current non-human evaluation loop: compare raw
human-review-guided artifacts with six-gate hybrid-review-guided artifacts on
the three deep OpenReview cases. The score is a reproducible rubric proxy, not
human expert evidence and not a model-call result.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
DEEP_DIR = DOC_DIR / "experiments" / "deep_regeneration_cases_20260602_203000"
HYBRID_DIR = DOC_DIR / "experiments" / "six_gate_hybrid_review_cases_20260602_211500"
RUN_ID = "deep_case_internal_review_20260602_224500"
OUT_DIR = DOC_DIR / "experiments" / RUN_ID


CASE_MAP = [
    ("case_01_openreview_sample_1", "case_01_openreview_sample_1"),
    ("case_02_openreview_sample_2", "case_02_openreview_sample_2"),
    ("case_03_openreview_sample_17", "case_03_openreview_sample_17"),
]

METHOD_TERMS = {
    "baseline",
    "dataset",
    "datasets",
    "metric",
    "metrics",
    "preference",
    "objective",
    "training",
    "diffusion",
    "unlearning",
    "calibration",
    "privacy",
    "rejection",
    "validity",
}
EXPERIMENT_TERMS = {
    "evaluate",
    "experiment",
    "experiments",
    "baseline",
    "baselines",
    "ablation",
    "metric",
    "metrics",
    "accuracy",
    "recall",
    "precision",
    "validity",
    "scaling",
    "curve",
    "trade-off",
}
CLAIM_TERMS = {
    "limitations",
    "limited",
    "claim boundary",
    "may not",
    "generalize",
    "bounded",
    "primarily relevant",
    "not yet",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9_-]+", text.lower()))


def _bounded_score(value: float) -> int:
    return max(1, min(5, int(round(value))))


def _keyword_score(text: str, terms: set[str], *, base: float = 1.0, scale: float = 1.0) -> int:
    lower = text.lower()
    hits = sum(1 for term in terms if term in lower)
    return _bounded_score(base + hits * scale)


def _frontier_score(text: str, frontier: dict[str, Any], hybrid_plan: dict[str, Any] | None) -> int:
    words = _words(text)
    frontier_terms = set(str(term).lower() for term in frontier.get("citation_frontier", {}).get("frontier_terms", []))
    overlap = len(words & frontier_terms)
    semantic_frontier = frontier.get("semantic_frontier") or {}
    semantic = semantic_frontier.get("judgement", {}).get("scores", {})
    base = 1.0 + min(overlap, 4) * 0.45
    if hybrid_plan:
        steering = hybrid_plan.get("frontier_steering") or []
        if isinstance(steering, list) and steering:
            base += min(len(steering), 3) * 0.35
    if semantic:
        # Add a small prior from the existing semantic frontier judge without
        # letting it dominate this local artifact review.
        review_guided_score = semantic.get("review_guided_artifact", {}).get("semantic_frontier_alignment")
        if isinstance(review_guided_score, (int, float)):
            base += (float(review_guided_score) - 3.0) * 0.2
    return _bounded_score(base)


def _artifact_text(artifact: dict[str, Any]) -> str:
    parts = []
    for key in ["core_contribution", "method_sketch", "experiment_plan", "limitations", "claim_boundary", "mini_paper_artifact"]:
        value = artifact.get(key)
        if value:
            parts.append(str(value))
    if artifact.get("six_gate_method_plan"):
        parts.append(json.dumps(artifact["six_gate_method_plan"], ensure_ascii=False))
    return "\n".join(parts)


def _score_artifact(
    *,
    artifact: dict[str, Any],
    frontier: dict[str, Any],
    condition: str,
) -> dict[str, Any]:
    text = _artifact_text(artifact)
    hybrid_plan = artifact.get("six_gate_method_plan") if condition == "six_gate_hybrid" else None
    routed_actions = 0
    if hybrid_plan:
        routed_actions = len([value for value in hybrid_plan.values() if value])
    review_insights = artifact.get("review_insights_used") or []
    proxy_metrics = artifact.get("proxy_metrics") or {}

    scores = {
        "method_specificity": _keyword_score(text, METHOD_TERMS, base=1.0, scale=0.42),
        "experiment_specificity": _keyword_score(text, EXPERIMENT_TERMS, base=1.0, scale=0.38),
        "claim_calibration": _keyword_score(text, CLAIM_TERMS, base=1.0, scale=0.55),
        "frontier_alignment": _frontier_score(text, frontier, hybrid_plan),
        "structured_actionability": _bounded_score(
            1.0
            + min(routed_actions, 6) * 0.45
            + min(len(review_insights), 3) * 0.25
            + min(float(proxy_metrics.get("frontier_target_count", 0)), 3) * 0.25
        ),
    }
    scores["overall"] = round(
        mean(
            [
                scores["method_specificity"],
                scores["experiment_specificity"],
                scores["claim_calibration"],
                scores["frontier_alignment"],
                scores["structured_actionability"],
            ]
        ),
        3,
    )
    return {
        "condition": condition,
        "scores": scores,
        "diagnostics": {
            "word_count": len(text.split()),
            "routed_action_count": routed_actions,
            "review_insight_count": len(review_insights),
            "frontier_terms_matched": sorted(list(_words(text) & set(str(term).lower() for term in frontier.get("citation_frontier", {}).get("frontier_terms", []))))[:12],
        },
    }


def _winner(raw: dict[str, Any], hybrid: dict[str, Any]) -> str:
    delta = hybrid["scores"]["overall"] - raw["scores"]["overall"]
    if delta > 0.15:
        return "six_gate_hybrid"
    if delta < -0.15:
        return "raw_review_guided"
    return "tie"


def _case_markdown(case: dict[str, Any]) -> str:
    raw = case["raw_review_guided"]
    hybrid = case["six_gate_hybrid"]
    lines = [
        f"# Internal Review: {case['paper_id']}",
        "",
        f"- Title: {case['title']}",
        f"- Winner: `{case['winner']}`",
        f"- Overall delta six_gate_minus_raw: `{case['overall_delta_six_gate_minus_raw']}`",
        "",
        "## Scores",
        "",
        "| Condition | Method | Experiment | Claim | Frontier | Actionability | Overall |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| raw_review_guided | {raw['scores']['method_specificity']} | "
            f"{raw['scores']['experiment_specificity']} | {raw['scores']['claim_calibration']} | "
            f"{raw['scores']['frontier_alignment']} | {raw['scores']['structured_actionability']} | "
            f"{raw['scores']['overall']} |"
        ),
        (
            f"| six_gate_hybrid | {hybrid['scores']['method_specificity']} | "
            f"{hybrid['scores']['experiment_specificity']} | {hybrid['scores']['claim_calibration']} | "
            f"{hybrid['scores']['frontier_alignment']} | {hybrid['scores']['structured_actionability']} | "
            f"{hybrid['scores']['overall']} |"
        ),
        "",
        "## Rationale",
        "",
        case["rationale"],
        "",
        "## Claim Boundary",
        "",
        case["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cases: list[dict[str, Any]] = []
    for deep_case, hybrid_case in CASE_MAP:
        deep_path = DEEP_DIR / deep_case
        hybrid_path = HYBRID_DIR / hybrid_case
        raw_artifacts = _load_json(deep_path / "regenerated_artifacts.json")
        frontier = _load_json(deep_path / "future_frontier_evidence.json")
        hybrid_artifact = _load_json(hybrid_path / "gate_optimized_regeneration.json")

        raw = _score_artifact(
            artifact=raw_artifacts["review_guided_regeneration"],
            frontier=frontier,
            condition="raw_review_guided",
        )
        hybrid = _score_artifact(
            artifact=hybrid_artifact,
            frontier=frontier,
            condition="six_gate_hybrid",
        )
        winner = _winner(raw, hybrid)
        delta = round(hybrid["scores"]["overall"] - raw["scores"]["overall"], 3)
        rationale = (
            "The six-gate artifact is favored when it converts raw review text into explicit "
            "frontier steering, evaluator stress, structured feedback, and claim-calibration "
            "actions. The raw-review artifact remains competitive when it contains concrete "
            "method or experiment details without adding gate overhead."
        )
        case = {
            "paper_id": raw_artifacts["paper_id"],
            "title": raw_artifacts["title"],
            "raw_review_guided": raw,
            "six_gate_hybrid": hybrid,
            "winner": winner,
            "overall_delta_six_gate_minus_raw": delta,
            "rationale": rationale,
            "claim_boundary": "Deterministic internal rubric review only; not human expert evidence, not independent model review, and not a benchmark-executed rerun.",
            "source_files": {
                "raw_review_guided": _rel(deep_path / "regenerated_artifacts.json"),
                "six_gate_hybrid": _rel(hybrid_path / "gate_optimized_regeneration.json"),
                "frontier_evidence": _rel(deep_path / "future_frontier_evidence.json"),
            },
        }
        (OUT_DIR / f"{case['paper_id']}.json").write_text(json.dumps(case, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (OUT_DIR / f"{case['paper_id']}.md").write_text(_case_markdown(case), encoding="utf-8")
        cases.append(case)

    winners = [case["winner"] for case in cases]
    summary = {
        "run_id": RUN_ID,
        "timestamp_utc": _utc_now(),
        "status": "completed_internal_deterministic_review",
        "case_count": len(cases),
        "six_gate_hybrid_wins": winners.count("six_gate_hybrid"),
        "raw_review_guided_wins": winners.count("raw_review_guided"),
        "ties": winners.count("tie"),
        "mean_delta_six_gate_minus_raw": round(mean(case["overall_delta_six_gate_minus_raw"] for case in cases), 3),
        "cases": cases,
        "claim_boundary": "This closes the current internal evaluation loop for the three deep cases. It is a reproducible rubric proxy and does not replace future human expert blind review.",
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Deep Case Internal Review",
        "",
        f"- Run ID: `{RUN_ID}`",
        f"- Status: `{summary['status']}`",
        f"- Cases: `{summary['case_count']}`",
        f"- Six-gate hybrid wins: `{summary['six_gate_hybrid_wins']}`",
        f"- Raw review-guided wins: `{summary['raw_review_guided_wins']}`",
        f"- Ties: `{summary['ties']}`",
        f"- Mean delta six_gate_minus_raw: `{summary['mean_delta_six_gate_minus_raw']}`",
        "",
        "## Per-Case Results",
        "",
        "| Case | Winner | Delta | Raw overall | Six-gate overall |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for case in cases:
        md_lines.append(
            f"| {case['paper_id']} | `{case['winner']}` | {case['overall_delta_six_gate_minus_raw']} | "
            f"{case['raw_review_guided']['scores']['overall']} | {case['six_gate_hybrid']['scores']['overall']} |"
        )
    md_lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"], ""])
    (OUT_DIR / "README.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(json.dumps({"summary": _rel(OUT_DIR / "summary.json"), "status": summary["status"]}, indent=2))


if __name__ == "__main__":
    main()
