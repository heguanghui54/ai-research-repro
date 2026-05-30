from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

from .artifact_quality_judge import _pearson, _rank


BASELINE_METHOD = "single_fixed"


def _key(item: dict[str, Any]) -> tuple[str, int, str]:
    return (str(item.get("method", "")), int(item.get("seed", -1)), str(item.get("task_id", "")))


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _std(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[int(index)]
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _bootstrap_mean_ci(values: list[float], *, samples: int = 5000, seed: int = 0) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    if len(values) == 1:
        return (values[0], values[0])
    rng = random.Random(seed)
    means = []
    for _ in range(samples):
        draw = [values[rng.randrange(len(values))] for _ in values]
        means.append(statistics.mean(draw))
    return (_quantile(means, 0.025), _quantile(means, 0.975))


def _paired_sign_flip_p_value(values: list[float], *, samples: int = 50000, seed: int = 0) -> float:
    non_zero = [float(value) for value in values if float(value) != 0.0]
    if not non_zero:
        return 1.0
    observed = abs(statistics.mean(non_zero))
    n = len(non_zero)
    if n <= 20:
        total = 2**n
        extreme = 0
        for mask in range(total):
            signed = [value if (mask >> i) & 1 else -value for i, value in enumerate(non_zero)]
            if abs(statistics.mean(signed)) >= observed - 1e-12:
                extreme += 1
        return extreme / total
    rng = random.Random(seed)
    extreme = 0
    for _ in range(samples):
        signed = [value if rng.random() < 0.5 else -value for value in non_zero]
        if abs(statistics.mean(signed)) >= observed - 1e-12:
            extreme += 1
    return extreme / samples


def _risk_index(value: Any) -> float:
    return {"low": 0.0, "medium": 1.0, "high": 2.0}.get(str(value).lower(), 1.0)


def analyze_quality_primary(
    *,
    judge_a_path: Path,
    judge_b_path: Path,
    output_dir: Path,
    output_prefix: str = "quality_primary_analysis",
    baseline_method: str = BASELINE_METHOD,
) -> dict[str, Any]:
    judge_a = json.loads(judge_a_path.read_text(encoding="utf-8"))
    judge_b = json.loads(judge_b_path.read_text(encoding="utf-8"))
    a_map = {_key(item): item for item in judge_a.get("evaluations", [])}
    b_map = {_key(item): item for item in judge_b.get("evaluations", [])}
    keys = sorted(set(a_map) & set(b_map))

    rows: list[dict[str, Any]] = []
    for key in keys:
        a = a_map[key]
        b = b_map[key]
        qa = float(a.get("overall_quality", 0) or 0)
        qb = float(b.get("overall_quality", 0) or 0)
        rows.append(
            {
                "method": key[0],
                "seed": key[1],
                "task_id": key[2],
                "rubric_score": float(a.get("rubric_score", b.get("rubric_score", 0)) or 0),
                "judge_a_quality": qa,
                "judge_b_quality": qb,
                "mean_quality": round((qa + qb) / 2.0, 4),
                "judge_disagreement_abs": round(abs(qb - qa), 4),
                "mean_overclaim_risk_index": round((_risk_index(a.get("overclaim_risk")) + _risk_index(b.get("overclaim_risk"))) / 2.0, 4),
            }
        )

    baseline_by_seed_task = {
        (row["seed"], row["task_id"]): row
        for row in rows
        if row["method"] == baseline_method
    }
    by_method: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_method.setdefault(row["method"], []).append(row)

    method_summary: list[dict[str, Any]] = []
    for method, items in sorted(by_method.items()):
        qualities = [float(item["mean_quality"]) for item in items]
        judge_a_qualities = [float(item["judge_a_quality"]) for item in items]
        judge_b_qualities = [float(item["judge_b_quality"]) for item in items]
        rubrics = [float(item["rubric_score"]) for item in items]
        disagreements = [float(item["judge_disagreement_abs"]) for item in items]
        risks = [float(item["mean_overclaim_risk_index"]) for item in items]
        paired_deltas: list[float] = []
        paired_judge_a_deltas: list[float] = []
        paired_judge_b_deltas: list[float] = []
        wins = ties = losses = 0
        judge_a_wins = judge_a_ties = judge_a_losses = 0
        judge_b_wins = judge_b_ties = judge_b_losses = 0
        for item in items:
            baseline = baseline_by_seed_task.get((item["seed"], item["task_id"]))
            if not baseline:
                continue
            delta = float(item["mean_quality"]) - float(baseline["mean_quality"])
            judge_a_delta = float(item["judge_a_quality"]) - float(baseline["judge_a_quality"])
            judge_b_delta = float(item["judge_b_quality"]) - float(baseline["judge_b_quality"])
            paired_deltas.append(delta)
            paired_judge_a_deltas.append(judge_a_delta)
            paired_judge_b_deltas.append(judge_b_delta)
            if delta > 0:
                wins += 1
            elif delta < 0:
                losses += 1
            else:
                ties += 1
            if judge_a_delta > 0:
                judge_a_wins += 1
            elif judge_a_delta < 0:
                judge_a_losses += 1
            else:
                judge_a_ties += 1
            if judge_b_delta > 0:
                judge_b_wins += 1
            elif judge_b_delta < 0:
                judge_b_losses += 1
            else:
                judge_b_ties += 1
        delta_ci_low, delta_ci_high = _bootstrap_mean_ci(paired_deltas, seed=31)
        judge_a_ci_low, judge_a_ci_high = _bootstrap_mean_ci(paired_judge_a_deltas, seed=41)
        judge_b_ci_low, judge_b_ci_high = _bootstrap_mean_ci(paired_judge_b_deltas, seed=43)
        method_summary.append(
            {
                "method": method,
                "n": len(items),
                "mean_quality": round(_mean(qualities), 4),
                "std_quality": round(_std(qualities), 4),
                "mean_judge_a_quality": round(_mean(judge_a_qualities), 4),
                "mean_judge_b_quality": round(_mean(judge_b_qualities), 4),
                "mean_rubric_score": round(_mean(rubrics), 4),
                "mean_judge_disagreement_abs": round(_mean(disagreements), 4),
                "mean_overclaim_risk_index": round(_mean(risks), 4),
                "paired_mean_quality_delta_vs_baseline": round(_mean(paired_deltas), 4),
                "paired_mean_judge_a_delta_vs_baseline": round(_mean(paired_judge_a_deltas), 4),
                "paired_judge_a_delta_ci95_low": round(judge_a_ci_low, 4),
                "paired_judge_a_delta_ci95_high": round(judge_a_ci_high, 4),
                "paired_judge_a_wins_vs_baseline": judge_a_wins,
                "paired_judge_a_ties_vs_baseline": judge_a_ties,
                "paired_judge_a_losses_vs_baseline": judge_a_losses,
                "paired_judge_a_sign_flip_p_two_sided": round(_paired_sign_flip_p_value(paired_judge_a_deltas, seed=47), 6),
                "paired_mean_judge_b_delta_vs_baseline": round(_mean(paired_judge_b_deltas), 4),
                "paired_judge_b_delta_ci95_low": round(judge_b_ci_low, 4),
                "paired_judge_b_delta_ci95_high": round(judge_b_ci_high, 4),
                "paired_judge_b_wins_vs_baseline": judge_b_wins,
                "paired_judge_b_ties_vs_baseline": judge_b_ties,
                "paired_judge_b_losses_vs_baseline": judge_b_losses,
                "paired_judge_b_sign_flip_p_two_sided": round(_paired_sign_flip_p_value(paired_judge_b_deltas, seed=53), 6),
                "paired_wins_vs_baseline": wins,
                "paired_ties_vs_baseline": ties,
                "paired_losses_vs_baseline": losses,
                "paired_count": len(paired_deltas),
                "paired_delta_ci95_low": round(delta_ci_low, 4),
                "paired_delta_ci95_high": round(delta_ci_high, 4),
                "paired_sign_flip_p_two_sided": round(_paired_sign_flip_p_value(paired_deltas, seed=37), 6),
            }
        )

    quality_scores = [float(row["mean_quality"]) for row in rows]
    rubric_scores = [float(row["rubric_score"]) for row in rows]
    api_rows = [row for row in rows if row["method"] not in {"fixed_template", "author_curated_reference"}]
    api_quality = [float(row["mean_quality"]) for row in api_rows]
    api_rubric = [float(row["rubric_score"]) for row in api_rows]
    result = {
        "judge_a_path": str(judge_a_path),
        "judge_b_path": str(judge_b_path),
        "judge_a_model": judge_a.get("model", ""),
        "judge_b_model": judge_b.get("model", ""),
        "baseline_method": baseline_method,
        "matched_artifact_count": len(rows),
        "correlations": {
            "all": {
                "pearson_rubric_vs_quality": _pearson(rubric_scores, quality_scores),
                "spearman_rubric_vs_quality": _pearson(_rank(rubric_scores), _rank(quality_scores)),
            },
            "api_backed_only": {
                "pearson_rubric_vs_quality": _pearson(api_rubric, api_quality),
                "spearman_rubric_vs_quality": _pearson(_rank(api_rubric), _rank(api_quality)),
            },
        },
        "best_by_mean_quality": max(method_summary, key=lambda item: item["mean_quality"])["method"] if method_summary else "",
        "method_summary": method_summary,
        "records": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{output_prefix}.json"
    md_path = output_dir / f"{output_prefix}.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_path.write_text(quality_primary_to_markdown(result), encoding="utf-8")
    result["paths"] = {"json": str(json_path), "markdown": str(md_path)}
    return result


def quality_primary_to_markdown(result: dict[str, Any]) -> str:
    corr = result.get("correlations", {})
    api_corr = corr.get("api_backed_only", {})
    lines = [
        "# Quality-Primary Cross-Judge Analysis",
        "",
        f"- Judge A: `{result.get('judge_a_model', '')}`",
        f"- Judge B: `{result.get('judge_b_model', '')}`",
        f"- Matched artifacts: {result.get('matched_artifact_count', 0)}",
        f"- Baseline for paired deltas: `{result.get('baseline_method', '')}`",
        f"- Best by cross-judge mean quality: `{result.get('best_by_mean_quality', '')}`",
        f"- API-backed rubric/quality Pearson: {api_corr.get('pearson_rubric_vs_quality')}",
        f"- API-backed rubric/quality Spearman: {api_corr.get('spearman_rubric_vs_quality')}",
        "",
        "## Method Summary",
        "",
        "| Method | N | Mean Quality | Std | Mean Rubric | Delta vs Baseline | 95% CI | W/T/L | Sign-Flip p | Judge Disagreement | Overclaim Risk |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result.get("method_summary", []):
        lines.append(
            f"| `{row['method']}` | {row['n']} | {row['mean_quality']:.3f} | "
            f"{row['std_quality']:.3f} | {row['mean_rubric_score']:.3f} | "
            f"{row['paired_mean_quality_delta_vs_baseline']:.3f} | "
            f"[{row['paired_delta_ci95_low']:.3f}, {row['paired_delta_ci95_high']:.3f}] | "
            f"{row['paired_wins_vs_baseline']}/{row['paired_ties_vs_baseline']}/{row['paired_losses_vs_baseline']} | "
            f"{row['paired_sign_flip_p_two_sided']:.3f} | "
            f"{row['mean_judge_disagreement_abs']:.3f} | {row['mean_overclaim_risk_index']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Judge-Specific Paired Sensitivity",
            "",
            "| Method | DeepSeek Mean | DeepSeek Delta | DeepSeek CI | DeepSeek W/T/L | Monica Mean | Monica Delta | Monica CI | Monica W/T/L |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in result.get("method_summary", []):
        lines.append(
            f"| `{row['method']}` | {row['mean_judge_a_quality']:.3f} | "
            f"{row['paired_mean_judge_a_delta_vs_baseline']:.3f} | "
            f"[{row['paired_judge_a_delta_ci95_low']:.3f}, {row['paired_judge_a_delta_ci95_high']:.3f}] | "
            f"{row['paired_judge_a_wins_vs_baseline']}/{row['paired_judge_a_ties_vs_baseline']}/{row['paired_judge_a_losses_vs_baseline']} | "
            f"{row['mean_judge_b_quality']:.3f} | "
            f"{row['paired_mean_judge_b_delta_vs_baseline']:.3f} | "
            f"[{row['paired_judge_b_delta_ci95_low']:.3f}, {row['paired_judge_b_delta_ci95_high']:.3f}] | "
            f"{row['paired_judge_b_wins_vs_baseline']}/{row['paired_judge_b_ties_vs_baseline']}/{row['paired_judge_b_losses_vs_baseline']} |"
        )
    lines.extend(
        [
            "",
            "Interpretation: this table treats cross-model mean judge quality as the primary artifact-quality metric. "
            "Rubric scores remain useful instrumentation, but methods that gain structural score without improving this table should not be described as producing better research artifacts.",
            "The judge-specific sensitivity table checks whether the direction of the result depends on the DeepSeek judge or the Monica/gpt-4o judge alone.",
            "The confidence intervals are paired bootstraps over matched seed/task artifacts. The sign-flip p-values are descriptive paired randomization checks, not confirmatory hypothesis tests.",
            "",
        ]
    )
    return "\n".join(lines)
