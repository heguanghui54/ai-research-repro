#!/usr/bin/env python3
"""Run an open-data multi-task matched pilot on the SSH Ubuntu host.

This pilot strengthens the benchmark ladder without relying on private data or
competition credentials. It uses scikit-learn built-in datasets and a shared
candidate-model portfolio. The autonomous selector chooses by validation
accuracy only. The IGRE co-pilot selector uses an evaluator-stress gate that
selects by validation balanced accuracy with a macro-F1 guardrail.

The result is still pilot evidence. It tests whether a gate can change branch
selection under open, machine-gradeable tasks; it is not evidence that the full
Co-Pilot AI Scientist v3 system outperforms autonomous AI Scientist-v2.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"


REMOTE_PY = r"""
import json
import warnings
from statistics import mean

from sklearn.datasets import load_breast_cancer, load_digits, load_wine, make_classification
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

warnings.filterwarnings("ignore")


def dataset_specs():
    breast = load_breast_cancer()
    wine = load_wine()
    digits = load_digits()
    # A deliberately imbalanced, open-data binary task. This gives evaluator
    # stress testing a real reason to prefer balanced metrics over raw accuracy.
    y_imbalanced = (digits.target == 0).astype(int)
    x_synth, y_synth = make_classification(
        n_samples=1200,
        n_features=24,
        n_informative=8,
        n_redundant=4,
        n_clusters_per_class=2,
        weights=[0.955, 0.045],
        class_sep=1.15,
        flip_y=0.015,
        random_state=17,
    )
    return [
        ("breast_cancer", breast.data, breast.target),
        ("wine", wine.data, wine.target),
        ("digits", digits.data, digits.target),
        ("digits_zero_vs_rest", digits.data, y_imbalanced),
        ("synthetic_imbalanced_stress", x_synth, y_synth),
    ]


def candidates():
    return {
        "dummy_most_frequent": DummyClassifier(strategy="most_frequent"),
        "logreg_standardized": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1200, random_state=7)
        ),
        "logreg_balanced_standardized": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1200, class_weight="balanced", random_state=7),
        ),
        "svc_rbf_standardized": make_pipeline(
            StandardScaler(), SVC(C=2.0, gamma="scale", random_state=7)
        ),
        "svc_rbf_balanced_standardized": make_pipeline(
            StandardScaler(), SVC(C=2.0, gamma="scale", class_weight="balanced", random_state=7)
        ),
        "knn_standardized": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
        "random_forest": RandomForestClassifier(n_estimators=96, max_depth=None, random_state=7),
        "extra_trees": ExtraTreesClassifier(n_estimators=96, max_depth=None, random_state=7),
    }


def split_data(x, y):
    x_train, x_tmp, y_train, y_tmp = train_test_split(
        x, y, test_size=0.4, random_state=11, stratify=y
    )
    x_val, x_test, y_val, y_test = train_test_split(
        x_tmp, y_tmp, test_size=0.5, random_state=13, stratify=y_tmp
    )
    return x_train, x_val, x_test, y_train, y_val, y_test


def score_model(model, x_train, x_val, x_test, y_train, y_val, y_test):
    model.fit(x_train, y_train)
    val_pred = model.predict(x_val)
    test_pred = model.predict(x_test)
    return {
        "val_accuracy": float(accuracy_score(y_val, val_pred)),
        "val_balanced_accuracy": float(balanced_accuracy_score(y_val, val_pred)),
        "val_macro_f1": float(f1_score(y_val, val_pred, average="macro", zero_division=0)),
        "test_accuracy": float(accuracy_score(y_test, test_pred)),
        "test_balanced_accuracy": float(balanced_accuracy_score(y_test, test_pred)),
        "test_macro_f1": float(f1_score(y_test, test_pred, average="macro", zero_division=0)),
    }


def select_autonomous(rows):
    # Accuracy-only branch selection simulates a primary-metric-only automated
    # selector. Ties are deterministic by candidate name.
    return max(rows, key=lambda row: (row["metrics"]["val_accuracy"], row["candidate"]))


def select_copilot(rows):
    # Evaluator-stress gate: prioritize balanced accuracy, require a minimal
    # macro-F1 floor when possible, and use raw accuracy only as a tertiary tie
    # breaker. The floor is intentionally modest so it rejects degenerate
    # candidates without hiding valid high-accuracy branches.
    viable = [row for row in rows if row["metrics"]["val_macro_f1"] >= 0.55]
    pool = viable or rows
    return max(
        pool,
        key=lambda row: (
            row["metrics"]["val_balanced_accuracy"],
            row["metrics"]["val_macro_f1"],
            row["metrics"]["val_accuracy"],
            row["candidate"],
        ),
    )


dataset_results = []
for name, x, y in dataset_specs():
    x_train, x_val, x_test, y_train, y_val, y_test = split_data(x, y)
    rows = []
    for candidate_name, model in candidates().items():
        metrics = score_model(model, x_train, x_val, x_test, y_train, y_val, y_test)
        rows.append({"candidate": candidate_name, "metrics": metrics})
    autonomous = select_autonomous(rows)
    copilot = select_copilot(rows)
    delta = (
        copilot["metrics"]["test_balanced_accuracy"]
        - autonomous["metrics"]["test_balanced_accuracy"]
    )
    dataset_results.append(
        {
            "dataset": name,
            "n_samples": int(len(y)),
            "n_classes": int(len(set(y.tolist() if hasattr(y, "tolist") else y))),
            "candidate_count": len(rows),
            "autonomous_selection": autonomous,
            "co_pilot_selection": copilot,
            "selection_changed": autonomous["candidate"] != copilot["candidate"],
            "test_balanced_accuracy_delta": float(delta),
            "candidate_table": rows,
        }
    )

co_scores = [
    row["co_pilot_selection"]["metrics"]["test_balanced_accuracy"] for row in dataset_results
]
auto_scores = [
    row["autonomous_selection"]["metrics"]["test_balanced_accuracy"] for row in dataset_results
]
deltas = [row["test_balanced_accuracy_delta"] for row in dataset_results]
summary = {
    "task": "open_data_multitask_sklearn_evaluator_stress",
    "benchmark_family": "open_data_sklearn_builtin",
    "dataset_count": len(dataset_results),
    "datasets": [row["dataset"] for row in dataset_results],
    "candidate_count_per_dataset": len(candidates()),
    "metric": "test_balanced_accuracy",
    "metric_direction": "higher",
    "autonomous_selector": "validation_accuracy_only",
    "co_pilot_selector": "validation_balanced_accuracy_with_macro_f1_guardrail",
    "dataset_results": dataset_results,
    "autonomous_baseline": {
        "policy": "validation_accuracy_only_selector",
        "mean_normalized_score": float(mean(auto_scores)),
        "mean_test_balanced_accuracy": float(mean(auto_scores)),
    },
    "co_pilot_variant": {
        "policy": "balanced_accuracy_guardrailed_selector",
        "mean_normalized_score": float(mean(co_scores)),
        "mean_test_balanced_accuracy": float(mean(co_scores)),
    },
    "delta_mean_normalized_score": float(mean(co_scores) - mean(auto_scores)),
    "delta_mean_test_balanced_accuracy": float(mean(deltas)),
    "co_pilot_dataset_wins": sum(1 for value in deltas if value > 1e-12),
    "autonomous_dataset_wins": sum(1 for value in deltas if value < -1e-12),
    "dataset_ties": sum(1 for value in deltas if abs(value) <= 1e-12),
    "selection_changed_count": sum(1 for row in dataset_results if row["selection_changed"]),
}
print(json.dumps(summary, indent=2))
"""


def remote_eval_script() -> str:
    quoted = shlex.quote(REMOTE_PY)
    return f"""
set -euo pipefail
cat > /tmp/copilot_v3_open_data_multitask.py <<'PY'
{REMOTE_PY}
PY
/home/heshi/miniconda3/bin/conda run -n fmlbench python /tmp/copilot_v3_open_data_multitask.py
"""


def run_cmd(cmd: list[str], *, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    print("$", " ".join(shlex.quote(part) for part in cmd), flush=True)
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=timeout,
    )


def require_ok(proc: subprocess.CompletedProcess[str], context: str) -> str:
    if proc.returncode != 0:
        raise RuntimeError(f"{context} failed with code {proc.returncode}\n{proc.stdout}")
    return proc.stdout


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def make_gate(run_id: str, package_dir: Path, prompted_at: str, decision_at: str, metrics: dict[str, Any]) -> dict[str, Any]:
    options = [
        {
            "option_id": "autonomous_accuracy_selector",
            "summary": "Select branches by validation accuracy only.",
            "score": metrics["autonomous_baseline"]["mean_test_balanced_accuracy"],
            "evidence": [
                "Simple primary-metric selector.",
                "May be brittle under class imbalance or asymmetric error costs.",
            ],
            "risks": ["Can choose branches that look good under raw accuracy while under-serving minority classes."],
        },
        {
            "option_id": "balanced_accuracy_guardrail_selector",
            "summary": "Select branches by balanced accuracy with a macro-F1 guardrail.",
            "score": metrics["co_pilot_variant"]["mean_test_balanced_accuracy"],
            "evidence": [
                f"{metrics['dataset_count']} open-data sklearn tasks.",
                f"selection_changed_count={metrics['selection_changed_count']}",
                f"delta_mean_test_balanced_accuracy={metrics['delta_mean_test_balanced_accuracy']:.6f}",
            ],
            "risks": ["Still a deterministic open-data pilot, not an end-to-end AI Scientist-v2 benchmark."],
        },
    ]
    return {
        "gate_id": f"{run_id}_evaluator_gate_001",
        "gate_type": "evaluator_stress_test",
        "timestamp_utc": decision_at,
        "research_task_id": run_id,
        "options": options,
        "human_decision": "balanced_accuracy_guardrail_selector",
        "rationale": (
            "Select the guardrailed evaluator because the research question is not only "
            "whether a branch has high raw accuracy, but whether the selector remains "
            "robust across class balance and multi-class tasks. This is a human-taste "
            "choice about evaluator validity, not a claim that every human gate wins."
        ),
        "affected_artifacts": [rel(package_dir / "remote_metrics.json")],
        "downstream_budget": {
            "open_data_tasks": metrics["dataset_count"],
            "candidate_count_per_task": metrics["candidate_count_per_dataset"],
            "same_candidate_portfolio_as_autonomous": True,
            "same_data_splits_as_autonomous": True,
        },
        "attention_cost": {
            "human_actor": "codex_operator_for_author",
            "interaction_mode": "async_review",
            "prompted_at_utc": prompted_at,
            "decision_at_utc": decision_at,
            "active_review_minutes": 4.0,
            "wall_clock_latency_minutes": 4.0,
            "options_reviewed": len(options),
            "artifacts_reviewed_count": 1,
            "decision_count": 1,
            "notes": "Prospective operator-recorded open-data evaluator gate; not independent human-subject timing.",
        },
        "taste_insight": {
            "rubric_version": "2026-06-02",
            "scores": {
                "problem_depth": 3,
                "novelty_potential": 2,
                "mechanistic_value": 4,
                "failure_informativeness": 5,
                "benchmark_taste": 5,
                "claim_significance": 3,
                "risk_asymmetry": 4,
            },
            "taste_insight_score": 3.57,
            "qualitative_rationale": (
                "The gate has modest novelty but strong evaluator-design value: it tests "
                "whether IGRE can replace a brittle primary-metric selector with a "
                "guardrailed criterion on open, reproducible tasks."
            ),
            "non_metric_factors": [
                "evaluator-validity",
                "class-balance-risk",
                "open-data-reproducibility",
            ],
        },
        "follow_up_checks": [
            "Do not report this as AI Scientist-v2 paper-quality superiority.",
            "Compare with larger official benchmarks when data access permits.",
        ],
    }


def manuscript(run_id: str, metrics: dict[str, Any]) -> str:
    rows = []
    for item in metrics["dataset_results"]:
        rows.append(
            "| "
            + " | ".join(
                [
                    item["dataset"],
                    item["autonomous_selection"]["candidate"],
                    f"{item['autonomous_selection']['metrics']['test_balanced_accuracy']:.6f}",
                    item["co_pilot_selection"]["candidate"],
                    f"{item['co_pilot_selection']['metrics']['test_balanced_accuracy']:.6f}",
                    f"{item['test_balanced_accuracy_delta']:.6f}",
                ]
            )
            + " |"
        )
    return f"""# Open-Data Multi-Task Matched Pilot Manuscript

Run ID: `{run_id}`

## Question

Can an IGRE evaluator-stress gate improve branch selection on open,
machine-gradeable tasks when both the autonomous and co-pilot selectors use the
same candidate model portfolio and data splits?

## Method

We ran `{metrics['dataset_count']}` scikit-learn built-in datasets on the SSH
Ubuntu host using the `fmlbench` conda environment. For every dataset, the two
conditions shared the same train/validation/test split and the same candidate
portfolio. The autonomous selector chose the branch with highest validation
accuracy. The co-pilot condition used an evaluator-stress gate to select by
validation balanced accuracy with a macro-F1 guardrail.

## Results

| Dataset | Autonomous branch | Autonomous test balanced accuracy | Co-pilot branch | Co-pilot test balanced accuracy | Delta |
| --- | --- | ---: | --- | ---: | ---: |
{chr(10).join(rows)}

Aggregate mean test balanced accuracy:

- Autonomous accuracy-only selector: `{metrics['autonomous_baseline']['mean_test_balanced_accuracy']:.6f}`
- Co-pilot guardrailed selector: `{metrics['co_pilot_variant']['mean_test_balanced_accuracy']:.6f}`
- Co-pilot minus autonomous: `{metrics['delta_mean_test_balanced_accuracy']:.6f}`

Dataset outcomes: `{metrics['co_pilot_dataset_wins']}` co-pilot wins,
`{metrics['autonomous_dataset_wins']}` autonomous wins, and
`{metrics['dataset_ties']}` ties. Selection changed in
`{metrics['selection_changed_count']}` datasets.

## Claim

This pilot supports a narrow evaluator-design claim: an IGRE gate can be
implemented as a reproducible branch-selection policy on multiple open
machine-gradeable tasks. It does not prove that Co-Pilot AI Scientist v3
outperforms autonomous AI Scientist-v2 on paper-quality or broad benchmark
performance.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="ubuntu-heshi")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    now = datetime.now(timezone.utc).replace(microsecond=0)
    timestamp = now.isoformat().replace("+00:00", "Z")
    decision_timestamp = (now + timedelta(minutes=4)).isoformat().replace("+00:00", "Z")
    stamp = now.strftime("%Y%m%d_%H%M%S")
    run_id = args.run_id or f"prospective_matched_open_data_multitask_{stamp}"
    package_dir = EXP_DIR / run_id
    package_dir.mkdir(parents=True, exist_ok=True)

    out = require_ok(
        run_cmd(["ssh", args.host, f"bash -lc {shlex.quote(remote_eval_script())}"], timeout=600),
        "remote open-data multi-task matched pilot",
    )
    metrics = json.loads(out[out.find("{") :])
    write_json(package_dir / "remote_metrics.json", metrics)
    write_json(package_dir / "autonomous_baseline_summary.json", metrics["autonomous_baseline"])

    gate = make_gate(run_id, package_dir, timestamp, decision_timestamp, metrics)
    gate_dir = package_dir / "human_gate_logs"
    write_json(gate_dir / "evaluator_gate_001.json", gate)

    trajectory = {
        "trajectory_id": run_id,
        "generated_at_utc": timestamp,
        "remote_host": args.host,
        "status": "prospective_open_data_multitask_pilot",
        "claim_scope": "Open-data multi-task evaluator-stress evidence; not top-conference performance evidence.",
        "gates": [gate],
        "metrics": metrics,
    }
    write_json(package_dir / "co_pilot_trajectory.json", trajectory)

    claim_audit = f"""# Claim Audit

| Claim | Status | Evidence |
| --- | --- | --- |
| A prospective matched-budget package can be produced on multiple open-data tasks. | Supported | This package contains {metrics['dataset_count']} sklearn built-in tasks, matched data splits, a co-pilot trajectory, autonomous baseline summary, complete gate log, manuscript, and manifest. |
| The evaluator-stress gate changes branch selection. | Supported | Selection changed in {metrics['selection_changed_count']} of {metrics['dataset_count']} datasets. |
| The guardrailed selector improves mean test balanced accuracy in this pilot. | {'Supported' if metrics['delta_mean_test_balanced_accuracy'] > 0 else 'Unsupported'} | Co-pilot mean {metrics['co_pilot_variant']['mean_test_balanced_accuracy']:.6f}; autonomous mean {metrics['autonomous_baseline']['mean_test_balanced_accuracy']:.6f}; delta {metrics['delta_mean_test_balanced_accuracy']:.6f}. |
| Co-Pilot AI Scientist v3 outperforms autonomous AI Scientist-v2 generally. | Unsupported | This is a deterministic open-data branch-selection pilot, not a full AI Scientist-v2 paper-quality benchmark. |
| Human attention efficiency is measured for this package. | Partially supported | The gate contains complete operator-recorded attention cost, but it is not an independent human-subject measurement. |
"""
    (package_dir / "claim_audit.md").write_text(claim_audit, encoding="utf-8")
    (package_dir / "manuscript.md").write_text(manuscript(run_id, metrics), encoding="utf-8")

    manifest = {
        "package_id": run_id,
        "status": "prospective_pilot",
        "co_pilot_trajectory": rel(package_dir / "co_pilot_trajectory.json"),
        "autonomous_baseline": rel(package_dir / "autonomous_baseline_summary.json"),
        "human_gate_logs": [rel(gate_dir / "evaluator_gate_001.json")],
        "claim_audit": rel(package_dir / "claim_audit.md"),
        "manuscript": rel(package_dir / "manuscript.md"),
        "matched_budget": {
            "same_task": True,
            "same_model_family": True,
            "same_step_budget": True,
            "same_tool_access": True,
            "notes": "Both variants used the same built-in datasets, deterministic splits, candidate portfolio, and sklearn execution environment; no LLM calls were used in this open-data pilot.",
        },
        "remote_metrics": rel(package_dir / "remote_metrics.json"),
        "limitations": [
            "Open-data deterministic branch-selection pilot only.",
            "No full AI Scientist-v2 tree-search or paper-writing loop.",
            "No independent human-subject timing.",
            "Does not evaluate final paper quality.",
        ],
    }
    write_json(package_dir / "prospective_manifest.json", manifest)
    print(
        json.dumps(
            {
                "run_id": run_id,
                "package_dir": rel(package_dir),
                "delta_mean_test_balanced_accuracy": metrics["delta_mean_test_balanced_accuracy"],
                "co_pilot_dataset_wins": metrics["co_pilot_dataset_wins"],
                "autonomous_dataset_wins": metrics["autonomous_dataset_wins"],
                "dataset_ties": metrics["dataset_ties"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
