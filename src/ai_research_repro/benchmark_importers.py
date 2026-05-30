from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    return value.strip("'\"")


def _parse_logging_info(metadata_text: str) -> dict[str, Any]:
    logging: dict[str, Any] = {}
    in_logging = False
    for raw in metadata_text.splitlines():
        if raw.startswith("logging_info:"):
            in_logging = True
            continue
        if in_logging and raw and not raw.startswith(" "):
            break
        if not in_logging or not raw.startswith("  "):
            continue
        match = re.match(r"\s{2}([A-Za-z0-9_]+):\s*(.*)$", raw)
        if match:
            logging[match.group(1)] = _parse_scalar(match.group(2))
    return logging


def _parse_top_level(metadata_text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for raw in metadata_text.splitlines():
        match = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", raw)
        if match:
            parsed[match.group(1)] = _parse_scalar(match.group(2))
    return parsed


def _first_sentence(text: str, *, max_chars: int = 900) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= max_chars:
        return normalized
    clipped = normalized[:max_chars].rsplit(" ", 1)[0]
    return clipped.rstrip(".,;:") + "..."


def _git_revision(path: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def import_airs_tasks(
    *,
    repo_dir: Path,
    output_path: Path,
    split: str = "rad",
    limit: int = 0,
    max_per_category: int = 0,
) -> dict[str, Any]:
    task_root = repo_dir / "airsbench" / "tasks" / split
    if not task_root.exists():
        raise ValueError(f"AIRS-Bench task directory does not exist: {task_root}")

    tasks = []
    metadata_paths = sorted(task_root.glob("*/metadata.yaml"))

    for metadata_path in metadata_paths:
        task_dir = metadata_path.parent
        metadata_text = metadata_path.read_text(encoding="utf-8")
        project_path = task_dir / "project_description.md"
        project_text = project_path.read_text(encoding="utf-8") if project_path.exists() else ""
        top = _parse_top_level(metadata_text)
        info = _parse_logging_info(metadata_text)
        task_name = str(info.get("name") or task_dir.name)
        metric = str(info.get("metric") or "official metric")
        dataset = str(info.get("dataset") or "official dataset")
        category = str(info.get("category") or "unknown category")
        research_problem = str(info.get("research_problem") or task_name)
        lower_is_better = bool(top.get("metric_lower_is_better", False))
        direction = "lower is better" if lower_is_better else "higher is better"
        sota = info.get("sota", "")
        optimal = info.get("optimal_score", "")
        worst = info.get("estimated_worst_score", "")

        question = (
            f"AIRS-Bench task `{task_name}`: solve {research_problem} on `{dataset}` "
            f"using metric `{metric}` ({direction}). Official task brief excerpt: "
            f"{_first_sentence(project_text)}"
        )
        task = {
            "task_id": f"airs_{task_name}",
            "source": "AIRS-Bench official task definition",
            "domain": category,
            "question": question,
            "related_work_trap": (
                "Do not report official AIRS-Bench performance unless the generated submission is evaluated "
                "by the task's official evaluate.py script; planning-only runs are not official benchmark scores."
            ),
            "required_evidence": [
                "official task metadata",
                "submission artifact",
                "official evaluator command",
                "metric direction",
                "SOTA or baseline comparison plan",
            ],
            "toy_experiment": (
                f"Prepare `submission.csv`, run the task-local `evaluate.py`, report `{metric}` with "
                f"metric direction `{direction}`, and compare against SOTA `{sota}` when available."
            ),
            "expected_artifacts": [
                "submission.csv",
                "evaluate.py command",
                "metrics.json",
                "reproducibility commands",
                "claim-evidence table",
            ],
            "official_metadata": {
                "task_name": task_name,
                "split": split,
                "dataset": dataset,
                "category": category,
                "research_problem": research_problem,
                "metric": metric,
                "metric_lower_is_better": lower_is_better,
                "sota": sota,
                "optimal_score": optimal,
                "estimated_worst_score": worst,
                "metadata_path": str(metadata_path.relative_to(repo_dir)),
                "project_description_path": str(project_path.relative_to(repo_dir)) if project_path.exists() else "",
            },
        }
        tasks.append(task)

    if max_per_category:
        selected = []
        counts: dict[str, int] = {}
        for task in sorted(tasks, key=lambda item: (item["domain"], item["task_id"])):
            category = str(task["domain"])
            count = counts.get(category, 0)
            if count >= max_per_category:
                continue
            selected.append(task)
            counts[category] = count + 1
            if limit and len(selected) >= limit:
                break
        tasks = selected
    elif limit:
        tasks = tasks[:limit]

    output = {
        "source": "AIRS-Bench official task definitions",
        "source_url": "https://github.com/facebookresearch/airs-bench",
        "source_revision": _git_revision(repo_dir),
        "split": split,
        "tasks": tasks,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return {
        "output": str(output_path),
        "task_count": len(tasks),
        "source_revision": output["source_revision"],
        "split": split,
        "max_per_category": max_per_category,
    }
