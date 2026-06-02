#!/usr/bin/env python3
"""Build a frontier-breakthrough taxonomy and score deep regenerated artifacts.

The goal is not to decide whether a regenerated paper is "better" by its local
experimental score. It creates a quantitative bridge between historical review
guidance and current frontier research directions, so TFR-style replay can ask
whether a review steers an artifact toward later field trajectories.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments" / "frontier_alignment_taxonomy_20260602_233000"
DEEP_BUILD = DOC_DIR / "build" / "deep_regeneration_cases"


FRONTIER_SEEDS = [
    {
        "venue": "ICLR 2025",
        "source_url": "https://blog.iclr.cc/2025/04/22/announcing-the-outstanding-paper-awards-at-iclr-2025/",
        "source_note": "Official ICLR blog outstanding-paper announcement.",
        "items": [
            {
                "title": "Safety Alignment Should be Made More Than Just a Few Tokens Deep",
                "tags": ["alignment", "safety", "mechanistic robustness", "long-context behavior"],
            },
            {
                "title": "Learning Dynamics of LLM Finetuning",
                "tags": ["training dynamics", "LLM finetuning", "mechanistic understanding"],
            },
            {
                "title": "AlphaEdit: Null-Space Constrained Model Editing for Language Models",
                "tags": ["model editing", "controllability", "representation geometry"],
            },
            {
                "title": "Data Shapley in One Training Run",
                "tags": ["data valuation", "efficient attribution", "training efficiency"],
            },
            {
                "title": "SAM 2: Segment Anything in Images and Videos",
                "tags": ["foundation models", "video segmentation", "scalable perception"],
            },
            {
                "title": "Faster Cascades via Speculative Decoding",
                "tags": ["inference efficiency", "speculative decoding", "systems"],
            },
        ],
    },
    {
        "venue": "ICML 2025",
        "source_url": "https://icml.cc/virtual/2025/awards_detail",
        "source_note": "Official ICML 2025 awards page.",
        "items": [
            {
                "title": "The Value of Prediction in Identifying the Worst-Off",
                "tags": ["welfare", "equity", "high-stakes ML", "decision theory"],
            },
            {
                "title": "Roll the dice & look before you leap: Going beyond the creative limits of next-token prediction",
                "tags": ["creative reasoning", "stochastic planning", "LLM limits", "long-horizon search"],
            },
            {
                "title": "Train for the Worst, Plan for the Best: Understanding Token Ordering in Masked Diffusions",
                "tags": ["masked diffusion", "adaptive inference", "planning", "discrete generation"],
            },
            {
                "title": "CollabLLM: From Passive Responders to Active Collaborators",
                "tags": ["human-AI collaboration", "multiturn rewards", "active assistance"],
            },
            {
                "title": "Score Matching with Missing Data",
                "tags": ["score matching", "missing data", "statistical robustness"],
            },
            {
                "title": "Conformal Prediction as Bayesian Quadrature",
                "tags": ["uncertainty quantification", "Bayesian methods", "deployment guarantees"],
            },
        ],
    },
    {
        "venue": "ACL 2025",
        "source_url": "https://2025.aclweb.org/program/awards/",
        "source_note": "Official ACL 2025 awards page.",
        "items": [
            {
                "title": "A Theory of Response Sampling in LLMs: Part Descriptive and Part Prescriptive",
                "tags": ["LLM sampling", "theory", "generation control"],
            },
            {
                "title": "Fairness through Difference Awareness: Measuring Desired Group Discrimination in LLMs",
                "tags": ["fairness", "measurement", "LLM evaluation"],
            },
            {
                "title": "Language Models Resist Alignment: Evidence From Data Compression",
                "tags": ["alignment", "data compression", "model behavior"],
            },
            {
                "title": "Native Sparse Attention: Hardware-Aligned and Natively Trainable Sparse Attention",
                "tags": ["sparse attention", "hardware alignment", "efficient inference"],
            },
            {
                "title": "AfriMed-QA: A Pan-African, Multi-Specialty, Medical Question-Answering Benchmark Dataset",
                "tags": ["benchmark", "medical QA", "global inclusion", "dataset"],
            },
            {
                "title": "OLMoTrace: Tracing Language Model Outputs Back to Trillions of Training Tokens",
                "tags": ["traceability", "training data", "interpretability", "open models"],
            },
        ],
    },
]


DIMENSIONS = {
    "alignment_safety_reliability": {
        "weight": 1.15,
        "keywords": [
            "alignment",
            "safety",
            "refusal",
            "reliability",
            "robust",
            "compression",
            "privacy",
            "unlearning",
        ],
    },
    "mechanistic_theoretical_insight": {
        "weight": 1.1,
        "keywords": [
            "theory",
            "mechanistic",
            "dynamics",
            "representation",
            "geometry",
            "proof",
            "causal",
            "understanding",
        ],
    },
    "efficient_systems_and_inference": {
        "weight": 1.0,
        "keywords": [
            "efficient",
            "efficiency",
            "inference",
            "sparse",
            "hardware",
            "speculative",
            "latency",
            "training run",
        ],
    },
    "adaptive_long_horizon_search": {
        "weight": 1.2,
        "keywords": [
            "planning",
            "adaptive",
            "long-horizon",
            "creative",
            "frontier",
            "search",
            "hypothesis",
            "collaboration",
        ],
    },
    "evaluation_benchmark_shift": {
        "weight": 1.05,
        "keywords": [
            "benchmark",
            "evaluation",
            "measurement",
            "metric",
            "dataset",
            "stress",
            "audit",
            "traceability",
        ],
    },
    "deployment_and_social_value": {
        "weight": 0.9,
        "keywords": [
            "welfare",
            "fairness",
            "medical",
            "equity",
            "deployment",
            "global",
            "human-centered",
            "policy",
        ],
    },
}


ARTIFACTS = [
    {
        "case_id": "openreview_sample_1",
        "condition": "raw_review_guided",
        "path": DEEP_BUILD / "openreview_sample_1_llm_refusal_and_reliability_review_guided.md",
    },
    {
        "case_id": "openreview_sample_1",
        "condition": "six_gate_hybrid",
        "path": DEEP_BUILD / "openreview_sample_1_llm_refusal_and_reliability_six_gate_hybrid.md",
    },
    {
        "case_id": "openreview_sample_2",
        "condition": "raw_review_guided",
        "path": DEEP_BUILD / "openreview_sample_2_conditional_graph_generation_and_molecular_design_review_guided.md",
    },
    {
        "case_id": "openreview_sample_2",
        "condition": "six_gate_hybrid",
        "path": DEEP_BUILD / "openreview_sample_2_conditional_graph_generation_and_molecular_design_six_gate_hybrid.md",
    },
    {
        "case_id": "openreview_sample_17",
        "condition": "raw_review_guided",
        "path": DEEP_BUILD / "openreview_sample_17_knowledge_unlearning_and_privacy_risk_review_guided.md",
    },
    {
        "case_id": "openreview_sample_17",
        "condition": "six_gate_hybrid",
        "path": DEEP_BUILD / "openreview_sample_17_knowledge_unlearning_and_privacy_risk_six_gate_hybrid.md",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _keyword_count(text: str, keyword: str) -> int:
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    if " " in keyword or "-" in keyword:
        return text.count(keyword.lower())
    return len(re.findall(pattern, text))


def _score_text(text: str) -> dict[str, Any]:
    normalized = _norm(text)
    dimension_scores = {}
    matched_terms: dict[str, dict[str, int]] = {}
    total = 0.0
    for name, spec in DIMENSIONS.items():
        counts = {kw: _keyword_count(normalized, kw) for kw in spec["keywords"]}
        counts = {kw: count for kw, count in counts.items() if count > 0}
        raw = sum(min(count, 3) for count in counts.values())
        capped = min(raw, 10)
        weighted = round(capped * spec["weight"], 3)
        dimension_scores[name] = {
            "raw_keyword_hits_capped": capped,
            "weighted_score": weighted,
        }
        matched_terms[name] = counts
        total += weighted
    return {
        "frontier_alignment_score": round(total, 3),
        "dimension_scores": dimension_scores,
        "matched_terms": matched_terms,
    }


def _taxonomy_from_seeds() -> dict[str, Any]:
    tag_counter: Counter[str] = Counter()
    venue_counter: dict[str, Counter[str]] = {}
    for source in FRONTIER_SEEDS:
        venue_counts: Counter[str] = Counter()
        for item in source["items"]:
            tag_counter.update(item["tags"])
            venue_counts.update(item["tags"])
        venue_counter[source["venue"]] = venue_counts
    return {
        "seed_count": sum(len(source["items"]) for source in FRONTIER_SEEDS),
        "source_count": len(FRONTIER_SEEDS),
        "top_tags": tag_counter.most_common(),
        "venue_tags": {venue: counts.most_common() for venue, counts in venue_counter.items()},
        "dimensions": DIMENSIONS,
    }


def main() -> None:
    EXP_DIR.mkdir(parents=True, exist_ok=True)
    taxonomy = _taxonomy_from_seeds()
    scored = []
    errors: list[str] = []
    for artifact in ARTIFACTS:
        path = artifact["path"]
        if not path.exists():
            errors.append(f"missing artifact: {path.relative_to(ROOT)}")
            continue
        score = _score_text(path.read_text(encoding="utf-8"))
        scored.append(
            {
                "case_id": artifact["case_id"],
                "condition": artifact["condition"],
                "path": str(path.relative_to(ROOT)),
                **score,
            }
        )

    by_case: dict[str, dict[str, Any]] = {}
    for item in scored:
        by_case.setdefault(item["case_id"], {})[item["condition"]] = item
    comparisons = []
    six_gate_wins = 0
    raw_wins = 0
    ties = 0
    deltas = []
    for case_id, conditions in sorted(by_case.items()):
        raw = conditions.get("raw_review_guided")
        six = conditions.get("six_gate_hybrid")
        if not raw or not six:
            errors.append(f"incomplete condition pair for {case_id}")
            continue
        delta = round(six["frontier_alignment_score"] - raw["frontier_alignment_score"], 3)
        deltas.append(delta)
        if delta > 0:
            winner = "six_gate_hybrid"
            six_gate_wins += 1
        elif delta < 0:
            winner = "raw_review_guided"
            raw_wins += 1
        else:
            winner = "tie"
            ties += 1
        comparisons.append(
            {
                "case_id": case_id,
                "raw_score": raw["frontier_alignment_score"],
                "six_gate_score": six["frontier_alignment_score"],
                "delta_six_minus_raw": delta,
                "winner": winner,
            }
        )

    summary = {
        "created_at": _utc_now(),
        "status": "pass" if not errors else "fail",
        "purpose": (
            "Quantify alignment between regenerated artifacts and current frontier "
            "research directions, so review-guided replay is not judged only by local "
            "experiment metrics."
        ),
        "sources": [
            {
                "venue": source["venue"],
                "source_url": source["source_url"],
                "source_note": source["source_note"],
                "item_count": len(source["items"]),
            }
            for source in FRONTIER_SEEDS
        ],
        "taxonomy": taxonomy,
        "artifact_count": len(scored),
        "case_count": len(comparisons),
        "six_gate_hybrid_wins": six_gate_wins,
        "raw_review_guided_wins": raw_wins,
        "ties": ties,
        "mean_delta_six_gate_minus_raw": round(sum(deltas) / len(deltas), 3) if deltas else None,
        "comparisons": comparisons,
        "scored_artifacts": scored,
        "errors": errors,
        "claim_boundary": (
            "This is a deterministic lexical frontier-alignment proxy seeded from a "
            "small official award-paper sample. It is useful for measurement design, "
            "not a substitute for citation-based frontier modeling or expert judgement."
        ),
    }

    summary_path = EXP_DIR / "summary.json"
    readme_path = EXP_DIR / "README.md"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Frontier Alignment Taxonomy",
        "",
        "This artifact operationalizes the user's point that regenerated research should be compared with current frontier directions, not only with local experiment scores.",
        "",
        "## Sources",
        "",
    ]
    for source in summary["sources"]:
        lines.append(f"- `{source['venue']}`: {source['source_url']}")
    lines.extend(
        [
            "",
            "## Frontier Dimensions",
            "",
        ]
    )
    for name, spec in DIMENSIONS.items():
        lines.append(f"- `{name}` (weight `{spec['weight']}`): {', '.join(spec['keywords'])}")
    lines.extend(
        [
            "",
            "## Deep Case Alignment Results",
            "",
            f"- Six-gate hybrid wins: `{six_gate_wins}/3`",
            f"- Raw review-guided wins: `{raw_wins}/3`",
            f"- Ties: `{ties}/3`",
            f"- Mean delta, six-gate minus raw: `{summary['mean_delta_six_gate_minus_raw']}`",
            "",
            "| Case | Raw score | Six-gate score | Delta | Winner |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for item in comparisons:
        lines.append(
            f"| `{item['case_id']}` | {item['raw_score']} | {item['six_gate_score']} | "
            f"{item['delta_six_minus_raw']} | `{item['winner']}` |"
        )
    lines.extend(["", "## Boundary", "", summary["claim_boundary"], ""])
    readme_path.write_text("\n".join(lines), encoding="utf-8")

    print(
        json.dumps(
            {
                "summary": str(summary_path.relative_to(ROOT)),
                "status": summary["status"],
                "case_count": summary["case_count"],
                "mean_delta_six_gate_minus_raw": summary["mean_delta_six_gate_minus_raw"],
            },
            indent=2,
        )
    )
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
