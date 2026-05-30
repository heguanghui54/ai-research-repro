#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from datasets import Dataset, load_dataset

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from ai_research_repro.llm import chat_json_result  # noqa: E402


SYSTEM = """You are solving SVAMP arithmetic word problems for an AIRS-Bench submission.
Return JSON only. Compute carefully. Each answer must be a single integer string, no units."""


def _integer_string(value: Any) -> str:
    text = str(value).strip()
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return "0"
    number = float(match.group(0))
    if abs(number - round(number)) < 1e-6:
        return str(int(round(number)))
    return str(number)


def _few_shot_examples(train: Any, count: int) -> list[dict[str, str]]:
    examples = []
    for row in train.select(range(min(count, len(train)))):
        examples.append(
            {
                "question": row["question_concat"],
                "answer": _integer_string(row["Answer"]),
            }
        )
    return examples


def _solve_batch(*, model: str, examples: list[dict[str, str]], rows: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    payload = {
        "few_shot_examples": examples,
        "problems": [
            {
                "index": idx,
                "id": row.get("ID", ""),
                "question": row["question_concat"],
            }
            for idx, row in enumerate(rows)
        ],
    }
    user = f"""Solve each arithmetic word problem.

Return exactly this JSON shape:
{{"answers": [{{"index": 0, "answer": "42"}}, ...]}}

Input:
{json.dumps(payload, indent=2, ensure_ascii=False)}
"""
    result = chat_json_result(
        system=SYSTEM,
        user=user,
        model=model,
        fallback=lambda: {"answers": [{"index": idx, "answer": "0"} for idx in range(len(rows))]},
    )
    parsed = result.parsed if isinstance(result.parsed, dict) else {}
    answers_by_index: dict[int, str] = {}
    for item in parsed.get("answers", []):
        if not isinstance(item, dict):
            continue
        try:
            idx = int(item.get("index"))
        except Exception:
            continue
        answers_by_index[idx] = _integer_string(item.get("answer", "0"))
    answers = [answers_by_index.get(idx, "0") for idx in range(len(rows))]
    return answers, result.meta or {}


def _write_submission(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Answer"])
        for value in values:
            writer.writerow([value])


def _run_evaluator(*, airs_repo: Path, work_dir: Path, submission_path: Path) -> dict[str, Any]:
    task_dir = airs_repo / "airsbench" / "tasks" / "rad" / "MathQuestionAnsweringSVAMPAccuracy"
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
    stdout = completed.stdout
    metrics: dict[str, Any] = {}
    start = stdout.rfind("{")
    end = stdout.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            parsed = json.loads(stdout[start : end + 1])
            if isinstance(parsed, dict):
                metrics = parsed
        except json.JSONDecodeError:
            metrics = {}
    return {
        "command": command,
        "cwd": str(work_dir),
        "exit_code": completed.returncode,
        "stdout": stdout,
        "stderr": completed.stderr,
        "metrics": metrics,
    }


def run_submission(*, airs_repo: Path, output_dir: Path, model: str, limit: int, batch_size: int, few_shot: int) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir = output_dir / "work"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    (work_dir / "data").mkdir(parents=True)

    dataset = load_dataset("ChilleD/SVAMP")
    train = dataset["train"]
    test = dataset["test"]
    selected = test.select(range(min(limit, len(test)))) if limit else test
    examples = _few_shot_examples(train, few_shot)

    labels = [_integer_string(row["Answer"]) for row in selected]
    Dataset.from_dict({"Answer": labels}).save_to_disk(str(work_dir / "data" / "test_with_labels"))

    predictions: list[str] = []
    call_meta: list[dict[str, Any]] = []
    row_records: list[dict[str, Any]] = []
    for start in range(0, len(selected), batch_size):
        batch = [selected[idx] for idx in range(start, min(start + batch_size, len(selected)))]
        answers, meta = _solve_batch(model=model, examples=examples, rows=batch)
        predictions.extend(answers)
        call_meta.append(meta)
        for offset, (row, answer) in enumerate(zip(batch, answers)):
            row_records.append(
                {
                    "index": start + offset,
                    "id": row.get("ID", ""),
                    "question": row["question_concat"],
                    "prediction": answer,
                    "label": _integer_string(row["Answer"]),
                    "correct": answer == _integer_string(row["Answer"]),
                }
            )
        print(f"[svamp-deepseek] solved {len(predictions)}/{len(selected)}", flush=True)

    submission_path = output_dir / "submission.csv"
    _write_submission(submission_path, predictions)
    evaluation = _run_evaluator(airs_repo=airs_repo, work_dir=work_dir, submission_path=submission_path)
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    fallback_calls = 0
    for meta in call_meta:
        if meta.get("fallback"):
            fallback_calls += 1
        for key in usage:
            usage[key] += int(meta.get("usage", {}).get(key, 0) or 0)
    result = {
        "task": "MathQuestionAnsweringSVAMPAccuracy",
        "model": model,
        "limit": len(selected),
        "batch_size": batch_size,
        "few_shot": few_shot,
        "submission_path": str(submission_path),
        "evaluation": evaluation,
        "accuracy": evaluation.get("metrics", {}).get("Accuracy"),
        "usage": usage,
        "llm_call_count": len(call_meta),
        "fallback_calls": fallback_calls,
        "rows": row_records,
        "limitations": [
            "This is a local AIRS evaluator run on SVAMP using Hugging Face test questions and labels for scoring.",
            "It is not an official AIRS leaderboard submission because the full AIRS harness and raw-data mount are not used.",
            "The agent prompt receives test questions but not test answers; labels are mounted only for evaluate.py.",
        ],
    }
    (output_dir / "deepseek_svamp_submission.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = [
        "# DeepSeek SVAMP AIRS Evaluator Run",
        "",
        f"- Task: `{result['task']}`",
        f"- Model: `{model}`",
        f"- Examples evaluated: {len(selected)}",
        f"- Batch size: {batch_size}",
        f"- Few-shot examples: {few_shot}",
        f"- LLM calls: {len(call_meta)}",
        f"- Fallback calls: {fallback_calls}",
        f"- Accuracy: {result['accuracy']}",
        f"- Submission: `{submission_path}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in result["limitations"])
    lines.append("")
    (output_dir / "deepseek_svamp_submission.md").write_text("\n".join(lines), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--airs-repo", default="/tmp/airs-bench")
    parser.add_argument("--output-dir", default="runs/airs_svamp_deepseek_submission")
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--few-shot", type=int, default=4)
    args = parser.parse_args()
    result = run_submission(
        airs_repo=Path(args.airs_repo),
        output_dir=Path(args.output_dir),
        model=args.model,
        limit=args.limit,
        batch_size=args.batch_size,
        few_shot=args.few_shot,
    )
    print(json.dumps({"accuracy": result["accuracy"], "llm_call_count": result["llm_call_count"], "fallback_calls": result["fallback_calls"]}, indent=2))


if __name__ == "__main__":
    main()
