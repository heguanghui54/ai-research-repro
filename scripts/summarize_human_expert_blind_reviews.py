#!/usr/bin/env python3
"""Summarize completed human-expert blind review score sheets."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
RUBRIC_FIELDS = [
    "problem_framing",
    "method_specificity",
    "experiment_design",
    "limitation_honesty",
    "claim_calibration",
    "overall_quality",
]


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _score(value: str) -> float | None:
    value = value.strip()
    if not value:
        return None
    try:
        score = float(value)
    except ValueError:
        return None
    if score < 1 or score > 5:
        return None
    return score


def _read_scores(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _bootstrap_ci(values: list[float], *, samples: int = 2000) -> dict[str, float] | None:
    if not values:
        return None
    if len(values) == 1:
        return {"mean": round(values[0], 4), "low": round(values[0], 4), "high": round(values[0], 4)}
    import random

    rng = random.Random(20260602)
    means = []
    for _ in range(samples):
        draw = [values[rng.randrange(len(values))] for _ in values]
        means.append(mean(draw))
    means.sort()
    low = means[int(0.025 * (len(means) - 1))]
    high = means[int(0.975 * (len(means) - 1))]
    return {"mean": round(mean(values), 4), "low": round(low, 4), "high": round(high, 4)}


def _fleiss_kappa(votes_by_pair: dict[str, list[str]]) -> dict[str, Any]:
    """Compute Fleiss' kappa for nominal A/B/tie winners.

    Only pairs with at least two valid votes and the same number of votes are
    included. This keeps the statistic conservative and transparent for small
    expert panels.
    """

    categories = ["A", "B", "tie"]
    complete = {pair: votes for pair, votes in votes_by_pair.items() if len(votes) >= 2}
    if not complete:
        return {
            "status": "not_enough_valid_votes",
            "included_pairs": 0,
            "kappa": None,
        }
    vote_counts = [len(votes) for votes in complete.values()]
    n = min(vote_counts)
    included = {
        pair: votes[:n]
        for pair, votes in complete.items()
        if len(votes) >= n
    }
    if len(included) < 2 or n < 2:
        return {
            "status": "not_enough_balanced_votes",
            "included_pairs": len(included),
            "votes_per_pair": n,
            "kappa": None,
        }
    per_pair_agreement = []
    category_totals = {category: 0 for category in categories}
    for votes in included.values():
        counts = {category: votes.count(category) for category in categories}
        for category, count in counts.items():
            category_totals[category] += count
        per_pair_agreement.append(
            sum(count * count for count in counts.values()) - n
        )
    p_i = [value / (n * (n - 1)) for value in per_pair_agreement]
    p_bar = mean(p_i)
    total_votes = len(included) * n
    p_e = sum((count / total_votes) ** 2 for count in category_totals.values())
    if p_e == 1:
        kappa = 1.0
    else:
        kappa = (p_bar - p_e) / (1 - p_e)
    return {
        "status": "computed",
        "included_pairs": len(included),
        "votes_per_pair": n,
        "categories": categories,
        "category_totals": category_totals,
        "mean_observed_agreement": round(p_bar, 4),
        "expected_agreement": round(p_e, 4),
        "kappa": round(kappa, 4),
    }


def _summarize(packet_dir: Path, score_csv: Path) -> dict[str, Any]:
    key = _load_json(packet_dir / "condition_key.json")
    rows = _read_scores(score_csv)
    by_pair = {pair_id: item for pair_id, item in key["mapping"].items()}
    condition_scores: dict[str, list[float]] = defaultdict(list)
    condition_wins: dict[str, int] = defaultdict(int)
    condition_deltas: list[float] = []
    votes_by_pair: dict[str, list[str]] = defaultdict(list)
    pair_results = []
    invalid_rows = []
    for row in rows:
        pair_id = row.get("pair_id", "")
        mapping = by_pair.get(pair_id)
        if not mapping:
            invalid_rows.append({"pair_id": pair_id, "reason": "unknown_pair_id"})
            continue
        winner = row.get("winner", "").strip()
        if winner in {"A", "B"}:
            condition_wins[mapping[winner]] += 1
            votes_by_pair[pair_id].append(winner)
        elif winner == "tie":
            condition_wins["tie"] += 1
            votes_by_pair[pair_id].append("tie")
        else:
            invalid_rows.append({"pair_id": pair_id, "reason": "missing_or_invalid_winner"})

        pair_score: dict[str, Any] = {"pair_id": pair_id, "mapping": mapping, "winner": winner}
        side_means = {}
        for side in ["A", "B"]:
            side_scores = []
            for field in RUBRIC_FIELDS:
                value = _score(row.get(f"{side}_{field}", ""))
                if value is not None:
                    side_scores.append(value)
            if side_scores:
                avg = mean(side_scores)
                condition_scores[mapping[side]].append(avg)
                side_means[side] = avg
                pair_score[f"{side}_mean"] = round(avg, 4)
        if "A" in side_means and "B" in side_means:
            review_side = "A" if mapping["A"] == "review_guided" else "B" if mapping["B"] == "review_guided" else None
            other_side = "B" if review_side == "A" else "A" if review_side == "B" else None
            if review_side and other_side:
                delta = side_means[review_side] - side_means[other_side]
                condition_deltas.append(delta)
                pair_score["review_guided_minus_other_mean"] = round(delta, 4)
        pair_results.append(pair_score)

    condition_means = {
        condition: round(mean(values), 4)
        for condition, values in condition_scores.items()
        if values
    }
    total_valid_wins = sum(condition_wins.values())
    condition_win_rates = {
        condition: round(count / total_valid_wins, 4)
        for condition, count in condition_wins.items()
        if total_valid_wins
    }
    return {
        "packet": _rel(packet_dir),
        "score_csv": _rel(score_csv),
        "row_count": len(rows),
        "invalid_rows": invalid_rows,
        "condition_wins": dict(condition_wins),
        "condition_win_rates": condition_win_rates,
        "condition_means": condition_means,
        "review_guided_minus_other_mean_delta": _bootstrap_ci(condition_deltas),
        "inter_rater_agreement": _fleiss_kappa(votes_by_pair),
        "pair_results": pair_results,
        "claim_boundary": (
            "This summary is valid only if the CSV contains independent human "
            "expert ratings collected under the packet instructions."
        ),
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Human Expert Blind Review Summary",
        "",
        f"- Packet: `{summary['packet']}`",
        f"- Score CSV: `{summary['score_csv']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Invalid rows: `{len(summary['invalid_rows'])}`",
        "",
        "## Condition Wins",
        "",
    ]
    for condition, count in summary["condition_wins"].items():
        lines.append(f"- `{condition}`: `{count}`")
    lines.extend(["", "## Condition Win Rates", ""])
    for condition, value in summary["condition_win_rates"].items():
        lines.append(f"- `{condition}`: `{value}`")
    lines.extend(["", "## Condition Means", ""])
    for condition, value in summary["condition_means"].items():
        lines.append(f"- `{condition}`: `{value}`")
    lines.extend(["", "## Review-Guided Mean Delta", ""])
    delta = summary.get("review_guided_minus_other_mean_delta")
    if delta:
        lines.append(
            f"- Mean: `{delta['mean']}`; 95% bootstrap CI: "
            f"`[{delta['low']}, {delta['high']}]`"
        )
    else:
        lines.append("- Not enough scored rows.")
    lines.extend(["", "## Inter-Rater Agreement", ""])
    agreement = summary.get("inter_rater_agreement", {})
    if agreement.get("kappa") is None:
        lines.append(f"- Status: `{agreement.get('status')}`")
    else:
        lines.append(
            f"- Fleiss kappa: `{agreement['kappa']}` over "
            f"`{agreement['included_pairs']}` pairs with "
            f"`{agreement['votes_per_pair']}` votes per pair."
        )
    lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"], ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-dir", required=True)
    parser.add_argument("--score-csv", required=True)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    packet_dir = ROOT / args.packet_dir
    score_csv = ROOT / args.score_csv
    out_dir = ROOT / args.output_dir if args.output_dir else packet_dir / "human_rating_summary"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = _summarize(packet_dir, score_csv)
    json_path = out_dir / "summary.json"
    md_path = out_dir / "summary.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps({"summary_json": _rel(json_path), "summary_md": _rel(md_path)}, indent=2))


if __name__ == "__main__":
    main()
