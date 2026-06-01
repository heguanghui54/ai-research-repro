#!/usr/bin/env python3
"""Assemble a reproducible Co-Pilot AI Scientist v3 full-gate trajectory.

This runner makes one continuous sequence of gate decisions from existing
experiment artifacts. It is intentionally conservative: it does not claim to
launch a fresh AI Scientist-v2 or OpenEvolve run. Instead, it verifies that the
current artifact package can be traversed end-to-end by the proposed gate
logic, with every decision grounded in a logged result.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _primary_metric(summary: dict[str, Any]) -> float:
    result = summary["test_result"]
    return float(result["primary_metric"])


def _step_metric(step: dict[str, Any]) -> float | None:
    try:
        return float(step["val_result"]["filtered_results"]["ihdp_test"]["means"]["mae_mean"])
    except KeyError:
        return None


def build_trajectory() -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    candidates = _read_json(DOC_DIR / "candidates.json")
    fml_frontier = _read_json(EXP_DIR / "fml_online_branch_gate_drafts" / "summary.json")
    fml_continuation = _read_json(EXP_DIR / "fml_selected_branch_continuation" / "summary.json")
    fml_autonomous = _read_json(EXP_DIR / "fml_autonomous_matched_budget_4step" / "summary.json")
    knapsack_direct = _read_json(EXP_DIR / "knapsack_direct_baseline" / "summary.json")
    knapsack_openevolve = _read_json(EXP_DIR / "knapsack_openevolve_5iter" / "summary.json")
    vectorization = _read_json(EXP_DIR / "mlagentbench_vectorization_multiseed_summary.json")
    tabular = _read_json(EXP_DIR / "sklearn_diabetes_tabular_summary.json")

    best_direction = candidates["current_best_direction"]
    candidate_options = [
        {
            "option_id": item["id"],
            "summary": item["title"],
            "score": (
                item["scores"]["novelty"]
                + item["scores"]["testability"]
                + item["scores"]["paper_value"]
                + item["scores"]["human_leverage"]
                - item["scores"]["risk"]
            ),
            "evidence": [item["minimal_experiment"], item["evaluation_target"]],
            "risks": [item["main_risk"]],
        }
        for item in candidates["candidates"]
    ]

    branch_steps = []
    for step in fml_frontier["val_steps"]:
        metric = _step_metric(step)
        if metric is None:
            continue
        branch_steps.append(
            {
                "option_id": f"step_{step['step_id']:04d}",
                "summary": f"{step['action']} branch {step['idea_id']} on Causality_causalml",
                "score": metric,
                "evidence": [f"validation_mae={metric:.6f}", "lower_is_better"],
                "risks": ["Only two-draft frontier; not a statistical comparison."],
            }
        )
    selected_branch = min(branch_steps, key=lambda item: item["score"])

    direct_knapsack = float(knapsack_direct["metrics"]["combined_score"])
    openevolve_knapsack = float(knapsack_openevolve["best_score"])
    vectorization_speedup = float(vectorization["aggregate"]["median_speedup_over_starter"])
    tabular_direct = float(tabular["direct_deepseek_rewrite"]["mean_rmse"])
    tabular_oe = float(tabular["openevolve_3iter"]["median_rmse"])

    gated_test = _primary_metric(fml_continuation)
    autonomous_test = _primary_metric(fml_autonomous)
    lower_is_better_delta = autonomous_test - gated_test

    gates = [
        {
            "gate_id": "idea_gate_executable_trace_001",
            "gate_type": "idea_selection",
            "timestamp_utc": timestamp,
            "research_task_id": "copilot_v3_executable_full_gate_trace",
            "options": candidate_options,
            "human_decision": best_direction,
            "rationale": (
                "Select the narrow human-gated tree-search contribution because it is the "
                "most experimentally defensible core and can absorb Co-Scientist and "
                "OpenEvolve modules as supporting layers."
            ),
            "affected_artifacts": ["docs/co_pilot_ai_scientist_v3/candidates.json"],
            "downstream_budget": {"next_gate": "evaluator_gate_executable_trace_001"},
            "follow_up_checks": ["Keep full-system superiority as an unproven target claim."],
        },
        {
            "gate_id": "evaluator_gate_executable_trace_001",
            "gate_type": "evaluator_approval",
            "timestamp_utc": timestamp,
            "research_task_id": "copilot_v3_executable_full_gate_trace",
            "options": [
                {
                    "option_id": "primary_metric_only",
                    "summary": "Accept candidates using only their target metric.",
                    "score": None,
                    "evidence": ["Fairness degenerate predictor can game demographic parity."],
                    "risks": ["Metric gaming and non-executable branches can pass too late."],
                },
                {
                    "option_id": "correctness_and_utility_guardrails",
                    "summary": "Require execution/correctness checks and task-utility floors before continuation.",
                    "score": 1.0,
                    "evidence": [
                        "MLAgentBench vectorization direct rewrite failed correctness gate.",
                        "Fairness repair probe shows single-metric gaming risk.",
                    ],
                    "risks": ["May reject some creative but initially incomplete branches."],
                },
            ],
            "human_decision": "correctness_and_utility_guardrails",
            "rationale": (
                "The current artifact set contains both invalid fast code and fairness "
                "metric-gaming examples, so the evaluator gate must approve guardrails before "
                "additional search budget is spent."
            ),
            "affected_artifacts": [
                "docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_multiseed_summary.json",
                "docs/co_pilot_ai_scientist_v3/experiments/fml_fairness_evaluator_gate_repair_summary.json",
            ],
            "downstream_budget": {"next_gate": "branch_gate_executable_trace_001"},
            "follow_up_checks": ["Report invalid or metric-gamed candidates as failures, not wins."],
        },
        {
            "gate_id": "branch_gate_executable_trace_001",
            "gate_type": "branch_selection",
            "timestamp_utc": timestamp,
            "research_task_id": "copilot_v3_executable_full_gate_trace",
            "options": branch_steps,
            "human_decision": selected_branch["option_id"],
            "rationale": (
                f"Select the lower-validation-MAE branch from the live Causality frontier "
                f"({selected_branch['score']:.6f})."
            ),
            "affected_artifacts": [
                "docs/co_pilot_ai_scientist_v3/experiments/fml_online_branch_gate_drafts/summary.json",
                "docs/co_pilot_ai_scientist_v3/experiments/fml_selected_branch_continuation/summary.json",
            ],
            "downstream_budget": {
                "selected_snapshot_continuation_steps": fml_continuation["total_steps"],
                "continuation_test_mae": gated_test,
            },
            "follow_up_checks": ["Compare selected continuation with an equal-budget autonomous baseline."],
        },
        {
            "gate_id": "program_search_gate_executable_trace_001",
            "gate_type": "program_search_escalation",
            "timestamp_utc": timestamp,
            "research_task_id": "copilot_v3_executable_full_gate_trace",
            "options": [
                {
                    "option_id": "direct_edit_only",
                    "summary": "Use direct LLM edits for all machine-gradeable subproblems.",
                    "score": direct_knapsack,
                    "evidence": [
                        f"Knapsack direct score={direct_knapsack:.6f}",
                        f"Sklearn direct RMSE={tabular_direct:.6f}",
                    ],
                    "risks": ["Can fail correctness gates on vectorization and may under-explore combinatorial tasks."],
                },
                {
                    "option_id": "selective_openevolve",
                    "summary": "Escalate richer automatic-evaluator subproblems to OpenEvolve.",
                    "score": openevolve_knapsack,
                    "evidence": [
                        f"Knapsack OpenEvolve score={openevolve_knapsack:.6f}",
                        f"MLAgentBench vectorization median speedup={vectorization_speedup:.2f}x",
                        f"Sklearn median OpenEvolve RMSE={tabular_oe:.6f}",
                    ],
                    "risks": ["Tiny-budget search is seed-sensitive and does not always beat direct editing."],
                },
            ],
            "human_decision": "selective_openevolve",
            "rationale": (
                "Escalate selectively: OpenEvolve is useful for richer or correctness-gated "
                "subproblems, while the sklearn tabular result shows direct editing can match it "
                "on standard small modeling changes."
            ),
            "affected_artifacts": [
                "docs/co_pilot_ai_scientist_v3/experiments/knapsack_program_search_comparison.md",
                "docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_comparison.md",
                "docs/co_pilot_ai_scientist_v3/experiments/sklearn_diabetes_tabular_comparison.md",
            ],
            "downstream_budget": {"next_gate": "claim_gate_executable_trace_001"},
            "follow_up_checks": ["Require direct-edit baselines before claiming program-search gains."],
        },
        {
            "gate_id": "claim_gate_executable_trace_001",
            "gate_type": "claim_audit",
            "timestamp_utc": timestamp,
            "research_task_id": "copilot_v3_executable_full_gate_trace",
            "options": [
                {
                    "option_id": "claim_human_gate_superiority",
                    "summary": "Claim that Co-Pilot v3 outperforms autonomous AI Scientist-v2.",
                    "score": None,
                    "evidence": [f"Pair-1 gated test MAE={gated_test:.6f}; autonomous={autonomous_test:.6f}"],
                    "risks": ["Current broader matched evidence is mixed and too small."],
                },
                {
                    "option_id": "claim_feasibility_and_boundary_conditions",
                    "summary": "Claim feasibility, evaluability, and boundary conditions while reserving superiority claims.",
                    "score": 1.0,
                    "evidence": [
                        "Branch gate and continuation are executable.",
                        "Program-search escalation has positive and boundary-condition probes.",
                        "Paper-quality reviews ask for more matched tasks and seeds.",
                    ],
                    "risks": ["A narrower claim is less ambitious but better supported."],
                },
            ],
            "human_decision": "claim_feasibility_and_boundary_conditions",
            "rationale": (
                "The selected continuation beats the first matched autonomous baseline by "
                f"{lower_is_better_delta:.6f} MAE in this pair, but the full evidence set is "
                "still mixed. The paper should claim an executable co-pilot architecture and "
                "logged boundary conditions, not general superiority."
            ),
            "affected_artifacts": [
                "docs/co_pilot_ai_scientist_v3/paper_en.md",
                "docs/co_pilot_ai_scientist_v3/paper_zh.md",
                "docs/co_pilot_ai_scientist_v3/audits/claim_evidence_audit.md",
            ],
            "downstream_budget": {
                "next_required_run": "single online four-loop trajectory with equal-budget autonomous baseline"
            },
            "follow_up_checks": [
                "Run more matched tasks and seeds.",
                "Add independent paper-quality ratings after a true online full trajectory.",
            ],
        },
    ]

    return {
        "trajectory_id": "copilot_v3_executable_full_gate_trace_001",
        "generated_at_utc": timestamp,
        "mode": "executable_artifact_replay",
        "is_single_online_training_run": False,
        "claim_scope": (
            "This is one continuous executable traversal over archived experiment artifacts. "
            "It verifies gate logic and evidence linkage, but it is not a fresh online run of "
            "all four loops."
        ),
        "gates": gates,
        "summary": {
            "selected_research_direction": best_direction,
            "selected_branch": selected_branch["option_id"],
            "selected_branch_val_mae": selected_branch["score"],
            "selected_continuation_test_mae": gated_test,
            "matched_autonomous_test_mae": autonomous_test,
            "pair1_test_mae_delta_autonomous_minus_gated": lower_is_better_delta,
            "knapsack_direct_score": direct_knapsack,
            "knapsack_openevolve_score": openevolve_knapsack,
            "mlagentbench_vectorization_median_speedup": vectorization_speedup,
            "sklearn_direct_rmse": tabular_direct,
            "sklearn_openevolve_median_rmse": tabular_oe,
        },
        "remaining_gap": (
            "A true online full-gate experiment must generate ideas, approve evaluators, "
            "select branches, run program search, and audit claims in one continuous run, then "
            "compare against a matched autonomous baseline."
        ),
    }


def write_markdown(path: Path, trajectory: dict[str, Any]) -> None:
    lines = [
        "# Executable Full-Gate Trajectory",
        "",
        f"- Trajectory ID: `{trajectory['trajectory_id']}`",
        f"- Generated at: `{trajectory['generated_at_utc']}`",
        f"- Mode: `{trajectory['mode']}`",
        f"- Single online training run: `{trajectory['is_single_online_training_run']}`",
        "",
        trajectory["claim_scope"],
        "",
        "## Gate Decisions",
        "",
    ]
    for gate in trajectory["gates"]:
        lines.extend(
            [
                f"### {gate['gate_id']}",
                "",
                f"- Type: `{gate['gate_type']}`",
                f"- Decision: `{gate['human_decision']}`",
                f"- Rationale: {gate['rationale']}",
                "- Affected artifacts:",
            ]
        )
        lines.extend(f"  - `{artifact}`" for artifact in gate["affected_artifacts"])
        lines.append("")

    lines.extend(
        [
            "## Summary Metrics",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
        ]
    )
    for key, value in trajectory["summary"].items():
        if isinstance(value, float):
            display = f"{value:.6f}"
        else:
            display = f"`{value}`"
        lines.append(f"| `{key}` | {display} |")
    lines.extend(["", "## Remaining Gap", "", trajectory["remaining_gap"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=EXP_DIR / "full_gate_executable_trace",
        help="Directory where trajectory.json and README.md will be written.",
    )
    args = parser.parse_args()

    trajectory = build_trajectory()
    _write_json(args.output_dir / "trajectory.json", trajectory)
    write_markdown(args.output_dir / "README.md", trajectory)
    print(args.output_dir / "trajectory.json")
    print(args.output_dir / "README.md")


if __name__ == "__main__":
    main()
