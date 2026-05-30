from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


def analyze_structured_memory(*, results_path: Path, output_dir: Path) -> dict[str, Any]:
    summary = json.loads(results_path.read_text(encoding="utf-8"))
    method = None
    for item in summary.get("results", []):
        if item.get("method") == "multi_structured_evolution":
            method = item
            break
    if not method:
        raise ValueError("No multi_structured_evolution method found in results.")

    rows: list[dict[str, Any]] = []
    tag_counts: Counter[str] = Counter()
    retrieved_counts: list[int] = []
    retrieved_relevances: list[float] = []
    seed_summary: list[dict[str, Any]] = []
    for seed_result in method.get("seeds", []):
        seed = seed_result.get("seed")
        seed_tags: Counter[str] = Counter()
        seed_retrieved_counts: list[int] = []
        seed_relevances: list[float] = []
        for step, task_result in enumerate(seed_result.get("tasks", [])):
            task = task_result.get("task", {})
            after = task_result.get("structured_memory_after", {}) or {}
            before = task_result.get("structured_memory_before", []) or []
            tags = [str(tag) for tag in after.get("failure_tags", [])]
            seed_tags.update(tags)
            tag_counts.update(tags)
            seed_retrieved_counts.append(len(before))
            retrieved_counts.append(len(before))
            for item in before:
                relevance = float(item.get("relevance", 0) or 0)
                seed_relevances.append(relevance)
                retrieved_relevances.append(relevance)
            rows.append(
                {
                    "seed": seed,
                    "step": step,
                    "task_id": task.get("task_id", ""),
                    "score": task_result.get("score", {}).get("score", 0),
                    "retrieved_count": len(before),
                    "mean_retrieval_relevance": round(statistics.mean([float(item.get("relevance", 0) or 0) for item in before]), 4)
                    if before
                    else 0.0,
                    "failure_tags": tags,
                    "missing_evidence": after.get("missing_evidence", []),
                    "missing_artifacts": after.get("missing_artifacts", []),
                    "prevention_rules": after.get("prevention_rules", []),
                }
            )
        seed_summary.append(
            {
                "seed": seed,
                "total_score": seed_result.get("total_score", 0),
                "task_count": len(seed_result.get("tasks", [])),
                "mean_retrieved_count": round(statistics.mean(seed_retrieved_counts), 4) if seed_retrieved_counts else 0.0,
                "mean_retrieval_relevance": round(statistics.mean(seed_relevances), 4) if seed_relevances else 0.0,
                "tag_counts": dict(seed_tags),
            }
        )

    result = {
        "results_path": str(results_path),
        "method": "multi_structured_evolution",
        "record_count": len(rows),
        "overall": {
            "mean_retrieved_count": round(statistics.mean(retrieved_counts), 4) if retrieved_counts else 0.0,
            "mean_retrieval_relevance": round(statistics.mean(retrieved_relevances), 4) if retrieved_relevances else 0.0,
            "failure_tag_counts": dict(tag_counts),
        },
        "seed_summary": seed_summary,
        "records": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "structured_memory_analysis.json"
    md_path = output_dir / "structured_memory_analysis.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_path.write_text(structured_memory_analysis_to_markdown(result), encoding="utf-8")
    result["paths"] = {"json": str(json_path), "markdown": str(md_path)}
    return result


def structured_memory_analysis_to_markdown(result: dict[str, Any]) -> str:
    overall = result.get("overall", {})
    tag_counts = overall.get("failure_tag_counts", {})
    lines = [
        "# Structured Memory Analysis",
        "",
        f"- Method: `{result.get('method', '')}`",
        f"- Records analyzed: {result.get('record_count', 0)}",
        f"- Mean retrieved records per task: {overall.get('mean_retrieved_count', 0)}",
        f"- Mean retrieval relevance: {overall.get('mean_retrieval_relevance', 0)}",
        "",
        "## Failure Tags",
        "",
        "| Tag | Count |",
        "| --- | ---: |",
    ]
    for tag, count in sorted(tag_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{tag}` | {count} |")
    lines.extend(
        [
            "",
            "## Seed Summary",
            "",
            "| Seed | Total Score | Mean Retrieved | Mean Relevance | Tag Counts |",
            "| ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in result.get("seed_summary", []):
        lines.append(
            f"| {row.get('seed', '')} | {row.get('total_score', 0)} | "
            f"{row.get('mean_retrieved_count', 0)} | {row.get('mean_retrieval_relevance', 0)} | "
            f"`{json.dumps(row.get('tag_counts', {}), sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Records",
            "",
            "| Seed | Step | Task | Score | Retrieved | Relevance | Tags | Missing Evidence | Missing Artifacts |",
            "| ---: | ---: | --- | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in result.get("records", []):
        lines.append(
            f"| {row.get('seed', '')} | {row.get('step', '')} | `{row.get('task_id', '')}` | "
            f"{row.get('score', 0)} | {row.get('retrieved_count', 0)} | "
            f"{row.get('mean_retrieval_relevance', 0)} | "
            f"`{', '.join(row.get('failure_tags', []))}` | "
            f"`{', '.join(row.get('missing_evidence', []))}` | "
            f"`{', '.join(row.get('missing_artifacts', []))}` |"
        )
    return "\n".join(lines).rstrip() + "\n"
