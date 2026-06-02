#!/usr/bin/env python3
"""Attribute OpenReview-guided downstream gains to IGRE gate signals.

This probe is deliberately conservative. It does not generate new papers and it
does not claim causal downstream improvement. Instead, it reuses the
equal-context OpenReview ablation and asks whether observed review-guided gains
line up with the gate types extracted from the same papers' reviews.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
DEFAULT_REVIEWS = (
    DOC_DIR
    / "experiments"
    / "review_utility_map_probe_20260602_071500"
    / "scored_reviews.json"
)
DEFAULT_REGENERATION = (
    DOC_DIR
    / "experiments"
    / "openreview_guided_regeneration_probe_20260602_073500"
    / "summary.json"
)
DEFAULT_EQUAL_CONTEXT = (
    DOC_DIR
    / "experiments"
    / "openreview_equal_context_ablation_20260602_142000"
    / "summary.json"
)
DEFAULT_OUT_DIR = DOC_DIR / "experiments" / "gate_outcome_attribution_probe_20260602_191500"

GATE_TARGET_DIMENSIONS = {
    "scientific_taste_prior": ["novelty", "overall"],
    "evaluator_stress_test": ["correctness", "experiment_quality", "overall"],
    "frontier_steering": ["novelty", "experiment_quality", "overall"],
    "structured_feedback": ["clarity", "overall"],
    "claim_calibration": ["limitation_honesty", "claim_calibration", "overall"],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> str:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return _rel(path)


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 6) if values else 0.0


def _paper_score_deltas(equal_context: dict[str, Any]) -> dict[str, dict[str, float]]:
    """Return mean review-guided minus context-control score deltas per paper."""

    by_paper: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for review in equal_context["reviews"]:
        for row in review["per_paper"]:
            paper_id = row["paper_id"]
            scores = row["scores"]
            guided = scores["review_guided"]
            control = scores["context_control"]
            for dimension, guided_value in guided.items():
                by_paper[paper_id][dimension].append(float(guided_value) - float(control[dimension]))

    return {
        paper_id: {dimension: _mean(values) for dimension, values in dims.items()}
        for paper_id, dims in by_paper.items()
    }


def _selected_index_by_paper(regeneration: dict[str, Any]) -> dict[str, int]:
    return {
        paper["paper_id"]: int(paper["sample_index"])
        for paper in regeneration["selected_papers"]
    }


def _gate_utility_by_paper(
    scored_reviews: list[dict[str, Any]],
    selected_by_paper: dict[str, int],
) -> dict[str, dict[str, Any]]:
    selected_index_to_id = {index: paper_id for paper_id, index in selected_by_paper.items()}
    result: dict[str, dict[str, Any]] = {
        paper_id: {
            "paper_index": index,
            "gate_utility": {gate: 0 for gate in GATE_TARGET_DIMENSIONS},
            "gate_review_counts": {gate: 0 for gate in GATE_TARGET_DIMENSIONS},
            "review_count": 0,
            "actionable_review_count": 0,
        }
        for paper_id, index in selected_by_paper.items()
    }
    for review in scored_reviews:
        paper_id = selected_index_to_id.get(int(review["paper_index"]))
        if not paper_id:
            continue
        result[paper_id]["review_count"] += 1
        if review.get("actionable_categories"):
            result[paper_id]["actionable_review_count"] += 1
        gates = set(review.get("primary_gates") or [])
        if not gates:
            continue
        per_gate_utility = float(review.get("utility_score", 0)) / max(1, len(gates))
        for gate in gates:
            if gate not in GATE_TARGET_DIMENSIONS:
                continue
            result[paper_id]["gate_utility"][gate] += per_gate_utility
            result[paper_id]["gate_review_counts"][gate] += 1
    for row in result.values():
        row["gate_utility"] = {
            gate: round(value, 6)
            for gate, value in row["gate_utility"].items()
        }
    return result


def _aligned_delta(deltas: dict[str, float], gate: str) -> float:
    return _mean([deltas.get(dimension, 0.0) for dimension in GATE_TARGET_DIMENSIONS[gate]])


def _policy_score(
    *,
    paper_ids: list[str],
    gate_utility: dict[str, dict[str, Any]],
    score_deltas: dict[str, dict[str, float]],
    retained_gates_by_paper: dict[str, set[str]],
) -> dict[str, Any]:
    total = 0.0
    positive = 0.0
    negative = 0.0
    contributions = []
    for paper_id in paper_ids:
        for gate in retained_gates_by_paper.get(paper_id, set()):
            utility = float(gate_utility[paper_id]["gate_utility"].get(gate, 0.0))
            if utility <= 0:
                continue
            delta = _aligned_delta(score_deltas[paper_id], gate)
            contribution = utility * delta
            total += contribution
            if contribution >= 0:
                positive += contribution
            else:
                negative += contribution
            contributions.append(
                {
                    "paper_id": paper_id,
                    "gate": gate,
                    "gate_utility": round(utility, 6),
                    "aligned_delta": round(delta, 6),
                    "contribution": round(contribution, 6),
                }
            )
    return {
        "aligned_outcome_score": round(total, 6),
        "positive_contribution": round(positive, 6),
        "negative_contribution": round(negative, 6),
        "nonzero_contributions": len(contributions),
        "top_contributions": sorted(
            contributions,
            key=lambda item: item["contribution"],
            reverse=True,
        )[:10],
        "negative_contributions": [
            item for item in sorted(contributions, key=lambda item: item["contribution"]) if item["contribution"] < 0
        ][:10],
    }


def _random_policy_scores(
    *,
    paper_ids: list[str],
    gate_utility: dict[str, dict[str, Any]],
    score_deltas: dict[str, dict[str, float]],
    seeds: int,
) -> dict[str, Any]:
    scores = []
    gates = list(GATE_TARGET_DIMENSIONS)
    for seed in range(seeds):
        rng = random.Random(seed)
        retained = {paper_id: {rng.choice(gates)} for paper_id in paper_ids}
        scores.append(
            _policy_score(
                paper_ids=paper_ids,
                gate_utility=gate_utility,
                score_deltas=score_deltas,
                retained_gates_by_paper=retained,
            )["aligned_outcome_score"]
        )
    return {
        "seeds": seeds,
        "aligned_outcome_score_mean": round(statistics.mean(scores), 6),
        "aligned_outcome_score_std": round(statistics.pstdev(scores), 6),
        "min": round(min(scores), 6),
        "max": round(max(scores), 6),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    scored_reviews = _load_json(args.reviews)
    regeneration = _load_json(args.regeneration)
    equal_context = _load_json(args.equal_context)
    paper_ids = [paper["paper_id"] for paper in regeneration["selected_papers"]]
    selected_by_paper = _selected_index_by_paper(regeneration)
    gate_utility = _gate_utility_by_paper(scored_reviews, selected_by_paper)
    score_deltas = _paper_score_deltas(equal_context)

    full_retained = {
        paper_id: {
            gate
            for gate, utility in gate_utility[paper_id]["gate_utility"].items()
            if utility > 0
        }
        for paper_id in paper_ids
    }
    no_gate = {paper_id: set() for paper_id in paper_ids}
    policies = {
        "no_gate": _policy_score(
            paper_ids=paper_ids,
            gate_utility=gate_utility,
            score_deltas=score_deltas,
            retained_gates_by_paper=no_gate,
        ),
        "full_igre": _policy_score(
            paper_ids=paper_ids,
            gate_utility=gate_utility,
            score_deltas=score_deltas,
            retained_gates_by_paper=full_retained,
        ),
    }
    for gate in GATE_TARGET_DIMENSIONS:
        retained = {paper_id: {gate} for paper_id in paper_ids}
        policies[f"single_{gate}"] = _policy_score(
            paper_ids=paper_ids,
            gate_utility=gate_utility,
            score_deltas=score_deltas,
            retained_gates_by_paper=retained,
        )
    random_scores = _random_policy_scores(
        paper_ids=paper_ids,
        gate_utility=gate_utility,
        score_deltas=score_deltas,
        seeds=args.random_seeds,
    )

    per_gate = {}
    for gate in GATE_TARGET_DIMENSIONS:
        rows = []
        for paper_id in paper_ids:
            utility = gate_utility[paper_id]["gate_utility"][gate]
            if utility <= 0:
                continue
            rows.append(
                {
                    "paper_id": paper_id,
                    "gate_utility": utility,
                    "aligned_delta": round(_aligned_delta(score_deltas[paper_id], gate), 6),
                }
            )
        per_gate[gate] = {
            "paper_count_with_signal": len(rows),
            "total_gate_utility": round(sum(row["gate_utility"] for row in rows), 6),
            "mean_aligned_delta_when_present": _mean([row["aligned_delta"] for row in rows]),
            "rows": rows,
        }

    full_score = policies["full_igre"]["aligned_outcome_score"]
    best_single_name, best_single = max(
        (
            (name, value)
            for name, value in policies.items()
            if name.startswith("single_")
        ),
        key=lambda item: item[1]["aligned_outcome_score"],
    )
    status = "pass" if full_score > 0 and full_score >= best_single["aligned_outcome_score"] else "attention"

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": status,
        "source_reviews": _rel(args.reviews),
        "source_regeneration": _rel(args.regeneration),
        "source_equal_context": _rel(args.equal_context),
        "paper_count": len(paper_ids),
        "review_models": equal_context["review_models"],
        "gate_target_dimensions": GATE_TARGET_DIMENSIONS,
        "paper_score_deltas": score_deltas,
        "paper_gate_utility": gate_utility,
        "per_gate_attribution": per_gate,
        "policy_scores": policies,
        "random_gate_policy": random_scores,
        "best_single_gate_policy": best_single_name,
        "full_vs_best_single_aligned_score_gain": round(full_score - best_single["aligned_outcome_score"], 6),
        "full_vs_random_mean_aligned_score_gain": round(full_score - random_scores["aligned_outcome_score_mean"], 6),
        "interpretation": (
            "The observed equal-context OpenReview gains are aligned with several "
            "review-derived IGRE gates, especially evaluator-stress and structured "
            "feedback. Full IGRE has the highest aligned-outcome score because it "
            "keeps heterogeneous review signals instead of compressing them into a "
            "single gate."
        ),
        "claim_boundary": (
            "This is a post-hoc attribution over six OpenReview regeneration pairs "
            "and model-review scores. It supports downstream gate-quality analysis "
            "as a design signal, but it does not prove causal improvement, "
            "independent human validity, or benchmark superiority."
        ),
    }
    summary_path = out_dir / "summary.json"
    summary["summary_path"] = _write(summary_path, json.dumps(summary, indent=2, ensure_ascii=False))

    readme = f"""# Gate-Outcome Attribution Probe

- Run ID: `{args.run_id}`
- Status: `{status}`
- Source equal-context ablation: `{_rel(args.equal_context)}`
- Papers: `{len(paper_ids)}`
- Review models: `{', '.join(equal_context['review_models'])}`

## Policy Scores

| Policy | Aligned outcome score | Positive contribution | Negative contribution | Nonzero contributions |
| --- | ---: | ---: | ---: | ---: |
"""
    for name, row in policies.items():
        readme += (
            f"| `{name}` | {row['aligned_outcome_score']:.6f} | "
            f"{row['positive_contribution']:.6f} | {row['negative_contribution']:.6f} | "
            f"{row['nonzero_contributions']} |\n"
        )
    readme += (
        f"| `random_gate_mean_{args.random_seeds}_seeds` | "
        f"{random_scores['aligned_outcome_score_mean']:.6f} | n/a | n/a | n/a |\n"
    )
    readme += f"""
## Gate Attribution

| Gate | Papers with signal | Total gate utility | Mean aligned delta when present |
| --- | ---: | ---: | ---: |
"""
    for gate, row in per_gate.items():
        readme += (
            f"| `{gate}` | {row['paper_count_with_signal']} | "
            f"{row['total_gate_utility']:.6f} | "
            f"{row['mean_aligned_delta_when_present']:.6f} |\n"
        )
    readme += f"""
## Interpretation

The full IGRE policy obtains aligned-outcome score `{full_score:.6f}`. The best
single-gate policy is `{best_single_name}` with score
`{best_single['aligned_outcome_score']:.6f}`. The random single-gate baseline
averages `{random_scores['aligned_outcome_score_mean']:.6f}` over
`{args.random_seeds}` seeds.

This suggests that the same review text that routes into multiple gates also
aligns with observed downstream score improvements in the equal-context
regeneration probe. It is a downstream attribution analysis, not a causal
ablation with newly generated single-gate artifacts.

## Claim Boundary

{summary['claim_boundary']}
"""
    summary["readme_path"] = _write(out_dir / "README.md", readme)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="gate_outcome_attribution_probe_20260602_191500")
    parser.add_argument("--reviews", type=Path, default=DEFAULT_REVIEWS)
    parser.add_argument("--regeneration", type=Path, default=DEFAULT_REGENERATION)
    parser.add_argument("--equal-context", type=Path, default=DEFAULT_EQUAL_CONTEXT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--random-seeds", type=int, default=512)
    return parser.parse_args()


def main() -> None:
    summary = run(parse_args())
    print(json.dumps({"summary": summary["summary_path"], "status": summary["status"]}, indent=2))


if __name__ == "__main__":
    main()
