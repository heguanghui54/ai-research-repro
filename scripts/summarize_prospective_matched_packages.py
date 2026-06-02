#!/usr/bin/env python3
"""Summarize prospective matched-budget evidence packages.

The package audit checks whether required artifacts exist. This companion script
summarizes what the passing packages actually show: task, metric direction,
co-pilot score, autonomous score, gate completeness, and claim implication.
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _as_float(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _score_label(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.6f}"


def _complete_attention(gate: dict[str, Any]) -> bool:
    cost = gate.get("attention_cost")
    if not isinstance(cost, dict):
        return False
    required = [
        "active_review_minutes",
        "wall_clock_latency_minutes",
        "options_reviewed",
        "artifacts_reviewed_count",
        "decision_count",
    ]
    return all(isinstance(cost.get(field), (int, float)) for field in required)


def _complete_taste(gate: dict[str, Any]) -> bool:
    taste = gate.get("taste_insight")
    if not isinstance(taste, dict):
        return False
    return (
        isinstance(taste.get("scores"), dict)
        and isinstance(taste.get("taste_insight_score"), (int, float))
        and isinstance(taste.get("qualitative_rationale"), str)
        and bool(taste.get("qualitative_rationale", "").strip())
        and isinstance(taste.get("non_metric_factors"), list)
        and bool(taste.get("non_metric_factors"))
    )


def _gate_summary(trajectory: dict[str, Any]) -> dict[str, Any]:
    gates = [gate for gate in trajectory.get("gates", []) if isinstance(gate, dict)]
    taste_scores = []
    active_minutes = []
    for gate in gates:
        taste = gate.get("taste_insight")
        cost = gate.get("attention_cost")
        if isinstance(taste, dict):
            score = _as_float(taste.get("taste_insight_score"))
            if score is not None:
                taste_scores.append(score)
        if isinstance(cost, dict):
            minutes = _as_float(cost.get("active_review_minutes"))
            if minutes is not None:
                active_minutes.append(minutes)
    return {
        "gate_count": len(gates),
        "complete_attention_gates": sum(1 for gate in gates if _complete_attention(gate)),
        "complete_taste_gates": sum(1 for gate in gates if _complete_taste(gate)),
        "total_active_review_minutes": round(sum(active_minutes), 4),
        "mean_taste_insight_score": round(sum(taste_scores) / len(taste_scores), 4)
        if taste_scores
        else None,
    }


def _micro_metrics(trajectory: dict[str, Any]) -> dict[str, Any]:
    metrics = trajectory.get("metrics", {})
    auto = metrics.get("autonomous_baseline", {}) if isinstance(metrics, dict) else {}
    copilot = metrics.get("co_pilot_variant", {}) if isinstance(metrics, dict) else {}
    co_score = _as_float(copilot.get("mean_normalized_score"))
    auto_score = _as_float(auto.get("mean_normalized_score"))
    delta = co_score - auto_score if co_score is not None and auto_score is not None else None
    return {
        "task": metrics.get("task", "controlled_weighted_maxcut_micro_pilot"),
        "benchmark_family": "controlled_micro_task",
        "metric": "mean_normalized_score",
        "metric_direction": "higher",
        "co_pilot_score": co_score,
        "autonomous_score": auto_score,
        "co_pilot_minus_autonomous": delta,
        "winner": "co_pilot" if delta is not None and delta > 0 else "autonomous_or_tie",
    }


def _fml_metrics(trajectory: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    co_score = _as_float(trajectory.get("co_pilot_test_metric"))
    auto_score = _as_float(trajectory.get("autonomous_test_metric"))
    if auto_score is None:
        auto_score = _as_float(baseline.get("test_result", {}).get("primary_metric"))
    delta = co_score - auto_score if co_score is not None and auto_score is not None else None
    return {
        "task": baseline.get("benchmark", "Causality_causalml"),
        "benchmark_family": "FML-bench",
        "metric": baseline.get("task_config", {}).get("metric", "mae_mean"),
        "metric_direction": baseline.get("task_config", {}).get("metric_direction", "lower"),
        "co_pilot_score": co_score,
        "autonomous_score": auto_score,
        "co_pilot_minus_autonomous": delta,
        "winner": "co_pilot" if delta is not None and delta < 0 else "autonomous_or_tie",
    }


def summarize_manifest(path: Path) -> dict[str, Any]:
    manifest = _load_json(path)
    package_dir = path.parent
    trajectory_path = ROOT / manifest["co_pilot_trajectory"]
    baseline_path = ROOT / manifest["autonomous_baseline"]
    trajectory = _load_json(trajectory_path)
    baseline = _load_json(baseline_path)
    package_id = manifest.get("package_id", package_dir.name)

    if "fml" in package_id:
        metrics = _fml_metrics(trajectory, baseline)
        claim_implication = (
            "Negative co-pilot performance result for this small FML budget; "
            "supports prospective package feasibility, not superiority."
        )
    else:
        metrics = _micro_metrics(trajectory)
        claim_implication = (
            "Positive controlled micro-task result; supports evidence-shape and "
            "mechanistic feasibility, not paper-quality or general superiority."
        )

    return {
        "package_id": package_id,
        "manifest": _rel(path),
        "status": manifest.get("status"),
        "matched_budget": manifest.get("matched_budget", {}),
        "metrics": metrics,
        "gate_summary": _gate_summary(trajectory),
        "claim_implication": claim_implication,
        "limitations": manifest.get("limitations", []),
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Prospective Matched-Budget Package Summary",
        "",
        "This table summarizes what the currently passing prospective packages show.",
        "It complements the package audit: passing the audit means the evidence shape",
        "is present; this summary records whether the measured outcome is positive,",
        "negative, or only a format/feasibility signal.",
        "",
        "## Aggregate",
        "",
        f"- Packages summarized: {summary['package_count']}",
        f"- Co-pilot wins: {summary['co_pilot_wins']}",
        f"- Autonomous or tied wins: {summary['autonomous_or_tie_wins']}",
        f"- Complete attention gates: {summary['complete_attention_gates']}/{summary['gate_count']}",
        f"- Complete taste/insight gates: {summary['complete_taste_gates']}/{summary['gate_count']}",
        f"- Total recorded active review minutes: {summary['total_active_review_minutes']:.2f}",
        "",
        "## Packages",
        "",
        "| Package | Benchmark | Metric | Direction | Co-pilot | Autonomous | Delta | Winner | Claim implication |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for package in summary["packages"]:
        metrics = package["metrics"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{package['package_id']}`",
                    str(metrics["benchmark_family"]),
                    str(metrics["metric"]),
                    str(metrics["metric_direction"]),
                    _score_label(metrics["co_pilot_score"]),
                    _score_label(metrics["autonomous_score"]),
                    _score_label(metrics["co_pilot_minus_autonomous"]),
                    str(metrics["winner"]),
                    package["claim_implication"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The current prospective evidence is deliberately mixed. The controlled",
            "Max-Cut micro-pilot is positive for a human-selected branch, but it is not",
            "an AI Scientist-v2 task and should not be used as a paper-quality result.",
            "The FML-bench Causality packages are stronger as benchmark-shaped packages,",
            "but they are negative for co-pilot performance at the current two-step budget.",
            "Together, these packages support the IGRE logging and matched-budget",
            "protocol, while preserving the central limitation: human taste and insight",
            "are high-variance search interventions whose value must be tested across",
            "more tasks, seeds, budgets, and paper-quality outcomes.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest-glob",
        default="docs/co_pilot_ai_scientist_v3/experiments/prospective_matched_*/prospective_manifest.json",
    )
    parser.add_argument(
        "--json-out",
        default="docs/co_pilot_ai_scientist_v3/audits/prospective_matched_package_summary.json",
    )
    parser.add_argument(
        "--markdown-out",
        default="docs/co_pilot_ai_scientist_v3/audits/prospective_matched_package_summary.md",
    )
    args = parser.parse_args()

    packages = [
        summarize_manifest(path)
        for path in sorted(Path(item) for item in glob.glob(str(ROOT / args.manifest_glob)))
    ]
    gate_count = sum(package["gate_summary"]["gate_count"] for package in packages)
    summary = {
        "status": "summary_only",
        "package_count": len(packages),
        "co_pilot_wins": sum(
            1 for package in packages if package["metrics"]["winner"] == "co_pilot"
        ),
        "autonomous_or_tie_wins": sum(
            1 for package in packages if package["metrics"]["winner"] != "co_pilot"
        ),
        "gate_count": gate_count,
        "complete_attention_gates": sum(
            package["gate_summary"]["complete_attention_gates"] for package in packages
        ),
        "complete_taste_gates": sum(
            package["gate_summary"]["complete_taste_gates"] for package in packages
        ),
        "total_active_review_minutes": round(
            sum(package["gate_summary"]["total_active_review_minutes"] for package in packages),
            4,
        ),
        "packages": packages,
    }

    json_out = ROOT / args.json_out
    markdown_out = ROOT / args.markdown_out
    json_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_out.write_text(_markdown(summary), encoding="utf-8")
    print(f"Wrote {_rel(json_out)}")
    print(f"Wrote {_rel(markdown_out)}")


if __name__ == "__main__":
    main()
