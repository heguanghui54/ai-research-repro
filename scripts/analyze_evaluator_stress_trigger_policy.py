#!/usr/bin/env python3
"""Analyze trigger policies for the open-data evaluator-stress gate.

This turns the multi-seed open-data pilot into participation-mode design
evidence. The question is not whether the evaluator-stress gate should always
override the autonomous selector, but when it should be triggered.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
PACKAGE_DIR = DOC_DIR / "experiments" / "prospective_matched_open_data_multitask_20260603"
AUDIT_DIR = DOC_DIR / "audits"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _dummy_val_accuracy(row: dict[str, Any]) -> float:
    dummy = next(item for item in row["candidate_table"] if item["candidate"] == "dummy_most_frequent")
    return float(dummy["metrics"]["val_accuracy"])


def _score_selection(selection: dict[str, Any]) -> float:
    return float(selection["metrics"]["test_balanced_accuracy"])


def _auto(row: dict[str, Any]) -> dict[str, Any]:
    return row["autonomous_selection"]


def _gate(row: dict[str, Any]) -> dict[str, Any]:
    return row["co_pilot_selection"]


def _best_candidate_by(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    return max(
        rows,
        key=lambda item: (
            item["metrics"][key],
            item["metrics"].get("val_macro_f1", 0.0),
            item["metrics"].get("val_accuracy", 0.0),
            item["candidate"],
        ),
    )


def _policy_rows(dataset_results: list[dict[str, Any]], policy_name: str) -> list[dict[str, Any]]:
    selected = []
    for row in dataset_results:
        auto = _auto(row)
        gate = _gate(row)
        dummy_acc = _dummy_val_accuracy(row)
        best_bal = _best_candidate_by(row["candidate_table"], "val_balanced_accuracy")
        best_acc = _best_candidate_by(row["candidate_table"], "val_accuracy")
        val_bal_gap = (
            best_bal["metrics"]["val_balanced_accuracy"]
            - best_acc["metrics"]["val_balanced_accuracy"]
        )

        if policy_name == "autonomous_accuracy_only":
            choice = auto
            triggered = False
        elif policy_name == "always_on_evaluator_stress":
            choice = gate
            triggered = auto["candidate"] != gate["candidate"]
        elif policy_name == "class_imbalance_trigger_0_90":
            triggered = dummy_acc >= 0.90
            choice = gate if triggered else auto
        elif policy_name == "class_imbalance_trigger_0_94":
            triggered = dummy_acc >= 0.94
            choice = gate if triggered else auto
        elif policy_name == "validation_balanced_gap_trigger_0_02":
            triggered = val_bal_gap >= 0.02
            choice = gate if triggered else auto
        elif policy_name == "hybrid_imbalance_or_gap_trigger":
            triggered = dummy_acc >= 0.90 or val_bal_gap >= 0.02
            choice = gate if triggered else auto
        else:
            raise ValueError(f"unknown policy: {policy_name}")

        selected.append(
            {
                "split_seed": row["split_seed"],
                "dataset": row["dataset"],
                "policy": policy_name,
                "dummy_val_accuracy": dummy_acc,
                "val_balanced_gap_best_balanced_minus_best_accuracy": float(val_bal_gap),
                "triggered": triggered,
                "candidate": choice["candidate"],
                "test_balanced_accuracy": _score_selection(choice),
                "autonomous_test_balanced_accuracy": _score_selection(auto),
                "always_gate_test_balanced_accuracy": _score_selection(gate),
                "delta_vs_autonomous": _score_selection(choice) - _score_selection(auto),
            }
        )
    return selected


def _summarize_policy(rows: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = [row["delta_vs_autonomous"] for row in rows]
    scores = [row["test_balanced_accuracy"] for row in rows]
    return {
        "mean_test_balanced_accuracy": float(mean(scores)),
        "delta_vs_autonomous_mean": float(mean(deltas)),
        "wins_vs_autonomous": sum(1 for value in deltas if value > 1e-12),
        "losses_vs_autonomous": sum(1 for value in deltas if value < -1e-12),
        "ties_vs_autonomous": sum(1 for value in deltas if abs(value) <= 1e-12),
        "triggered_count": sum(1 for row in rows if row["triggered"]),
    }


def _dataset_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for dataset in sorted({row["dataset"] for row in rows}):
        subset = [row for row in rows if row["dataset"] == dataset]
        deltas = [row["delta_vs_autonomous"] for row in subset]
        out.append(
            {
                "dataset": dataset,
                "split_count": len(subset),
                "delta_vs_autonomous_mean": float(mean(deltas)),
                "wins": sum(1 for value in deltas if value > 1e-12),
                "losses": sum(1 for value in deltas if value < -1e-12),
                "ties": sum(1 for value in deltas if abs(value) <= 1e-12),
                "triggered_count": sum(1 for row in subset if row["triggered"]),
            }
        )
    return out


def _update_manifest(summary_path: Path, md_path: Path) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    if not manifest_path.exists():
        return
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in [summary_path, md_path, Path(__file__)]:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["evaluator_stress_trigger_policy_analysis"] = {
        "status": "pass",
        "script": "scripts/analyze_evaluator_stress_trigger_policy.py",
        "summary": _rel(md_path),
        "json": _rel(summary_path),
        "claim_boundary": (
            "trigger-policy design evidence from an existing open-data pilot; "
            "not a new independent benchmark run"
        ),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    metrics = _load_json(PACKAGE_DIR / "remote_metrics.json")
    dataset_results = metrics["dataset_results"]
    policies = [
        "autonomous_accuracy_only",
        "always_on_evaluator_stress",
        "class_imbalance_trigger_0_90",
        "class_imbalance_trigger_0_94",
        "validation_balanced_gap_trigger_0_02",
        "hybrid_imbalance_or_gap_trigger",
    ]
    policy_rows = {policy: _policy_rows(dataset_results, policy) for policy in policies}
    policy_summaries = {
        policy: _summarize_policy(rows) for policy, rows in policy_rows.items()
    }
    best_policy = max(
        policies,
        key=lambda policy: (
            policy_summaries[policy]["delta_vs_autonomous_mean"],
            -policy_summaries[policy]["losses_vs_autonomous"],
            -policy_summaries[policy]["triggered_count"],
        ),
    )
    always = policy_summaries["always_on_evaluator_stress"]
    best = policy_summaries[best_policy]
    summary = {
        "status": "pass",
        "source_metrics": _rel(PACKAGE_DIR / "remote_metrics.json"),
        "dataset_count": metrics["dataset_count"],
        "split_count": metrics["split_count"],
        "total_dataset_split_evaluations": metrics["total_dataset_split_evaluations"],
        "policies": policy_summaries,
        "best_policy": best_policy,
        "best_policy_dataset_summary": _dataset_summary(policy_rows[best_policy]),
        "always_on_dataset_summary": _dataset_summary(policy_rows["always_on_evaluator_stress"]),
        "overreach_reduction": {
            "always_on_losses": always["losses_vs_autonomous"],
            "best_policy_losses": best["losses_vs_autonomous"],
            "always_on_triggered_count": always["triggered_count"],
            "best_policy_triggered_count": best["triggered_count"],
            "always_on_delta_vs_autonomous_mean": always["delta_vs_autonomous_mean"],
            "best_policy_delta_vs_autonomous_mean": best["delta_vs_autonomous_mean"],
        },
        "claim_boundary": (
            "This is a post-hoc trigger-policy analysis over one archived pilot. "
            "It supports a design rule for future prospective evaluator gates, "
            "not a broad performance claim."
        ),
    }

    json_path = PACKAGE_DIR / "evaluator_stress_trigger_policy_summary.json"
    md_path = PACKAGE_DIR / "evaluator_stress_trigger_policy_summary.md"
    _write_json(json_path, summary)

    lines = [
        "# Evaluator-Stress Trigger Policy Analysis",
        "",
        "This analysis uses the archived multi-seed open-data pilot to test whether",
        "the evaluator-stress gate should be always on or triggered only when the",
        "validation data indicate evaluator risk.",
        "",
        "## Aggregate Policy Results",
        "",
        "| Policy | Mean test balanced accuracy | Delta vs autonomous | Wins | Losses | Ties | Triggered |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for policy in policies:
        item = policy_summaries[policy]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{policy}`",
                    f"{item['mean_test_balanced_accuracy']:.6f}",
                    f"{item['delta_vs_autonomous_mean']:.6f}",
                    str(item["wins_vs_autonomous"]),
                    str(item["losses_vs_autonomous"]),
                    str(item["ties_vs_autonomous"]),
                    str(item["triggered_count"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            f"Best policy by mean delta with loss/trigger parsimony tie-breaks: `{best_policy}`.",
            "",
            "## Best Policy Dataset Summary",
            "",
            "| Dataset | Splits | Delta vs autonomous | Wins | Losses | Ties | Triggered |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in summary["best_policy_dataset_summary"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["dataset"],
                    str(row["split_count"]),
                    f"{row['delta_vs_autonomous_mean']:.6f}",
                    str(row["wins"]),
                    str(row["losses"]),
                    str(row["ties"]),
                    str(row["triggered_count"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The always-on evaluator-stress gate is mixed: it improves the "
                "synthetic imbalance stress case but creates small overreach losses on "
                "breast cancer. A class-imbalance trigger based on the validation "
                "majority baseline keeps the imbalance benefit while avoiding those "
                "clean-task losses in this pilot."
            ),
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    _update_manifest(json_path, md_path)
    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "best_policy": best_policy}, indent=2))


if __name__ == "__main__":
    main()
