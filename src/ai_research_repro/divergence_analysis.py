from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

from .artifact_quality_judge import _pearson, _rank
from .quality_gap_analysis import _feature_row, _key, _quality_rows
from .quality_primary_analysis import BASELINE_METHOD, _bootstrap_mean_ci, _paired_sign_flip_p_value


_FEATURE_CONTROLS = [
    "estimated_output_chars",
    "risk_term_count",
    "nonfinal_claim_rows",
    "hedge_term_count",
    "unique_token_ratio",
]


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _std(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def _safe_round(value: float | None, digits: int = 4) -> float | None:
    if value is None or math.isnan(value) or math.isinf(value):
        return None
    return round(float(value), digits)


def _solve_linear_system(a: list[list[float]], b: list[float]) -> list[float] | None:
    n = len(b)
    matrix = [row[:] + [b[idx]] for idx, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(matrix[row][col]))
        if abs(matrix[pivot][col]) < 1e-10:
            return None
        if pivot != col:
            matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        denom = matrix[col][col]
        for j in range(col, n + 1):
            matrix[col][j] /= denom
        for row in range(n):
            if row == col:
                continue
            factor = matrix[row][col]
            for j in range(col, n + 1):
                matrix[row][j] -= factor * matrix[col][j]
    return [matrix[row][n] for row in range(n)]


def _ols_coefficients(x_rows: list[list[float]], y: list[float], *, ridge: float = 1e-8) -> list[float] | None:
    if not x_rows or len(x_rows) != len(y):
        return None
    width = len(x_rows[0])
    xtx = [[0.0 for _ in range(width)] for _ in range(width)]
    xty = [0.0 for _ in range(width)]
    for x, value in zip(x_rows, y):
        for i in range(width):
            xty[i] += x[i] * value
            for j in range(width):
                xtx[i][j] += x[i] * x[j]
    for i in range(width):
        xtx[i][i] += ridge
    return _solve_linear_system(xtx, xty)


def _adjusted_intercept(rows: list[dict[str, Any]]) -> float | None:
    if len(rows) <= len(_FEATURE_CONTROLS) + 1:
        return None
    x_rows = [[1.0] + [float(row[f"delta_{name}"]) for name in _FEATURE_CONTROLS] for row in rows]
    y = [float(row["quality_delta"]) for row in rows]
    coeffs = _ols_coefficients(x_rows, y)
    return coeffs[0] if coeffs else None


def _bootstrap_adjusted_intercept(rows: list[dict[str, Any]], *, samples: int = 2000, seed: int = 0) -> tuple[float, float] | None:
    if len(rows) <= len(_FEATURE_CONTROLS) + 1:
        return None
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(samples):
        draw = [rows[rng.randrange(len(rows))] for _ in rows]
        value = _adjusted_intercept(draw)
        if value is not None:
            values.append(value)
    if not values:
        return None
    values.sort()
    low = values[int(0.025 * (len(values) - 1))]
    high = values[int(0.975 * (len(values) - 1))]
    return (low, high)


def _collect_records(
    *,
    results_path: Path,
    judge_a_path: Path,
    judge_b_path: Path,
    baseline_method: str,
) -> list[dict[str, Any]]:
    summary = json.loads(results_path.read_text(encoding="utf-8"))
    qualities = _quality_rows(judge_a_path, judge_b_path)
    feature_rows: dict[tuple[str, int, str], dict[str, Any]] = {}
    for method_result in summary.get("results", []):
        for seed_result in method_result.get("seeds", []):
            for task_result in seed_result.get("tasks", []):
                row = _feature_row(task_result)
                quality = qualities.get(_key(row["method"], row["seed"], row["task_id"]))
                if not quality:
                    continue
                feature_rows[_key(row["method"], row["seed"], row["task_id"])] = {**row, **quality}

    baseline_by_seed_task = {
        (row["seed"], row["task_id"]): row
        for row in feature_rows.values()
        if row["method"] == baseline_method
    }
    records: list[dict[str, Any]] = []
    for row in feature_rows.values():
        if row["method"] == baseline_method:
            continue
        baseline = baseline_by_seed_task.get((row["seed"], row["task_id"]))
        if not baseline:
            continue
        record = {
            "method": row["method"],
            "seed": row["seed"],
            "task_id": row["task_id"],
            "rubric_score": row["rubric_score"],
            "baseline_rubric_score": baseline["rubric_score"],
            "structural_delta": float(row["rubric_score"]) - float(baseline["rubric_score"]),
            "mean_quality": row["mean_quality"],
            "baseline_mean_quality": baseline["mean_quality"],
            "quality_delta": float(row["mean_quality"]) - float(baseline["mean_quality"]),
        }
        for name in _FEATURE_CONTROLS:
            record[f"delta_{name}"] = float(row[name]) - float(baseline[name])
        records.append(record)
    return records


def analyze_divergence(
    *,
    results_path: Path,
    judge_a_path: Path,
    judge_b_path: Path,
    output_dir: Path,
    output_prefix: str = "divergence_analysis",
    baseline_method: str = BASELINE_METHOD,
) -> dict[str, Any]:
    records = _collect_records(
        results_path=results_path,
        judge_a_path=judge_a_path,
        judge_b_path=judge_b_path,
        baseline_method=baseline_method,
    )
    api_records = [
        row
        for row in records
        if row["method"] not in {"fixed_template", "author_curated_reference"}
    ]
    by_method: dict[str, list[dict[str, Any]]] = {}
    for row in records:
        by_method.setdefault(row["method"], []).append(row)

    method_summary = []
    for method, rows in sorted(by_method.items()):
        structural = [float(row["structural_delta"]) for row in rows]
        quality = [float(row["quality_delta"]) for row in rows]
        structural_ci = _bootstrap_mean_ci(structural, seed=101)
        quality_ci = _bootstrap_mean_ci(quality, seed=103)
        adjusted = _adjusted_intercept(rows)
        adjusted_ci = _bootstrap_adjusted_intercept(rows, seed=107)
        opposite = [row for row in rows if float(row["structural_delta"]) > 0 and float(row["quality_delta"]) < 0]
        same_positive = [row for row in rows if float(row["structural_delta"]) > 0 and float(row["quality_delta"]) > 0]
        method_summary.append(
            {
                "method": method,
                "paired_count": len(rows),
                "mean_structural_delta": round(_mean(structural), 4),
                "std_structural_delta": round(_std(structural), 4),
                "structural_delta_ci95_low": round(structural_ci[0], 4),
                "structural_delta_ci95_high": round(structural_ci[1], 4),
                "mean_quality_delta": round(_mean(quality), 4),
                "std_quality_delta": round(_std(quality), 4),
                "quality_delta_ci95_low": round(quality_ci[0], 4),
                "quality_delta_ci95_high": round(quality_ci[1], 4),
                "quality_delta_sign_flip_p_two_sided": round(_paired_sign_flip_p_value(quality, seed=109), 6),
                "opposite_direction_count": len(opposite),
                "opposite_direction_rate": round(len(opposite) / len(rows), 4) if rows else 0.0,
                "same_positive_count": len(same_positive),
                "structural_quality_delta_pearson": _safe_round(_pearson(structural, quality)),
                "structural_quality_delta_spearman": _safe_round(_pearson(_rank(structural), _rank(quality))),
                "length_controlled_quality_delta_at_zero_covariates": _safe_round(adjusted),
                "length_controlled_ci95_low": _safe_round(adjusted_ci[0]) if adjusted_ci else None,
                "length_controlled_ci95_high": _safe_round(adjusted_ci[1]) if adjusted_ci else None,
                "mean_delta_estimated_output_chars": round(_mean([float(row["delta_estimated_output_chars"]) for row in rows]), 4),
                "mean_delta_risk_term_count": round(_mean([float(row["delta_risk_term_count"]) for row in rows]), 4),
                "mean_delta_nonfinal_claim_rows": round(_mean([float(row["delta_nonfinal_claim_rows"]) for row in rows]), 4),
                "mean_delta_hedge_term_count": round(_mean([float(row["delta_hedge_term_count"]) for row in rows]), 4),
                "mean_delta_unique_token_ratio": round(_mean([float(row["delta_unique_token_ratio"]) for row in rows]), 4),
            }
        )

    structural_all = [float(row["structural_delta"]) for row in api_records]
    quality_all = [float(row["quality_delta"]) for row in api_records]
    result = {
        "results_path": str(results_path),
        "judge_a_path": str(judge_a_path),
        "judge_b_path": str(judge_b_path),
        "baseline_method": baseline_method,
        "paired_record_count": len(records),
        "api_backed_paired_record_count": len(api_records),
        "feature_controls": _FEATURE_CONTROLS,
        "api_backed_delta_correlations": {
            "pearson_structural_delta_vs_quality_delta": _safe_round(_pearson(structural_all, quality_all)),
            "spearman_structural_delta_vs_quality_delta": _safe_round(_pearson(_rank(structural_all), _rank(quality_all))),
        },
        "method_summary": method_summary,
        "records": records,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{output_prefix}.json"
    md_path = output_dir / f"{output_prefix}.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_path.write_text(divergence_to_markdown(result), encoding="utf-8")
    result["paths"] = {"json": str(json_path), "markdown": str(md_path)}
    return result


def divergence_to_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Structural/Quality Divergence Analysis",
        "",
        f"- Baseline for paired deltas: `{result.get('baseline_method', '')}`",
        f"- Paired records: {result.get('paired_record_count', 0)}",
        f"- API-backed paired records: {result.get('api_backed_paired_record_count', 0)}",
        f"- Feature controls: {', '.join(f'`{name}`' for name in result.get('feature_controls', []))}",
        "",
        "## Method Summary",
        "",
        "| Method | Pairs | Mean Structural Delta | Structural CI | Mean Quality Delta | Quality CI | Sign-Flip p | Opposite Direction | Length-Controlled Q Delta | Controlled CI | Delta Chars | Delta Risk Terms | Delta Nonfinal Claims |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result.get("method_summary", []):
        adjusted = row.get("length_controlled_quality_delta_at_zero_covariates")
        adjusted_text = "NA" if adjusted is None else f"{adjusted:.3f}"
        adjusted_low = row.get("length_controlled_ci95_low")
        adjusted_high = row.get("length_controlled_ci95_high")
        adjusted_ci = "NA" if adjusted_low is None or adjusted_high is None else f"[{adjusted_low:.3f}, {adjusted_high:.3f}]"
        lines.append(
            f"| `{row['method']}` | {row['paired_count']} | "
            f"{row['mean_structural_delta']:.3f} | "
            f"[{row['structural_delta_ci95_low']:.3f}, {row['structural_delta_ci95_high']:.3f}] | "
            f"{row['mean_quality_delta']:.3f} | "
            f"[{row['quality_delta_ci95_low']:.3f}, {row['quality_delta_ci95_high']:.3f}] | "
            f"{row['quality_delta_sign_flip_p_two_sided']:.3f} | "
            f"{row['opposite_direction_count']}/{row['paired_count']} ({row['opposite_direction_rate']:.3f}) | "
            f"{adjusted_text} | {adjusted_ci} | "
            f"{row['mean_delta_estimated_output_chars']:.1f} | "
            f"{row['mean_delta_risk_term_count']:.3f} | "
            f"{row['mean_delta_nonfinal_claim_rows']:.3f} |"
        )
    corr = result.get("api_backed_delta_correlations", {})
    lines.extend(
        [
            "",
            "## API-Backed Delta Correlation",
            "",
            f"- Pearson structural-delta vs quality-delta: {corr.get('pearson_structural_delta_vs_quality_delta')}",
            f"- Spearman structural-delta vs quality-delta: {corr.get('spearman_structural_delta_vs_quality_delta')}",
            "",
            "Interpretation: a method shows the target divergence when its paired structural delta is positive while its paired cross-judge quality delta is negative. The length-controlled column is an ordinary least-squares intercept from paired quality deltas after controlling for output-length, risk-term, non-final-claim, hedge-term, and lexical-diversity deltas. This is still observational; it is a confound diagnostic, not a causal estimate.",
            "",
        ]
    )
    return "\n".join(lines)
