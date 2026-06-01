#!/usr/bin/env python3
"""Summarize archived FML matched-budget comparisons.

This script turns scattered FML matched-comparison artifacts into a single
machine-generated evidence table. It deliberately separates formal two-pair
4-step Causality replicates from the smaller online-smoke comparison.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean, stdev
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
OUT_JSON = DOC_DIR / "audits" / "fml_matched_comparison_summary.json"
OUT_MD = DOC_DIR / "audits" / "fml_matched_comparison_summary.md"

FORMAL_PAIRS = [
    {
        "pair_id": "causality_pair_1",
        "task": "Causality_causalml",
        "human_path": "docs/co_pilot_ai_scientist_v3/experiments/fml_selected_branch_continuation/summary.json",
        "autonomous_path": "docs/co_pilot_ai_scientist_v3/experiments/fml_autonomous_matched_budget_4step/summary.json",
        "notes": "Two draft frontier steps plus two selected-snapshot continuation steps vs. autonomous four-step baseline.",
    },
    {
        "pair_id": "causality_pair_2",
        "task": "Causality_causalml",
        "human_path": "docs/co_pilot_ai_scientist_v3/experiments/fml_matched_budget_rep2_selected_continuation/summary.json",
        "autonomous_path": "docs/co_pilot_ai_scientist_v3/experiments/fml_matched_budget_rep2_autonomous_4step/summary.json",
        "notes": "Second matched replicate using the same task/model budget shape.",
    },
]

SMOKE_COMPARISONS = [
    "docs/co_pilot_ai_scientist_v3/experiments/online_smoke_matched_autonomous_comparison.json"
]


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads((ROOT / path if isinstance(path, str) else path).read_text(encoding="utf-8"))


def _metric(summary: dict[str, Any]) -> float:
    value = summary.get("test_result", {}).get("primary_metric")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError("summary lacks numeric test_result.primary_metric")
    return float(value)


def _val_metric(summary: dict[str, Any]) -> float:
    value = summary.get("best_val_metric")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError("summary lacks numeric best_val_metric")
    return float(value)


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def _sem(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    return stdev(values) / math.sqrt(len(values))


def summarize_formal_pairs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pair in FORMAL_PAIRS:
        human = _load_json(pair["human_path"])
        autonomous = _load_json(pair["autonomous_path"])
        human_test = _metric(human)
        autonomous_test = _metric(autonomous)
        delta = autonomous_test - human_test
        rows.append(
            {
                "pair_id": pair["pair_id"],
                "task": pair["task"],
                "human_path": pair["human_path"],
                "autonomous_path": pair["autonomous_path"],
                "human_val_mae": _val_metric(human),
                "human_test_mae": human_test,
                "autonomous_val_mae": _val_metric(autonomous),
                "autonomous_test_mae": autonomous_test,
                "delta_autonomous_minus_human": delta,
                "winner": "human_gated" if delta > 0 else "autonomous_or_tie",
                "notes": pair["notes"],
            }
        )
    return rows


def summarize_smoke() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in SMOKE_COMPARISONS:
        data = _load_json(path)
        human = data["human_gated_path"]
        autonomous = data["autonomous_baseline"]
        rows.append(
            {
                "comparison_id": data["comparison_id"],
                "task": "Causality_causalml",
                "human_test_mae": float(human["continuation_test_mae"]),
                "autonomous_test_mae": float(autonomous["test_mae"]),
                "delta_autonomous_minus_human": float(data["test_mae_delta_autonomous_minus_human_gated"]),
                "winner": "human_gated"
                if float(data["test_mae_delta_autonomous_minus_human_gated"]) > 0
                else "autonomous_or_tie",
                "fml_steps": {
                    "human_gated": human["fml_steps"],
                    "autonomous": autonomous["fml_steps"],
                },
                "interpretation": data["interpretation"],
                "source": path,
            }
        )
    return rows


def build_summary() -> dict[str, Any]:
    formal = summarize_formal_pairs()
    smoke = summarize_smoke()
    human_scores = [row["human_test_mae"] for row in formal]
    autonomous_scores = [row["autonomous_test_mae"] for row in formal]
    deltas = [row["delta_autonomous_minus_human"] for row in formal]
    return {
        "status": "mixed_underpowered_fml_matched_evidence",
        "metric": "IHDP test MAE",
        "metric_direction": "lower",
        "formal_pair_count": len(formal),
        "formal_pairs": formal,
        "formal_aggregate": {
            "human_gated_mean_test_mae": mean(human_scores),
            "autonomous_mean_test_mae": mean(autonomous_scores),
            "mean_delta_autonomous_minus_human": mean(deltas),
            "delta_sem": _sem(deltas),
            "human_gated_wins": sum(1 for row in formal if row["winner"] == "human_gated"),
            "autonomous_or_tie_wins": sum(1 for row in formal if row["winner"] != "human_gated"),
            "statistical_claim": "not_supported_n_too_small",
        },
        "smoke_comparisons": smoke,
        "claim_implication": (
            "The formal FML Causality pairs are mixed and slightly favor "
            "autonomous on the two-pair mean. The online smoke comparison is "
            "also negative for co-pilot performance. These artifacts support "
            "branch-gate feasibility and evidence discipline, not superiority."
        ),
    }


def _markdown(summary: dict[str, Any]) -> str:
    agg = summary["formal_aggregate"]
    lines = [
        "# FML Matched-Comparison Summary",
        "",
        "This is a machine-generated summary of archived FML matched-budget",
        "comparisons. It separates the formal two-pair Causality replicate from",
        "the smaller online-smoke comparison.",
        "",
        "## Formal Four-Step Causality Pairs",
        "",
        "| Pair | Human-gated test MAE | Autonomous test MAE | Autonomous - human | Winner |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in summary["formal_pairs"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['pair_id']}`",
                    _fmt(row["human_test_mae"]),
                    _fmt(row["autonomous_test_mae"]),
                    _fmt(row["delta_autonomous_minus_human"]),
                    row["winner"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Formal Aggregate",
            "",
            f"- Formal pair count: {summary['formal_pair_count']}",
            f"- Human-gated mean test MAE: `{_fmt(agg['human_gated_mean_test_mae'])}`",
            f"- Autonomous mean test MAE: `{_fmt(agg['autonomous_mean_test_mae'])}`",
            f"- Mean autonomous-minus-human delta: `{_fmt(agg['mean_delta_autonomous_minus_human'])}`",
            f"- Delta SEM: `{_fmt(agg['delta_sem'])}`",
            f"- Human-gated wins: {agg['human_gated_wins']}",
            f"- Autonomous/tie wins: {agg['autonomous_or_tie_wins']}",
            f"- Statistical claim: `{agg['statistical_claim']}`",
            "",
            "Because lower MAE is better, the negative mean delta means the two-pair",
            "mean slightly favors the autonomous baseline. With only two formal",
            "pairs, this is underpowered evidence and should not be presented as a",
            "stable performance conclusion.",
            "",
            "## Online Smoke Comparison",
            "",
            "| Comparison | Human-gated test MAE | Autonomous test MAE | Autonomous - human | Winner |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in summary["smoke_comparisons"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['comparison_id']}`",
                    _fmt(row["human_test_mae"]),
                    _fmt(row["autonomous_test_mae"]),
                    _fmt(row["delta_autonomous_minus_human"]),
                    row["winner"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Claim Implication",
            "",
            summary["claim_implication"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    summary = build_summary()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(OUT_JSON.relative_to(ROOT)), "markdown": str(OUT_MD.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
