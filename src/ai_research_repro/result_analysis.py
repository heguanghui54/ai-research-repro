from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

from .charts import save_bar_chart

BASELINE_METHOD = "single_fixed"


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


def _two_sided_sign_p_value(wins: int, losses: int) -> float:
    trials = wins + losses
    if trials == 0:
        return 1.0
    observed = min(wins, losses)
    tail = sum(math.comb(trials, k) for k in range(observed + 1)) / (2**trials)
    return min(1.0, 2 * tail)


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


def _seed_map(method_result: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(seed_result["seed"]): seed_result for seed_result in method_result.get("seeds", [])}


def analyze_results(summary: dict[str, Any], *, baseline_method: str = BASELINE_METHOD) -> dict[str, Any]:
    method_maps = {item["method"]: _seed_map(item) for item in summary.get("results", [])}
    baseline = method_maps.get(baseline_method, {})
    methods = []

    for method_result in summary.get("results", []):
        method = method_result["method"]
        seeds = method_result.get("seeds", [])
        totals = [float(item["total_score"]) for item in seeds]
        calls = [float(item.get("llm_call_count", 0)) for item in seeds]
        chars = [float(item.get("estimated_prompt_chars", 0) + item.get("estimated_output_chars", 0)) for item in seeds]
        tokens = [float(item.get("token_usage", {}).get("total_tokens", 0)) for item in seeds]

        paired_deltas = []
        wins = 0
        ties = 0
        losses = 0
        for seed_result in seeds:
            seed = int(seed_result["seed"])
            if seed not in baseline:
                continue
            delta = float(seed_result["total_score"]) - float(baseline[seed]["total_score"])
            paired_deltas.append(delta)
            if delta > 0:
                wins += 1
            elif delta < 0:
                losses += 1
            else:
                ties += 1

        delta_ci_low, delta_ci_high = _bootstrap_mean_ci(paired_deltas, seed=17)
        non_tie = wins + losses
        mean_calls = _mean(calls)
        mean_chars = _mean(chars)
        mean_tokens = _mean(tokens)
        mean_score = _mean(totals)
        methods.append(
            {
                "method": method,
                "seed_count": len(seeds),
                "paired_count": len(paired_deltas),
                "mean_score": round(mean_score, 4),
                "std_score": round(_std(totals), 4),
                "mean_delta_vs_baseline": round(_mean(paired_deltas), 4),
                "std_delta_vs_baseline": round(_std(paired_deltas), 4),
                "delta_ci95_low": round(delta_ci_low, 4),
                "delta_ci95_high": round(delta_ci_high, 4),
                "wins_vs_baseline": wins,
                "ties_vs_baseline": ties,
                "losses_vs_baseline": losses,
                "paired_non_tie_count": non_tie,
                "win_rate_excluding_ties": round(wins / non_tie, 6) if non_tie else 0.0,
                "sign_test_p_two_sided": round(_two_sided_sign_p_value(wins, losses), 6),
                "paired_sign_flip_p_two_sided": round(_paired_sign_flip_p_value(paired_deltas, seed=23), 6),
                "mean_llm_calls": round(mean_calls, 4),
                "score_per_call": round(mean_score / mean_calls, 6) if mean_calls else 0.0,
                "mean_total_tokens": round(mean_tokens, 4),
                "score_per_1k_tokens": round(mean_score / (mean_tokens / 1000), 6) if mean_tokens else 0.0,
                "mean_total_chars": round(mean_chars, 4),
                "score_per_10k_chars": round(mean_score / (mean_chars / 10000), 6) if mean_chars else 0.0,
            }
        )

    best_score = max(methods, key=lambda item: item["mean_score"], default=None)
    best_cost_normalized = max(methods, key=lambda item: item["score_per_call"], default=None)
    return {
        "baseline_method": baseline_method,
        "model": summary.get("model"),
        "role_mode": summary.get("role_mode"),
        "task_source": summary.get("task_source"),
        "task_count": summary.get("task_count"),
        "seeds": summary.get("seeds", []),
        "methods": methods,
        "best_by_score": best_score["method"] if best_score else "",
        "best_by_score_per_call": best_cost_normalized["method"] if best_cost_normalized else "",
    }


def write_analysis(analysis: dict[str, Any], workspace: Path) -> dict[str, str]:
    json_path = workspace / "analysis.json"
    md_path = workspace / "analysis.md"
    figure_dir = workspace / "figures"
    json_path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    score_fig = figure_dir / "analysis_scores.svg"
    call_fig = figure_dir / "analysis_score_per_call.svg"
    token_fig = figure_dir / "analysis_score_per_1k_tokens.svg"
    delta_fig = figure_dir / "analysis_delta_vs_baseline.svg"
    save_bar_chart(rows=analysis["methods"], metric="mean_score", title="Mean Benchmark Score", ylabel="Raw rubric score", path=score_fig)
    save_bar_chart(rows=analysis["methods"], metric="score_per_call", title="Score Per LLM Call", ylabel="Score / API call", path=call_fig)
    save_bar_chart(rows=analysis["methods"], metric="score_per_1k_tokens", title="Score Per 1k API Tokens", ylabel="Score / 1k API tokens", path=token_fig)
    save_bar_chart(rows=analysis["methods"], metric="mean_delta_vs_baseline", title="Delta vs Single-Agent Fixed Baseline", ylabel="Score delta", path=delta_fig)

    lines = [
        "# Result Analysis",
        "",
        f"- Baseline: `{analysis['baseline_method']}`",
        f"- Model: `{analysis.get('model', '')}`",
        f"- Role mode: `{analysis.get('role_mode', '')}`",
        f"- Task source: `{analysis.get('task_source', '')}`",
        f"- Seeds: {', '.join(str(seed) for seed in analysis.get('seeds', []))}",
        f"- Best by raw score: `{analysis.get('best_by_score', '')}`",
        f"- Best by score per call: `{analysis.get('best_by_score_per_call', '')}`",
        "",
        "## Figures",
        "",
        "Figure labels: Curated-Ref=`author_curated_reference`, Fixed-Template=`fixed_template`, S-Fixed=`single_fixed`, S-Reflect=`single_reflection`, S-Consist=`single_self_consistency`, M-Fixed=`multi_fixed`, M-Evolve=`multi_artifact_evolution`, M-StructEvolve=`multi_structured_evolution`.",
        "",
        f"![Mean benchmark score](figures/{score_fig.name})",
        "",
        f"![Score per LLM call](figures/{call_fig.name})",
        "",
        f"![Score per 1k tokens](figures/{token_fig.name})",
        "",
        f"![Delta vs baseline](figures/{delta_fig.name})",
        "",
        "## Table",
        "",
        "| Method | Seeds | Mean Score | Delta vs Baseline | W/T/L | Mean Calls | Score/Call | Mean Tokens | Score/1k Tokens | Score/10k Chars |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in analysis["methods"]:
        lines.append(
            f"| `{item['method']}` | {item.get('seed_count', 0)} | {item['mean_score']:.2f} | {item['mean_delta_vs_baseline']:.2f} | "
            f"{item['wins_vs_baseline']}/{item['ties_vs_baseline']}/{item['losses_vs_baseline']} | "
            f"{item['mean_llm_calls']:.1f} | {item['score_per_call']:.3f} | "
            f"{item['mean_total_tokens']:.0f} | {item['score_per_1k_tokens']:.3f} | "
            f"{item['score_per_10k_chars']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Paired Uncertainty",
            "",
            "| Method | Paired Seeds | Mean Delta | Descriptive 95% Bootstrap Interval | Win Rate Excl. Ties | Sign-Test p | Sign-Flip p |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in analysis["methods"]:
        lines.append(
            f"| `{item['method']}` | {item.get('paired_count', 0)} | {item['mean_delta_vs_baseline']:.2f} | "
            f"[{item['delta_ci95_low']:.2f}, {item['delta_ci95_high']:.2f}] | "
            f"{item['win_rate_excluding_ties']:.2f} | {item['sign_test_p_two_sided']:.3f} | "
            f"{item['paired_sign_flip_p_two_sided']:.3f} |"
        )
    seed_count = len(analysis.get("seeds", []))
    if seed_count <= 1:
        uncertainty_note = (
            "Uncertainty note: this run has one seed, so paired bootstrap intervals collapse to the observed delta "
            "and sign-test p-values are descriptive placeholders rather than statistical evidence."
        )
    else:
        method_seed_counts = sorted({int(item.get("seed_count", 0)) for item in analysis.get("methods", []) if int(item.get("seed_count", 0)) > 0})
        mixed_seed_note = ""
        if len(method_seed_counts) > 1:
            mixed_seed_note = (
                f" Method seed counts are mixed ({', '.join(str(count) for count in method_seed_counts)}); "
                "interpret each row using its Seeds and Paired Seeds columns rather than the global seed list. "
            )
        uncertainty_note = (
            f"Uncertainty note: confidence intervals use paired bootstrap resampling over the paired seeds available for each row. {mixed_seed_note}"
            "The sign-flip column is a paired randomization test over seed-level deltas. With a small seed count, all p-values are descriptive stability checks rather than confirmatory statistics or statistical-significance claims."
        )
    lines.extend(
        [
            "",
            uncertainty_note,
            "",
            "Interpretation rule: raw-score improvements are only candidate evidence. Prefer claims that remain positive under call/token-normalized metrics and survive claim audit.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "json": str(json_path),
        "markdown": str(md_path),
        "score_figure": str(score_fig),
        "score_per_call_figure": str(call_fig),
        "score_per_1k_tokens_figure": str(token_fig),
        "delta_figure": str(delta_fig),
    }


def analyze_results_file(results_path: Path) -> dict[str, Any]:
    summary = json.loads(results_path.read_text(encoding="utf-8"))
    analysis = analyze_results(summary)
    analysis["paths"] = write_analysis(analysis, results_path.parent)
    return analysis
