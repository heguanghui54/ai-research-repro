#!/usr/bin/env python3
"""Run a deterministic gate-structure ablation over OpenReview-derived signals.

This probe compares no-gate, single-gate, random-gate, and full-IGRE routing on
the archived review-utility map. It measures how much actionable review signal
each policy can route into concrete workflow gates. It does not evaluate
downstream paper quality.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXPERIMENT_DIR = DOC_DIR / "experiments"
SOURCE_DIR = EXPERIMENT_DIR / "review_utility_map_probe_20260602_071500"
SOURCE_SUMMARY = SOURCE_DIR / "summary.json"
SOURCE_REVIEWS = SOURCE_DIR / "scored_reviews.json"

IGRE_GATES = [
    "scientific_taste_prior",
    "evaluator_stress_test",
    "frontier_steering",
    "structured_feedback",
    "claim_calibration",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _category_weights(summary: dict[str, Any]) -> dict[str, int]:
    return {
        category: int(definition["actionability"])
        for category, definition in summary["category_definitions"].items()
    }


def _category_gates(summary: dict[str, Any]) -> dict[str, str]:
    return {
        category: str(definition["gate"])
        for category, definition in summary["category_definitions"].items()
    }


def _selected_gates(policy: str, review_id: str, seed: int) -> set[str]:
    if policy == "no_gate":
        return set()
    if policy == "full_igre":
        return set(IGRE_GATES)
    if policy.startswith("single_"):
        return {policy.removeprefix("single_")}
    if policy == "random_gate":
        digest = hashlib.sha256(f"{seed}:{review_id}".encode("utf-8")).hexdigest()
        return {IGRE_GATES[int(digest[:8], 16) % len(IGRE_GATES)]}
    raise ValueError(f"unknown policy: {policy}")


def _score_policy(
    reviews: list[dict[str, Any]],
    *,
    policy: str,
    seed: int,
    category_weights: dict[str, int],
    category_gates: dict[str, str],
) -> dict[str, Any]:
    total_available = 0
    total_captured = 0
    covered_reviews = 0
    high_utility_available = 0
    high_utility_covered = 0
    low_score_available = 0
    low_score_covered = 0
    noisy_only_covered = 0

    for row in reviews:
        actionable_categories = row.get("actionable_categories", [])
        available = sum(category_weights[c] for c in actionable_categories)
        selected = _selected_gates(policy, row["review_id"], seed)
        captured = sum(
            category_weights[c]
            for c in actionable_categories
            if category_gates.get(c) in selected
        )
        total_available += available
        total_captured += captured
        if available > 0 and captured > 0:
            covered_reviews += 1
        if available >= 10:
            high_utility_available += 1
            if captured > 0:
                high_utility_covered += 1
        if row.get("mean_score") is not None and float(row["mean_score"]) < 0.5 and available > 0:
            low_score_available += 1
            if captured > 0:
                low_score_covered += 1
        if available == 0 and row.get("noisy_categories") and selected:
            noisy_only_covered += 1

    actionable_reviews = sum(1 for row in reviews if row.get("actionable_categories"))
    return {
        "policy": policy,
        "seed": seed,
        "captured_utility": total_captured,
        "available_utility": total_available,
        "utility_capture_rate": round(total_captured / total_available, 6) if total_available else 0.0,
        "actionable_reviews_covered": covered_reviews,
        "actionable_reviews_available": actionable_reviews,
        "actionable_review_coverage": round(covered_reviews / actionable_reviews, 6) if actionable_reviews else 0.0,
        "high_utility_reviews_covered": high_utility_covered,
        "high_utility_reviews_available": high_utility_available,
        "high_utility_coverage": round(high_utility_covered / high_utility_available, 6)
        if high_utility_available
        else 0.0,
        "low_score_actionable_reviews_covered": low_score_covered,
        "low_score_actionable_reviews_available": low_score_available,
        "low_score_actionable_coverage": round(low_score_covered / low_score_available, 6)
        if low_score_available
        else 0.0,
        "noisy_only_reviews_touched": noisy_only_covered,
    }


def _aggregate_random(rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = [
        "captured_utility",
        "utility_capture_rate",
        "actionable_review_coverage",
        "high_utility_coverage",
        "low_score_actionable_coverage",
        "noisy_only_reviews_touched",
    ]
    out: dict[str, Any] = {"policy": "random_gate", "seeds": len(rows)}
    for key in keys:
        values = [float(row[key]) for row in rows]
        out[f"{key}_mean"] = round(mean(values), 6)
        out[f"{key}_std"] = round(pstdev(values), 6)
    out["example_seed_0"] = rows[0]
    return out


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Gate-Structure Ablation Probe",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Status: `{summary['status']}`",
        f"- Source: `{summary['source_reviews']}`",
        f"- Review snippets: `{summary['review_snippets']}`",
        f"- Actionable snippets: `{summary['actionable_review_snippets']}`",
        f"- Best policy by utility capture: `{summary['best_policy_by_utility_capture']}`",
        "",
        "## Policy Scores",
        "",
        "| Policy | Captured utility | Utility capture | Actionable coverage | High-utility coverage | Low-score actionable coverage |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["policy_scores"]:
        lines.append(
            f"| `{row['policy']}` | {row['captured_utility']} | "
            f"{row['utility_capture_rate']:.6f} | {row['actionable_review_coverage']:.6f} | "
            f"{row['high_utility_coverage']:.6f} | {row['low_score_actionable_coverage']:.6f} |"
        )
    random_row = summary["random_gate_aggregate"]
    lines.extend(
        [
            f"| `random_gate_mean_{random_row['seeds']}_seeds` | "
            f"{random_row['captured_utility_mean']:.2f} | "
            f"{random_row['utility_capture_rate_mean']:.6f} | "
            f"{random_row['actionable_review_coverage_mean']:.6f} | "
            f"{random_row['high_utility_coverage_mean']:.6f} | "
            f"{random_row['low_score_actionable_coverage_mean']:.6f} |",
            "",
            "## Interpretation",
            "",
            summary["interpretation"],
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="gate_structure_ablation_probe_20260602_183000")
    parser.add_argument("--random-seeds", type=int, default=128)
    args = parser.parse_args()

    source_summary = json.loads(SOURCE_SUMMARY.read_text(encoding="utf-8"))
    reviews = json.loads(SOURCE_REVIEWS.read_text(encoding="utf-8"))
    category_weights = _category_weights(source_summary)
    category_gates = _category_gates(source_summary)

    policies = [
        "no_gate",
        "single_scientific_taste_prior",
        "single_evaluator_stress_test",
        "single_frontier_steering",
        "single_structured_feedback",
        "single_claim_calibration",
        "full_igre",
    ]
    policy_scores = [
        _score_policy(
            reviews,
            policy=policy,
            seed=0,
            category_weights=category_weights,
            category_gates=category_gates,
        )
        for policy in policies
    ]
    random_scores = [
        _score_policy(
            reviews,
            policy="random_gate",
            seed=seed,
            category_weights=category_weights,
            category_gates=category_gates,
        )
        for seed in range(args.random_seeds)
    ]
    best_policy = max(policy_scores, key=lambda row: row["utility_capture_rate"])["policy"]
    single_best = max(
        [row for row in policy_scores if row["policy"].startswith("single_")],
        key=lambda row: row["utility_capture_rate"],
    )
    full = next(row for row in policy_scores if row["policy"] == "full_igre")
    no_gate = next(row for row in policy_scores if row["policy"] == "no_gate")
    random_aggregate = _aggregate_random(random_scores)

    out_dir = EXPERIMENT_DIR / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "pass",
        "source_summary": _rel(SOURCE_SUMMARY),
        "source_reviews": _rel(SOURCE_REVIEWS),
        "review_snippets": len(reviews),
        "actionable_review_snippets": sum(1 for row in reviews if row.get("actionable_categories")),
        "gate_set": IGRE_GATES,
        "policy_scores": policy_scores,
        "random_gate_aggregate": random_aggregate,
        "best_policy_by_utility_capture": best_policy,
        "best_single_gate_policy": single_best["policy"],
        "full_vs_best_single_utility_gain": full["captured_utility"] - single_best["captured_utility"],
        "full_vs_no_gate_utility_gain": full["captured_utility"] - no_gate["captured_utility"],
        "full_vs_random_mean_utility_gain": round(
            full["captured_utility"] - random_aggregate["captured_utility_mean"], 6
        ),
        "interpretation": (
            "On the archived OpenReview-derived review-utility map, full IGRE captures all routed "
            "actionable signal by construction, while no-gate captures none. Among single gates, "
            f"{single_best['policy']} captures the most utility, but it misses review signals routed "
            "to the other gate types. The random-gate baseline captures only a fraction of the "
            "available utility on average. This supports the architectural reason for multiple "
            "explicit gates: expert-review signals are heterogeneous and should not be compressed "
            "into one approval step."
        ),
        "claim_boundary": (
            "This is a deterministic routing ablation over archived OpenReview-derived review snippets. "
            "It supports the need for a multi-gate logging and routing structure, but it does not prove "
            "downstream paper-quality improvement, benchmark superiority, or independent human-review validity."
        ),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps({"summary": _rel(out_dir / "summary.json"), "status": summary["status"]}, indent=2))


if __name__ == "__main__":
    main()
