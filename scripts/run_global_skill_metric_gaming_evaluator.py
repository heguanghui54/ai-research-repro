#!/usr/bin/env python3
"""Run an executable evaluator-stress smoke tied to the global skill reuse task."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
SOURCE_DIR = DOC_DIR / "experiments" / "global_skill_reuse_smoke_20260603"
MANIFEST_PATH = DOC_DIR / "repro_manifest.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _balanced_accuracy(y_true: list[int], y_pred: list[int]) -> float:
    positives = [idx for idx, label in enumerate(y_true) if label == 1]
    negatives = [idx for idx, label in enumerate(y_true) if label == 0]
    tpr = sum(y_pred[idx] == 1 for idx in positives) / len(positives)
    tnr = sum(y_pred[idx] == 0 for idx in negatives) / len(negatives)
    return (tpr + tnr) / 2


def _demographic_parity_difference(groups: list[int], y_pred: list[int]) -> float:
    positive_rates = []
    for group in sorted(set(groups)):
        indexes = [idx for idx, value in enumerate(groups) if value == group]
        positive_rates.append(mean(y_pred[idx] for idx in indexes))
    return max(positive_rates) - min(positive_rates)


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


def _winner(scores: dict[str, dict[str, Any]], key: str) -> str:
    return max(scores.items(), key=lambda item: item[1][key])[0]


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Global Skill Metric-Gaming Evaluator Smoke",
        "",
        f"- Run id: `{summary['run_id']}`",
        f"- Status: `{summary['status']}`",
        f"- Source global skill reuse smoke: `{summary['source_global_skill_reuse_smoke']}`",
        f"- Gate decision: `{summary['source_gate_decision']}`",
        f"- Primary-only winner: `{summary['primary_only_winner']}`",
        f"- Evaluator-stress winner: `{summary['evaluator_stress_winner']}`",
        f"- Metric-gaming incidents reduced: `{summary['metric_gaming_incidents_reduced']}`",
        "",
        "## Scores",
        "",
        "| Candidate | DP diff | Balanced accuracy | Primary-only score | Guardrail pass | Evaluator-stress score |",
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


def _update_manifest(paths: list[Path], summary: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["global_skill_metric_gaming_evaluator_smoke"] = {
        "status": summary["status"],
        "summary": _rel(paths[0]),
        "markdown": _rel(paths[1]),
        "source_global_skill_reuse_smoke": summary["source_global_skill_reuse_smoke"],
        "metric_gaming_incidents_reduced": summary["metric_gaming_incidents_reduced"],
        "claim_boundary": summary["claim_boundary"],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="global_skill_metric_gaming_evaluator_20260603")
    parser.add_argument("--utility-floor", type=float, default=0.65)
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    source_summary_path = SOURCE_DIR / "summary.json"
    source_gate_path = SOURCE_DIR / "human_gate_log.json"
    if not source_summary_path.exists():
        errors.append("source global skill reuse summary is missing")
        source_summary: dict[str, Any] = {}
    else:
        source_summary = json.loads(source_summary_path.read_text(encoding="utf-8"))
    if not source_gate_path.exists():
        errors.append("source global skill reuse gate log is missing")
        source_gate: dict[str, Any] = {}
    else:
        source_gate = json.loads(source_gate_path.read_text(encoding="utf-8"))

    source_decision = source_gate.get("human_decision")
    if source_decision != "guarded_evaluator":
        errors.append("source global skill gate did not select guarded_evaluator")

    # The fixture intentionally creates a metric-gaming candidate: all-negative
    # predictions have perfect demographic parity but unusable utility.
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
    if incident_reduction < 1:
        errors.append("evaluator-stress guardrail did not reduce the metric-gaming incident")
    if stressed_winner != "guardrailed_utility_model":
        warnings.append("evaluator-stress winner was not the named guarded utility model")

    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "pass" if not errors else "fail",
        "source_global_skill_reuse_smoke": _rel(source_summary_path),
        "source_gate_log": _rel(source_gate_path),
        "source_gate_decision": source_decision,
        "source_generated_from_global_install": source_summary.get("generated_from_global_install"),
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
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "This executable toy evaluator is tied to the globally installed "
            "skill reuse smoke. It shows that the fresh evaluator-stress gate's "
            "guarded_evaluator decision rejects one synthetic metric-gaming "
            "winner. It is not an official benchmark, not human evidence, and "
            "not proof of average co-pilot superiority."
        ),
    }
    summary_path = out_dir / "summary.json"
    md_path = out_dir / "README.md"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(summary), encoding="utf-8")

    if args.update_manifest:
        _update_manifest([summary_path, md_path, Path(__file__)], summary)

    print(json.dumps({"summary": _rel(summary_path), "markdown": _rel(md_path), "status": summary["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
