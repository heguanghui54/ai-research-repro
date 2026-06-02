#!/usr/bin/env python3
"""Run a deterministic retrospective frontier-alignment smoke test.

This smoke test operationalizes the Retrospective Frontier Alignment protocol
without making a strong historical-SOTA claim. It reuses the six OpenReview
regeneration pairs already in the package and compares paper-only,
review-guided, and shuffled-review-control artifacts against manually specified
future-frontier descriptors.

The descriptors are heuristic, citation-light placeholders for a future
literature-backed run. Their purpose is to prove that the evaluation pipeline is
machine-checkable and to surface which review-guided artifacts contain more
future-relevant directions than matched controls.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
SOURCE_DIR = DOC_DIR / "experiments" / "openreview_guided_regeneration_probe_20260602_073500"
CONTROL_DIR = DOC_DIR / "experiments" / "openreview_equal_context_ablation_20260602_142000"


FRONTIER_DESCRIPTORS: dict[str, dict[str, Any]] = {
    "openreview_sample_1": {
        "frontier_summary": (
            "Reliable LLM deployment increasingly emphasizes calibrated refusal, "
            "selective prediction, hallucination auditing, knowledge-boundary "
            "estimation, and abstention-aware evaluation beyond narrow arithmetic tasks."
        ),
        "keywords": [
            "refusal",
            "reject",
            "abstain",
            "knowledge boundary",
            "hallucination",
            "calibration",
            "selective",
            "uncertainty",
            "out-of-domain",
            "benchmark",
        ],
    },
    "openreview_sample_2": {
        "frontier_summary": (
            "Conditional graph and molecule generation later centers on controllable "
            "property optimization, validity, scaffold or structure constraints, "
            "classifier-free/property guidance, scalability, and evaluation beyond "
            "single aggregate generation scores."
        ),
        "keywords": [
            "conditional",
            "molecular",
            "property",
            "control",
            "validity",
            "scaffold",
            "guidance",
            "scalability",
            "baseline",
            "diversity",
        ],
    },
    "openreview_sample_17": {
        "frontier_summary": (
            "Language-model unlearning becomes tied to targeted removal, extraction "
            "and membership-inference audits, retain-forget tradeoffs, privacy risk, "
            "evaluation leakage, and post-training safety controls."
        ),
        "keywords": [
            "unlearning",
            "forget",
            "privacy",
            "membership",
            "extraction",
            "retain",
            "forget set",
            "deletion",
            "leakage",
            "audit",
        ],
    },
    "openreview_sample_34": {
        "frontier_summary": (
            "In-context-learning analysis increasingly studies transformers as "
            "implicit learning algorithms, including linear-regression probes, "
            "induction-like mechanisms, task inference, algorithmic generalization, "
            "and mechanistic explanations of context updates."
        ),
        "keywords": [
            "in-context",
            "linear regression",
            "implicit",
            "learning algorithm",
            "transformer",
            "task inference",
            "mechanistic",
            "generalization",
            "induction",
            "context",
        ],
    },
    "openreview_sample_49": {
        "frontier_summary": (
            "Semi-supervised and robust learning continues to connect mixup-style "
            "vicinal objectives with consistency regularization, adversarial "
            "robustness, calibration, label noise, and distribution-shift evaluation."
        ),
        "keywords": [
            "mixup",
            "semi-supervised",
            "robust",
            "consistency",
            "adversarial",
            "calibration",
            "label noise",
            "distribution shift",
            "vicinal",
            "regularization",
        ],
    },
    "openreview_sample_64": {
        "frontier_summary": (
            "Safety-critical scene generation later emphasizes causal structure, "
            "counterfactual scenarios, closed-loop or downstream safety evaluation, "
            "rare-event coverage, distribution shift, and autonomous-driving "
            "validation realism."
        ),
        "keywords": [
            "causal",
            "counterfactual",
            "safety",
            "scene",
            "closed-loop",
            "rare event",
            "distribution shift",
            "autonomous",
            "validation",
            "realism",
        ],
    },
}

ACTIONABILITY_TERMS = [
    "experiment",
    "benchmark",
    "baseline",
    "ablation",
    "metric",
    "evaluate",
    "validation",
    "dataset",
    "robust",
    "limitation",
    "claim",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_text(artifact: dict[str, Any]) -> str:
    parts = []
    for key in [
        "core_contribution",
        "method_sketch",
        "experiment_plan",
        "limitations",
        "claim_boundary",
        "mini_paper_artifact",
    ]:
        value = artifact.get(key)
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
    if "review_insights_used" in artifact:
        parts.extend(str(item) for item in artifact.get("review_insights_used") or [])
    if "generic_review_pressures_used" in artifact:
        parts.extend(str(item) for item in artifact.get("generic_review_pressures_used") or [])
    return "\n".join(parts).lower()


def _count_term(text: str, term: str) -> int:
    escaped = re.escape(term.lower())
    if " " in term:
        return len(re.findall(escaped, text))
    return len(re.findall(rf"\b{escaped}\b", text))


def _score(text: str, descriptor: dict[str, Any]) -> dict[str, Any]:
    keyword_hits = {term: _count_term(text, term) for term in descriptor["keywords"]}
    action_hits = {term: _count_term(text, term) for term in ACTIONABILITY_TERMS}
    matched_keywords = [term for term, count in keyword_hits.items() if count > 0]
    matched_action_terms = [term for term, count in action_hits.items() if count > 0]
    # Keep a simple, auditable score. Keyword coverage is the main frontier
    # signal; actionability and claim calibration are light bonuses.
    frontier_alignment = len(matched_keywords) / len(descriptor["keywords"])
    actionability = min(1.0, len(matched_action_terms) / 6)
    claim_calibration = 1.0 if any(term in text for term in ["limitation", "claim", "boundary", "generalize"]) else 0.0
    total = (0.7 * frontier_alignment) + (0.2 * actionability) + (0.1 * claim_calibration)
    return {
        "score": round(total, 4),
        "frontier_alignment": round(frontier_alignment, 4),
        "actionability": round(actionability, 4),
        "claim_calibration": round(claim_calibration, 4),
        "matched_frontier_keywords": matched_keywords,
        "matched_actionability_terms": matched_action_terms,
    }


def _winner(scores: dict[str, dict[str, Any]]) -> str:
    ordered = sorted(scores.items(), key=lambda item: item[1]["score"], reverse=True)
    if len(ordered) >= 2 and ordered[0][1]["score"] == ordered[1][1]["score"]:
        return "tie"
    return ordered[0][0]


def _summarize(per_paper: list[dict[str, Any]]) -> dict[str, Any]:
    winners = Counter(item["winner"] for item in per_paper)
    conditions = ["paper_only", "review_guided", "shuffled_review_control"]
    means = {}
    for condition in conditions:
        values = [item["scores"][condition]["score"] for item in per_paper]
        means[condition] = round(mean(values), 4)
    return {
        "winner_counts": dict(winners),
        "mean_scores": means,
        "mean_delta_review_guided_minus_paper_only": round(means["review_guided"] - means["paper_only"], 4),
        "mean_delta_review_guided_minus_shuffled_control": round(
            means["review_guided"] - means["shuffled_review_control"], 4
        ),
        "delayed_value_case_count": sum(1 for item in per_paper if item["temporal_diagnostic"]["pattern"] == "delayed_value_review_signal"),
        "short_term_positive_long_term_negative_count": sum(
            1 for item in per_paper if item["temporal_diagnostic"]["pattern"] == "short_term_positive_long_term_negative"
        ),
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Retrospective Frontier Alignment Smoke",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Status: `{summary['status']}`",
        f"- Source regeneration: `{summary['source_regeneration_summary']}`",
        f"- Control source: `{summary['control_source_summary']}`",
        "",
        "## Aggregate",
        "",
    ]
    aggregate = summary["aggregate"]
    lines.append(f"- Winner counts: `{json.dumps(aggregate['winner_counts'], sort_keys=True)}`")
    lines.append(f"- Mean scores: `{json.dumps(aggregate['mean_scores'], sort_keys=True)}`")
    lines.append(
        "- Review-guided minus paper-only mean delta: "
        f"`{aggregate['mean_delta_review_guided_minus_paper_only']}`"
    )
    lines.append(
        "- Review-guided minus shuffled-control mean delta: "
        f"`{aggregate['mean_delta_review_guided_minus_shuffled_control']}`"
    )
    lines.append(f"- Delayed-value cases: `{aggregate['delayed_value_case_count']}`")
    lines.append(
        "- Short-term-positive/long-term-negative cases: "
        f"`{aggregate['short_term_positive_long_term_negative_count']}`"
    )
    lines.extend(["", "## Per Paper", ""])
    for item in summary["per_paper"]:
        lines.append(
            f"- `{item['paper_id']}`: winner `{item['winner']}`, "
            f"scores `{json.dumps({k: v['score'] for k, v in item['scores'].items()}, sort_keys=True)}`, "
            f"temporal pattern `{item['temporal_diagnostic']['pattern']}`"
        )
    lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"], ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="retrospective_frontier_alignment_smoke_20260602_160000")
    args = parser.parse_args()

    selected = {item["paper_id"]: item for item in _load_json(SOURCE_DIR / "selected_papers.json")}
    local_quality = {
        item["paper_id"]: item
        for item in _load_json(SOURCE_DIR / "summary.json")["scoring"]["per_paper"]
    }
    regenerated = {item["paper_id"]: item for item in _load_json(SOURCE_DIR / "regenerated_artifacts.json")["papers"]}
    controls = {
        item["paper_id"]: item["context_control_regeneration"]
        for item in _load_json(CONTROL_DIR / "context_control_artifacts.json")["papers"]
    }

    per_paper = []
    for paper_id, descriptor in FRONTIER_DESCRIPTORS.items():
        source = selected[paper_id]
        regen = regenerated[paper_id]
        condition_artifacts = {
            "paper_only": regen["baseline_regeneration"],
            "review_guided": regen["review_guided_regeneration"],
            "shuffled_review_control": controls[paper_id],
        }
        scores = {
            condition: _score(_artifact_text(artifact), descriptor)
            for condition, artifact in condition_artifacts.items()
        }
        local_scores = local_quality.get(paper_id, {}).get("scores", {})
        local_paper_only = local_scores.get("baseline", {}).get("overall")
        local_review_guided = local_scores.get("review_guided", {}).get("overall")
        local_delta = None
        if isinstance(local_paper_only, (int, float)) and isinstance(local_review_guided, (int, float)):
            local_delta = local_review_guided - local_paper_only
        frontier_delta = scores["review_guided"]["score"] - scores["paper_only"]["score"]
        pattern = "not_classified"
        if local_delta is not None:
            if local_delta < 0 and frontier_delta > 0:
                pattern = "delayed_value_review_signal"
            elif local_delta > 0 and frontier_delta < 0:
                pattern = "short_term_positive_long_term_negative"
            elif local_delta > 0 and frontier_delta > 0:
                pattern = "short_and_long_term_positive"
            elif local_delta < 0 and frontier_delta < 0:
                pattern = "short_and_long_term_negative"
            else:
                pattern = "mixed_or_tie"
        per_paper.append(
            {
                "paper_id": paper_id,
                "title": source["title"],
                "frontier_summary": descriptor["frontier_summary"],
                "scores": scores,
                "winner": _winner(scores),
                "temporal_diagnostic": {
                    "short_term_quality_source": _rel(SOURCE_DIR / "summary.json"),
                    "short_term_review_guided_minus_paper_only": local_delta,
                    "long_term_frontier_review_guided_minus_paper_only": round(frontier_delta, 4),
                    "pattern": pattern,
                },
            }
        )

    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "deterministic_retrospective_frontier_alignment_smoke",
        "source_regeneration_summary": _rel(SOURCE_DIR / "summary.json"),
        "control_source_summary": _rel(CONTROL_DIR / "summary.json"),
        "descriptor_status": "manual_heuristic_frontier_descriptors_not_literature_verified",
        "conditions": ["paper_only", "review_guided", "shuffled_review_control"],
        "temporal_asymmetry_hypothesis": (
            "A review-guided rerun can be worse under short-term quality or original-task "
            "criteria while better aligned with later field evolution. This smoke records "
            "that diagnostic, but the current heuristic run does not find delayed-value cases."
        ),
        "per_paper": per_paper,
        "aggregate": _summarize(per_paper),
        "claim_boundary": (
            "This is a deterministic smoke test for the retrospective frontier-alignment "
            "protocol. Frontier descriptors are manually specified placeholders, not a "
            "citation-backed SOTA reconstruction. Use it as pipeline evidence, not as "
            "proof that historical reviewers predicted later research."
        ),
    }
    summary_json = out_dir / "summary.json"
    summary_md = out_dir / "README.md"
    descriptor_json = out_dir / "frontier_descriptors.json"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_md.write_text(_markdown(summary), encoding="utf-8")
    descriptor_json.write_text(
        json.dumps(FRONTIER_DESCRIPTORS, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"summary": _rel(summary_json), "readme": _rel(summary_md)}, indent=2))


if __name__ == "__main__":
    main()
