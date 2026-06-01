#!/usr/bin/env python3
"""Run a small online Co-Pilot AI Scientist v3 full-gate smoke trajectory.

The script orchestrates a real remote sequence on the Ubuntu host:

1. idea gate: choose the current narrow contribution from candidates.json;
2. evaluator gate: approve Causality MAE plus correctness/utility guardrails;
3. branch gate: run a fresh two-draft FML-bench frontier and select the better
   validation branch;
4. continuation: run AI Scientist-v2 from the selected code snapshot;
5. program-search gate: run a tiny OpenEvolve knapsack search on the same host;
6. claim gate: mark the trajectory as online smoke evidence, not superiority.

It is intentionally small-budget. The output is a reproducibility artifact for
the online orchestration path, not top-conference-level evidence by itself.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from datetime import datetime, timezone
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
        timeout=timeout,
        check=False,
    )


def require_ok(proc: subprocess.CompletedProcess[str], context: str) -> str:
    if proc.returncode != 0:
        raise RuntimeError(f"{context} failed with code {proc.returncode}\n{proc.stdout}")
    return proc.stdout


def ssh(host: str, script: str, *, timeout: int | None = None) -> str:
    proc = run_cmd(["ssh", host, f"bash -lc {shlex.quote(script)}"], timeout=timeout)
    return require_ok(proc, f"ssh {host}")


def scp_to(host: str, source: Path, dest: str, *, recursive: bool = False) -> None:
    cmd = ["scp"]
    if recursive:
        cmd.append("-r")
    cmd.extend([str(source), f"{host}:{dest}"])
    require_ok(run_cmd(cmd), f"scp {source}")


def scp_from(host: str, source: str, dest: Path, *, recursive: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["scp"]
    if recursive:
        cmd.append("-r")
    cmd.extend([f"{host}:{source}", str(dest)])
    require_ok(run_cmd(cmd), f"scp {source}")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def step_metric(step: dict[str, Any]) -> float | None:
    if step.get("primary_metric") is not None:
        return float(step["primary_metric"])
    try:
        return float(step["val_result"]["filtered_results"]["ihdp_test"]["means"]["mae_mean"])
    except KeyError:
        return None


def primary_metric(summary: dict[str, Any]) -> float | None:
    try:
        return float(summary["test_result"]["primary_metric"])
    except KeyError:
        return None


def latest_summary_remote(host: str, remote_dir: str) -> str:
    script = f"find {shlex.quote(remote_dir)} -name summary.json -type f | sort | tail -n 1"
    out = ssh(host, script)
    path = out.strip().splitlines()[-1] if out.strip() else ""
    if not path:
        raise RuntimeError(f"No summary.json found under {remote_dir}")
    return path


def build_agent_config_patch(num_ideas: int, num_parallel: int, stage_budgets: str) -> str:
    return f"""
TMP=$(mktemp /tmp/copilotv3_agent_XXXX.yaml)
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


def run_branch_frontier(host: str, remote_root: str, max_steps: int, model: str, provider: str) -> str:
    output_dir = f"{remote_root}/branch_frontier"
    script = f"""
set -euo pipefail
source ~/.codex/env
cd /home/heshi/work/FML-bench
{build_agent_config_patch(num_ideas=2, num_parallel=2, stage_budgets='[1.0, 0.0, 0.0, 0.0]')}
/home/heshi/miniconda3/bin/conda run -n fmlbench python run_agent_benchmark.py \\
  --agent-config "$TMP" \\
  --task-config configs/tasks/causality_causalml.yaml \\
  --model {shlex.quote(model)} \\
  --provider {shlex.quote(provider)} \\
  --output-dir {shlex.quote(output_dir)} \\
  agent.ai_scientist_v2.max_steps={max_steps}
rm -f "$TMP"
find {shlex.quote(output_dir)} -name summary.json -type f | sort | tail -n 1
"""
    out = ssh(host, script, timeout=3600)
    return out.strip().splitlines()[-1]


def run_continuation(
    host: str,
    remote_root: str,
    selected_snapshot: str,
    max_steps: int,
    model: str,
    provider: str,
) -> str:
    remote_work = "/home/heshi/work/co-pilot-ai-scientist-v3"
    ssh(host, f"mkdir -p {shlex.quote(remote_work)}")
    scp_to(host, ROOT / "scripts" / "run_fmlbench_snapshot_continuation.py", f"{remote_work}/run_fmlbench_snapshot_continuation.py")
    output_dir = f"{remote_root}/selected_continuation"
    script = f"""
set -euo pipefail
source ~/.codex/env
cd /home/heshi/work/FML-bench
/home/heshi/miniconda3/bin/conda run -n fmlbench python {remote_work}/run_fmlbench_snapshot_continuation.py \\
  --benchmark-name Causality_causalml \\
  --snapshot-json {shlex.quote(selected_snapshot)} \\
  --agent-config configs/agents/ai_scientist_v2.yaml \\
  --task-config configs/tasks/causality_causalml.yaml \\
  --output-dir {shlex.quote(output_dir)} \\
  --model {shlex.quote(model)} \\
  --provider {shlex.quote(provider)} \\
  --max-steps {max_steps} \\
  --num-ideas 1 \\
  --num-parallel 1 \\
  --stage-budgets "[1.0, 0.0, 0.0, 0.0]"
find {shlex.quote(output_dir)} -name summary.json -type f | sort | tail -n 1
"""
    out = ssh(host, script, timeout=3600)
    return out.strip().splitlines()[-1]


def run_program_search(host: str, remote_root: str, iterations: int, model: str) -> str:
    remote_work = "/home/heshi/work/co-pilot-ai-scientist-v3"
    ssh(host, f"mkdir -p {remote_work}/knapsack_task")
    scp_to(host, ROOT / "scripts" / "run_openevolve_program_search.py", f"{remote_work}/run_openevolve_program_search.py")
    scp_to(host, EXP_DIR / "knapsack_task" / "initial_program.py", f"{remote_work}/knapsack_task/initial_program.py")
    scp_to(host, EXP_DIR / "knapsack_task" / "evaluator.py", f"{remote_work}/knapsack_task/evaluator.py")
    output_dir = f"{remote_root}/program_search/knapsack_openevolve_{iterations}iter/run"
    script = f"""
set -euo pipefail
source ~/.codex/env
cd {remote_work}
. .venv/bin/activate
python run_openevolve_program_search.py \\
  --initial-program knapsack_task/initial_program.py \\
  --evaluator knapsack_task/evaluator.py \\
  --output-dir {shlex.quote(output_dir)} \\
  --iterations {iterations} \\
  --provider deepseek \\
  --model {shlex.quote(model)}
"""
    ssh(host, script, timeout=3600)
    return f"{remote_root}/program_search/knapsack_openevolve_{iterations}iter/summary.json"


def write_readme(path: Path, trajectory: dict[str, Any]) -> None:
    summary = trajectory["summary"]
    lines = [
        "# Online Full-Gate Smoke Trajectory",
        "",
        f"- Trajectory ID: `{trajectory['trajectory_id']}`",
        f"- Generated at: `{trajectory['generated_at_utc']}`",
        f"- Remote host: `{trajectory['remote_host']}`",
        f"- Remote root: `{trajectory['remote_root']}`",
        f"- Single online smoke run: `{trajectory['is_single_online_smoke_run']}`",
        "",
        trajectory["claim_scope"],
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in summary.items():
        if isinstance(value, float):
            display = f"{value:.6f}"
        else:
            display = f"`{value}`"
        lines.append(f"| `{key}` | {display} |")
    lines.extend(["", "## Gate Decisions", ""])
    for gate in trajectory["gates"]:
        lines.extend(
            [
                f"### {gate['gate_id']}",
                "",
                f"- Type: `{gate['gate_type']}`",
                f"- Decision: `{gate['human_decision']}`",
                f"- Rationale: {gate['rationale']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="ubuntu-heshi")
    parser.add_argument("--remote-root", default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--branch-summary-local", type=Path, default=None)
    parser.add_argument("--branch-summary-remote", default=None)
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--provider", default="DeepSeek")
    parser.add_argument("--branch-steps", type=int, default=2)
    parser.add_argument("--continuation-steps", type=int, default=1)
    parser.add_argument("--program-iterations", type=int, default=1)
    args = parser.parse_args()

    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    run_id = timestamp.strftime("%Y%m%d_%H%M%S")
    remote_root = args.remote_root or f"/home/heshi/work/copilotv3-online-full-gate-smoke-{run_id}"
    out_dir = args.output_dir or EXP_DIR / f"online_full_gate_smoke_{run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = read_json(DOC_DIR / "candidates.json")
    selected_direction = candidates["current_best_direction"]

    branch_summary_local = out_dir / "branch_frontier_summary.json"
    if args.branch_summary_local:
        branch_summary_remote = args.branch_summary_remote or "provided_local_branch_summary"
        branch_summary_local.write_text(
            args.branch_summary_local.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    else:
        branch_summary_remote = run_branch_frontier(
            args.host, remote_root, args.branch_steps, args.model, args.provider
        )
        scp_from(args.host, branch_summary_remote, branch_summary_local)
    branch_summary = read_json(branch_summary_local)

    branch_options = []
    for step in branch_summary.get("val_steps", []):
        metric = step_metric(step)
        if metric is None:
            continue
        snapshot = step.get("code_snapshot_path") or step.get("metadata", {}).get("code_snapshot_path")
        if not snapshot:
            raise RuntimeError(f"Step {step.get('step_id')} has no code_snapshot_path")
        branch_options.append(
            {
                "option_id": f"step_{step['step_id']:04d}",
                "summary": f"{step['action']} branch {step['idea_id']}",
                "score": metric,
                "snapshot_path": snapshot,
                "evidence": [f"validation_mae={metric:.6f}", "lower_is_better"],
                "risks": ["Small two-draft smoke frontier."],
            }
        )
    if not branch_options:
        raise RuntimeError("No scored branch options found in branch summary")
    selected_branch = min(branch_options, key=lambda item: item["score"])

    continuation_summary_remote = run_continuation(
        args.host,
        remote_root,
        selected_branch["snapshot_path"],
        args.continuation_steps,
        args.model,
        args.provider,
    )
    continuation_summary_local = out_dir / "selected_continuation_summary.json"
    scp_from(args.host, continuation_summary_remote, continuation_summary_local)
    continuation_summary = read_json(continuation_summary_local)

    program_summary_remote = run_program_search(
        args.host, remote_root, args.program_iterations, args.model
    )
    program_summary_local = out_dir / "program_search_summary.json"
    scp_from(args.host, program_summary_remote, program_summary_local)
    program_summary = read_json(program_summary_local)

    generated_at = timestamp.isoformat().replace("+00:00", "Z")
    continuation_test = primary_metric(continuation_summary)
    program_score = float(program_summary["best_score"])

    gates = [
        {
            "gate_id": "idea_gate_online_smoke_001",
            "gate_type": "idea_selection",
            "timestamp_utc": generated_at,
            "research_task_id": "copilot_v3_online_full_gate_smoke",
            "options": [
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
                    "evidence": [item["minimal_experiment"]],
                    "risks": [item["main_risk"]],
                }
                for item in candidates["candidates"]
            ],
            "human_decision": selected_direction,
            "rationale": "Use the currently selected narrow contribution as the online smoke trajectory target.",
            "affected_artifacts": ["docs/co_pilot_ai_scientist_v3/candidates.json"],
            "downstream_budget": {"branch_steps": args.branch_steps},
            "follow_up_checks": ["Do not claim superiority from a single smoke trajectory."],
        },
        {
            "gate_id": "evaluator_gate_online_smoke_001",
            "gate_type": "evaluator_approval",
            "timestamp_utc": generated_at,
            "research_task_id": "copilot_v3_online_full_gate_smoke",
            "options": [
                {
                    "option_id": "causality_mae_plus_guardrails",
                    "summary": "Use Causality validation MAE for branch selection plus correctness/utility guardrails for subproblem search.",
                    "score": 1.0,
                    "evidence": ["FML Causality exposes validation/test MAE.", "Knapsack evaluator exposes validity and optimality ratio."],
                    "risks": ["MAE branch selection does not measure whole-paper quality."],
                }
            ],
            "human_decision": "causality_mae_plus_guardrails",
            "rationale": "Approve a low-cost evaluator bundle for an online smoke run.",
            "affected_artifacts": [str(branch_summary_local), str(program_summary_local)],
            "downstream_budget": {"continuation_steps": args.continuation_steps, "program_iterations": args.program_iterations},
            "follow_up_checks": ["Use matched autonomous baselines before performance claims."],
        },
        {
            "gate_id": "branch_gate_online_smoke_001",
            "gate_type": "branch_selection",
            "timestamp_utc": generated_at,
            "research_task_id": "copilot_v3_online_full_gate_smoke",
            "options": [
                {k: v for k, v in option.items() if k != "snapshot_path"}
                for option in branch_options
            ],
            "human_decision": selected_branch["option_id"],
            "rationale": f"Select the lower-validation-MAE branch ({selected_branch['score']:.6f}) from the fresh remote frontier.",
            "affected_artifacts": [str(branch_summary_local)],
            "downstream_budget": {
                "selected_snapshot_remote": selected_branch["snapshot_path"],
                "continuation_summary_remote": continuation_summary_remote,
            },
            "follow_up_checks": ["Archive the selected snapshot and continuation summary."],
        },
        {
            "gate_id": "program_search_gate_online_smoke_001",
            "gate_type": "program_search_escalation",
            "timestamp_utc": generated_at,
            "research_task_id": "copilot_v3_online_full_gate_smoke",
            "options": [
                {
                    "option_id": "run_tiny_openevolve_knapsack",
                    "summary": "Run a tiny OpenEvolve knapsack search as the AlphaEvolve-style subproblem module.",
                    "score": program_score,
                    "evidence": [f"best_score={program_score:.6f}", f"iterations={args.program_iterations}"],
                    "risks": ["One-iteration program search is only a smoke check."],
                }
            ],
            "human_decision": "run_tiny_openevolve_knapsack",
            "rationale": "Exercise the program-search escalation gate in the same online smoke trajectory.",
            "affected_artifacts": [str(program_summary_local)],
            "downstream_budget": {"program_summary_remote": program_summary_remote},
            "follow_up_checks": ["Repeat with direct-edit baseline or larger budget before claiming improvement."],
        },
        {
            "gate_id": "claim_gate_online_smoke_001",
            "gate_type": "claim_audit",
            "timestamp_utc": generated_at,
            "research_task_id": "copilot_v3_online_full_gate_smoke",
            "options": [
                {
                    "option_id": "claim_online_orchestration_feasible",
                    "summary": "Claim that the online five-gate smoke orchestration is executable.",
                    "score": 1.0,
                    "evidence": [
                        f"branch_summary={branch_summary_remote}",
                        f"continuation_summary={continuation_summary_remote}",
                        f"program_summary={program_summary_remote}",
                    ],
                    "risks": ["Single smoke trajectory is not top-conference-level evidence."],
                },
                {
                    "option_id": "claim_general_superiority",
                    "summary": "Claim full co-pilot superiority over autonomous AI Scientist-v2.",
                    "score": 0.0,
                    "evidence": [],
                    "risks": ["No matched autonomous baseline in this smoke run."],
                },
            ],
            "human_decision": "claim_online_orchestration_feasible",
            "rationale": "The trajectory proves online orchestration feasibility only; superiority remains unproven.",
            "affected_artifacts": ["paper_en.md", "paper_zh.md", str(out_dir / "trajectory.json")],
            "downstream_budget": {"next_required_run": "matched autonomous baseline for this exact online trajectory"},
            "follow_up_checks": ["Run matched autonomous baseline and repeat across tasks/seeds."],
        },
    ]

    trajectory = {
        "trajectory_id": f"online_full_gate_smoke_{run_id}",
        "generated_at_utc": generated_at,
        "remote_host": args.host,
        "remote_root": remote_root,
        "is_single_online_smoke_run": True,
        "is_top_conference_evidence": False,
        "claim_scope": (
            "This is a fresh online smoke trajectory that exercises all five gate types "
            "and launches remote FML-bench plus OpenEvolve work. It proves orchestration "
            "feasibility, not general performance superiority."
        ),
        "gates": gates,
        "summary": {
            "selected_research_direction": selected_direction,
            "selected_branch": selected_branch["option_id"],
            "selected_branch_val_mae": selected_branch["score"],
            "continuation_test_mae": continuation_test,
            "program_search_best_score": program_score,
            "branch_summary_remote": branch_summary_remote,
            "continuation_summary_remote": continuation_summary_remote,
            "program_summary_remote": program_summary_remote,
        },
        "remaining_gap": "Run a matched autonomous baseline for the same budget, then repeat across more tasks and seeds.",
    }

    write_json(out_dir / "trajectory.json", trajectory)
    write_readme(out_dir / "README.md", trajectory)
    print(out_dir / "trajectory.json")
    print(out_dir / "README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
