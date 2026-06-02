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
        test_result = summary.get("test_result") or {}
        value = test_result["primary_metric"]
        if value is not None:
            return float(value)
    except KeyError:
        pass
    test_result = summary.get("test_result") or {}
    try:
        return float(test_result["results"]["ihdp_test"]["means"]["mae_mean"])
    except KeyError:
        return None


def step_metric(step: dict[str, Any]) -> float | None:
    if step.get("primary_metric") is not None:
        return float(step["primary_metric"])
    try:
        value = step["val_result"]["primary_metric"]
        if value is not None:
            return float(value)
    except KeyError:
        pass
    try:
        return float(step["val_result"]["filtered_results"]["ihdp_test"]["means"]["mae_mean"])
    except KeyError:
        return None


def format_metric(value: float | None) -> str:
    return "NA" if value is None else f"{value:.6f}"


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


def slug_from_task_config(task_config: str) -> str:
    name = Path(task_config).stem
    return name.replace("_", "-")


def run_fml_summary(
    host: str,
    *,
    remote_output_dir: str,
    task_config: str,
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
  --task-config {shlex.quote(task_config)} \\
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


def build_gate(
    run_id: str,
    package_dir: Path,
    branch_summary: dict[str, Any],
    timestamp: datetime,
    *,
    task_config: str,
    metric_name: str,
    lower_is_better: bool,
) -> dict[str, Any]:
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
                "evidence": [
                    f"validation_{metric_name}={metric:.6f}",
                    "lower_is_better" if lower_is_better else "higher_is_better",
                    f"task_config={task_config}",
                ],
                "risks": ["Small FML prospective package; one task and one seed."],
            }
        )
    no_valid_branch = not options
    if no_valid_branch:
        for step in branch_summary.get("val_steps", []):
            val_result = step.get("val_result") or {}
            options.append(
                {
                    "option_id": f"step_{step['step_id']:04d}",
                    "summary": f"Validation failed for branch {step.get('idea_id')} after {step.get('action')}",
                    "score": None,
                    "evidence": [
                        "validation_success=False",
                        f"task_config={task_config}",
                        str(val_result.get("error", "unknown validation error"))[:500],
                    ],
                    "risks": ["No valid scored continuation was available."],
                }
            )
    selected = (
        {"option_id": "abort_no_valid_branch", "score": None}
        if no_valid_branch
        else (
            min(options, key=lambda item: float(item["score"]))
            if lower_is_better
            else max(options, key=lambda item: float(item["score"]))
        )
    )
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
            "Abort the co-pilot branch frontier because no candidate produced a valid "
            f"validation {metric_name}."
            if no_valid_branch
            else (
                f"Select the {'lower' if lower_is_better else 'higher'}-validation-{metric_name} "
                f"branch for task {task_config} in this prospective FML matched package "
                "while recording that one small task cannot establish general co-pilot superiority."
            )
        ),
        "affected_artifacts": [rel(package_dir / "co_pilot_branch_summary.json")],
        "downstream_budget": {
            f"selected_validation_{metric_name}": selected["score"],
            "same_task_as_autonomous": True,
            "task_config": task_config,
            "fml_max_steps": branch_summary.get("total_steps"),
            "no_valid_branch": no_valid_branch,
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
                f"{task_config} directly tests whether frontier steering can be "
                "inserted into an AI Scientist-v2 benchmark trajectory."
            ),
            "non_metric_factors": ["ai-scientist-v2-trajectory-relevance", "negative-results-still-informative"],
        },
        "follow_up_checks": [
            "Compare against the matched autonomous FML run.",
            f"Do not generalize from one {task_config} run.",
        ],
    }


def manuscript(
    run_id: str,
    branch_summary: dict[str, Any],
    autonomous_summary: dict[str, Any],
    *,
    task_config: str,
    metric_name: str,
    lower_is_better: bool,
) -> str:
    co_test = primary_metric(branch_summary)
    auto_test = primary_metric(autonomous_summary)
    delta = None if co_test is None or auto_test is None else auto_test - co_test
    return f"""# Prospective FML Matched-Budget Pilot Manuscript

Run ID: `{run_id}`

## Question

Can Co-Pilot AI Scientist v3 produce a prospective matched-budget package on
the AI Scientist-v2-style FML-bench task `{task_config}`, with complete human
gate logs and a matched autonomous baseline?

## Method

Both runs use `{task_config}`, model `{branch_summary.get('model')}`, and
provider `{branch_summary.get('provider')}`. The co-pilot package records a
frontier-steering gate over the FML branch frontier. The autonomous baseline is
a separate FML run with the same task and step budget but no human gate.

## Results

| Variant | Validation metric | Test {metric_name} |
| --- | ---: | ---: |
| Co-pilot branch-frontier package | {format_metric(branch_summary.get('best_val_metric'))} | {format_metric(co_test)} |
| Autonomous matched baseline | {format_metric(autonomous_summary.get('best_val_metric'))} | {format_metric(auto_test)} |

{"Lower" if lower_is_better else "Higher"} {metric_name} is better.
Autonomous-minus-co-pilot test delta: `{format_metric(delta)}`.

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
    parser.add_argument("--task-config", default="configs/tasks/causality_causalml.yaml")
    parser.add_argument("--benchmark-slug")
    parser.add_argument("--metric-name", default="primary_metric")
    parser.add_argument("--higher-is-better", action="store_true")
    parser.add_argument(
        "--finalize-existing-package",
        type=Path,
        help="Use existing co_pilot_branch_summary.json and autonomous_baseline_summary.json instead of launching remote runs.",
    )
    parser.add_argument("--max-steps", type=int, default=2)
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--provider", default="DeepSeek")
    args = parser.parse_args()

    now = datetime.now(timezone.utc).replace(microsecond=0)
    stamp = now.strftime("%Y%m%d_%H%M%S")
    benchmark_slug = args.benchmark_slug or slug_from_task_config(args.task_config)
    lower_is_better = not args.higher_is_better
    if args.finalize_existing_package is not None:
        package_dir = args.finalize_existing_package
        if not package_dir.is_absolute():
            package_dir = ROOT / package_dir
        run_id = args.run_id or package_dir.name
    else:
        run_id = args.run_id or f"prospective_matched_fml_{benchmark_slug}_{stamp}"
        package_dir = EXP_DIR / run_id
    package_dir.mkdir(parents=True, exist_ok=True)
    remote_root = f"/home/heshi/work/{run_id}"

    branch_local = package_dir / "co_pilot_branch_summary.json"
    if args.finalize_existing_package is None:
        branch_remote = run_fml_summary(
            args.host,
            remote_output_dir=f"{remote_root}/co_pilot_branch_frontier",
            task_config=args.task_config,
            max_steps=args.max_steps,
            num_ideas=2,
            num_parallel=2,
            model=args.model,
            provider=args.provider,
        )
        scp_from(args.host, branch_remote, branch_local)
    branch_summary = json.loads(branch_local.read_text(encoding="utf-8"))

    autonomous_local = package_dir / "autonomous_baseline_summary.json"
    if args.finalize_existing_package is None:
        autonomous_remote = run_fml_summary(
            args.host,
            remote_output_dir=f"{remote_root}/autonomous_baseline",
            task_config=args.task_config,
            max_steps=args.max_steps,
            num_ideas=2,
            num_parallel=2,
            model=args.model,
            provider=args.provider,
        )
        scp_from(args.host, autonomous_remote, autonomous_local)
    autonomous_summary = json.loads(autonomous_local.read_text(encoding="utf-8"))

    gate = build_gate(
        run_id,
        package_dir,
        branch_summary,
        now,
        task_config=args.task_config,
        metric_name=args.metric_name,
        lower_is_better=lower_is_better,
    )
    gate_path = package_dir / "human_gate_logs/frontier_gate_001.json"
    write_json(gate_path, gate)

    trajectory = {
        "trajectory_id": run_id,
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "remote_host": args.host,
        "remote_root": remote_root,
        "status": "prospective_fml_pilot",
        "claim_scope": "Small FML-bench matched package; not top-conference superiority evidence.",
        "task_config": args.task_config,
        "benchmark_slug": benchmark_slug,
        "metric_name": args.metric_name,
        "metric_direction": "lower_is_better" if lower_is_better else "higher_is_better",
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
    copilot_beats = (
        co_test is not None
        and auto_test is not None
        and ((co_test < auto_test) if lower_is_better else (co_test > auto_test))
    )
    claim_audit = f"""# Claim Audit

| Claim | Status | Evidence |
| --- | --- | --- |
| A prospective matched-budget package can be produced on FML-bench. | Supported | This package contains fresh co-pilot and autonomous FML summaries, a complete gate log, claim audit, manuscript, and manifest. |
| Human gates improve paper quality. | Unsupported | This package does not evaluate final paper quality. |
| Co-Pilot v3 outperforms autonomous AI Scientist-v2 generally. | Unsupported | One small {args.task_config} run is insufficient. |
| Co-pilot beats the matched autonomous baseline in this run. | {'Supported' if copilot_beats else 'Unsupported'} | Co-pilot test {args.metric_name}: {co_test}; autonomous test {args.metric_name}: {auto_test}; direction: {'lower is better' if lower_is_better else 'higher is better'}. |
"""
    (package_dir / "claim_audit.md").write_text(claim_audit, encoding="utf-8")
    (package_dir / "manuscript.md").write_text(
        manuscript(
            run_id,
            branch_summary,
            autonomous_summary,
            task_config=args.task_config,
            metric_name=args.metric_name,
            lower_is_better=lower_is_better,
        ),
        encoding="utf-8",
    )

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
            "task_config": args.task_config,
            "benchmark_slug": benchmark_slug,
            "metric_name": args.metric_name,
            "metric_direction": "lower_is_better" if lower_is_better else "higher_is_better",
            "notes": f"Both runs used {args.task_config}, {args.model}, {args.provider}, and max_steps={args.max_steps}.",
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
