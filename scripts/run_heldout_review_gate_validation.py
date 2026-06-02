#!/usr/bin/env python3
"""Held-out validation for OpenReview-derived IGRE gate routing.

This probe reduces one source of self-evaluation bias: the same OpenReview
sample should not both define and evaluate the review-to-gate policy. The
script splits papers deterministically into train and held-out folds, selects
actionable review categories on train only, and reports held-out routeability
against no-gate, best-single-gate, and random-gate baselines.

It is still an offline proxy rather than independent human expert evaluation.
The labels come from deterministic category rules over real review text, not
from a live reviewer panel.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
SOURCE_DIR = DOC_DIR / "experiments" / "review_utility_map_probe_20260602_071500"
OUT_DIR = DOC_DIR / "experiments" / "heldout_review_gate_validation_20260602_235000"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _split(rows: list[dict[str, Any]], *, heldout_mod: int, heldout_value: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train = []
    heldout = []
    for row in rows:
        paper_index = int(row.get("paper_index", -1))
        if paper_index % heldout_mod == heldout_value:
            heldout.append(row)
        else:
            train.append(row)
    return train, heldout


def _category_stats(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    for row in rows:
        categories = row.get("categories") or []
        actionable = set(row.get("actionable_categories") or [])
        noisy = set(row.get("noisy_categories") or [])
        gates = row.get("primary_gates") or []
        for category in categories:
            item = stats.setdefault(
                category,
                {
                    "count": 0,
                    "actionable_count": 0,
                    "noisy_count": 0,
                    "utility_sum": 0.0,
                    "gate_counts": Counter(),
                },
            )
            item["count"] += 1
            item["utility_sum"] += float(row.get("utility_score") or 0)
            if category in actionable:
                item["actionable_count"] += 1
            if category in noisy:
                item["noisy_count"] += 1
            for gate in gates:
                item["gate_counts"][gate] += 1
    for category, item in stats.items():
        count = item["count"]
        item["actionable_rate"] = round(item["actionable_count"] / count, 4) if count else 0.0
        item["noisy_rate"] = round(item["noisy_count"] / count, 4) if count else 0.0
        item["mean_utility_when_present"] = round(item["utility_sum"] / count, 4) if count else 0.0
        gate_counts = item.pop("gate_counts")
        item["primary_gate"] = gate_counts.most_common(1)[0][0] if gate_counts else "none"
        item["gate_counts"] = dict(gate_counts)
    return stats


def _select_categories(
    stats: dict[str, dict[str, Any]],
    *,
    min_count: int,
    min_actionable_rate: float,
    max_noisy_rate: float,
) -> list[str]:
    selected = []
    for category, item in sorted(stats.items()):
        if item["count"] < min_count:
            continue
        if item["actionable_rate"] < min_actionable_rate:
            continue
        if item["noisy_rate"] > max_noisy_rate:
            continue
        if item["primary_gate"] in {"none", "triage_before_gate"}:
            continue
        selected.append(category)
    return selected


def _gate_for_category(category: str, stats: dict[str, dict[str, Any]]) -> str:
    return str(stats.get(category, {}).get("primary_gate", "none"))


def _score_policy(
    rows: list[dict[str, Any]],
    *,
    selected_categories: set[str],
    category_to_gate: dict[str, str],
) -> dict[str, Any]:
    routed_rows = 0
    utility_capture = 0.0
    max_utility = 0.0
    noisy_rows = 0
    gate_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    accepted_routed = 0
    rejected_routed = 0
    per_row = []
    for row in rows:
        row_categories = set(row.get("categories") or [])
        actionable = set(row.get("actionable_categories") or [])
        noisy = set(row.get("noisy_categories") or [])
        available_utility = float(row.get("utility_score") or 0)
        max_utility += available_utility
        selected = row_categories & selected_categories
        selected_actionable = selected & actionable
        selected_noisy = selected & noisy
        captured = 0.0
        gates = set()
        for category in selected_actionable:
            captured += available_utility / max(1, len(actionable))
            gate = category_to_gate.get(category, "none")
            if gate not in {"none", "triage_before_gate"}:
                gates.add(gate)
                gate_counts[gate] += 1
                category_counts[category] += 1
        if gates:
            routed_rows += 1
            if bool(row.get("decision")):
                accepted_routed += 1
            else:
                rejected_routed += 1
        if selected_noisy and not selected_actionable:
            noisy_rows += 1
        utility_capture += captured
        per_row.append(
            {
                "review_id": row.get("review_id"),
                "paper_index": row.get("paper_index"),
                "captured_utility": round(captured, 4),
                "available_utility": available_utility,
                "routed_gates": sorted(gates),
                "selected_categories": sorted(selected),
                "decision": row.get("decision"),
                "mean_score": row.get("mean_score"),
            }
        )
    return {
        "review_count": len(rows),
        "routed_review_count": routed_rows,
        "routed_review_rate": round(routed_rows / len(rows), 4) if rows else 0.0,
        "utility_capture": round(utility_capture, 4),
        "max_available_utility": round(max_utility, 4),
        "utility_capture_rate": round(utility_capture / max_utility, 4) if max_utility else 0.0,
        "noisy_only_route_count": noisy_rows,
        "noisy_only_route_rate": round(noisy_rows / len(rows), 4) if rows else 0.0,
        "accepted_routed": accepted_routed,
        "rejected_routed": rejected_routed,
        "gate_counts": dict(gate_counts),
        "category_counts": dict(category_counts),
        "per_row": per_row,
    }


def _random_baseline(
    rows: list[dict[str, Any]],
    *,
    all_categories: list[str],
    selected_count: int,
    category_to_gate: dict[str, str],
    seeds: int,
) -> dict[str, Any]:
    rng = random.Random(20260602)
    rates = []
    utilities = []
    routed = []
    best = None
    for _ in range(seeds):
        draw = set(rng.sample(all_categories, min(selected_count, len(all_categories))))
        score = _score_policy(rows, selected_categories=draw, category_to_gate=category_to_gate)
        rates.append(score["utility_capture_rate"])
        utilities.append(score["utility_capture"])
        routed.append(score["routed_review_rate"])
        if best is None or score["utility_capture_rate"] > best["utility_capture_rate"]:
            best = {"selected_categories": sorted(draw), **{k: v for k, v in score.items() if k != "per_row"}}
    rates_sorted = sorted(rates)
    return {
        "seeds": seeds,
        "mean_utility_capture_rate": round(mean(rates), 4),
        "p05_utility_capture_rate": round(rates_sorted[int(0.05 * (len(rates_sorted) - 1))], 4),
        "p95_utility_capture_rate": round(rates_sorted[int(0.95 * (len(rates_sorted) - 1))], 4),
        "mean_utility_capture": round(mean(utilities), 4),
        "mean_routed_review_rate": round(mean(routed), 4),
        "best_random_draw": best,
    }


def _markdown(summary: dict[str, Any]) -> str:
    full = summary["heldout_full_policy"]
    best_single = summary["heldout_best_single_gate_policy"]
    random_baseline = summary["heldout_random_category_baseline"]
    lines = [
        "# Held-Out Review-Gate Validation",
        "",
        f"Run date: {summary['run_date']}",
        "",
        "## Purpose",
        "",
        "This probe checks whether OpenReview-derived gate routing is stable on",
        "held-out papers. Categories are selected on the train split only, then",
        "evaluated on held-out reviews. This reduces sample-reuse bias in the",
        "review-to-gate evidence, although it is still an offline deterministic",
        "proxy rather than independent human expert validation.",
        "",
        "## Split",
        "",
        f"- Train reviews: `{summary['split']['train_review_count']}`",
        f"- Held-out reviews: `{summary['split']['heldout_review_count']}`",
        f"- Held-out rule: `paper_index % {summary['split']['heldout_mod']} == {summary['split']['heldout_value']}`",
        "",
        "## Selected Categories",
        "",
    ]
    for category in summary["selected_categories"]:
        gate = summary["category_to_gate"][category]
        lines.append(f"- `{category}` -> `{gate}`")
    lines.extend(
        [
            "",
            "## Held-Out Results",
            "",
            "| Policy | Utility capture rate | Routed review rate | Noisy-only route rate |",
            "| --- | ---: | ---: | ---: |",
            f"| Full selected policy | {full['utility_capture_rate']:.3f} | {full['routed_review_rate']:.3f} | {full['noisy_only_route_rate']:.3f} |",
            f"| Best single-gate policy | {best_single['utility_capture_rate']:.3f} | {best_single['routed_review_rate']:.3f} | {best_single['noisy_only_route_rate']:.3f} |",
            f"| Random category baseline mean | {random_baseline['mean_utility_capture_rate']:.3f} | {random_baseline['mean_routed_review_rate']:.3f} | n/a |",
            "| No-gate baseline | 0.000 | 0.000 | 0.000 |",
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
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--heldout-mod", type=int, default=5)
    parser.add_argument("--heldout-value", type=int, default=4)
    parser.add_argument("--min-count", type=int, default=10)
    parser.add_argument("--min-actionable-rate", type=float, default=0.75)
    parser.add_argument("--max-noisy-rate", type=float, default=0.25)
    parser.add_argument("--random-seeds", type=int, default=512)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = _load_json(SOURCE_DIR / "scored_reviews.json")
    train, heldout = _split(rows, heldout_mod=args.heldout_mod, heldout_value=args.heldout_value)
    train_stats = _category_stats(train)
    heldout_stats = _category_stats(heldout)
    selected = _select_categories(
        train_stats,
        min_count=args.min_count,
        min_actionable_rate=args.min_actionable_rate,
        max_noisy_rate=args.max_noisy_rate,
    )
    category_to_gate = {category: _gate_for_category(category, train_stats) for category in train_stats}
    full = _score_policy(heldout, selected_categories=set(selected), category_to_gate=category_to_gate)

    gate_to_categories: dict[str, set[str]] = defaultdict(set)
    for category in selected:
        gate_to_categories[category_to_gate[category]].add(category)
    single_scores = []
    for gate, categories in sorted(gate_to_categories.items()):
        score = _score_policy(heldout, selected_categories=categories, category_to_gate=category_to_gate)
        single_scores.append({"gate": gate, "categories": sorted(categories), **{k: v for k, v in score.items() if k != "per_row"}})
    best_single = max(single_scores, key=lambda item: item["utility_capture_rate"]) if single_scores else {}
    random_baseline = _random_baseline(
        heldout,
        all_categories=sorted(train_stats),
        selected_count=len(selected),
        category_to_gate=category_to_gate,
        seeds=args.random_seeds,
    )
    summary = {
        "run_date": _utc_now(),
        "script": _rel(Path(__file__)),
        "source_scored_reviews": _rel(SOURCE_DIR / "scored_reviews.json"),
        "split": {
            "heldout_mod": args.heldout_mod,
            "heldout_value": args.heldout_value,
            "train_review_count": len(train),
            "heldout_review_count": len(heldout),
            "train_paper_count": len({row["paper_index"] for row in train}),
            "heldout_paper_count": len({row["paper_index"] for row in heldout}),
        },
        "selection_rule": {
            "min_count": args.min_count,
            "min_actionable_rate": args.min_actionable_rate,
            "max_noisy_rate": args.max_noisy_rate,
            "selected_on": "train_split_only",
        },
        "selected_categories": selected,
        "category_to_gate": {category: category_to_gate[category] for category in selected},
        "train_category_stats": train_stats,
        "heldout_category_stats": heldout_stats,
        "heldout_full_policy": {k: v for k, v in full.items() if k != "per_row"},
        "heldout_best_single_gate_policy": best_single,
        "heldout_single_gate_policies": single_scores,
        "heldout_random_category_baseline": random_baseline,
        "claim_boundary": (
            "Held-out validation supports stability of deterministic OpenReview-to-gate routing "
            "under a paper-level split. It does not provide independent human labels, does not "
            "prove downstream paper-quality improvement, and should be treated as an offline "
            "bias-reduction check for the review-derived gate policy."
        ),
    }
    summary_path = args.out_dir / "summary.json"
    per_row_path = args.out_dir / "heldout_per_review.json"
    readme_path = args.out_dir / "README.md"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    per_row_path.write_text(json.dumps(full["per_row"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme_path.write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps({"summary": _rel(summary_path), "readme": _rel(readme_path)}, indent=2))


if __name__ == "__main__":
    main()
