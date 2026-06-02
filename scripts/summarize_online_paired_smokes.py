#!/usr/bin/env python3
"""Summarize same-continuous online paired smoke trajectories.

The summary is intentionally conservative. It aggregates only online full-gate
smokes that contain a same-run autonomous baseline, and it reports benchmark
outcomes separately from manuscript-review probes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPERIMENTS_DIR = ROOT / "docs/co_pilot_ai_scientist_v3/experiments"
DEFAULT_JSON = DEFAULT_EXPERIMENTS_DIR / "online_same_run_paired_summary.json"
DEFAULT_MD = DEFAULT_EXPERIMENTS_DIR / "online_same_run_paired_summary.md"
EPSILON = 1e-9


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return "n/a"
    return str(value)


def _primary_metric(summary: dict[str, Any]) -> float | None:
    metric = (summary.get("test_result") or {}).get("primary_metric")
    return metric if isinstance(metric, (int, float)) else None


def _load_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


def _winner(delta: float | None) -> str:
    if delta is None:
        return "unknown"
    if abs(delta) <= EPSILON:
        return "tie"
    if delta < 0:
        return "autonomous"
    return "co_pilot"


def _record_from_trajectory(path: Path) -> dict[str, Any] | None:
    trajectory = _load_json(path)
    summary = trajectory.get("summary") or {}
    if not summary.get("same_run_autonomous_enabled"):
        return None

    autonomous_path = path.parent / "autonomous_baseline_summary.json"
    autonomous_summary = _load_optional(autonomous_path)
    auto_metric = _primary_metric(autonomous_summary or {})
    co_metric = summary.get("continuation_test_mae")
    delta = None
    if isinstance(co_metric, (int, float)) and isinstance(auto_metric, (int, float)):
        delta = auto_metric - co_metric

    manuscript_summary = _load_optional(path.parent / "online_manuscript/summary.json")
    comparison_summary = _load_optional(
        path.parent / "online_manuscript/matched_budget_comparison_summary.json"
    )
    review_summary = _load_optional(path.parent / "online_manuscript/paper_quality/summary.json")

    return {
        "trajectory_id": trajectory.get("trajectory_id") or path.parent.name,
        "trajectory": _rel(path),
        "selected_branch": summary.get("selected_branch"),
        "selected_branch_val_mae": summary.get("selected_branch_val_mae"),
        "continuation_test_mae": co_metric,
        "same_run_autonomous_test_mae": auto_metric,
        "autonomous_minus_copilot_test_mae": delta,
        "benchmark_winner": _winner(delta),
        "program_search_best_score": summary.get("program_search_best_score"),
        "co_pilot_manuscript_score": (
            (manuscript_summary or {}).get("scores") or {}
        ).get("overall"),
        "autonomous_manuscript_score": (
            (comparison_summary or {}).get("autonomous_scores") or {}
        ).get("overall"),
        "model_review_summary": (
            _rel(path.parent / "online_manuscript/paper_quality/summary.json")
            if review_summary
            else None
        ),
        "model_review_successful_reviews": (review_summary or {}).get("successful_reviews"),
        "model_review_co_pilot_wins": (review_summary or {}).get("co_pilot_wins"),
        "model_review_autonomous_wins": (review_summary or {}).get("autonomous_wins"),
        "model_review_ties": (review_summary or {}).get("ties"),
        "interpretation": (
            "same-run tie on the held-out benchmark metric"
            if _winner(delta) == "tie"
            else (
                "same-run autonomous baseline has the lower held-out MAE"
                if _winner(delta) == "autonomous"
                else "same-run co-pilot continuation has the lower held-out MAE"
            )
        ),
    }


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    co_metrics = [
        record["continuation_test_mae"]
        for record in records
        if isinstance(record.get("continuation_test_mae"), (int, float))
    ]
    auto_metrics = [
        record["same_run_autonomous_test_mae"]
        for record in records
        if isinstance(record.get("same_run_autonomous_test_mae"), (int, float))
    ]
    deltas = [
        record["autonomous_minus_copilot_test_mae"]
        for record in records
        if isinstance(record.get("autonomous_minus_copilot_test_mae"), (int, float))
    ]
    review_records = [record for record in records if record.get("model_review_summary")]
    return {
        "paired_smoke_count": len(records),
        "co_pilot_benchmark_wins": sum(
            1 for record in records if record.get("benchmark_winner") == "co_pilot"
        ),
        "autonomous_benchmark_wins": sum(
            1 for record in records if record.get("benchmark_winner") == "autonomous"
        ),
        "benchmark_ties": sum(
            1 for record in records if record.get("benchmark_winner") == "tie"
        ),
        "mean_co_pilot_test_mae": mean(co_metrics) if co_metrics else None,
        "mean_autonomous_test_mae": mean(auto_metrics) if auto_metrics else None,
        "mean_autonomous_minus_copilot_test_mae": mean(deltas) if deltas else None,
        "model_review_probe_count": len(review_records),
        "model_review_successful_reviews": sum(
            int(record.get("model_review_successful_reviews") or 0)
            for record in review_records
        ),
        "model_review_co_pilot_wins": sum(
            int(record.get("model_review_co_pilot_wins") or 0)
            for record in review_records
        ),
        "model_review_autonomous_wins": sum(
            int(record.get("model_review_autonomous_wins") or 0)
            for record in review_records
        ),
        "model_review_ties": sum(
            int(record.get("model_review_ties") or 0) for record in review_records
        ),
        "claim_implication": (
            "Repeated same-continuous online smokes support orchestration and "
            "manuscript-measurement readiness, but not co-pilot benchmark "
            "superiority. Current benchmark aggregate favors autonomous or tie."
        ),
    }


def _markdown(summary: dict[str, Any]) -> str:
    aggregate = summary["aggregate"]
    rows = [
        "| Trajectory | Co-pilot test MAE | Autonomous test MAE | Delta auto-co | Winner | Co-pilot manuscript | Autonomous manuscript | Model-review wins |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for record in summary["records"]:
        model_wins = record.get("model_review_co_pilot_wins")
        model_total = record.get("model_review_successful_reviews")
        rows.append(
            "| `{}` | {} | {} | {} | {} | {} | {} | {} |".format(
                record["trajectory_id"],
                _fmt(record.get("continuation_test_mae")),
                _fmt(record.get("same_run_autonomous_test_mae")),
                _fmt(record.get("autonomous_minus_copilot_test_mae")),
                record.get("benchmark_winner"),
                _fmt(record.get("co_pilot_manuscript_score")),
                _fmt(record.get("autonomous_manuscript_score")),
                "n/a" if model_wins is None else f"{model_wins}/{model_total}",
            )
        )
    return "\n".join(
        [
            "# Online Same-Run Paired Smoke Summary",
            "",
            "This file aggregates only online full-gate smoke trajectories that",
            "contain a same-continuous-run autonomous AI Scientist-v2 baseline.",
            "Lower MAE is better for the FML Causality metric.",
            "",
            "## Aggregate",
            "",
            f"- Paired smoke count: `{aggregate['paired_smoke_count']}`",
            f"- Co-pilot benchmark wins: `{aggregate['co_pilot_benchmark_wins']}`",
            f"- Autonomous benchmark wins: `{aggregate['autonomous_benchmark_wins']}`",
            f"- Benchmark ties: `{aggregate['benchmark_ties']}`",
            f"- Mean co-pilot test MAE: `{_fmt(aggregate['mean_co_pilot_test_mae'])}`",
            f"- Mean autonomous test MAE: `{_fmt(aggregate['mean_autonomous_test_mae'])}`",
            "- Mean autonomous-minus-co-pilot test MAE: "
            f"`{_fmt(aggregate['mean_autonomous_minus_copilot_test_mae'])}`",
            f"- Model-review probes: `{aggregate['model_review_probe_count']}`",
            f"- Model-review co-pilot wins: `{aggregate['model_review_co_pilot_wins']}`",
            f"- Model-review autonomous wins: `{aggregate['model_review_autonomous_wins']}`",
            f"- Model-review ties: `{aggregate['model_review_ties']}`",
            "",
            "## Records",
            "",
            *rows,
            "",
            "## Interpretation",
            "",
            aggregate["claim_implication"],
            "The model-review wins are useful process checks, not independent",
            "human expert peer review or top-conference evidence.",
            "",
        ]
    )


def _update_manifest(summary_json: Path, summary_md: Path) -> None:
    manifest_path = ROOT / "docs/co_pilot_ai_scientist_v3/repro_manifest.json"
    if not manifest_path.exists():
        return
    manifest = _load_json(manifest_path)
    manifest["status"] = "pilot_package_with_repeated_same_run_online_smokes"
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in (summary_json, summary_md):
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiments-dir", type=Path, default=DEFAULT_EXPERIMENTS_DIR)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    experiments_dir = args.experiments_dir
    if not experiments_dir.is_absolute():
        experiments_dir = ROOT / experiments_dir
    records = []
    for path in sorted(experiments_dir.glob("online_full_gate_smoke_*/trajectory.json")):
        record = _record_from_trajectory(path)
        if record:
            records.append(record)
    summary = {
        "status": "online_same_run_paired_smoke_summary",
        "lower_is_better": True,
        "epsilon_for_tie": EPSILON,
        "records": records,
        "aggregate": _aggregate(records),
        "limitations": [
            "Tiny smoke budgets; not a top-conference empirical result.",
            "FML Causality MAE does not measure high-tail scientific novelty.",
            "Model-review probes are not independent human expert peer review.",
        ],
    }

    output_json = args.output_json if args.output_json.is_absolute() else ROOT / args.output_json
    output_md = args.output_md if args.output_md.is_absolute() else ROOT / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    output_md.write_text(_markdown(summary), encoding="utf-8")
    if args.update_manifest:
        _update_manifest(output_json, output_md)
    print(json.dumps({"json": _rel(output_json), "markdown": _rel(output_md)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
