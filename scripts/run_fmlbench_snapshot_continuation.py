#!/usr/bin/env python3
"""Continue an FML-bench run from a selected AI Scientist-v2 code snapshot.

This script is intended to run from the official FML-bench repository root. It
temporarily applies a previously selected step snapshot to the task template
workspace, launches a short AI Scientist-v2 continuation run, and then restores
the original template files.

The purpose is to make a human branch gate executable without permanently
patching the upstream benchmark repository.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _load_task_repo_and_files(benchmark_name: str) -> tuple[Path, list[str]]:
    config_path = Path("ml_tasks") / benchmark_name / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing task config: {config_path}")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    return Path(config["repo_dir"]), list(config["target_files"])


def _snapshot_to_target_map(
    snapshot: dict[str, str],
    repo_dir: Path,
    target_files: list[str],
) -> dict[Path, str]:
    mapped: dict[Path, str] = {}
    for rel in target_files:
        matched = None
        normalized_rel = rel.replace("\\", "/")
        for source_path, content in snapshot.items():
            normalized_source = source_path.replace("\\", "/")
            if normalized_source.endswith("/" + normalized_rel) or normalized_source == normalized_rel:
                matched = content
                break
        if matched is None:
            raise KeyError(f"Snapshot does not contain target file suffix: {rel}")
        mapped[repo_dir / rel] = matched
    return mapped


def _build_temp_agent_config(
    source: Path,
    num_ideas: int,
    num_parallel: int,
    stage_budgets: str,
) -> Path:
    text = source.read_text(encoding="utf-8")
    replacements = {
        "num_ideas: 3": f"num_ideas: {num_ideas}",
        "num_parallel: 4": f"num_parallel: {num_parallel}",
        "stage_budgets: [0.10, 0.20, 0.50, 0.20]": f"stage_budgets: {stage_budgets}",
    }
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".yaml",
        prefix="copilotv3_ai_scientist_v2_",
        delete=False,
        encoding="utf-8",
    )
    with tmp:
        tmp.write(text)
    return Path(tmp.name)


def _run(cmd: list[str], env: dict[str, str]) -> int:
    print("Running:", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, env=env)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run FML-bench continuation from a selected code snapshot."
    )
    parser.add_argument("--benchmark-name", default="Causality_causalml")
    parser.add_argument("--snapshot-json", required=True)
    parser.add_argument("--agent-config", default="configs/agents/ai_scientist_v2.yaml")
    parser.add_argument("--task-config", default="configs/tasks/causality_causalml.yaml")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--provider", default="DeepSeek")
    parser.add_argument("--max-steps", type=int, default=2)
    parser.add_argument("--num-ideas", type=int, default=1)
    parser.add_argument("--num-parallel", type=int, default=1)
    parser.add_argument(
        "--stage-budgets",
        default="[1.0, 0.0, 0.0, 0.0]",
        help="YAML list string for the continuation run.",
    )
    args = parser.parse_args()

    if not Path("run_agent_benchmark.py").exists():
        raise RuntimeError("Run this script from the official FML-bench repository root.")

    snapshot = json.loads(Path(args.snapshot_json).read_text(encoding="utf-8"))
    repo_dir, target_files = _load_task_repo_and_files(args.benchmark_name)
    target_map = _snapshot_to_target_map(snapshot, repo_dir, target_files)

    backups: dict[Path, str | None] = {}
    temp_agent_config = _build_temp_agent_config(
        Path(args.agent_config),
        num_ideas=args.num_ideas,
        num_parallel=args.num_parallel,
        stage_budgets=args.stage_budgets,
    )

    try:
        for path, content in target_map.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            backups[path] = path.read_text(encoding="utf-8") if path.exists() else None
            path.write_text(content, encoding="utf-8")
            print(f"Applied selected snapshot file: {path}")

        env = os.environ.copy()
        env.setdefault("CUDA_VISIBLE_DEVICES", "0")
        cmd = [
            sys.executable,
            "run_agent_benchmark.py",
            "--agent-config",
            str(temp_agent_config),
            "--task-config",
            args.task_config,
            "--model",
            args.model,
            "--provider",
            args.provider,
            "--output-dir",
            args.output_dir,
            f"agent.ai_scientist_v2.max_steps={args.max_steps}",
        ]
        return _run(cmd, env)
    finally:
        for path, old_content in backups.items():
            if old_content is None:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            else:
                path.write_text(old_content, encoding="utf-8")
            print(f"Restored template file: {path}")
        temp_agent_config.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
