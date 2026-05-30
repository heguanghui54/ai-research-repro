from __future__ import annotations

import json
import re
import statistics
from pathlib import Path
from typing import Any


_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]+")
_FEEDBACK_TERMS = (
    "score",
    "failure",
    "error",
    "warning",
    "audit",
    "measured",
    "observed",
    "runtime",
    "token",
    "call",
    "diff",
    "drift",
)
_NO_UPDATE_TERMS = ("no update", "not executed", "none", "not applied")


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in _TOKEN_RE.findall(text)}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _update_text(answer: dict[str, Any]) -> str:
    raw = answer.get("policy_update", "")
    if isinstance(raw, str):
        return raw.strip()
    return json.dumps(raw, ensure_ascii=False, sort_keys=True)


def analyze_policy_updates(*, results_path: Path, output_dir: Path) -> dict[str, Any]:
    summary = json.loads(results_path.read_text(encoding="utf-8"))
    method = None
    for item in summary.get("results", []):
        if item.get("method") == "multi_artifact_evolution":
            method = item
            break
    if not method:
        raise ValueError("No multi_artifact_evolution method found in results.")

    rows: list[dict[str, Any]] = []
    seed_summaries: list[dict[str, Any]] = []
    for seed_result in method.get("seeds", []):
        seed = seed_result.get("seed")
        previous_tokens: set[str] = set()
        repeated_count = 0
        no_update_count = 0
        feedback_count = 0
        task_specific_count = 0
        similarities: list[float] = []
        update_lengths: list[int] = []
        for idx, task_result in enumerate(seed_result.get("tasks", [])):
            task = task_result.get("task", {})
            answer = task_result.get("answer", {})
            update = _update_text(answer)
            update_tokens = _tokens(update)
            task_terms = _tokens(" ".join(
                [
                    str(task.get("task_id", "")),
                    str(task.get("question", "")),
                    " ".join(str(item) for item in task.get("required_evidence", [])),
                    " ".join(str(item) for item in task.get("expected_artifacts", []) or []),
                ]
            ))
            similarity = _jaccard(update_tokens, previous_tokens) if idx else 0.0
            task_overlap = _jaccard(update_tokens, task_terms)
            has_no_update = any(term in update.lower() for term in _NO_UPDATE_TERMS)
            has_feedback = any(term in update.lower() for term in _FEEDBACK_TERMS)
            is_task_specific = task_overlap >= 0.08
            is_repeated = idx > 0 and similarity >= 0.45
            repeated_count += int(is_repeated)
            no_update_count += int(has_no_update)
            feedback_count += int(has_feedback)
            task_specific_count += int(is_task_specific)
            similarities.append(similarity)
            update_lengths.append(len(update))
            rows.append(
                {
                    "seed": seed,
                    "step": idx,
                    "task_id": task.get("task_id", ""),
                    "task_score": task_result.get("score", {}).get("score", 0),
                    "update_chars": len(update),
                    "jaccard_vs_prior_policy": round(similarity, 4),
                    "task_term_overlap": round(task_overlap, 4),
                    "has_feedback_term": has_feedback,
                    "has_no_update_term": has_no_update,
                    "is_repeated": is_repeated,
                    "is_task_specific": is_task_specific,
                    "update_excerpt": update[:240],
                }
            )
            previous_tokens |= update_tokens
        count = max(1, len(seed_result.get("tasks", [])))
        seed_summaries.append(
            {
                "seed": seed,
                "total_score": seed_result.get("total_score", 0),
                "task_count": count,
                "final_policy_chars": len(seed_result.get("final_strategy_policy", "")),
                "mean_update_chars": round(statistics.mean(update_lengths), 4) if update_lengths else 0.0,
                "mean_jaccard_vs_prior_policy": round(statistics.mean(similarities), 4) if similarities else 0.0,
                "repeated_update_rate": round(repeated_count / count, 4),
                "no_update_rate": round(no_update_count / count, 4),
                "feedback_term_rate": round(feedback_count / count, 4),
                "task_specific_rate": round(task_specific_count / count, 4),
            }
        )

    all_rows = rows
    result = {
        "results_path": str(results_path),
        "method": "multi_artifact_evolution",
        "update_count": len(all_rows),
        "seed_summary": seed_summaries,
        "overall": {
            "mean_update_chars": round(statistics.mean(row["update_chars"] for row in all_rows), 4) if all_rows else 0.0,
            "mean_jaccard_vs_prior_policy": round(statistics.mean(row["jaccard_vs_prior_policy"] for row in all_rows), 4) if all_rows else 0.0,
            "repeated_update_rate": round(sum(row["is_repeated"] for row in all_rows) / len(all_rows), 4) if all_rows else 0.0,
            "no_update_rate": round(sum(row["has_no_update_term"] for row in all_rows) / len(all_rows), 4) if all_rows else 0.0,
            "feedback_term_rate": round(sum(row["has_feedback_term"] for row in all_rows) / len(all_rows), 4) if all_rows else 0.0,
            "task_specific_rate": round(sum(row["is_task_specific"] for row in all_rows) / len(all_rows), 4) if all_rows else 0.0,
        },
        "updates": all_rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "policy_update_analysis.json"
    md_path = output_dir / "policy_update_analysis.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_path.write_text(policy_update_analysis_to_markdown(result), encoding="utf-8")
    result["paths"] = {"json": str(json_path), "markdown": str(md_path)}
    return result


def policy_update_analysis_to_markdown(result: dict[str, Any]) -> str:
    overall = result.get("overall", {})
    lines = [
        "# Policy Update Failure Analysis",
        "",
        f"- Method: `{result.get('method', '')}`",
        f"- Updates analyzed: {result.get('update_count', 0)}",
        f"- Mean update chars: {overall.get('mean_update_chars', 0)}",
        f"- Mean Jaccard vs prior policy: {overall.get('mean_jaccard_vs_prior_policy', 0)}",
        f"- Repeated update rate: {overall.get('repeated_update_rate', 0)}",
        f"- No-update rate: {overall.get('no_update_rate', 0)}",
        f"- Feedback-term rate: {overall.get('feedback_term_rate', 0)}",
        f"- Task-specific rate: {overall.get('task_specific_rate', 0)}",
        "",
        "## Seed Summary",
        "",
        "| Seed | Total Score | Final Policy Chars | Mean Update Chars | Repeat Rate | No-Update Rate | Feedback-Term Rate | Task-Specific Rate |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result.get("seed_summary", []):
        lines.append(
            f"| {row.get('seed', '')} | {row.get('total_score', 0)} | {row.get('final_policy_chars', 0)} | "
            f"{row.get('mean_update_chars', 0)} | {row.get('repeated_update_rate', 0)} | "
            f"{row.get('no_update_rate', 0)} | {row.get('feedback_term_rate', 0)} | "
            f"{row.get('task_specific_rate', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Update Rows",
            "",
            "| Seed | Step | Task | Score | Chars | Jaccard Prior | Task Overlap | Feedback | No Update | Repeated | Excerpt |",
            "| ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in result.get("updates", []):
        excerpt = str(row.get("update_excerpt", "")).replace("|", "/").replace("\n", " ")
        lines.append(
            f"| {row.get('seed', '')} | {row.get('step', '')} | `{row.get('task_id', '')}` | "
            f"{row.get('task_score', 0)} | {row.get('update_chars', 0)} | "
            f"{row.get('jaccard_vs_prior_policy', 0)} | {row.get('task_term_overlap', 0)} | "
            f"{row.get('has_feedback_term', False)} | {row.get('has_no_update_term', False)} | "
            f"{row.get('is_repeated', False)} | {excerpt} |"
        )
    return "\n".join(lines).rstrip() + "\n"
