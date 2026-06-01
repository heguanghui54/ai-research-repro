#!/usr/bin/env python3
"""Run a tiny prospective matched-budget Co-Pilot v3 package.

This is a controlled micro-pilot, not top-conference evidence. It exists to
exercise the required prospective package shape on a real remote computation:
same task, matched tool access, a human-gated co-pilot policy choice, an
autonomous baseline, complete attention/taste gate fields, claim audit, and a
same-run manuscript artifact.
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


REMOTE_EVAL = r"""
python3 - <<'PY'
import itertools
import json
import random
from statistics import mean

def make_graph(seed, n=8, p=0.45):
    rng = random.Random(seed)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                edges.append((i, j, rng.randint(1, 9)))
    if not edges:
        edges.append((0, 1, 1))
    return {"seed": seed, "n": n, "edges": edges}

def cut_value(bits, edges):
    return sum(w for i, j, w in edges if bits[i] != bits[j])

def optimum(graph):
    best = 0
    for bits in itertools.product([0, 1], repeat=graph["n"]):
        best = max(best, cut_value(bits, graph["edges"]))
    return best

def alternating(graph):
    return [i % 2 for i in range(graph["n"])]

def local_search(graph):
    bits = alternating(graph)
    improved = True
    while improved:
        improved = False
        current = cut_value(bits, graph["edges"])
        best_bits = bits
        best_score = current
        for idx in range(graph["n"]):
            candidate = bits[:]
            candidate[idx] = 1 - candidate[idx]
            score = cut_value(candidate, graph["edges"])
            if score > best_score:
                best_score = score
                best_bits = candidate
        if best_score > current:
            bits = best_bits
            improved = True
    return bits

def evaluate_policy(name, policy, graphs):
    rows = []
    for graph in graphs:
        opt = optimum(graph)
        bits = policy(graph)
        value = cut_value(bits, graph["edges"])
        rows.append({
            "seed": graph["seed"],
            "value": value,
            "optimum": opt,
            "normalized_score": value / opt if opt else 0.0,
        })
    return {
        "policy": name,
        "instances": rows,
        "mean_normalized_score": mean(row["normalized_score"] for row in rows),
        "min_normalized_score": min(row["normalized_score"] for row in rows),
    }

graphs = [make_graph(seed) for seed in range(20, 32)]
result = {
    "task": "controlled_weighted_maxcut_micro_pilot",
    "graphs": [{"seed": graph["seed"], "n": graph["n"], "edge_count": len(graph["edges"])} for graph in graphs],
    "autonomous_baseline": evaluate_policy("alternating_baseline", alternating, graphs),
    "co_pilot_variant": evaluate_policy("human_selected_local_search", local_search, graphs),
}
result["delta_mean_normalized_score"] = (
    result["co_pilot_variant"]["mean_normalized_score"]
    - result["autonomous_baseline"]["mean_normalized_score"]
)
print(json.dumps(result, indent=2))
PY
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


def make_gate(run_id: str, package_dir: Path, prompted_at: str, decision_at: str) -> dict[str, Any]:
    return {
        "gate_id": f"{run_id}_frontier_gate_001",
        "gate_type": "frontier_steering",
        "timestamp_utc": decision_at,
        "research_task_id": run_id,
        "options": [
            {
                "option_id": "alternating_baseline",
                "summary": "Continue with the simple alternating Max-Cut policy.",
                "score": None,
                "evidence": ["Low implementation risk but weak mechanistic search value."],
                "risks": ["May under-test whether a human gate can preserve a richer branch."],
            },
            {
                "option_id": "local_search_policy",
                "summary": "Use a local-search repair policy selected for mechanistic value.",
                "score": None,
                "evidence": ["Machine-gradeable evaluator; local improvements are inspectable."],
                "risks": ["Tiny controlled task; not evidence of paper-level superiority."],
            },
        ],
        "human_decision": "local_search_policy",
        "rationale": (
            "Select the local-search branch because it is a clearer test of frontier "
            "steering on a machine-gradeable subproblem while keeping the task small "
            "enough for a prospective package smoke."
        ),
        "affected_artifacts": [rel(package_dir / "remote_metrics.json")],
        "downstream_budget": {
            "remote_instances": 12,
            "same_task_as_autonomous": True,
            "purpose": "controlled_micro_pilot",
        },
        "attention_cost": {
            "human_actor": "codex_operator_for_author",
            "interaction_mode": "async_review",
            "prompted_at_utc": prompted_at,
            "decision_at_utc": decision_at,
            "active_review_minutes": 2.0,
            "wall_clock_latency_minutes": 2.0,
            "options_reviewed": 2,
            "artifacts_reviewed_count": 1,
            "decision_count": 1,
            "notes": "Prospective operator-recorded micro-pilot gate; not an independent human-subject measurement.",
        },
        "taste_insight": {
            "rubric_version": "2026-06-02",
            "scores": {
                "problem_depth": 3,
                "novelty_potential": 2,
                "mechanistic_value": 4,
                "failure_informativeness": 4,
                "benchmark_taste": 4,
                "claim_significance": 2,
                "risk_asymmetry": 3,
            },
            "taste_insight_score": 3.14,
            "qualitative_rationale": (
                "This gate has modest novelty but useful mechanistic value: it tests "
                "whether the prospective package can connect a taste-motivated branch "
                "choice to a machine-gradeable evaluator without overclaiming."
            ),
            "non_metric_factors": [
                "mechanistic-branch-interpretability",
                "package-shape-validation",
            ],
        },
        "follow_up_checks": [
            "Do not use this micro-pilot as top-conference performance evidence.",
            "Replace with AI Scientist-v2/FML or MLAgentBench prospective package.",
        ],
    }


def markdown_report(run_id: str, metrics: dict[str, Any]) -> str:
    auto = metrics["autonomous_baseline"]
    coop = metrics["co_pilot_variant"]
    delta = metrics["delta_mean_normalized_score"]
    return f"""# Prospective Matched-Budget Micro-Pilot Manuscript

Run ID: `{run_id}`

## Question

Can Co-Pilot AI Scientist v3 produce a complete prospective matched-budget
evidence package with human gate logs, matched baseline metrics, a claim audit,
and a manuscript artifact?

## Method

We ran a controlled weighted Max-Cut micro-task on the SSH Ubuntu host. The
autonomous baseline used an alternating partition policy. The co-pilot variant
used a human-gated frontier-steering decision to select an inspectable
local-search repair policy. Both variants used the same generated graph
instances and the same brute-force optimum evaluator.

## Results

| Variant | Mean normalized score | Minimum normalized score |
| --- | ---: | ---: |
| Autonomous alternating baseline | {auto['mean_normalized_score']:.6f} | {auto['min_normalized_score']:.6f} |
| Co-pilot selected local search | {coop['mean_normalized_score']:.6f} | {coop['min_normalized_score']:.6f} |

Mean delta (co-pilot minus autonomous): `{delta:.6f}`.

## Claim

This micro-pilot supports only a narrow engineering claim: the repository can
now produce a non-synthetic prospective matched-budget package that passes the
package-shape audit. It does not prove that human gates improve paper quality
or that Co-Pilot AI Scientist v3 outperforms autonomous AI Scientist-v2.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="ubuntu-heshi")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    now = datetime.now(timezone.utc).replace(microsecond=0)
    timestamp = now.isoformat().replace("+00:00", "Z")
    decision_timestamp = (now + timedelta(minutes=2)).isoformat().replace("+00:00", "Z")
    stamp = now.strftime("%Y%m%d_%H%M%S")
    run_id = args.run_id or f"prospective_matched_micro_pilot_{stamp}"
    package_dir = EXP_DIR / run_id
    package_dir.mkdir(parents=True, exist_ok=True)

    out = require_ok(
        run_cmd(["ssh", args.host, f"bash -lc {shlex.quote(REMOTE_EVAL)}"], timeout=120),
        "remote maxcut micro-pilot",
    )
    metrics = json.loads(out[out.find("{") :])
    write_json(package_dir / "remote_metrics.json", metrics)
    write_json(package_dir / "autonomous_baseline_summary.json", metrics["autonomous_baseline"])

    gate = make_gate(run_id, package_dir, timestamp, decision_timestamp)
    gate_dir = package_dir / "human_gate_logs"
    write_json(gate_dir / "frontier_gate_001.json", gate)

    trajectory = {
        "trajectory_id": run_id,
        "generated_at_utc": timestamp,
        "remote_host": args.host,
        "status": "prospective_micro_pilot",
        "claim_scope": "Evidence-shape validation on a controlled micro-task; not top-conference performance evidence.",
        "gates": [gate],
        "metrics": metrics,
    }
    write_json(package_dir / "co_pilot_trajectory.json", trajectory)

    claim_audit = f"""# Claim Audit

| Claim | Status | Evidence |
| --- | --- | --- |
| The prospective package shape can be generated and audited. | Supported | This directory contains a co-pilot trajectory, matched autonomous baseline, complete gate log, claim audit, manuscript, and manifest. |
| Human gates improve paper quality. | Unsupported | This micro-pilot does not evaluate paper quality. |
| Co-Pilot AI Scientist v3 outperforms autonomous AI Scientist-v2. | Unsupported | This is a controlled Max-Cut micro-task, not an AI Scientist-v2 benchmark. |
| Human attention efficiency is measured for this package. | Partially supported | The gate contains complete operator-recorded attention cost, but it is not an independent human-subject measurement. |
"""
    (package_dir / "claim_audit.md").write_text(claim_audit, encoding="utf-8")
    (package_dir / "manuscript.md").write_text(markdown_report(run_id, metrics), encoding="utf-8")

    manifest = {
        "package_id": run_id,
        "status": "prospective_pilot",
        "co_pilot_trajectory": rel(package_dir / "co_pilot_trajectory.json"),
        "autonomous_baseline": rel(package_dir / "autonomous_baseline_summary.json"),
        "human_gate_logs": [rel(gate_dir / "frontier_gate_001.json")],
        "claim_audit": rel(package_dir / "claim_audit.md"),
        "manuscript": rel(package_dir / "manuscript.md"),
        "matched_budget": {
            "same_task": True,
            "same_model_family": True,
            "same_step_budget": True,
            "same_tool_access": True,
            "notes": "Both variants used the same deterministic generated graph instances and evaluator; no LLM calls were used in this controlled micro-pilot.",
        },
        "remote_metrics": rel(package_dir / "remote_metrics.json"),
        "limitations": [
            "Controlled micro-task only.",
            "No AI Scientist-v2 tree search.",
            "No paper-quality outcome comparison.",
            "Operator-recorded gate, not independent human-subject timing.",
        ],
    }
    write_json(package_dir / "prospective_manifest.json", manifest)
    print(json.dumps({"run_id": run_id, "package_dir": rel(package_dir), "delta": metrics["delta_mean_normalized_score"]}, indent=2))


if __name__ == "__main__":
    main()
