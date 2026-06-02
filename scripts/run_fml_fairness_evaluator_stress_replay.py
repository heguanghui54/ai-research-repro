#!/usr/bin/env python3
"""Replay evaluator-stress gating on archived FML Fairness_fairlearn artifacts.

The replay uses real FML-Bench Fairness_fairlearn evaluation outputs already
archived in the package. It checks a narrow gate-design claim: a primary fairness
metric alone selects a degenerate all-negative predictor, while an IGRE
evaluator-stress gate rejects that metric-gaming branch and aborts continuation
because no non-degenerate candidate improves the baseline fairness metric.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXPERIMENT_DIR = DOC_DIR / "experiments"
LIVE_SKILL_SUMMARY = (
    EXPERIMENT_DIR
    / "live_skill_invocation_smoke_20260602_170000"
    / "summary.json"
)


VARIANT_PATHS = {
    "baseline_reference": EXPERIMENT_DIR / "fml_fairness_baseline_eval" / "test_info.json",
    "api_repaired_candidate": EXPERIMENT_DIR / "fml_fairness_repair_eval" / "test_info.json",
    "metric_gaming_all_negative": EXPERIMENT_DIR / "fml_fairness_degenerate_eval" / "test_info.json",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_metrics(path: Path) -> dict[str, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["adult"]["means"]


def _score(metrics: dict[str, float], *, utility_floor: float, baseline_fairness: float) -> dict[str, Any]:
    fairness = metrics["abs_demographic_parity_diff_mean"]
    balanced_accuracy = metrics["balanced_accuracy_mean"]
    utility_pass = balanced_accuracy >= utility_floor
    fairness_improves_baseline = fairness < baseline_fairness
    accepted_for_continuation = utility_pass and fairness_improves_baseline
    return {
        "abs_demographic_parity_diff_mean": round(fairness, 6),
        "balanced_accuracy_mean": round(balanced_accuracy, 6),
        "accuracy_mean": round(metrics["accuracy_mean"], 6),
        "equalized_odds_diff_mean": round(metrics["abs_equalized_odds_diff_mean"], 6),
        "primary_only_score": round(-fairness, 6),
        "utility_floor": utility_floor,
        "utility_guardrail_pass": utility_pass,
        "fairness_improves_baseline": fairness_improves_baseline,
        "accepted_for_continuation": accepted_for_continuation,
        "evaluator_stress_score": round(-fairness, 6) if accepted_for_continuation else -999.0,
    }


def _winner(rows: dict[str, dict[str, Any]], key: str) -> str:
    return max(rows.items(), key=lambda item: item[1][key])[0]


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# FML Fairness Evaluator-Stress Replay",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Status: `{summary['status']}`",
        f"- Benchmark: `{summary['benchmark']}`",
        f"- Linked live skill invocation: `{summary['linked_live_skill_invocation']}`",
        f"- Primary-only winner: `{summary['primary_only_winner']}`",
        f"- Evaluator-stress decision: `{summary['evaluator_stress_decision']}`",
        f"- Metric-gaming incidents reduced: `{summary['metric_gaming_incidents_reduced']}`",
        "",
        "## Scores",
        "",
        "| Variant | Test DPD abs | Test balanced accuracy | Primary-only score | Utility pass | Improves baseline | Accepted for continuation |",
        "| --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for name, row in summary["scores"].items():
        lines.append(
            f"| `{name}` | {row['abs_demographic_parity_diff_mean']:.6f} | "
            f"{row['balanced_accuracy_mean']:.6f} | {row['primary_only_score']:.6f} | "
            f"{row['utility_guardrail_pass']} | {row['fairness_improves_baseline']} | "
            f"{row['accepted_for_continuation']} |"
        )
    lines.extend(
        [
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
    parser.add_argument("--run-id", default="fml_fairness_evaluator_stress_replay_20260602_180000")
    parser.add_argument("--utility-floor", type=float, default=0.65)
    args = parser.parse_args()

    raw = {name: _load_metrics(path) for name, path in VARIANT_PATHS.items()}
    baseline_fairness = raw["baseline_reference"]["abs_demographic_parity_diff_mean"]
    scores = {
        name: _score(metrics, utility_floor=args.utility_floor, baseline_fairness=baseline_fairness)
        for name, metrics in raw.items()
    }
    primary_winner = _winner(scores, "primary_only_score")
    accepted = [
        name
        for name, row in scores.items()
        if name != "baseline_reference" and row["accepted_for_continuation"]
    ]
    evaluator_decision = "continue_" + accepted[0] if accepted else "abort_no_valid_non_degenerate_improvement"
    primary_gaming_incidents = int(primary_winner == "metric_gaming_all_negative")
    stress_gaming_incidents = int(evaluator_decision == "continue_metric_gaming_all_negative")

    out_dir = EXPERIMENT_DIR / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "pass",
        "benchmark": "FML-Bench Fairness_fairlearn",
        "metric": "abs_demographic_parity_diff_mean",
        "metric_direction": "lower",
        "linked_live_skill_invocation": _rel(LIVE_SKILL_SUMMARY),
        "source_artifacts": {name: _rel(path) for name, path in VARIANT_PATHS.items()},
        "scores": scores,
        "primary_only_winner": primary_winner,
        "evaluator_stress_decision": evaluator_decision,
        "primary_only_metric_gaming_incidents": primary_gaming_incidents,
        "evaluator_stress_metric_gaming_incidents": stress_gaming_incidents,
        "metric_gaming_incidents_reduced": primary_gaming_incidents - stress_gaming_incidents,
        "interpretation": (
            "On archived FML-Bench Fairness_fairlearn outputs, the primary fairness metric alone "
            "selects the degenerate all-negative predictor because it achieves zero demographic "
            "parity difference. The evaluator-stress gate rejects that branch with a balanced-"
            "accuracy utility floor and also refuses to continue the API-repaired candidate because "
            "it worsens the baseline fairness metric. The correct gate action is therefore to abort "
            "the Fairness continuation until a non-degenerate candidate improves both fairness and "
            "utility constraints."
        ),
        "claim_boundary": (
            "This is a replay over archived real FML-Bench Fairness_fairlearn evaluation artifacts. "
            "It supports evaluator-gate design against metric gaming, but it does not show a "
            "Fairness improvement, does not rerun the remote benchmark, and does not prove that "
            "IGRE improves average benchmark performance."
        ),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps({"summary": _rel(out_dir / "summary.json"), "status": summary["status"]}, indent=2))


if __name__ == "__main__":
    main()
