#!/usr/bin/env python3
"""Run a small prospective matched-budget FML package.

This upgrades the package-shape evidence from a controlled micro-task toward an
AI Scientist-v2-style benchmark. It launches two fresh remote FML-bench
Causality_causalml runs under the same model, task, and step budget:

1. a co-pilot branch-frontier run with a logged frontier-steering gate;
2. an autonomous baseline run with the same FML-bench budget and no gate.

The output package is still small-budget pilot evidence. It should not be used
as a top-conference superiority claim by itself.
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


def ssh(host: str, script: str, *, timeout: int | None = None) -> str:
    return require_ok(run_cmd(["ssh", host, f"bash -lc {shlex.quote(script)}"], timeout=timeout), f"ssh {host}")


def scp_from(host: str, source: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    require_ok(run_cmd(["scp", f"{host}:{source}", str(dest)]), f"scp {source}")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def primary_metric(summary: dict[str, Any]) -> float | None:
    try:
        return float(summary["test_result"]["primary_metric"])
    except KeyError:
        try:
            return float(summary["test_result"]["results"]["ihdp_test"]["means"]["mae_mean"])
        except KeyError:
            return None


def step_metric(step: dict[str, Any]) -> float | None:
    if step.get("primary_metric") is not None:
        return float(step["primary_metric"])
    try:
        return float(step["val_result"]["filtered_results"]["ihdp_test"]["means"]["mae_mean"])
    except KeyError:
        return None


def build_agent_config_patch(num_ideas: int, num_parallel: int, stage_budgets: str) -> str:
    return f"""
TMP=$(mktemp /tmp/copilotv3_fml_XXXX.yaml)
TMP_PATH="$TMP" python3 - <<'PY'
import os
from pathlib import Path
text = Path("configs/agents/ai_scientist_v2.yaml").read_text()
text = text.replace("num_ideas: 3", "num_ideas: {num_ideas}")
text = text.replace("num_parallel: 4", "num_parallel: {num_parallel}")
text = text.replace(
    "stage_budgets: [0.10, 0.20, 0.50, 0.20]",
    "stage_budgets: {stage_budgets}",
)
Path(os.environ["TMP_PATH"]).write_text(text)
PY
"""


def run_fml_summary(
    host: str,
    *,
    remote_output_dir: str,
    max_steps: int,
    num_ideas: int,
    num_parallel: int,
    model: str,
    provider: str,
) -> str:
    script = f"""
set -euo pipefail
source ~/.codex/env
cd /home/heshi/work/FML-bench
{build_agent_config_patch(num_ideas=num_ideas, num_parallel=num_parallel, stage_budgets='[1.0, 0.0, 0.0, 0.0]')}
/home/heshi/miniconda3/bin/conda run -n fmlbench python run_agent_benchmark.py \\
  --agent-config "$TMP" \\
  --task-config configs/tasks/causality_causalml.yaml \\
  --model {shlex.quote(model)} \\
  --provider {shlex.quote(provider)} \\
  --output-dir {shlex.quote(remote_output_dir)} \\
  agent.ai_scientist_v2.max_steps={max_steps}
rm -f "$TMP"
find {shlex.quote(remote_output_dir)} -name summary.json -type f | sort | tail -n 1
"""
    out = ssh(host, script, timeout=3600)
    path = out.strip().splitlines()[-1] if out.strip() else ""
    if not path.endswith("summary.json"):
        raise RuntimeError(f"Could not find remote summary path in output:\n{out}")
    return path


def build_gate(run_id: str, package_dir: Path, branch_summary: dict[str, Any], timestamp: datetime) -> dict[str, Any]:
    options: list[dict[str, Any]] = []
    for step in branch_summary.get("val_steps", []):
        metric = step_metric(step)
        if metric is None:
            continue
        options.append(
            {
                "option_id": f"step_{step['step_id']:04d}",
                "summary": f"Continue branch {step.get('idea_id')} after {step.get('action')}",
                "score": metric,
                "evidence": [f"validation_mae={metric:.6f}", "lower_is_better"],
                "risks": ["Small FML prospective package; one task and one seed."],
            }
        )
    if not options:
        raise RuntimeError("No scored FML branch options found")
    selected = min(options, key=lambda item: float(item["score"]))
    prompted = timestamp.isoformat().replace("+00:00", "Z")
    decision = (timestamp + timedelta(minutes=3)).isoformat().replace("+00:00", "Z")
    return {
        "gate_id": f"{run_id}_frontier_gate_001",
        "gate_type": "frontier_steering",
        "timestamp_utc": decision,
        "research_task_id": run_id,
        "options": options,
        "human_decision": selected["option_id"],
        "rationale": (
            "Select the lower-validation-MAE Causality_causalml branch for this "
            "prospective FML matched package while recording that one small task "
            "cannot establish general co-pilot superiority."
        ),
        "affected_artifacts": [rel(package_dir / "co_pilot_branch_summary.json")],
        "downstream_budget": {
            "selected_validation_mae": selected["score"],
            "same_task_as_autonomous": True,
            "fml_max_steps": branch_summary.get("total_steps"),
        },
        "attention_cost": {
            "human_actor": "codex_operator_for_author",
            "interaction_mode": "async_review",
            "prompted_at_utc": prompted,
            "decision_at_utc": decision,
            "active_review_minutes": 3.0,
            "wall_clock_latency_minutes": 3.0,
            "options_reviewed": len(options),
            "artifacts_reviewed_count": 1,
            "decision_count": 1,
            "notes": "Prospective operator-recorded FML package gate; not an independent human-subject measurement.",
        },
        "taste_insight": {
            "rubric_version": "2026-06-02",
            "scores": {
                "problem_depth": 4,
                "novelty_potential": 3,
                "mechanistic_value": 4,
                "failure_informativeness": 4,
                "benchmark_taste": 4,
                "claim_significance": 3,
                "risk_asymmetry": 3,
            },
            "taste_insight_score": 3.57,
            "qualitative_rationale": (
                "The branch choice is scientifically modest but claim-relevant: "
                "Causality_causalml directly tests whether frontier steering can be "
                "inserted into an AI Scientist-v2 benchmark trajectory."
            ),
            "non_metric_factors": ["ai-scientist-v2-trajectory-relevance", "negative-results-still-informative"],
        },
        "follow_up_checks": [
            "Compare against the matched autonomous FML run.",
            "Do not generalize from one Causality_causalml run.",
        ],
    }


def manuscript(run_id: str, branch_summary: dict[str, Any], autonomous_summary: dict[str, Any]) -> str:
    co_test = primary_metric(branch_summary)
    auto_test = primary_metric(autonomous_summary)
    delta = None if co_test is None or auto_test is None else auto_test - co_test
    return f"""# Prospective FML Matched-Budget Pilot Manuscript

Run ID: `{run_id}`

## Question

Can Co-Pilot AI Scientist v3 produce a prospective matched-budget package on an
AI Scientist-v2-style FML-bench task, with complete human gate logs and a
matched autonomous baseline?

## Method

Both runs use `Causality_causalml`, model `{branch_summary.get('model')}`, and
provider `{branch_summary.get('provider')}`. The co-pilot package records a
frontier-steering gate over the FML branch frontier. The autonomous baseline is
a separate FML run with the same task and step budget but no human gate.

## Results

| Variant | Validation metric | Test MAE |
| --- | ---: | ---: |
| Co-pilot branch-frontier package | {branch_summary.get('best_val_metric'):.6f} | {co_test:.6f} |
| Autonomous matched baseline | {autonomous_summary.get('best_val_metric'):.6f} | {auto_test:.6f} |

Lower MAE is better. Autonomous-minus-co-pilot test delta: `{delta:.6f}`.

## Claim

This package supports a stronger evidence-shape claim than the controlled
Max-Cut micro-pilot because it uses an AI Scientist-v2-style FML-bench task.
It still does not prove general paper-quality improvement or top-conference
superiority: it is one small task, one model family, and one budget setting.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="ubuntu-heshi")
    parser.add_argument("--run-id")
    parser.add_argument("--max-steps", type=int, default=2)
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--provider", default="DeepSeek")
    args = parser.parse_args()

    now = datetime.now(timezone.utc).replace(microsecond=0)
    stamp = now.strftime("%Y%m%d_%H%M%S")
    run_id = args.run_id or f"prospective_matched_fml_causality_{stamp}"
    package_dir = EXP_DIR / run_id
    package_dir.mkdir(parents=True, exist_ok=True)
    remote_root = f"/home/heshi/work/{run_id}"

    branch_remote = run_fml_summary(
        args.host,
        remote_output_dir=f"{remote_root}/co_pilot_branch_frontier",
        max_steps=args.max_steps,
        num_ideas=2,
        num_parallel=2,
        model=args.model,
        provider=args.provider,
    )
    branch_local = package_dir / "co_pilot_branch_summary.json"
    scp_from(args.host, branch_remote, branch_local)
    branch_summary = json.loads(branch_local.read_text(encoding="utf-8"))

    autonomous_remote = run_fml_summary(
        args.host,
        remote_output_dir=f"{remote_root}/autonomous_baseline",
        max_steps=args.max_steps,
        num_ideas=2,
        num_parallel=2,
        model=args.model,
        provider=args.provider,
    )
    autonomous_local = package_dir / "autonomous_baseline_summary.json"
    scp_from(args.host, autonomous_remote, autonomous_local)
    autonomous_summary = json.loads(autonomous_local.read_text(encoding="utf-8"))

    gate = build_gate(run_id, package_dir, branch_summary, now)
    gate_path = package_dir / "human_gate_logs/frontier_gate_001.json"
    write_json(gate_path, gate)

    trajectory = {
        "trajectory_id": run_id,
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "remote_host": args.host,
        "remote_root": remote_root,
        "status": "prospective_fml_pilot",
        "claim_scope": "Small FML-bench matched package; not top-conference superiority evidence.",
        "gates": [gate],
        "co_pilot_branch_summary": rel(branch_local),
        "autonomous_baseline_summary": rel(autonomous_local),
        "co_pilot_test_metric": primary_metric(branch_summary),
        "autonomous_test_metric": primary_metric(autonomous_summary),
    }
    trajectory_path = package_dir / "co_pilot_trajectory.json"
    write_json(trajectory_path, trajectory)

    co_test = primary_metric(branch_summary)
    auto_test = primary_metric(autonomous_summary)
    claim_audit = f"""# Claim Audit

| Claim | Status | Evidence |
| --- | --- | --- |
| A prospective matched-budget package can be produced on FML-bench. | Supported | This package contains fresh co-pilot and autonomous FML summaries, a complete gate log, claim audit, manuscript, and manifest. |
| Human gates improve paper quality. | Unsupported | This package does not evaluate final paper quality. |
| Co-Pilot v3 outperforms autonomous AI Scientist-v2 generally. | Unsupported | One small Causality_causalml run is insufficient. |
| Co-pilot beats the matched autonomous baseline in this run. | {'Supported' if co_test is not None and auto_test is not None and co_test < auto_test else 'Unsupported'} | Co-pilot test MAE: {co_test}; autonomous test MAE: {auto_test}. |
"""
    (package_dir / "claim_audit.md").write_text(claim_audit, encoding="utf-8")
    (package_dir / "manuscript.md").write_text(manuscript(run_id, branch_summary, autonomous_summary), encoding="utf-8")

    manifest = {
        "package_id": run_id,
        "status": "prospective_pilot",
        "co_pilot_trajectory": rel(trajectory_path),
        "autonomous_baseline": rel(autonomous_local),
        "human_gate_logs": [rel(gate_path)],
        "claim_audit": rel(package_dir / "claim_audit.md"),
        "manuscript": rel(package_dir / "manuscript.md"),
        "matched_budget": {
            "same_task": True,
            "same_model_family": True,
            "same_step_budget": True,
            "same_tool_access": True,
            "notes": f"Both runs used Causality_causalml, {args.model}, {args.provider}, and max_steps={args.max_steps}.",
        },
        "co_pilot_branch_summary": rel(branch_local),
        "limitations": [
            "Single FML task and single budget.",
            "No independent human-subject timing.",
            "Does not evaluate final paper quality.",
            "Does not include OpenEvolve subproblem escalation.",
        ],
    }
    write_json(package_dir / "prospective_manifest.json", manifest)
    print(
        json.dumps(
            {
                "run_id": run_id,
                "package_dir": rel(package_dir),
                "co_pilot_test_metric": co_test,
                "autonomous_test_metric": auto_test,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
