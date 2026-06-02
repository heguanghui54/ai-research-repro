#!/usr/bin/env python3
"""Summarize human expert blind-review score sheets after deblinding.

The script is intentionally conservative. Empty or incomplete score sheets
produce a `no_valid_rows` status rather than fabricated evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = ROOT / "docs" / "co_pilot_ai_scientist_v3" / "experiments" / "human_expert_blind_review_packet_20260602_143000"

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


def _pair_number(pair_id: str) -> str:
    digits = "".join(ch for ch in pair_id if ch.isdigit())
    return digits.zfill(2) if digits else pair_id


def _load_mapping(path: Path) -> dict[str, Any]:
    data = _load_json(path)
    if "mapping" in data:
        raw = data["mapping"]
    elif "pairs" in data:
        raw = {item["deep_pair_id"]: item for item in data["pairs"]}
    else:
        raise ValueError(f"unsupported condition-key format: {path}")
    mapping: dict[str, Any] = {}
    for key, value in raw.items():
        mapping[key] = value
        mapping[f"pair_{_pair_number(key)}"] = value
        mapping[f"deep_pair_{_pair_number(key)}"] = value
    return mapping


def _score(value: str) -> float | None:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None
    return score if 1 <= score <= 5 else None


def _side_mean(row: dict[str, str], side: str) -> tuple[float | None, dict[str, float]]:
    scores: dict[str, float] = {}
    for field in RUBRIC_FIELDS:
        value = _score(row.get(f"{side}_{field}", ""))
        if value is None:
            return None, scores
        scores[field] = value
    return mean(scores.values()), scores


def _condition_for_side(mapping: dict[str, Any], side: str) -> str:
    condition = mapping.get(side)
    if condition is None:
        raise ValueError(f"condition mapping missing side {side}: {mapping}")
    return str(condition)


def _primary_condition_names(mapping_values: list[dict[str, Any]]) -> tuple[str, str]:
    conditions = Counter()
    for item in mapping_values:
        for side in ("A", "B"):
            if side in item:
                conditions[str(item[side])] += 1
    names = list(conditions)
    if "review_guided" in conditions:
        target = "review_guided"
        comparator = next((name for name in names if name != target), "comparator")
    elif "six_gate_hybrid" in conditions:
        target = "six_gate_hybrid"
        comparator = next((name for name in names if name != target), "comparator")
    else:
        target = names[0] if names else "target"
        comparator = names[1] if len(names) > 1 else "comparator"
    return target, comparator


def _binom_two_sided_p(k: int, n: int) -> float | None:
    if n <= 0:
        return None
    probs = [math.comb(n, i) * (0.5**n) for i in range(n + 1)]
    observed = probs[k]
    return min(1.0, sum(p for p in probs if p <= observed + 1e-15))


def _bootstrap_ci(values: list[float], *, seed: int = 20260602, n_boot: int = 5000) -> dict[str, float] | None:
    if not values:
        return None
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(mean(sample))
    means.sort()
    lo = means[int(0.025 * (n_boot - 1))]
    hi = means[int(0.975 * (n_boot - 1))]
    return {"mean": mean(values), "ci95_low": lo, "ci95_high": hi, "n": len(values)}


def _fleiss_kappa(pair_votes: dict[str, list[str]], categories: list[str]) -> float | None:
    rows = [votes for votes in pair_votes.values() if len(votes) >= 2]
    if not rows:
        return None
    n = min(len(votes) for votes in rows)
    if n < 2:
        return None
    rows = [votes[:n] for votes in rows]
    category_counts = Counter()
    p_i = []
    for votes in rows:
        counts = Counter(votes)
        category_counts.update(counts)
        p_i.append((sum(count * count for count in counts.values()) - n) / (n * (n - 1)))
    p_bar = mean(p_i)
    total = len(rows) * n
    p_e = sum((category_counts[cat] / total) ** 2 for cat in categories)
    if abs(1 - p_e) < 1e-12:
        return None
    return (p_bar - p_e) / (1 - p_e)


def summarize(score_csv: Path, condition_key: Path) -> dict[str, Any]:
    mapping = _load_mapping(condition_key)
    target_condition, comparator_condition = _primary_condition_names(list({id(v): v for v in mapping.values()}.values()))

    rows = list(csv.DictReader(score_csv.read_text(encoding="utf-8-sig").splitlines()))
    valid = []
    invalid = []
    pair_votes: dict[str, list[str]] = defaultdict(list)

    for index, row in enumerate(rows, start=2):
        pair_id = (row.get("pair_id") or "").strip()
        winner = (row.get("winner") or "").strip()
        row_errors: list[str] = []
        if pair_id not in mapping:
            row_errors.append("unknown_pair_id")
        if winner not in {"A", "B", "tie"}:
            row_errors.append("invalid_or_missing_winner")
        a_mean, a_scores = _side_mean(row, "A")
        b_mean, b_scores = _side_mean(row, "B")
        if a_mean is None or b_mean is None:
            row_errors.append("missing_or_invalid_rubric_scores")
        reviewer_id = (row.get("reviewer_id") or "").strip()
        if not reviewer_id:
            row_errors.append("missing_reviewer_id")
        if row_errors:
            invalid.append({"csv_line": index, "pair_id": pair_id, "errors": row_errors})
            continue

        pair_map = mapping[pair_id]
        side_conditions = {"A": _condition_for_side(pair_map, "A"), "B": _condition_for_side(pair_map, "B")}
        condition_scores = {
            side_conditions["A"]: {"mean": a_mean, "fields": a_scores},
            side_conditions["B"]: {"mean": b_mean, "fields": b_scores},
        }
        if target_condition not in condition_scores or comparator_condition not in condition_scores:
            invalid.append({"csv_line": index, "pair_id": pair_id, "errors": ["target_or_comparator_condition_missing"]})
            continue
        target_side = "A" if side_conditions["A"] == target_condition else "B"
        comparator_side = "A" if side_conditions["A"] == comparator_condition else "B"
        if winner == "tie":
            condition_winner = "tie"
        elif winner == target_side:
            condition_winner = target_condition
        elif winner == comparator_side:
            condition_winner = comparator_condition
        else:
            condition_winner = "other_condition"
        pair_votes[pair_id].append(condition_winner)
        valid.append(
            {
                "reviewer_id": reviewer_id,
                "pair_id": pair_id,
                "paper_id": pair_map.get("paper_id"),
                "title": pair_map.get("title"),
                "winner_side": winner,
                "condition_winner": condition_winner,
                "target_condition": target_condition,
                "comparator_condition": comparator_condition,
                "target_mean": condition_scores[target_condition]["mean"],
                "comparator_mean": condition_scores[comparator_condition]["mean"],
                "target_minus_comparator": condition_scores[target_condition]["mean"]
                - condition_scores[comparator_condition]["mean"],
                "target_fields": condition_scores[target_condition]["fields"],
                "comparator_fields": condition_scores[comparator_condition]["fields"],
                "rationale": row.get("rationale", ""),
            }
        )

    win_counts = Counter(row["condition_winner"] for row in valid)
    deltas = [row["target_minus_comparator"] for row in valid]
    field_deltas = {
        field: [
            row["target_fields"][field] - row["comparator_fields"][field]
            for row in valid
        ]
        for field in RUBRIC_FIELDS
    }
    non_tie_n = win_counts[target_condition] + win_counts[comparator_condition]
    binom_p = _binom_two_sided_p(win_counts[target_condition], non_tie_n)
    raters = sorted({row["reviewer_id"] for row in valid})
    status = "no_valid_rows" if not valid else "human_scores_summarized"
    positive_threshold_met = (
        len(raters) >= 3
        and len(valid) >= 18
        and (
            ((_bootstrap_ci(deltas) or {}).get("ci95_low", 0) > 0)
            or (binom_p is not None and binom_p < 0.05 and win_counts[target_condition] > win_counts[comparator_condition])
        )
    )

    return {
        "status": status,
        "score_csv": _rel(score_csv),
        "condition_key": _rel(condition_key),
        "target_condition": target_condition,
        "comparator_condition": comparator_condition,
        "row_counts": {
            "raw_rows": len(rows),
            "valid_rows": len(valid),
            "invalid_rows": len(invalid),
            "independent_raters": len(raters),
        },
        "win_counts": {
            target_condition: win_counts[target_condition],
            comparator_condition: win_counts[comparator_condition],
            "tie": win_counts["tie"],
            "other_condition": win_counts["other_condition"],
        },
        "exact_binomial_p_excluding_ties": binom_p,
        "mean_delta": _bootstrap_ci(deltas),
        "per_field_delta": {
            field: _bootstrap_ci(values)
            for field, values in field_deltas.items()
        },
        "fleiss_kappa_condition_winner": _fleiss_kappa(
            pair_votes, [target_condition, comparator_condition, "tie", "other_condition"]
        ),
        "positive_evidence_threshold_met": positive_threshold_met,
        "valid_rows": valid,
        "invalid_rows": invalid,
        "claim_boundary": (
            "Human blind-review evidence is positive only if enough valid expert "
            "rows are collected under the preregistered protocol. Empty template "
            "or underpowered summaries are evaluation-readiness artifacts only."
        ),
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Human Expert Blind Review Summary",
        "",
        f"- Status: `{summary['status']}`",
        f"- Score CSV: `{summary['score_csv']}`",
        f"- Condition key: `{summary['condition_key']}`",
        f"- Target condition: `{summary['target_condition']}`",
        f"- Comparator condition: `{summary['comparator_condition']}`",
        f"- Valid rows: `{summary['row_counts']['valid_rows']}`",
        f"- Independent raters: `{summary['row_counts']['independent_raters']}`",
        f"- Positive evidence threshold met: `{summary['positive_evidence_threshold_met']}`",
        "",
        "## Win Counts",
        "",
    ]
    for key, value in summary["win_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Mean Delta", ""])
    delta = summary["mean_delta"]
    if delta:
        lines.append(
            f"- Mean target-comparator delta: `{delta['mean']:.6f}` "
            f"(95% bootstrap CI `{delta['ci95_low']:.6f}`, `{delta['ci95_high']:.6f}`; n={delta['n']})"
        )
    else:
        lines.append("- Mean target-comparator delta: unavailable")
    lines.extend(
        [
            f"- Exact binomial p excluding ties: `{summary['exact_binomial_p_excluding_ties']}`",
            f"- Fleiss kappa over condition winners: `{summary['fleiss_kappa_condition_winner']}`",
            "",
            "## Invalid Rows",
            "",
        ]
    )
    lines.extend(
        [f"- line {row['csv_line']}: `{row['pair_id']}` -> {', '.join(row['errors'])}" for row in summary["invalid_rows"]]
        or ["- None"]
    )
    lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"], ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--score-csv", type=Path, default=DEFAULT_PACKET / "score_sheet_template.csv")
    parser.add_argument("--condition-key", type=Path, default=DEFAULT_PACKET / "condition_key.json")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_PACKET / "human_score_summary_smoke")
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    score_csv = args.score_csv if args.score_csv.is_absolute() else ROOT / args.score_csv
    condition_key = args.condition_key if args.condition_key.is_absolute() else ROOT / args.condition_key
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = summarize(score_csv, condition_key)
    json_path = output_dir / "summary.json"
    md_path = output_dir / "summary.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(summary), encoding="utf-8")

    if args.update_manifest:
        manifest_path = ROOT / "docs" / "co_pilot_ai_scientist_v3" / "repro_manifest.json"
        manifest = _load_json(manifest_path)
        manifest["human_expert_blind_review_summary_tool"] = {
            "status": summary["status"],
            "json": _rel(json_path),
            "markdown": _rel(md_path),
            "positive_evidence_threshold_met": summary["positive_evidence_threshold_met"],
        }
        for path in [Path(__file__), json_path, md_path]:
            rel = _rel(path)
            if rel not in manifest["current_artifacts"]:
                manifest["current_artifacts"].append(rel)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": summary["status"]}, indent=2))


if __name__ == "__main__":
    main()
