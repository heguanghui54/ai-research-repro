#!/usr/bin/env python3
"""Run a deterministic evaluator-stress smoke for metric gaming.

This connects the live reusable-skill invocation to an actual machine-graded
evaluator. The toy benchmark is intentionally small: it shows that a primary
fairness metric alone can select a degenerate classifier, while an IGRE
evaluator-stress gate rejects that branch with a utility guardrail.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
LIVE_SKILL_DIR = DOC_DIR / "experiments" / "live_skill_invocation_smoke_20260602_170000"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _balanced_accuracy(y_true: list[int], y_pred: list[int]) -> float:
    positives = [i for i, y in enumerate(y_true) if y == 1]
    negatives = [i for i, y in enumerate(y_true) if y == 0]
    tpr = sum(y_pred[i] == 1 for i in positives) / len(positives)
    tnr = sum(y_pred[i] == 0 for i in negatives) / len(negatives)
    return (tpr + tnr) / 2


def _demographic_parity_difference(groups: list[int], y_pred: list[int]) -> float:
    rates = []
    for group in sorted(set(groups)):
        indexes = [i for i, value in enumerate(groups) if value == group]
        rates.append(mean(y_pred[i] for i in indexes))
    return max(rates) - min(rates)


def _evaluate(y_true: list[int], groups: list[int], y_pred: list[int], *, utility_floor: float) -> dict[str, Any]:
    dp = _demographic_parity_difference(groups, y_pred)
    bal_acc = _balanced_accuracy(y_true, y_pred)
    primary_score = -dp
    guardrail_pass = bal_acc >= utility_floor
    stressed_score = primary_score if guardrail_pass else -999.0
    return {
        "demographic_parity_difference": round(dp, 6),
        "balanced_accuracy": round(bal_acc, 6),
        "primary_only_score": round(primary_score, 6),
        "utility_floor": utility_floor,
        "guardrail_pass": guardrail_pass,
        "evaluator_stress_score": round(stressed_score, 6),
    }


def _winner(rows: dict[str, dict[str, Any]], score_key: str) -> str:
    return max(rows.items(), key=lambda item: item[1][score_key])[0]


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Metric-Gaming Evaluator-Stress Smoke",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Status: `{summary['status']}`",
        f"- Linked live skill invocation: `{summary['linked_live_skill_invocation']}`",
        f"- Primary-only winner: `{summary['primary_only_winner']}`",
        f"- Evaluator-stress winner: `{summary['evaluator_stress_winner']}`",
        f"- Metric-gaming incidents reduced: `{summary['metric_gaming_incidents_reduced']}`",
        "",
        "## Scores",
        "",
        "| Candidate | Demographic parity diff | Balanced accuracy | Primary-only score | Guardrail pass | Evaluator-stress score |",
        "| --- | ---: | ---: | ---: | --- | ---: |",
    ]
    for name, row in summary["scores"].items():
        lines.append(
            f"| `{name}` | {row['demographic_parity_difference']:.6f} | "
            f"{row['balanced_accuracy']:.6f} | {row['primary_only_score']:.6f} | "
            f"{row['guardrail_pass']} | {row['evaluator_stress_score']:.6f} |"
        )
    lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"], ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="metric_gaming_evaluator_stress_smoke_20260602_171500")
    parser.add_argument("--utility-floor", type=float, default=0.65)
    args = parser.parse_args()

    # A tiny binary classification fixture with two sensitive groups. The data
    # are constructed so that an all-negative predictor has perfect demographic
    # parity but unacceptable utility.
    y_true = [1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1]
    groups = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
    predictions = {
        "baseline_threshold_model": [1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        "metric_gaming_all_negative": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "guardrailed_utility_model": [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1],
    }
    scores = {
        name: _evaluate(y_true, groups, pred, utility_floor=args.utility_floor)
        for name, pred in predictions.items()
    }
    primary_winner = _winner(scores, "primary_only_score")
    stressed_winner = _winner(scores, "evaluator_stress_score")
    primary_gaming_incidents = int(primary_winner == "metric_gaming_all_negative")
    stressed_gaming_incidents = int(stressed_winner == "metric_gaming_all_negative")
    incident_reduction = primary_gaming_incidents - stressed_gaming_incidents

    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    linked = _rel(LIVE_SKILL_DIR / "summary.json")
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "pass",
        "linked_live_skill_invocation": linked,
        "dataset": {
            "y_true": y_true,
            "sensitive_group": groups,
            "candidate_predictions": predictions,
        },
        "scores": scores,
        "primary_only_winner": primary_winner,
        "evaluator_stress_winner": stressed_winner,
        "primary_only_metric_gaming_incidents": primary_gaming_incidents,
        "evaluator_stress_metric_gaming_incidents": stressed_gaming_incidents,
        "metric_gaming_incidents_reduced": incident_reduction,
        "claim_boundary": (
            "This is a deterministic evaluator-stress smoke linked to the live skill invocation. "
            "It demonstrates that a multi-metric guardrail can reject one synthetic metric-gaming "
            "candidate. It is not an FML-bench result, not a human-subject study, and not evidence "
            "that IGRE improves average benchmark performance."
        ),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps({"summary": _rel(out_dir / "summary.json"), "status": summary["status"]}, indent=2))


if __name__ == "__main__":
    main()
