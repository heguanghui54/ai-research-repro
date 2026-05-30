from __future__ import annotations

import json
import math
import statistics
from pathlib import Path
from typing import Any

from .llm import chat_json_result


JUDGE_SYSTEM = """You are an independent ML research artifact judge.
Score generated autonomous-research artifacts for actual research usefulness, not
for whether they merely contain required fields. Be skeptical of plans that claim
completed evidence without execution. Return strict JSON only."""


def _compact_answer(answer: dict[str, Any], *, max_chars: int = 2600) -> str:
    text = json.dumps(answer, ensure_ascii=False, indent=2)
    if len(text) <= max_chars:
        return text
    return text[: max_chars // 2] + "\n[... truncated ...]\n" + text[-max_chars // 2 :]


def _flatten_tasks(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for method_result in summary.get("results", []):
        method = method_result.get("method", "")
        for seed_result in method_result.get("seeds", []):
            seed = seed_result.get("seed")
            for task_result in seed_result.get("tasks", []):
                task = task_result.get("task", {})
                score = task_result.get("score", {})
                rows.append(
                    {
                        "method": method,
                        "seed": seed,
                        "task_id": task.get("task_id", ""),
                        "question": task.get("question", ""),
                        "related_work_trap": task.get("related_work_trap", ""),
                        "rubric_score": score.get("score", 0),
                        "rubric_components": score,
                        "answer": task_result.get("answer", {}),
                    }
                )
    return rows


def _fallback_batch(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evaluations = []
    for item in items:
        score = float(item.get("rubric_score", 0) or 0)
        has_command = bool(item.get("rubric_components", {}).get("has_actionable_reproducibility_command"))
        has_final = int(item.get("rubric_components", {}).get("final_claim_rows", 0) or 0)
        quality = max(1.0, min(5.0, 1.5 + score / 8.0 + (0.25 if has_command else 0.0) + min(has_final, 2) * 0.25))
        evaluations.append(
            {
                "method": item["method"],
                "seed": item["seed"],
                "task_id": item["task_id"],
                "overall_quality": round(quality, 2),
                "scientific_validity": round(max(1.0, quality - 0.5), 2),
                "claim_grounding": round(max(1.0, quality - 0.3), 2),
                "reproducibility": round(max(1.0, quality - (0.0 if has_command else 0.8)), 2),
                "novelty_calibration": round(max(1.0, quality - 0.4), 2),
                "overclaim_risk": "medium",
                "notes": "Fallback heuristic quality estimate; rerun with an API-backed judge for evidence.",
            }
        )
    return evaluations


def _judge_batch(*, items: list[dict[str, Any]], model: str, multimodal: bool = False) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = []
    for item in items:
        payload.append(
            {
                "method": item["method"],
                "seed": item["seed"],
                "task_id": item["task_id"],
                "question": item["question"],
                "related_work_trap": item["related_work_trap"],
                "rubric_score": item["rubric_score"],
                "artifact": _compact_answer(item["answer"]),
            }
        )
    user = f"""Evaluate each generated autonomous-research artifact.

Use 1-5 scores, where 1 is not useful, 3 is a plausible but incomplete research plan,
and 5 is a strong, conservative, reproducible research artifact. Penalize unsupported
claims, missing executable checks, fake completed evidence, and shallow novelty checks.

Return exactly:
{{
  "evaluations": [
    {{
      "method": "...",
      "seed": 0,
      "task_id": "...",
      "overall_quality": 1-5,
      "scientific_validity": 1-5,
      "claim_grounding": 1-5,
      "reproducibility": 1-5,
      "novelty_calibration": 1-5,
      "overclaim_risk": "low|medium|high",
      "notes": "one concise sentence"
    }}
  ]
}}

Artifacts:
{json.dumps(payload, indent=2, ensure_ascii=False)}
"""
    result = chat_json_result(
        system=JUDGE_SYSTEM,
        user=user,
        model=model,
        multimodal=multimodal,
        fallback=lambda: {"evaluations": _fallback_batch(items)},
    )
    parsed = result.parsed if isinstance(result.parsed, dict) else {}
    evaluations = parsed.get("evaluations", [])
    if not isinstance(evaluations, list) or len(evaluations) != len(items):
        evaluations = _fallback_batch(items)
    by_key = {
        (str(item.get("method")), int(item.get("seed", -1)), str(item.get("task_id"))): item
        for item in evaluations
        if isinstance(item, dict)
    }
    normalized = []
    for item in items:
        key = (str(item["method"]), int(item["seed"]), str(item["task_id"]))
        evaluation = dict(by_key.get(key, {}))
        if not evaluation:
            evaluation = _fallback_batch([item])[0]
        evaluation["method"] = item["method"]
        evaluation["seed"] = item["seed"]
        evaluation["task_id"] = item["task_id"]
        evaluation["rubric_score"] = item["rubric_score"]
        for field in ["overall_quality", "scientific_validity", "claim_grounding", "reproducibility", "novelty_calibration"]:
            try:
                evaluation[field] = max(1.0, min(5.0, float(evaluation.get(field, 1))))
            except Exception:
                evaluation[field] = 1.0
        normalized.append(evaluation)
    return normalized, result.meta or {}


def _rank(values: list[float]) -> list[float]:
    order = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    idx = 0
    while idx < len(order):
        end = idx + 1
        while end < len(order) and order[end][1] == order[idx][1]:
            end += 1
        avg_rank = (idx + 1 + end) / 2.0
        for original_idx, _ in order[idx:end]:
            ranks[original_idx] = avg_rank
        idx = end
    return ranks


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    x_mean = statistics.mean(xs)
    y_mean = statistics.mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_den = math.sqrt(sum((x - x_mean) ** 2 for x in xs))
    y_den = math.sqrt(sum((y - y_mean) ** 2 for y in ys))
    if x_den == 0 or y_den == 0:
        return None
    return numerator / (x_den * y_den)


def _method_summary(evaluations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_method: dict[str, list[dict[str, Any]]] = {}
    for item in evaluations:
        by_method.setdefault(str(item["method"]), []).append(item)
    rows = []
    risk_weight = {"low": 0, "medium": 1, "high": 2}
    for method, items in sorted(by_method.items()):
        qualities = [float(item["overall_quality"]) for item in items]
        rubrics = [float(item["rubric_score"]) for item in items]
        risks = [risk_weight.get(str(item.get("overclaim_risk", "medium")).lower(), 1) for item in items]
        rows.append(
            {
                "method": method,
                "n": len(items),
                "mean_overall_quality": round(statistics.mean(qualities), 4),
                "std_overall_quality": round(statistics.pstdev(qualities), 4) if len(qualities) > 1 else 0.0,
                "mean_rubric_score": round(statistics.mean(rubrics), 4),
                "mean_overclaim_risk_index": round(statistics.mean(risks), 4),
            }
        )
    return rows


def _correlations(evaluations: list[dict[str, Any]]) -> dict[str, float | None]:
    rubric_scores = [float(item["rubric_score"]) for item in evaluations]
    judge_scores = [float(item["overall_quality"]) for item in evaluations]
    return {
        "pearson_rubric_vs_quality": _pearson(rubric_scores, judge_scores),
        "spearman_rubric_vs_quality": _pearson(_rank(rubric_scores), _rank(judge_scores)),
    }


def judge_artifacts(
    *,
    results_path: Path,
    output_dir: Path,
    model: str = "deepseek-chat",
    batch_size: int = 5,
    multimodal: bool = False,
    output_prefix: str = "artifact_quality_judge",
) -> dict[str, Any]:
    summary = json.loads(results_path.read_text(encoding="utf-8"))
    rows = _flatten_tasks(summary)
    evaluations: list[dict[str, Any]] = []
    call_meta: list[dict[str, Any]] = []
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        judged, meta = _judge_batch(items=batch, model=model, multimodal=multimodal)
        evaluations.extend(judged)
        call_meta.append(meta)
    api_backed = [item for item in evaluations if item.get("method") != "fixed_template"]
    correlations = {
        "all": _correlations(evaluations),
        "api_backed_only": _correlations(api_backed),
    }
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    fallback_calls = 0
    for meta in call_meta:
        if meta.get("fallback"):
            fallback_calls += 1
        for key in usage:
            usage[key] += int(meta.get("usage", {}).get(key, 0) or 0)
    result = {
        "results_path": str(results_path),
        "model": model,
        "multimodal_route": multimodal,
        "batch_size": batch_size,
        "artifact_count": len(evaluations),
        "llm_call_count": len(call_meta),
        "fallback_calls": fallback_calls,
        "usage": usage,
        "correlations": correlations,
        "method_summary": _method_summary(evaluations),
        "evaluations": evaluations,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{output_prefix}.json"
    md_path = output_dir / f"{output_prefix}.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_path.write_text(judge_to_markdown(result), encoding="utf-8")
    result["paths"] = {"json": str(json_path), "markdown": str(md_path)}
    return result


def judge_to_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Artifact Quality Judge",
        "",
        f"- Model: `{result.get('model', '')}`",
        f"- Multimodal/Monica route: {result.get('multimodal_route', False)}",
        f"- Artifacts judged: {result.get('artifact_count', 0)}",
        f"- LLM calls: {result.get('llm_call_count', 0)}",
        f"- Fallback calls: {result.get('fallback_calls', 0)}",
        f"- Pearson rubric-vs-quality, all artifacts: {result.get('correlations', {}).get('all', {}).get('pearson_rubric_vs_quality')}",
        f"- Spearman rubric-vs-quality, all artifacts: {result.get('correlations', {}).get('all', {}).get('spearman_rubric_vs_quality')}",
        f"- Pearson rubric-vs-quality, API-backed only: {result.get('correlations', {}).get('api_backed_only', {}).get('pearson_rubric_vs_quality')}",
        f"- Spearman rubric-vs-quality, API-backed only: {result.get('correlations', {}).get('api_backed_only', {}).get('spearman_rubric_vs_quality')}",
        "",
        "## Method Summary",
        "",
        "| Method | N | Mean Judge Quality | Std | Mean Rubric Score | Mean Overclaim Risk Index |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result.get("method_summary", []):
        lines.append(
            f"| `{row['method']}` | {row['n']} | {row['mean_overall_quality']:.3f} | "
            f"{row['std_overall_quality']:.3f} | {row['mean_rubric_score']:.3f} | "
            f"{row['mean_overclaim_risk_index']:.3f} |"
        )
    lines.extend(["", "## Lowest-Rated Artifacts", ""])
    sorted_items = sorted(result.get("evaluations", []), key=lambda item: (float(item.get("overall_quality", 0)), -float(item.get("rubric_score", 0))))[:10]
    lines.extend(["| Method | Seed | Task | Judge Quality | Rubric | Risk | Notes |", "| --- | ---: | --- | ---: | ---: | --- | --- |"])
    for item in sorted_items:
        notes = str(item.get("notes", "")).replace("|", "/")
        lines.append(
            f"| `{item.get('method', '')}` | {item.get('seed', '')} | `{item.get('task_id', '')}` | "
            f"{float(item.get('overall_quality', 0)):.2f} | {float(item.get('rubric_score', 0)):.0f} | "
            f"{item.get('overclaim_risk', '')} | {notes} |"
        )
    return "\n".join(lines).rstrip() + "\n"
