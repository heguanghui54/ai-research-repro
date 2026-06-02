#!/usr/bin/env python3
"""Create vector-graph metrics for frontier alignment.

Each original paper and regenerated artifact is embedded into the same
six-dimensional frontier space as the award-paper seed taxonomy. The resulting
vectors let us quantify whether review guidance moves a paper toward the
current frontier centroid, sideways into a novel orthogonal direction, or away
from frontier themes.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_frontier_alignment_taxonomy import DIMENSIONS, FRONTIER_SEEDS, _score_text


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
DEEP_DIR = DOC_DIR / "experiments" / "deep_regeneration_cases_20260602_203000"
DEEP_BUILD = DOC_DIR / "build" / "deep_regeneration_cases"
OUT_DIR = DOC_DIR / "experiments" / "frontier_vector_graph_20260602_234500"


CASES = [
    {
        "case_id": "openreview_sample_1",
        "title": "LLM refusal and reliability",
        "original": DEEP_DIR / "case_01_openreview_sample_1" / "original_paper.md",
        "raw": DEEP_BUILD / "openreview_sample_1_llm_refusal_and_reliability_review_guided.md",
        "six": DEEP_BUILD / "openreview_sample_1_llm_refusal_and_reliability_six_gate_hybrid.md",
    },
    {
        "case_id": "openreview_sample_2",
        "title": "Conditional graph generation and molecular design",
        "original": DEEP_DIR / "case_02_openreview_sample_2" / "original_paper.md",
        "raw": DEEP_BUILD / "openreview_sample_2_conditional_graph_generation_and_molecular_design_review_guided.md",
        "six": DEEP_BUILD / "openreview_sample_2_conditional_graph_generation_and_molecular_design_six_gate_hybrid.md",
    },
    {
        "case_id": "openreview_sample_17",
        "title": "Knowledge unlearning and privacy risk",
        "original": DEEP_DIR / "case_03_openreview_sample_17" / "original_paper.md",
        "raw": DEEP_BUILD / "openreview_sample_17_knowledge_unlearning_and_privacy_risk_review_guided.md",
        "six": DEEP_BUILD / "openreview_sample_17_knowledge_unlearning_and_privacy_risk_six_gate_hybrid.md",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _vector_from_text(text: str) -> list[float]:
    score = _score_text(text)
    return [
        float(score["dimension_scores"][dimension]["weighted_score"])
        for dimension in DIMENSIONS
    ]


def _frontier_centroid() -> list[float]:
    vectors = []
    for source in FRONTIER_SEEDS:
        for item in source["items"]:
            text = item["title"] + " " + " ".join(item["tags"])
            vectors.append(_vector_from_text(text))
    return [round(sum(values) / len(values), 4) for values in zip(*vectors)]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _norm(a: list[float]) -> float:
    return math.sqrt(_dot(a, a))


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [x - y for x, y in zip(a, b)]


def _cosine(a: list[float], b: list[float]) -> float:
    denom = _norm(a) * _norm(b)
    if denom == 0:
        return 0.0
    return round(_dot(a, b) / denom, 4)


def _projection(a: list[float], direction: list[float]) -> float:
    denom = _norm(direction)
    if denom == 0:
        return 0.0
    return round(_dot(a, direction) / denom, 4)


def _orthogonal_norm(a: list[float], direction: list[float]) -> float:
    denom_sq = _dot(direction, direction)
    if denom_sq == 0:
        return round(_norm(a), 4)
    coeff = _dot(a, direction) / denom_sq
    parallel = [coeff * x for x in direction]
    return round(_norm(_sub(a, parallel)), 4)


def _metrics(original: list[float], candidate: list[float], frontier: list[float]) -> dict[str, Any]:
    movement = _sub(candidate, original)
    original_to_frontier = _sub(frontier, original)
    return {
        "candidate_cosine_to_frontier": _cosine(candidate, frontier),
        "original_cosine_to_frontier": _cosine(original, frontier),
        "cosine_gain": round(_cosine(candidate, frontier) - _cosine(original, frontier), 4),
        "movement_cosine_to_frontier_direction": _cosine(movement, original_to_frontier),
        "frontier_projection_gain": _projection(movement, original_to_frontier),
        "orthogonal_novelty_norm": _orthogonal_norm(movement, original_to_frontier),
        "movement_vector": [round(x, 4) for x in movement],
    }


def _radar_points(vector: list[float], max_value: float, cx: float, cy: float, radius: float) -> str:
    points = []
    n = len(vector)
    for i, value in enumerate(vector):
        angle = -math.pi / 2 + 2 * math.pi * i / n
        r = 0 if max_value == 0 else radius * value / max_value
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


def _svg(case_id: str, vectors: dict[str, list[float]]) -> str:
    labels = list(DIMENSIONS.keys())
    cx, cy, radius = 260.0, 250.0, 165.0
    max_value = max(max(v) for v in vectors.values()) or 1.0
    colors = {
        "frontier_centroid": "#111827",
        "original": "#64748b",
        "raw_review_guided": "#2563eb",
        "six_gate_hybrid": "#dc2626",
    }
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="560" viewBox="0 0 760 560">',
        '<rect width="760" height="560" fill="#ffffff"/>',
        f'<text x="28" y="34" font-family="Arial" font-size="20" font-weight="700">Frontier vector graph: {case_id}</text>',
        '<text x="28" y="58" font-family="Arial" font-size="12" fill="#475569">Six-dimensional frontier space; larger radius means stronger alignment with that dimension.</text>',
    ]
    for ring in range(1, 5):
        r = radius * ring / 4
        ring_points = _radar_points([max_value] * len(labels), max_value, cx, cy, r)
        lines.append(f'<polygon points="{ring_points}" fill="none" stroke="#e2e8f0" stroke-width="1"/>')
    for i, label in enumerate(labels):
        angle = -math.pi / 2 + 2 * math.pi * i / len(labels)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        lines.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="#cbd5e1" stroke-width="1"/>')
        tx = cx + (radius + 42) * math.cos(angle)
        ty = cy + (radius + 42) * math.sin(angle)
        anchor = "middle"
        if tx < cx - 20:
            anchor = "end"
        elif tx > cx + 20:
            anchor = "start"
        label_text = label.replace("_", " ")
        lines.append(
            f'<text x="{tx:.1f}" y="{ty:.1f}" font-family="Arial" font-size="11" text-anchor="{anchor}" fill="#334155">{label_text}</text>'
        )
    for name, vector in vectors.items():
        pts = _radar_points(vector, max_value, cx, cy, radius)
        opacity = "0.10" if name != "six_gate_hybrid" else "0.16"
        lines.append(
            f'<polygon points="{pts}" fill="{colors[name]}" fill-opacity="{opacity}" stroke="{colors[name]}" stroke-width="2"/>'
        )
    legend_x, legend_y = 550, 120
    for idx, name in enumerate(["frontier_centroid", "original", "raw_review_guided", "six_gate_hybrid"]):
        y = legend_y + idx * 28
        lines.append(f'<rect x="{legend_x}" y="{y - 12}" width="14" height="14" fill="{colors[name]}"/>')
        lines.append(
            f'<text x="{legend_x + 22}" y="{y}" font-family="Arial" font-size="13" fill="#0f172a">{name.replace("_", " ")}</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frontier = _frontier_centroid()
    per_case = []
    errors: list[str] = []
    for case in CASES:
        missing = [name for name in ["original", "raw", "six"] if not case[name].exists()]
        if missing:
            errors.append(f"{case['case_id']} missing: {missing}")
            continue
        original = _vector_from_text(case["original"].read_text(encoding="utf-8"))
        raw = _vector_from_text(case["raw"].read_text(encoding="utf-8"))
        six = _vector_from_text(case["six"].read_text(encoding="utf-8"))
        vectors = {
            "frontier_centroid": frontier,
            "original": original,
            "raw_review_guided": raw,
            "six_gate_hybrid": six,
        }
        svg_path = OUT_DIR / f"{case['case_id']}_vector_graph.svg"
        svg_path.write_text(_svg(case["case_id"], vectors), encoding="utf-8")
        raw_metrics = _metrics(original, raw, frontier)
        six_metrics = _metrics(original, six, frontier)
        per_case.append(
            {
                "case_id": case["case_id"],
                "title": case["title"],
                "vectors": {
                    key: [round(x, 4) for x in value]
                    for key, value in vectors.items()
                },
                "metrics": {
                    "raw_review_guided": raw_metrics,
                    "six_gate_hybrid": six_metrics,
                    "six_minus_raw_projection_gain": round(
                        six_metrics["frontier_projection_gain"] - raw_metrics["frontier_projection_gain"], 4
                    ),
                    "six_minus_raw_cosine_gain": round(
                        six_metrics["cosine_gain"] - raw_metrics["cosine_gain"], 4
                    ),
                },
                "svg": str(svg_path.relative_to(ROOT)),
            }
        )

    projection_deltas = [item["metrics"]["six_minus_raw_projection_gain"] for item in per_case]
    cosine_deltas = [item["metrics"]["six_minus_raw_cosine_gain"] for item in per_case]
    summary = {
        "created_at": _utc_now(),
        "status": "pass" if not errors else "fail",
        "dimension_order": list(DIMENSIONS.keys()),
        "frontier_centroid_vector": frontier,
        "case_count": len(per_case),
        "mean_six_minus_raw_projection_gain": round(sum(projection_deltas) / len(projection_deltas), 4)
        if projection_deltas
        else None,
        "mean_six_minus_raw_cosine_gain": round(sum(cosine_deltas) / len(cosine_deltas), 4)
        if cosine_deltas
        else None,
        "per_case": per_case,
        "errors": errors,
        "claim_boundary": (
            "Vector graphs quantify movement in a small, hand-specified frontier space. "
            "They support comparative alignment analysis, not a claim that the regenerated "
            "work has achieved the same scientific value as current frontier papers."
        ),
    }

    summary_path = OUT_DIR / "summary.json"
    readme_path = OUT_DIR / "README.md"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Frontier Vector Graph",
        "",
        "This artifact represents current frontier breakthroughs, original papers, and regenerated artifacts as vectors in the same six-dimensional frontier space.",
        "",
        f"- Mean six-gate minus raw projection gain: `{summary['mean_six_minus_raw_projection_gain']}`",
        f"- Mean six-gate minus raw cosine gain: `{summary['mean_six_minus_raw_cosine_gain']}`",
        "",
        "## Metrics",
        "",
        "- `candidate_cosine_to_frontier`: direction similarity between a candidate artifact and the current frontier centroid.",
        "- `frontier_projection_gain`: how much the movement from original to candidate projects onto the original-to-frontier direction.",
        "- `orthogonal_novelty_norm`: how much the movement goes sideways rather than directly toward the current frontier centroid.",
        "",
        "## Case Graphs",
        "",
    ]
    for item in per_case:
        lines.append(f"- `{item['case_id']}`: `{item['svg']}`")
    lines.extend(["", "## Boundary", "", summary["claim_boundary"], ""])
    readme_path.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "summary": str(summary_path.relative_to(ROOT)),
                "status": summary["status"],
                "case_count": summary["case_count"],
                "mean_projection_gain": summary["mean_six_minus_raw_projection_gain"],
            },
            indent=2,
        )
    )
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
