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


def _summarize(packet_dir: Path, score_csv: Path) -> dict[str, Any]:
    key = _load_json(packet_dir / "condition_key.json")
    rows = _read_scores(score_csv)
    by_pair = {pair_id: item for pair_id, item in key["mapping"].items()}
    condition_scores: dict[str, list[float]] = defaultdict(list)
    condition_wins: dict[str, int] = defaultdict(int)
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
        elif winner == "tie":
            condition_wins["tie"] += 1
        else:
            invalid_rows.append({"pair_id": pair_id, "reason": "missing_or_invalid_winner"})

        pair_score: dict[str, Any] = {"pair_id": pair_id, "mapping": mapping, "winner": winner}
        for side in ["A", "B"]:
            side_scores = []
            for field in RUBRIC_FIELDS:
                value = _score(row.get(f"{side}_{field}", ""))
                if value is not None:
                    side_scores.append(value)
            if side_scores:
                avg = mean(side_scores)
                condition_scores[mapping[side]].append(avg)
                pair_score[f"{side}_mean"] = round(avg, 4)
        pair_results.append(pair_score)

    condition_means = {
        condition: round(mean(values), 4)
        for condition, values in condition_scores.items()
        if values
    }
    return {
        "packet": _rel(packet_dir),
        "score_csv": _rel(score_csv),
        "row_count": len(rows),
        "invalid_rows": invalid_rows,
        "condition_wins": dict(condition_wins),
        "condition_means": condition_means,
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
    lines.extend(["", "## Condition Means", ""])
    for condition, value in summary["condition_means"].items():
        lines.append(f"- `{condition}`: `{value}`")
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
