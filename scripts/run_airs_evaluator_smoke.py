#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from datasets import Dataset


def _read_gold(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if "Answer" not in (reader.fieldnames or []):
            raise ValueError(f"Expected Answer column in {path}")
        return [row["Answer"] for row in reader]


def _write_submission(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Answer"])
        for value in values:
            writer.writerow([value])


def _extract_json(stdout: str) -> dict[str, Any]:
    start = stdout.rfind("{")
    end = stdout.rfind("}")
    if start == -1 or end == -1 or end < start:
        return {}
    try:
        parsed = json.loads(stdout[start : end + 1])
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _run_evaluator(*, task_dir: Path, work_dir: Path, submission_path: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        str(task_dir / "evaluate.py"),
        "--submission-file",
        str(submission_path.resolve()),
    ]
    completed = subprocess.run(
        command,
        cwd=work_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": command,
        "cwd": str(work_dir),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "metrics": _extract_json(completed.stdout),
    }


def run_svamp_smoke(*, airs_repo: Path, output_dir: Path) -> dict[str, Any]:
    task_dir = airs_repo / "airsbench" / "tasks" / "rad" / "MathQuestionAnsweringSVAMPAccuracy"
    gold_path = task_dir / "gold_submission.csv"
    if not gold_path.exists():
        raise FileNotFoundError(gold_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir = output_dir / "work"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    (work_dir / "data").mkdir(parents=True)
    submissions_dir = output_dir / "submissions"
    if submissions_dir.exists():
        shutil.rmtree(submissions_dir)
    submissions_dir.mkdir(parents=True)

    gold_answers = _read_gold(gold_path)
    Dataset.from_dict({"Answer": gold_answers}).save_to_disk(str(work_dir / "data" / "test_with_labels"))

    gold_submission = submissions_dir / "gold_submission.csv"
    zero_submission = submissions_dir / "constant_zero_submission.csv"
    shifted_submission = submissions_dir / "shifted_gold_submission.csv"
    _write_submission(gold_submission, gold_answers)
    _write_submission(zero_submission, ["0" for _ in gold_answers])
    _write_submission(shifted_submission, gold_answers[1:] + gold_answers[:1])

    evaluations = {
        "gold": _run_evaluator(task_dir=task_dir, work_dir=work_dir, submission_path=gold_submission),
        "constant_zero": _run_evaluator(task_dir=task_dir, work_dir=work_dir, submission_path=zero_submission),
        "shifted_gold": _run_evaluator(task_dir=task_dir, work_dir=work_dir, submission_path=shifted_submission),
    }
    result = {
        "task": "MathQuestionAnsweringSVAMPAccuracy",
        "airs_repo": str(airs_repo),
        "task_dir": str(task_dir),
        "sample_count": len(gold_answers),
        "evaluator": str(task_dir / "evaluate.py"),
        "status": "pass" if all(item["exit_code"] == 0 for item in evaluations.values()) else "fail",
        "evaluations": evaluations,
        "limitations": [
            "This is an evaluator API smoke test, not an official AIRS-Bench submission.",
            "The labeled test mount is reconstructed from the repository's gold_submission.csv because the full AIRS raw data directory is not present locally.",
            "The run verifies submission formatting, task-local evaluate.py execution, and metric parsing.",
        ],
    }
    json_path = output_dir / "evaluator_smoke.json"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_path = output_dir / "evaluator_smoke.md"
    lines = [
        "# AIRS Evaluator Smoke Test",
        "",
        f"- Task: `{result['task']}`",
        f"- Sample count: {result['sample_count']}",
        f"- Evaluator: `{result['evaluator']}`",
        f"- Status: `{result['status']}`",
        "",
        "| Submission | Exit | Accuracy |",
        "| --- | ---: | ---: |",
    ]
    for name, item in evaluations.items():
        accuracy = item.get("metrics", {}).get("Accuracy", "")
        lines.append(f"| `{name}` | {item['exit_code']} | {accuracy} |")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in result["limitations"])
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path), **result}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--airs-repo", default="/tmp/airs-bench")
    parser.add_argument("--output-dir", default="runs/airs_evaluator_smoke_svamp")
    args = parser.parse_args()
    result = run_svamp_smoke(airs_repo=Path(args.airs_repo), output_dir=Path(args.output_dir))
    print(json.dumps({"status": result["status"], "json": result["json"], "markdown": result["markdown"]}, indent=2))


if __name__ == "__main__":
    main()
