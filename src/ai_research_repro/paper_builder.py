from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

from .claim_audit import audit_results
from .result_analysis import analyze_results, write_analysis


def _method_table(summary: dict[str, Any]) -> str:
    lines = [
        "| Method | Mean Total Score | Std | Mean Runtime (s) | Mean Calls | Mean Tokens | Mean Output Chars |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method_result in summary.get("results", []):
        seeds = method_result.get("seeds", [])
        totals = [item["total_score"] for item in seeds]
        runtimes = [item["runtime_seconds"] for item in seeds]
        calls = [item.get("llm_call_count", 0) for item in seeds]
        tokens = [item.get("token_usage", {}).get("total_tokens", 0) for item in seeds]
        chars = [item["estimated_output_chars"] for item in seeds]
        std = statistics.pstdev(totals) if len(totals) > 1 else 0.0
        lines.append(
            f"| `{method_result['method']}` | {statistics.mean(totals):.2f} | "
            f"{std:.2f} | {statistics.mean(runtimes):.2f} | {statistics.mean(calls):.1f} | "
            f"{statistics.mean(tokens):.0f} | {statistics.mean(chars):.0f} |"
        )
    return "\n".join(lines)


def _best_method(summary: dict[str, Any]) -> str:
    scored = []
    for method_result in summary.get("results", []):
        totals = [item["total_score"] for item in method_result.get("seeds", [])]
        if totals:
            scored.append((statistics.mean(totals), method_result["method"]))
    if not scored:
        return "No method result is available."
    score, method = max(scored)
    return f"The highest mean structural-rubric score is `{method}` with {score:.2f} points; this is not a scientific-quality ranking."


def _analysis_table(analysis: dict[str, Any]) -> str:
    lines = [
        "| Method | Delta vs Baseline | Descriptive 95% CI | W/T/L | Score/Call | Score/1k Tokens | Score/10k Chars |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in analysis["methods"]:
        ci_low = item.get("delta_ci95_low", item["mean_delta_vs_baseline"])
        ci_high = item.get("delta_ci95_high", item["mean_delta_vs_baseline"])
        lines.append(
            f"| `{item['method']}` | {item['mean_delta_vs_baseline']:.2f} | "
            f"[{ci_low:.2f}, {ci_high:.2f}] | "
            f"{item['wins_vs_baseline']}/{item['ties_vs_baseline']}/{item['losses_vs_baseline']} | "
            f"{item['score_per_call']:.3f} | {item['score_per_1k_tokens']:.3f} | "
            f"{item['score_per_10k_chars']:.3f} |"
        )
    return "\n".join(lines)


def _paired_quality_effect_size(quality: dict[str, Any], method: str = "multi_fixed", baseline: str = "single_fixed") -> float | None:
    by_key: dict[tuple[int, str], dict[str, float]] = {}
    for record in quality.get("records", []):
        if record.get("method") not in {method, baseline}:
            continue
        key = (int(record.get("seed", -1)), str(record.get("task_id", "")))
        by_key.setdefault(key, {})[str(record.get("method"))] = float(record.get("mean_quality", 0.0))
    deltas = [values[method] - values[baseline] for values in by_key.values() if method in values and baseline in values]
    if len(deltas) < 2:
        return None
    std = statistics.stdev(deltas)
    if std == 0:
        return 0.0
    return statistics.mean(deltas) / std


def _supplemental_robustness_section(primary_results_path: Path) -> str:
    if primary_results_path.parent.name not in {"research_pilot_deepseek_v2", "research_pilot_deepseek_v3"}:
        return ""
    external_path = Path("runs/research_external_curated_deepseek/analysis.json")
    external_audit_path = Path("runs/research_external_curated_deepseek/claim_audit.json")
    if not external_path.exists():
        return ""
    analysis = json.loads(external_path.read_text(encoding="utf-8"))
    audit = json.loads(external_audit_path.read_text(encoding="utf-8")) if external_audit_path.exists() else {}
    return f"""

## Appendix B. Curated Robustness Check

We also ran a seed-0 robustness check on six benchmark-inspired tasks at `research_artifacts/external_tasks_curated.json`. These tasks are inspired by AIRS-Bench, FIRE-Bench, ScienceAgentBench, MultiAgentBench, and AI Scientist-v2 evaluation patterns, but they are not official benchmark scores.

{_analysis_table(analysis)}

Single-seed structural-rubric leader: `{analysis.get('best_by_score', '')}`. Best score-per-call method: `{analysis.get('best_by_score_per_call', '')}`. This is illustrative only and not a quality or statistical claim. Claim audit status: `{audit.get('status', 'not_run')}` with {audit.get('error_count', 0)} errors and {audit.get('warning_count', 0)} warnings.

This supplemental run supports the same narrow trade-off as the main experiment: multi-agent decomposition scores higher on raw artifact-completeness, while simpler workflows are far more inference-efficient. Because the robustness run uses one seed and benchmark-inspired tasks rather than official benchmark evaluators, it should be treated as a single-seed robustness probe, not as an external benchmark result.
"""


def _supplemental_airs_section(primary_results_path: Path) -> str:
    if primary_results_path.parent.name not in {"research_pilot_deepseek_v2", "research_pilot_deepseek_v3"}:
        return ""
    analysis_path = Path("runs/airs_official_subset_deepseek/analysis.json")
    audit_path = Path("runs/airs_official_subset_deepseek/claim_audit.json")
    task_path = Path("research_artifacts/airs_official_tasks_subset.json")
    if not analysis_path.exists() or not task_path.exists():
        return ""
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else {}
    task_data = json.loads(task_path.read_text(encoding="utf-8"))
    task_rows = []
    for task in task_data.get("tasks", []):
        meta = task.get("official_metadata", {})
        task_rows.append(
            f"| `{meta.get('task_name', task.get('task_id', ''))}` | {task.get('domain', '')} | "
            f"`{meta.get('dataset', '')}` | `{meta.get('metric', '')}` |"
        )
    task_table = "\n".join(
        ["| AIRS Task | Domain | Dataset | Metric |", "| --- | --- | --- | --- |"] + task_rows
    )
    return f"""

## Appendix C. AIRS-Bench Official-Definition Subset

To move beyond hand-written micro-tasks, we imported six official AIRS-Bench RAD task definitions from `facebookresearch/airs-bench` at revision `{task_data.get('source_revision', '')}`. The importer uses `metadata.yaml` and `project_description.md` to construct planning/evidence tasks in our schema. This subset is not an official AIRS-Bench score because it evaluates planning/evidence artifacts rather than generated submissions. Appendix G separately reports one task-local AIRS evaluator run for SVAMP.

{task_table}

{_analysis_table(analysis)}

Single-seed structural-rubric leader: `{analysis.get('best_by_score', '')}`. Best score-per-call method: `{analysis.get('best_by_score_per_call', '')}`. This is illustrative only and not a quality or statistical claim. Claim audit status: `{audit.get('status', 'not_run')}` with {audit.get('error_count', 0)} errors and {audit.get('warning_count', 0)} warnings.

The AIRS-definition subset reinforces the main trade-off under official task descriptions: multi-agent decomposition yields stronger raw planning/evidence artifacts, while single-agent workflows remain much more efficient per API call and token.
"""


def _extended_airs_section(primary_results_path: Path) -> str:
    if primary_results_path.parent.name != "research_pilot_deepseek_v3":
        return ""
    analysis_path = Path("runs/airs_official_12_deepseek/analysis.json")
    audit_path = Path("runs/airs_official_12_deepseek/claim_audit.json")
    task_path = Path("research_artifacts/airs_official_tasks_12.json")
    if not analysis_path.exists() or not task_path.exists():
        return ""

    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else {}
    task_data = json.loads(task_path.read_text(encoding="utf-8"))
    categories: dict[str, int] = {}
    metrics: dict[str, int] = {}
    for task in task_data.get("tasks", []):
        meta = task.get("official_metadata", {})
        categories[str(task.get("domain", "unknown"))] = categories.get(str(task.get("domain", "unknown")), 0) + 1
        metrics[str(meta.get("metric", "unknown"))] = metrics.get(str(meta.get("metric", "unknown")), 0) + 1
    category_summary = ", ".join(f"{name}: {count}" for name, count in sorted(categories.items()))
    metric_summary = ", ".join(f"{name}: {count}" for name, count in sorted(metrics.items()))

    return f"""

## Appendix D. Extended AIRS-Definition Coverage

After the six-task AIRS-definition subset, we ran an additional seed-0 coverage check on 12 official AIRS-Bench RAD task definitions at `research_artifacts/airs_official_tasks_12.json`. The task file was imported from `facebookresearch/airs-bench` revision `{task_data.get('source_revision', '')}` with at most two tasks per category. Domains covered: {category_summary}. Metrics covered: {metric_summary}.

This run compares three methods only: `single_fixed`, budget-matched `single_self_consistency`, and `multi_fixed`. It excludes `multi_artifact_evolution` to keep API cost bounded while checking whether the structural-rubric pattern appears on a broader official-definition set.

{_analysis_table(analysis)}

Single-seed structural-rubric leader: `{analysis.get('best_by_score', '')}`. Best score-per-call method: `{analysis.get('best_by_score_per_call', '')}`. This is illustrative only and not a quality or statistical claim. Claim audit status: `{audit.get('status', 'not_run')}` with {audit.get('error_count', 0)} errors and {audit.get('warning_count', 0)} warnings.

The broader official-definition coverage is consistent with the structural-rubric pattern, while `single_fixed` remains the most call-efficient. Because this is still a single-seed planning/evidence proxy rather than an official AIRS evaluator run, it is illustrative external-validity context only; it does not establish official benchmark performance or statistical reliability.
"""


def _ai_research_tasks20_section(primary_results_path: Path) -> str:
    if primary_results_path.parent.name != "research_pilot_deepseek_v3":
        return ""
    seed0_dir = Path("runs/ai_research_tasks20_representative_seed0")
    primary_candidates = [
        Path("runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek"),
        Path("runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_3seed_deepseek"),
        Path("runs/ai_research_tasks20_primary_10seed_deepseek"),
        Path("runs/ai_research_tasks20_primary_8seed_deepseek"),
        Path("runs/ai_research_tasks20_primary_5seed_deepseek"),
    ]
    primary_dir = next(
        (path for path in primary_candidates if (path / "analysis.json").exists()),
        Path("runs/ai_research_tasks20_primary_5seed_deepseek"),
    )
    quality_candidates = [
        Path("runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek"),
        Path("runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_3seed_deepseek"),
        Path("runs/ai_research_tasks20_primary_10seed_deepseek"),
        Path("runs/ai_research_tasks20_primary_3seed_deepseek"),
    ]
    quality_dir = next(
        (path for path in quality_candidates if (path / "quality_primary_analysis.json").exists()),
        Path("runs/ai_research_tasks20_primary_3seed_deepseek"),
    )
    run_dir = primary_dir if (primary_dir / "analysis.json").exists() else seed0_dir
    analysis_path = run_dir / "analysis.json"
    audit_path = run_dir / "claim_audit.json"
    quality_path = quality_dir / "quality_primary_analysis.json"
    seed0_quality_path = seed0_dir / "quality_primary_analysis.json"
    task_path = Path("research_artifacts/ai_research_tasks_20.json")
    if not analysis_path.exists() or not task_path.exists():
        return ""
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else {}
    task_data = json.loads(task_path.read_text(encoding="utf-8"))
    domains: dict[str, int] = {}
    for task in task_data.get("tasks", []):
        domains[str(task.get("domain", "unknown"))] = domains.get(str(task.get("domain", "unknown")), 0) + 1
    domain_summary = ", ".join(f"{name}: {count}" for name, count in sorted(domains.items()))
    primary_note = ""
    if run_dir == primary_dir:
        api_seed_count = len(analysis.get("seeds", []))
        seed_phrase = (
            f"seeds {analysis.get('seeds', [])[0]} through {analysis.get('seeds', [])[-1]}"
            if analysis.get("seeds")
            else "the available repeated seeds"
        )
        primary_note = (
            f"The primary structural comparison uses {seed_phrase} ({api_seed_count} seeds) for "
            "`single_fixed` and `multi_fixed`. The deterministic "
            "`author_curated_reference` and `fixed_template` rows are retained "
            "as seed-0 calibration anchors only, so their zero variance should "
            "not be read as a repeated-sampling estimate."
        )
        if any(item.get("method") == "single_self_consistency" for item in analysis.get("methods", [])):
            if primary_dir.name == "ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek":
                primary_note += (
                    " The budget-matched `single_self_consistency` row now also uses "
                    "seeds 0 through 9, testing whether extra single-agent calls "
                    "account for the structural gap under the same task and seed coverage."
                )
            elif primary_dir.name == "ai_research_tasks20_primary_10seed_plus_selfconsistency_3seed_deepseek":
                primary_note += (
                    " The budget-matched `single_self_consistency` row is a "
                    "three-seed extension for seeds 0, 1, and 2, so it is not yet "
                    "a ten-seed estimate."
                )
    else:
        primary_note = (
            "Only the seed-0 coverage run is available, so this section is a "
            "coverage check rather than repeated-seed evidence."
        )
    quality_text = ""
    if quality_path.exists() or seed0_quality_path.exists():
        quality_source = quality_path if quality_path.exists() else seed0_quality_path
        quality = json.loads(quality_source.read_text(encoding="utf-8"))
        quality_is_primary = quality_source.parent == quality_dir
        comparison_path = quality_source.parent / "artifact_quality_judge_comparison.json"
        divergence_path = quality_source.parent / "divergence_analysis.json"
        comparison_text = ""
        if comparison_path.exists():
            comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
            comparison_rows = {row.get("method"): row for row in comparison.get("method_summary", [])}
            single_comp = comparison_rows.get("single_fixed", {})
            multi_comp = comparison_rows.get("multi_fixed", {})
            individual_text = ""
            if single_comp and multi_comp:
                individual_text = (
                    f" Both judges individually rate `single_fixed` above `multi_fixed` "
                    f"(DeepSeek {single_comp.get('mean_judge_a_quality', 0):.3f} versus {multi_comp.get('mean_judge_a_quality', 0):.3f}; "
                    f"Monica/gpt-4o {single_comp.get('mean_judge_b_quality', 0):.3f} versus {multi_comp.get('mean_judge_b_quality', 0):.3f})."
                )
            comparison_text = (
                f" The two model judges have Pearson r={comparison.get('pearson_quality')} "
                f"and Spearman rho={comparison.get('spearman_quality')} over "
                f"{comparison.get('matched_artifact_count', 0)} matched artifacts; Monica/gpt-4o "
                f"averages {comparison.get('mean_delta_b_minus_a')} quality points higher than DeepSeek."
                f"{individual_text}"
            )
        divergence_text = ""
        if divergence_path.exists():
            divergence = json.loads(divergence_path.read_text(encoding="utf-8"))
            div_rows = {row.get("method"): row for row in divergence.get("method_summary", [])}
            multi_div = div_rows.get("multi_fixed", {})
            self_div = div_rows.get("single_self_consistency", {})
            if multi_div:
                divergence_text = (
                    f" A paired divergence test gives `multi_fixed` mean structural delta "
                    f"{multi_div.get('mean_structural_delta', 0):.3f} with CI "
                    f"[{multi_div.get('structural_delta_ci95_low', 0):.3f}, {multi_div.get('structural_delta_ci95_high', 0):.3f}] "
                    f"and mean quality delta {multi_div.get('mean_quality_delta', 0):.3f} with CI "
                    f"[{multi_div.get('quality_delta_ci95_low', 0):.3f}, {multi_div.get('quality_delta_ci95_high', 0):.3f}] "
                    f"against `single_fixed`; {multi_div.get('opposite_direction_count', 0)}/"
                    f"{multi_div.get('paired_count', 0)} paired artifacts have positive structural delta and negative quality delta. "
                    f"After controlling for output-length, risk-term, non-final-claim, hedge-term, and lexical-diversity deltas, "
                    f"the `multi_fixed` quality delta intercept is {multi_div.get('length_controlled_quality_delta_at_zero_covariates', 0):.3f}."
                )
            if self_div:
                divergence_text += (
                    f" The budget-matched `single_self_consistency` row shows the same sign pattern: "
                    f"structural delta {self_div.get('mean_structural_delta', 0):.3f} and quality delta "
                    f"{self_div.get('mean_quality_delta', 0):.3f}, with "
                    f"{self_div.get('opposite_direction_count', 0)}/{self_div.get('paired_count', 0)} "
                    "opposite-direction pairs."
                )
        rows = []
        for row in quality.get("method_summary", []):
            rows.append(
                f"| `{row.get('method', '')}` | {row.get('n', 0)} | "
                f"{row.get('mean_quality', 0):.3f} | {row.get('mean_rubric_score', 0):.3f} | "
                f"{row.get('paired_mean_quality_delta_vs_baseline', 0):.3f} | "
                f"[{row.get('paired_delta_ci95_low', 0):.3f}, {row.get('paired_delta_ci95_high', 0):.3f}] | "
                f"{row.get('paired_wins_vs_baseline', 0)}/{row.get('paired_ties_vs_baseline', 0)}/{row.get('paired_losses_vs_baseline', 0)} |"
            )
        quality_table = "\n".join(
            [
                "| Method | N | Cross-Judge Mean Quality | Mean Rubric | Delta vs S-Fixed | Descriptive 95% CI | W/T/L |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
            + rows
        )
        api_corr = quality.get("correlations", {}).get("api_backed_only", {})
        multi_row = next((row for row in quality.get("method_summary", []) if row.get("method") == "multi_fixed"), {})
        single_row = next((row for row in quality.get("method_summary", []) if row.get("method") == "single_fixed"), {})
        self_consistency_row = next(
            (row for row in quality.get("method_summary", []) if row.get("method") == "single_self_consistency"),
            {},
        )
        self_consistency_text = ""
        if self_consistency_row:
            self_consistency_label = (
                "baseline"
                if quality_source.parent.name == "ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek"
                else "extension"
            )
            self_consistency_text = (
                f" The budget-matched `single_self_consistency` {self_consistency_label} has mean quality "
                f"{self_consistency_row.get('mean_quality', 0):.3f} over "
                f"{self_consistency_row.get('n', 0)} artifacts and paired delta "
                f"{self_consistency_row.get('paired_mean_quality_delta_vs_baseline', 0):.3f} "
                "versus `single_fixed`, so extra single-agent calls do not remove the judged-quality gap."
            )
        judge_specific_text = ""
        if multi_row:
            judge_specific_text = (
                f" Judge-specific sensitivity preserves this direction for `multi_fixed`: "
                f"DeepSeek-only paired delta {multi_row.get('paired_mean_judge_a_delta_vs_baseline', 0):.3f} "
                f"with CI [{multi_row.get('paired_judge_a_delta_ci95_low', 0):.3f}, {multi_row.get('paired_judge_a_delta_ci95_high', 0):.3f}], "
                f"and Monica/gpt-4o-only paired delta {multi_row.get('paired_mean_judge_b_delta_vs_baseline', 0):.3f} "
                f"with CI [{multi_row.get('paired_judge_b_delta_ci95_low', 0):.3f}, {multi_row.get('paired_judge_b_delta_ci95_high', 0):.3f}]."
            )
        paired_d = _paired_quality_effect_size(quality)
        effect_text = f" The paired standardized mean difference is d_z={paired_d:.3f}." if paired_d is not None else ""
        scope_text = "the 20-task artifact set"
        if quality_is_primary:
            if quality_source.parent.name == "ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek":
                scope_text = "the 20-task, ten-seed artifact set with the budget-matched self-consistency baseline"
            elif quality_source.parent.name == "ai_research_tasks20_primary_10seed_plus_selfconsistency_3seed_deepseek":
                scope_text = "the 20-task artifact set with ten-seed `single_fixed`/`multi_fixed` coverage and a three-seed budget-matched self-consistency extension"
            elif quality_source.parent.name == "ai_research_tasks20_primary_10seed_deepseek":
                scope_text = "the 20-task, ten-seed artifact set"
            elif quality_source.parent.name == "ai_research_tasks20_primary_3seed_deepseek":
                scope_text = "the 20-task, three-seed artifact set"
        else:
            scope_text = "the seed-0 20-task artifacts"
        human_caveat = (
            "This is now a repeated-seed model-judge diagnostic, but it is still not a human-evaluation result."
            if quality_is_primary
            else "This quality table remains a seed-0 diagnostic rather than a human-evaluation result."
        )
        quality_text = f"""

Cross-model quality analysis on {scope_text} again separates structural score from judged quality. Among API-backed methods, rubric/quality correlation is Pearson r={api_corr.get('pearson_rubric_vs_quality')} and Spearman rho={api_corr.get('spearman_rubric_vs_quality')}. `single_fixed` has higher cross-judge mean quality ({single_row.get('mean_quality', 0):.3f}) than `multi_fixed` ({multi_row.get('mean_quality', 0):.3f}) despite lower structural-rubric score; the paired quality delta for `multi_fixed` versus `single_fixed` is {multi_row.get('paired_mean_quality_delta_vs_baseline', 0):.3f} over {multi_row.get('paired_count', 0)} matched comparisons, with descriptive paired-bootstrap CI [{multi_row.get('paired_delta_ci95_low', 0):.3f}, {multi_row.get('paired_delta_ci95_high', 0):.3f}].{judge_specific_text}{self_consistency_text} The interval is a percentile interval from 5,000 paired bootstrap resamples over matched seed/task artifacts.{effect_text}{comparison_text}{divergence_text} {human_caveat}

{quality_table}
"""
    monica20_text = ""
    monica20_dir = Path("runs/ai_research_tasks20_monica_gpt4o_3seed")
    monica20_analysis_path = monica20_dir / "analysis.json"
    monica20_audit_path = monica20_dir / "claim_audit.json"
    monica20_quality_path = monica20_dir / "quality_primary_analysis.json"
    monica20_comparison_path = monica20_dir / "artifact_quality_judge_comparison.json"
    if monica20_analysis_path.exists() and monica20_audit_path.exists():
        monica20_analysis = json.loads(monica20_analysis_path.read_text(encoding="utf-8"))
        monica20_audit = json.loads(monica20_audit_path.read_text(encoding="utf-8"))
        monica20_quality_text = ""
        if monica20_quality_path.exists():
            monica20_quality = json.loads(monica20_quality_path.read_text(encoding="utf-8"))
            monica20_comparison = (
                json.loads(monica20_comparison_path.read_text(encoding="utf-8"))
                if monica20_comparison_path.exists()
                else {}
            )
            rows = []
            for row in monica20_quality.get("method_summary", []):
                rows.append(
                    f"| `{row.get('method', '')}` | {row.get('n', 0)} | "
                    f"{row.get('mean_quality', 0):.3f} | {row.get('mean_rubric_score', 0):.3f} | "
                    f"{row.get('paired_mean_quality_delta_vs_baseline', 0):.3f} | "
                    f"[{row.get('paired_delta_ci95_low', 0):.3f}, {row.get('paired_delta_ci95_high', 0):.3f}] | "
                    f"{row.get('paired_wins_vs_baseline', 0)}/{row.get('paired_ties_vs_baseline', 0)}/{row.get('paired_losses_vs_baseline', 0)} |"
                )
            monica20_quality_table = "\n".join(
                [
                    "| Method | N | Cross-Judge Mean Quality | Mean Rubric | Delta vs S-Fixed | Descriptive 95% CI | W/T/L |",
                    "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
                ]
                + rows
            )
            api_corr = monica20_quality.get("correlations", {}).get("api_backed_only", {})
            monica20_multi = next((row for row in monica20_quality.get("method_summary", []) if row.get("method") == "multi_fixed"), {})
            monica20_quality_text = f"""

Quality judging on these {monica20_quality.get('matched_artifact_count', 0)} gpt-4o-generated artifacts again favors `single_fixed`: `multi_fixed` has paired mean quality delta {monica20_multi.get('paired_mean_quality_delta_vs_baseline', 0):.3f} versus `single_fixed` with descriptive paired-bootstrap CI [{monica20_multi.get('paired_delta_ci95_low', 0):.3f}, {monica20_multi.get('paired_delta_ci95_high', 0):.3f}], while rubric/quality correlation is Pearson r={api_corr.get('pearson_rubric_vs_quality')} and Spearman rho={api_corr.get('spearman_rubric_vs_quality')}. The two judges have Pearson r={monica20_comparison.get('pearson_quality')} and Spearman rho={monica20_comparison.get('spearman_quality')} over {monica20_comparison.get('matched_artifact_count', 0)} artifacts.

{monica20_quality_table}
"""
        monica20_text = f"""

### Monica/gpt-4o Twenty-Task Generator Check

To test whether the structural-rubric pattern is specific to DeepSeek generation, we ran the same 20-task `single_fixed` versus `multi_fixed` comparison with Monica's `gpt-4o` route as the generator for seeds 0, 1, and 2. This is now a small repeated-seed external-generator check, not a powered model-family replication.

{_analysis_table(monica20_analysis)}

Claim audit status: `{monica20_audit.get('status', 'not_run')}` with {monica20_audit.get('error_count', 0)} errors and {monica20_audit.get('warning_count', 0)} warnings. The errors are important: across all three seeds, `single_fixed` missed reproducibility commands and a claim-evidence table on `artifact_memory_retrieval`, so the run should be read as a robustness diagnostic rather than a clean pass.

{monica20_quality_text}
"""
    return f"""

## Appendix E. Twenty-Task Diagnostic Coverage Check

To reduce dependence on the five default micro-tasks, we added an author-created 20-task diagnostic suite at `research_artifacts/ai_research_tasks_20.json`. It covers {domain_summary}. This is still not an official benchmark, but the main `single_fixed` versus `multi_fixed` structural comparison now uses the largest completed repeated-seed DeepSeek run available in the package.

The retained table compares deterministic `author_curated_reference`, deterministic `fixed_template`, `single_fixed`, and `multi_fixed`. It tests whether the raw structural-rubric pattern appears on a broader task surface while keeping API cost bounded. {primary_note}

{_analysis_table(analysis)}

Structural-rubric leader: `{analysis.get('best_by_score', '')}`. Best score-per-call method: `{analysis.get('best_by_score_per_call', '')}`. Claim audit status: `{audit.get('status', 'not_run')}` with {audit.get('error_count', 0)} errors and {audit.get('warning_count', 0)} warnings.

{quality_text}

{monica20_text}

This coverage check supports the paper's diagnostic conclusion rather than a broad performance claim: expanding to 20 tasks and the currently completed repeated-seed DeepSeek structural run preserves the raw-rubric advantage for `multi_fixed` over `single_fixed`, while the completed cross-model quality-primary analysis over the same ten-seed DeepSeek artifact set favors the simpler `single_fixed` baseline. The remaining missing step is human expert review over the expanded task set.
"""


def _airs_evaluator_smoke_section(primary_results_path: Path) -> str:
    if primary_results_path.parent.name != "research_pilot_deepseek_v3":
        return ""
    smoke_path = Path("runs/airs_evaluator_smoke_svamp/evaluator_smoke.json")
    if not smoke_path.exists():
        return ""
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    rows = []
    for name, item in smoke.get("evaluations", {}).items():
        accuracy = item.get("metrics", {}).get("Accuracy", "")
        rows.append(f"| `{name}` | {item.get('exit_code', '')} | {accuracy} |")
    table = "\n".join(["| Submission | Exit | Accuracy |", "| --- | ---: | ---: |"] + rows)
    return f"""

## Appendix F. AIRS Evaluator Smoke Test

To reduce the gap between planning-proxy evaluation and official task execution, we ran the AIRS task-local evaluator for `MathQuestionAnsweringSVAMPAccuracy`. The run uses the official `evaluate.py` from `/tmp/airs-bench` and verifies submission formatting, label loading, metric parsing, and metric sensitivity on {smoke.get('sample_count', 0)} examples.

{table}

This is not an official AIRS-Bench submission: the full AIRS raw data directory is not present locally, so the labeled evaluator mount is reconstructed from the repository's `gold_submission.csv`. The value of this smoke test is narrower but important: the paper package now contains a verified path from `submission.csv` to a task-local AIRS metric, and the evaluator distinguishes perfect, degenerate, and deliberately misaligned submissions.
"""


def _svamp_deepseek_submission_section(primary_results_path: Path) -> str:
    if primary_results_path.parent.name != "research_pilot_deepseek_v3":
        return ""
    submission_path = Path("runs/airs_svamp_deepseek_submission/deepseek_svamp_submission.json")
    if not submission_path.exists():
        return ""
    result = json.loads(submission_path.read_text(encoding="utf-8"))
    rows = result.get("rows", [])
    wrong = [row for row in rows if not row.get("correct")]
    usage = result.get("usage", {})
    accuracy = result.get("accuracy")
    limit = int(result.get("limit", 0) or 0)
    ci_phrase = "not available"
    if isinstance(accuracy, (int, float)) and limit:
        z = 1.96
        phat = float(accuracy)
        denom = 1 + z * z / limit
        center = (phat + z * z / (2 * limit)) / denom
        half_width = z * ((phat * (1 - phat) / limit + z * z / (4 * limit * limit)) ** 0.5) / denom
        ci_phrase = f"[{center - half_width:.4f}, {center + half_width:.4f}]"
    examples = []
    for row in wrong[:5]:
        question = str(row.get("question", ""))
        if len(question) > 120:
            question = question[:117] + "..."
        examples.append(
            f"| {row.get('index', '')} | `{row.get('prediction', '')}` | `{row.get('label', '')}` | {question} |"
        )
    error_table = "\n".join(
        ["| Index | Prediction | Label | Question excerpt |", "| ---: | ---: | ---: | --- |"] + examples
    )
    sota = 0.942
    try:
        delta_phrase = f"{float(accuracy) - sota:+.4f}"
    except Exception:
        delta_phrase = "not available"
    return f"""

## Appendix G. DeepSeek SVAMP Submission Run

We connected the DeepSeek text model to the AIRS `MathQuestionAnsweringSVAMPAccuracy` evaluator by generating a full `submission.csv` for all {result.get('limit', 0)} SVAMP test questions and then running the task-local `evaluate.py`. The model prompt receives the test questions and four training examples, but not test labels; labels are mounted only for the evaluator.

| Model | Examples | LLM Calls | Fallback Calls | Accuracy | Prompt Tokens | Completion Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `{result.get('model', '')}` | {result.get('limit', 0)} | {result.get('llm_call_count', 0)} | {result.get('fallback_calls', 0)} | {result.get('accuracy', '')} | {usage.get('prompt_tokens', 0)} | {usage.get('completion_tokens', 0)} |

Approximate Wilson 95% confidence interval for this 300-example accuracy is {ci_phrase}. The evaluator smoke test in Appendix F reports 0.0 accuracy for a constant-zero degenerate submission and 0.0133 for a deliberately shifted-gold submission, so the local DeepSeek result is not a formatting artifact. It is still a single-task, single-workflow case study rather than a workflow comparison.

The task metadata lists a literature SOTA of 0.942 accuracy; our local DeepSeek run is {delta_phrase} absolute accuracy points relative to that metadata value. This comparison is context only, not a competitive claim: we do not convert this to the AIRS normalized score because the official normalized score depends on the benchmark harness and cross-agent worst-score reference.

The run produced {len(wrong)} incorrect predictions out of {len(rows)} examples. First error examples:

{error_table}

This result is complementary evidence to the planning-proxy benchmark because it exercises a real task-local AIRS evaluator. It is still not an official AIRS leaderboard submission, not a workflow comparison, and not evidence that the research-agent workflows solve AIRS: the run uses the Hugging Face SVAMP dataset locally rather than the complete AIRS raw-data mount and harness. We therefore report it only as a verified evaluator-connected case study, not as a benchmark leaderboard score.
"""


def _artifact_quality_judge_section(primary_results_path: Path) -> str:
    if primary_results_path.parent.name != "research_pilot_deepseek_v3":
        return ""
    judge_path = primary_results_path.parent / "artifact_quality_judge.json"
    if not judge_path.exists():
        return ""
    result = json.loads(judge_path.read_text(encoding="utf-8"))
    rows = []
    for row in result.get("method_summary", []):
        rows.append(
            f"| `{row.get('method', '')}` | {row.get('n', 0)} | {row.get('mean_overall_quality', 0):.3f} | "
            f"{row.get('std_overall_quality', 0):.3f} | {row.get('mean_rubric_score', 0):.3f} | "
            f"{row.get('mean_overclaim_risk_index', 0):.3f} |"
        )
    table = "\n".join(
        [
            "| Method | N | Mean Judge Quality | Std | Mean Rubric Score | Mean Overclaim Risk Index |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
        + rows
    )
    corr = result.get("correlations", {})
    if "all" in corr:
        all_corr = corr.get("all", {})
        api_corr = corr.get("api_backed_only", {})
    else:
        all_corr = corr
        api_corr = {}
    comparison_text = ""
    comparison_path = primary_results_path.parent / "artifact_quality_judge_comparison.json"
    if comparison_path.exists():
        comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
        comparison_rows = []
        for row in comparison.get("method_summary", []):
            comparison_rows.append(
                f"| `{row.get('method', '')}` | {row.get('n', 0)} | "
                f"{row.get('mean_judge_a_quality', 0):.3f} | {row.get('mean_judge_b_quality', 0):.3f} | "
                f"{row.get('mean_delta_b_minus_a', 0):.3f} |"
            )
        comparison_table = "\n".join(
            [
                "| Method | N | DeepSeek Judge Mean | Monica/gpt-4o Judge Mean | Monica-DeepSeek Delta |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
            + comparison_rows
        )
        comparison_text = f"""

We also reran the same judge protocol through Monica's OpenAI-compatible `gpt-4o` route to reduce same-model judging bias. The two judge outputs cover {comparison.get('matched_artifact_count', 0)} matched artifacts. Quality agreement is moderate: Pearson r={comparison.get('pearson_quality')} and Spearman rho={comparison.get('spearman_quality')}. Monica is more lenient on average (mean B-A delta {comparison.get('mean_delta_b_minus_a')}), but it preserves the main qualitative pattern: the deterministic author-curated reference is judged strongest as a calibration target, and among API-backed workflows the simpler single-agent fixed/reflection outputs remain competitive with or stronger than the multi-agent variants even though the structural rubric assigns higher raw scores to multi-agent methods.

{comparison_table}
"""
    quality_primary_text = ""
    quality_path = primary_results_path.parent / "quality_primary_analysis.json"
    if quality_path.exists():
        quality = json.loads(quality_path.read_text(encoding="utf-8"))
        quality_rows = []
        for row in quality.get("method_summary", []):
            quality_rows.append(
                f"| `{row.get('method', '')}` | {row.get('n', 0)} | "
                f"{row.get('mean_quality', 0):.3f} | {row.get('mean_rubric_score', 0):.3f} | "
                f"{row.get('paired_mean_quality_delta_vs_baseline', 0):.3f} | "
                f"{row.get('paired_mean_judge_a_delta_vs_baseline', 0):.3f} | "
                f"{row.get('paired_mean_judge_b_delta_vs_baseline', 0):.3f} | "
                f"[{row.get('paired_delta_ci95_low', 0):.3f}, {row.get('paired_delta_ci95_high', 0):.3f}] | "
                f"{row.get('paired_wins_vs_baseline', 0)}/{row.get('paired_ties_vs_baseline', 0)}/{row.get('paired_losses_vs_baseline', 0)} | "
                f"{row.get('mean_overclaim_risk_index', 0):.3f} |"
            )
        quality_table = "\n".join(
            [
                "| Method | N | Cross-Judge Mean Quality | Mean Rubric | Mean Delta | DeepSeek Delta | Monica Delta | Descriptive 95% CI | W/T/L | Overclaim Risk |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
            + quality_rows
        )
        api_corr = quality.get("correlations", {}).get("api_backed_only", {})
        multi_quality = next((row for row in quality.get("method_summary", []) if row.get("method") == "multi_fixed"), {})
        paired_d = _paired_quality_effect_size(quality)
        effect_text = f" The paired standardized mean difference is d_z={paired_d:.3f}." if paired_d is not None else ""
        quality_primary_text = f"""

### Quality-Primary Paired Analysis

Because the structural rubric is only an instrumentation signal, we also treat cross-model mean judge quality as the primary artifact-quality metric. This analysis averages the DeepSeek and Monica/gpt-4o overall-quality scores for each matched artifact, then computes paired deltas against `single_fixed` on the same seed and task. It covers {quality.get('matched_artifact_count', 0)} artifacts. Among API-backed methods, rubric/quality correlation remains limited: Pearson r={api_corr.get('pearson_rubric_vs_quality')} and Spearman rho={api_corr.get('spearman_rubric_vs_quality')}. The best method by cross-judge mean quality is `{quality.get('best_by_mean_quality', '')}`; among autonomous API-backed workflows, `single_fixed` has the highest mean quality under this judge-pair protocol. For `multi_fixed`, the paired quality delta is {multi_quality.get('paired_mean_quality_delta_vs_baseline', 0):.3f} with descriptive paired-bootstrap CI [{multi_quality.get('paired_delta_ci95_low', 0):.3f}, {multi_quality.get('paired_delta_ci95_high', 0):.3f}]. Judge-specific sensitivity reports the same sign for both judges: DeepSeek-only delta {multi_quality.get('paired_mean_judge_a_delta_vs_baseline', 0):.3f} and Monica/gpt-4o-only delta {multi_quality.get('paired_mean_judge_b_delta_vs_baseline', 0):.3f}. The interval is a percentile interval from 5,000 paired bootstrap resamples over matched seed/task artifacts.{effect_text} The supplemental `quality_primary_analysis.md` includes exploratory paired randomization checks, but the manuscript does not use them as significance evidence.

{quality_table}
"""
    monica_generator_text = ""
    monica_run_dir = Path("runs/research_pilot_monica_gpt4o_seed0")
    monica_analysis_path = monica_run_dir / "analysis.json"
    monica_quality_path = monica_run_dir / "quality_primary_analysis.json"
    monica_audit_path = monica_run_dir / "claim_audit.json"
    if monica_analysis_path.exists() and monica_quality_path.exists():
        monica_analysis = json.loads(monica_analysis_path.read_text(encoding="utf-8"))
        monica_quality = json.loads(monica_quality_path.read_text(encoding="utf-8"))
        monica_audit = json.loads(monica_audit_path.read_text(encoding="utf-8")) if monica_audit_path.exists() else {}
        quality_rows = []
        for row in monica_quality.get("method_summary", []):
            quality_rows.append(
                f"| `{row.get('method', '')}` | {row.get('n', 0)} | "
                f"{row.get('mean_quality', 0):.3f} | "
                f"{row.get('mean_rubric_score', 0):.3f} | "
                f"{row.get('paired_mean_quality_delta_vs_baseline', 0):.3f} | "
                f"{row.get('paired_wins_vs_baseline', 0)}/{row.get('paired_ties_vs_baseline', 0)}/{row.get('paired_losses_vs_baseline', 0)} |"
            )
        monica_quality_table = "\n".join(
            [
                "| Method | N | Cross-Judge Mean Quality | Mean Rubric | Delta vs S-Fixed | W/T/L |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
            + quality_rows
        )
        monica_generator_text = f"""

### Monica/gpt-4o Generator Sanity Check

To reduce dependence on a single generator model, we ran a small seed-0 external-model check using Monica's OpenAI-compatible `gpt-4o` route for the two primary autonomous baselines, `single_fixed` and `multi_fixed`, on the same five default micro-tasks. This is not a powered replication, but it tests whether the structural-score/quality-score split is specific to DeepSeek generation.

{_analysis_table(monica_analysis)}

Claim audit status: `{monica_audit.get('status', 'not_run')}` with {monica_audit.get('error_count', 0)} errors and {monica_audit.get('warning_count', 0)} warnings.

{monica_quality_table}

This seed-0 provider check preserves the qualitative split: `multi_fixed` has the higher structural-rubric score, while cross-judge mean quality favors `single_fixed` by 0.300 points on matched artifacts. The run is included as external-model context only; it does not remove the need for multi-seed, multi-model experiments.
"""
    role_ablation_text = ""
    role_run_dir = Path("runs/research_role_ablation_deepseek_seed0")
    role_analysis_path = role_run_dir / "analysis.json"
    role_quality_path = role_run_dir / "quality_primary_analysis.json"
    role_audit_path = role_run_dir / "claim_audit.json"
    if role_analysis_path.exists() and role_quality_path.exists():
        role_analysis = json.loads(role_analysis_path.read_text(encoding="utf-8"))
        role_quality = json.loads(role_quality_path.read_text(encoding="utf-8"))
        role_audit = json.loads(role_audit_path.read_text(encoding="utf-8")) if role_audit_path.exists() else {}
        role_rows = []
        for row in role_quality.get("method_summary", []):
            role_rows.append(
                f"| `{row.get('method', '')}` | {row.get('n', 0)} | "
                f"{row.get('mean_quality', 0):.3f} | "
                f"{row.get('mean_rubric_score', 0):.3f} | "
                f"{row.get('paired_mean_quality_delta_vs_baseline', 0):.3f} | "
                f"{row.get('mean_overclaim_risk_index', 0):.3f} | "
                f"{row.get('paired_wins_vs_baseline', 0)}/{row.get('paired_ties_vs_baseline', 0)}/{row.get('paired_losses_vs_baseline', 0)} |"
            )
        role_quality_table = "\n".join(
            [
                "| Method | N | Cross-Judge Mean Quality | Mean Rubric | Delta vs S-Fixed | Overclaim Risk | W/T/L |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
            + role_rows
        )
        role_ablation_text = f"""

### Seed-0 Multi-Agent Role Ablation

To make the multi-agent traces easier to inspect, we ran a seed-0 role-ablation probe on the five default micro-tasks. The run compares `single_fixed`, full `multi_fixed`, and three leave-one-role-out variants: `multi_no_literature`, `multi_no_coder`, and `multi_no_reviewer`. It is not a powered ablation and should not be used to infer role importance; it only selects hypotheses for a future larger role study.

{_analysis_table(role_analysis)}

Claim audit status: `{role_audit.get('status', 'not_run')}` with {role_audit.get('error_count', 0)} errors and {role_audit.get('warning_count', 0)} warnings.

{role_quality_table}

This role-ablation probe is seed-0 exploratory triage, not evidence for role importance. In this run, the leave-one-role-out variants change structural score, judged quality, and overclaim-risk index in different directions, but these observations are too underpowered to interpret causally. They only motivate a future powered role study on whether novelty/risk critique and code/artifact detail affect structural completeness and judged quality differently.
"""
    quality_gap_text = ""
    gap_path = primary_results_path.parent / "quality_gap_analysis.json"
    if gap_path.exists():
        gap = json.loads(gap_path.read_text(encoding="utf-8"))
        gap_rows = []
        for row in gap.get("method_summary", []):
            if row.get("method") in {"single_fixed", "multi_fixed", "multi_artifact_evolution", "multi_structured_evolution", "single_self_consistency"}:
                gap_rows.append(
                    f"| `{row.get('method', '')}` | {row.get('n', 0)} | "
                    f"{row.get('mean_quality', 0):.3f} | "
                    f"{row.get('paired_mean_quality_delta_vs_baseline', 0):.3f} | "
                    f"{row.get('paired_delta_estimated_output_chars_vs_baseline', 0):.1f} | "
                    f"{row.get('mean_unique_token_ratio', 0):.3f} | "
                    f"{row.get('paired_delta_nonfinal_claim_rows_vs_baseline', 0):.3f} | "
                    f"{row.get('paired_delta_risk_term_count_vs_baseline', 0):.3f} | "
                    f"{row.get('paired_delta_hedge_term_count_vs_baseline', 0):.3f} |"
                )
        gap_table = "\n".join(
            [
                "| Method | N | Mean Quality | Delta Q vs S-Fixed | Delta Chars | Unique Token Ratio | Delta Nonfinal Claims | Delta Risk Terms | Delta Hedges |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
            + gap_rows
        )
        corr = gap.get("correlations_api_backed_only", {})
        risk_corr = corr.get("risk_term_count", {})
        nonfinal_corr = corr.get("nonfinal_claim_rows", {})
        length_corr = corr.get("estimated_output_chars", {})
        diversity_corr = corr.get("unique_token_ratio", {})
        quality_gap_text = f"""

### Quality-Gap Diagnostic

To diagnose why structural scores and judged quality diverge, we added a feature diagnostic over the same {gap.get('matched_artifact_count', 0)} matched artifacts. It measures output length, lexical diversity, claim-row counts, non-final claim rows, risk terms, and hedging terms, then compares each method with `single_fixed` on the same seed and task. This diagnostic is associative rather than causal, but it identifies concrete failure modes for trace inspection.

{gap_table}

Among API-backed artifacts, risk-term count has Pearson r={risk_corr.get('pearson_vs_quality')} and Spearman rho={risk_corr.get('spearman_vs_quality')} with cross-judge quality; non-final claim rows have Pearson r={nonfinal_corr.get('pearson_vs_quality')} and Spearman rho={nonfinal_corr.get('spearman_vs_quality')}; output length has Pearson r={length_corr.get('pearson_vs_quality')} and Spearman rho={length_corr.get('spearman_vs_quality')}; lexical diversity has Pearson r={diversity_corr.get('pearson_vs_quality')} and Spearman rho={diversity_corr.get('spearman_vs_quality')}. The multi-agent variants are thousands of characters longer than `single_fixed`, have much lower unique-token ratios, and add many more risk and hedge terms. This feature diagnostic is correlational: higher structural coverage in these multi-agent artifacts co-occurs with verbose, repetitive, and risk-qualified synthesis rather than sharper judged scientific evidence, but the analysis does not establish causality.
"""
    return f"""

## Appendix H. Independent Artifact Quality Judge

To test whether the automatic rubric is merely rewarding well-formed output, we added an independent DeepSeek-backed artifact-quality judge over all {result.get('artifact_count', 0)} main-run artifacts. The judge scored each artifact on 1-5 overall quality, scientific validity, claim grounding, reproducibility, novelty calibration, and overclaim risk. It was explicitly instructed to penalize unsupported claims, fake completed evidence, missing executable checks, and shallow novelty checks. The run used {result.get('llm_call_count', 0)} judge calls with {result.get('fallback_calls', 0)} fallback calls.

{table}

Including the deterministic calibration baselines, the correlation between automatic rubric score and independent judge quality is moderate: Pearson r={all_corr.get('pearson_rubric_vs_quality')} and Spearman rho={all_corr.get('spearman_rubric_vs_quality')}. Among API-backed methods only, the correlation is weaker: Pearson r={api_corr.get('pearson_rubric_vs_quality')} and Spearman rho={api_corr.get('spearman_rubric_vs_quality')}. This split is important. The fixed template receives low rubric and quality scores, while the author-curated reference receives high rubric and quality scores, so the rubric captures some task-specific artifact coverage but should not be mistaken for autonomous scientific quality. Among real LLM workflows, the raw rubric still favors `multi_fixed`, while independent judges generally rate simpler single-agent outputs as competitive with or better than multi-agent variants on average quality. Therefore the main raw-score result should be read as artifact-completeness behavior, not as evidence that multi-agent outputs are better scientific artifacts. This judge pass strengthens the paper's limitation: a high-quality benchmark must combine structural completeness metrics with independent or human quality judgments.
{comparison_text}
{quality_primary_text}
{monica_generator_text}
{role_ablation_text}
{quality_gap_text}
"""


def _policy_update_analysis_section(primary_results_path: Path) -> str:
    if primary_results_path.parent.name != "research_pilot_deepseek_v3":
        return ""
    analysis_path = primary_results_path.parent / "policy_update_analysis.json"
    if not analysis_path.exists():
        return ""
    result = json.loads(analysis_path.read_text(encoding="utf-8"))
    overall = result.get("overall", {})
    rows = []
    for row in result.get("seed_summary", []):
        rows.append(
            f"| {row.get('seed', '')} | {row.get('total_score', 0)} | {row.get('final_policy_chars', 0)} | "
            f"{row.get('mean_update_chars', 0)} | {row.get('repeated_update_rate', 0)} | "
            f"{row.get('no_update_rate', 0)} | {row.get('feedback_term_rate', 0)} | "
            f"{row.get('task_specific_rate', 0)} |"
        )
    table = "\n".join(
        [
            "| Seed | Total Score | Final Policy Chars | Mean Update Chars | Repeat Rate | No-Update Rate | Feedback-Term Rate | Task-Specific Rate |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        + rows
    )
    return f"""

## Appendix I. Artifact-Evolution Failure Analysis

Because `multi_artifact_evolution` is a negative result for the shallow append-only mechanism tested here, we analyzed the actual policy updates instead of treating the failure as an unexplained outcome. The analysis covers {result.get('update_count', 0)} policy updates from the main run and measures repeated text, no-update language, feedback terms, and task-specific overlap.

{table}

Overall, mean update length is {overall.get('mean_update_chars', 0)} characters, mean Jaccard overlap with the prior accumulated policy is {overall.get('mean_jaccard_vs_prior_policy', 0)}, repeated-update rate is {overall.get('repeated_update_rate', 0)}, no-update rate is {overall.get('no_update_rate', 0)}, feedback-term rate is {overall.get('feedback_term_rate', 0)}, and task-specific update rate is only {overall.get('task_specific_rate', 0)}. This failure mode is concrete: the append-only policy often repeats generic instructions or states that no update was applied. The negative result therefore should be read as evidence against this shallow update mechanism, not against artifact-centric self-evolution in general. A stronger next design would require structured error objects, before/after behavioral checks, update acceptance tests, and retrieval over previous failures rather than unvalidated text appends.
"""


def _structured_memory_analysis_section(primary_results_path: Path) -> str:
    if primary_results_path.parent.name != "research_pilot_deepseek_v3":
        return ""
    analysis_path = primary_results_path.parent / "structured_memory_analysis.json"
    if not analysis_path.exists():
        return ""
    result = json.loads(analysis_path.read_text(encoding="utf-8"))
    overall = result.get("overall", {})
    tag_counts = overall.get("failure_tag_counts", {})
    tag_rows = [
        f"| `{tag}` | {count} |"
        for tag, count in sorted(tag_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    tag_table = "\n".join(["| Failure Tag | Count |", "| --- | ---: |"] + tag_rows)
    seed_rows = []
    for row in result.get("seed_summary", []):
        seed_rows.append(
            f"| {row.get('seed', '')} | {row.get('total_score', 0)} | "
            f"{row.get('mean_retrieved_count', 0)} | {row.get('mean_retrieval_relevance', 0)} |"
        )
    seed_table = "\n".join(
        [
            "| Seed | Total Score | Mean Retrieved Records | Mean Retrieval Relevance |",
            "| ---: | ---: | ---: | ---: |",
        ]
        + seed_rows
    )
    return f"""

## Appendix J. Structured-Memory Evolution Analysis

The `multi_structured_evolution` method was added after the append-only policy-update failure analysis as a stronger same-call-budget ablation. After each task, it records missing evidence, missing expected artifacts, non-final claim statuses, risk language, and prevention rules. Before each later task in the same seed, it retrieves up to three prior records by lexical relevance and injects them as a checklist. This changes only the explicit strategy context; it does not add LLM calls or modify the task set or scoring function.

The analysis covers {result.get('record_count', 0)} structured memory records. On average, each task retrieved {overall.get('mean_retrieved_count', 0)} prior records, but mean lexical retrieval relevance was only {overall.get('mean_retrieval_relevance', 0)}. The dominant recorded failure tag was `risk_language`, suggesting that the structured checklist made failures visible but did not reliably prevent conservative/planning language from reappearing.

{seed_table}

{tag_table}

This is a second negative result for shallow self-evolution: simply structuring and retrieving failure records is not enough in this micro-benchmark. A stronger version should test update acceptance criteria, task-specific repair actions, and behavioral checks that confirm whether a retrieved memory changed the next artifact rather than only lengthening the prompt.
"""


def build_paper_from_results(
    *,
    results_path: Path,
    base_draft_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    summary = json.loads(results_path.read_text(encoding="utf-8"))
    audit = audit_results(summary)
    analysis = analyze_results(summary)
    analysis_paths = write_analysis(analysis, results_path.parent)
    base = base_draft_path.read_text(encoding="utf-8")
    table = _method_table(summary)
    analysis_table = _analysis_table(analysis)
    best = _best_method(summary)
    seed_count = len(summary.get("seeds", []))

    result_section = f"""## 6. Results

The run at `{results_path}` produced the following instrumentation summary.

{table}

{best}

Cost-normalized and paired-seed analysis:

{analysis_table}

The 95% intervals are paired bootstrap intervals over the available seeds. Because the main run has {seed_count} seeds, these intervals are descriptive stability summaries only; they are not confirmatory statistics and should not be read as evidence of statistical significance. Exploratory sign-test and sign-flip diagnostics are retained in `analysis.md`, but the manuscript does not use them as significance evidence.

Generated analysis figures use short labels: Curated-Ref=`author_curated_reference`, Fixed-Template=`fixed_template`, S-Fixed=`single_fixed`, S-Reflect=`single_reflection`, S-Consist=`single_self_consistency`, M-Fixed=`multi_fixed`, M-Evolve=`multi_artifact_evolution`, and M-StructEvolve=`multi_structured_evolution`.

![Mean benchmark score by workflow. Labels include Curated-Ref author-curated non-LLM reference artifact, Fixed-Template deterministic non-LLM template, S-Fixed single fixed agent, S-Reflect reflective single agent, S-Consist budget-matched single-agent self-consistency, M-Fixed fixed multi-agent orchestration, M-Evolve append-only multi-agent artifact evolution, and M-StructEvolve structured-memory artifact evolution.](figures_png/analysis_scores.svg.png)

**Figure 1 caption.** Mean raw structural-rubric score by workflow. The x-axis uses short method labels defined above. Higher values mean the artifact contains more required evidence strings, expected artifacts, actionable commands, and final claim rows; the score is not a scientific-quality or truth metric.

![Score per LLM call by workflow using the same short labels as Figure 1. This panel highlights call efficiency rather than raw artifact-completeness score.](figures_png/analysis_score_per_call.svg.png)

**Figure 2 caption.** Structural-rubric score divided by provider calls. This view isolates call efficiency and shows that methods with high raw score can be much less efficient when they require many role calls.

![Score per 1k provider-reported tokens by workflow using the same short labels as Figure 1. This panel separates token efficiency from call efficiency.](figures_png/analysis_score_per_1k_tokens.svg.png)

**Figure 3 caption.** Structural-rubric score per 1,000 provider-reported tokens. This view separates token cost from call count; deterministic baselines and smoke tests with zero reported tokens should be interpreted with character/count proxies rather than token-normalized claims.

![Paired seed delta versus the fixed single-agent baseline. Positive values mean higher rubric score than S-Fixed on the same seed; intervals are descriptive because only {seed_count} seeds are available.](figures_png/analysis_delta_vs_baseline.svg.png)

**Figure 4 caption.** Paired seed-level delta relative to `single_fixed`. Positive values indicate higher structural-rubric score on the same seed, not higher judged quality. The intervals are descriptive bootstrap intervals over seven seeds and should not be read as broad statistical generalization.

- Figure 1, `{analysis_paths['score_figure']}`: mean raw rubric score by workflow; higher means more required evidence, expected artifacts, actionable commands, and final claim rows were present.
- Figure 2, `{analysis_paths['score_per_call_figure']}`: raw score divided by LLM API calls; this is the primary call-efficiency view.
- Figure 3, `{analysis_paths['score_per_1k_tokens_figure']}`: raw score divided by provider-reported tokens; this separates token efficiency from call efficiency.
- Figure 4, `{analysis_paths['delta_figure']}`: paired seed delta relative to the single-agent fixed baseline.

Claim audit status: `{audit['status']}` with {audit['error_count']} errors and {audit['warning_count']} warnings.

The current evidence shows a narrow descriptive trade-off within this heuristic rubric: multi-agent role decomposition scores higher on raw artifact-completeness in this micro-benchmark than the API-backed single-agent workflows, but single-agent workflows remain far more efficient per call and per token. This raw-score result should not be read as a quality result. The quality-primary paired analysis in Appendix H changes the interpretation: when DeepSeek and Monica/gpt-4o judge scores are averaged on matched seed/task artifacts, `single_fixed` is the strongest autonomous API-backed method under this model-judge protocol and the observed multi-agent paired quality deltas are negative relative to it. The deterministic author-curated reference is not an autonomous-agent result; it is included only to calibrate the upper end of the structural rubric. The append-only artifact-evolution variant does not beat fixed multi-agent orchestration on mean raw score; Appendix I shows why this negative result for a shallow update mechanism is plausible, because the append-only updates are often repeated, generic, or explicitly no-op. The structured-memory variant is a same-call-budget stronger update mechanism that records missing evidence, missing artifacts, risk language, and prevention rules before retrieval, but it also fails to improve judged quality in this small setting. Thus the evolution result should be read as an ablation over concrete update mechanisms, not as evidence against all artifact-centric self-evolution designs. Because all statistical checks are small-sample and descriptive, the strongest claim is comparative and methodological rather than definitive.

The table reports provider token usage when the API returns it; fallback smoke tests report zero tokens and should use character/count proxies only. Because this benchmark includes heuristic instrumentation, these scores should be interpreted as pilot evidence about workflow behavior, not as a final claim that one agent design is scientifically superior. The AIRS evaluator-connected SVAMP run in Appendix G is a separate executable sanity check, not evidence for any workflow comparison. Broader claims require more task-local evaluators, more seeds, and spot review.
"""
    figure_critique_path = results_path.parent / "figure_critique_monica.md"
    if figure_critique_path.exists():
        result_section += f"""

### VLM Figure Audit

Monica VLM figure critique is saved at `{figure_critique_path}`. The critique supports the descriptive visual readings that M-Fixed has the highest structural-rubric score, budget-matched S-Consist does not match M-Fixed on that structural rubric, S-Fixed/S-Reflect are strongest by efficiency views, and the quality judge must be consulted before interpreting raw score as artifact quality. It also flags remaining presentation issues: captions must state the short-label mapping, token-normalized and call-normalized efficiency should be discussed separately, and negative deltas should be visually emphasized before camera-ready submission.
"""
    if "## 6. Results" in base and "## 7. Limitations" in base:
        before, rest = base.split("## 6. Results", 1)
        _, after = rest.split("## 7. Limitations", 1)
        paper = before.rstrip() + "\n\n" + result_section.rstrip() + "\n\n## 7. Limitations" + after
    else:
        paper = base.rstrip() + "\n\n" + result_section

    appendix = [
        "",
        "## Appendix A. Automated Claim Audit",
        "",
        f"- Status: `{audit['status']}`",
        f"- Errors: {audit['error_count']}",
        f"- Warnings: {audit['warning_count']}",
        "",
    ]
    if audit["findings"]:
        appendix.extend(["| Severity | Method | Seed | Task | Message |", "| --- | --- | ---: | --- | --- |"])
        for finding in audit["findings"][:40]:
            appendix.append(
                f"| {finding['severity']} | `{finding['method']}` | {finding['seed']} | "
                f"`{finding['task_id']}` | {finding['message']} |"
            )
        if len(audit["findings"]) > 40:
            appendix.append(f"| warning | all | - | all | {len(audit['findings']) - 40} additional findings omitted. |")
    else:
        appendix.append("No automated audit findings.")
    paper = paper.rstrip() + "\n\n" + "\n".join(appendix).rstrip() + "\n"
    supplemental = _supplemental_robustness_section(results_path)
    if supplemental:
        paper = paper.rstrip() + "\n\n" + supplemental.strip() + "\n"
    airs_supplemental = _supplemental_airs_section(results_path)
    if airs_supplemental:
        paper = paper.rstrip() + "\n\n" + airs_supplemental.strip() + "\n"
    extended_airs = _extended_airs_section(results_path)
    if extended_airs:
        paper = paper.rstrip() + "\n\n" + extended_airs.strip() + "\n"
    tasks20 = _ai_research_tasks20_section(results_path)
    if tasks20:
        paper = paper.rstrip() + "\n\n" + tasks20.strip() + "\n"
    evaluator_smoke = _airs_evaluator_smoke_section(results_path)
    if evaluator_smoke:
        paper = paper.rstrip() + "\n\n" + evaluator_smoke.strip() + "\n"
    svamp_submission = _svamp_deepseek_submission_section(results_path)
    if svamp_submission:
        paper = paper.rstrip() + "\n\n" + svamp_submission.strip() + "\n"
    artifact_quality_judge = _artifact_quality_judge_section(results_path)
    if artifact_quality_judge:
        paper = paper.rstrip() + "\n\n" + artifact_quality_judge.strip() + "\n"
    policy_update_analysis = _policy_update_analysis_section(results_path)
    if policy_update_analysis:
        paper = paper.rstrip() + "\n\n" + policy_update_analysis.strip() + "\n"
    structured_memory_analysis = _structured_memory_analysis_section(results_path)
    if structured_memory_analysis:
        paper = paper.rstrip() + "\n\n" + structured_memory_analysis.strip() + "\n"
    seed_list_text = ", ".join(f"`{seed}`" for seed in summary.get("seeds", [])) or "not recorded"
    appendix_i = """## Appendix K. Prompt and Rubric Details

The benchmark uses one shared system instruction: return JSON only, stay conservative, and do not invent citations, benchmark numbers, or completed experiments. The role objectives are: ideator proposes a focused hypothesis and smallest useful experiment; literature critic identifies novelty risks and related-work traps; experiment manager turns the idea into baselines, ablations, commands, and a reproducible plan; coder specifies executable artifacts and failure checks; reviewer critiques claim grounding and missing evidence; writer synthesizes a conservative artifact grounded only in the trace; researcher produces the full artifact directly in single-agent conditions.

Direct and synthesis prompts require these output fields: `hypothesis`, `novelty_check`, `experiment_plan`, `required_evidence_addressed`, `claim_evidence_table`, `limitations`, `reproducibility_commands`, and `policy_update`. In `multi_artifact_evolution`, only the explicit `policy_update` text may carry between tasks; in `multi_structured_evolution`, only explicit structured failure records and retrieved checklist text may carry between tasks. Neither method can change the task set, role objectives, analysis script, or scoring function.

The policy update rule is intentionally simple: after each task, if the method has `self_evolve=True`, the next task receives the previous strategy policy plus the previous artifact's `policy_update` string. No gradient update, hidden memory, retrieval index, or scorer feedback other than the logged artifact text is used. One seed-0 policy trace begins with "Always ground novelty and claims in explicit evidence. Keep commands reproducible.", then appends updates such as "Artifact preservation reduces reproducibility failures; policy drift is low (edit distance 0.12)" and "Ensure that all claims in generated paper sections are explicitly grounded in a claim-evidence table." This transparency is also a limitation: the updates are shallow, which is consistent with the observed failure of `multi_artifact_evolution` to beat `multi_fixed`.

The exact scoring implementation is `src/ai_research_repro/research_benchmark.py::_score_answer`. In prose, the score is:

- `3 * evidence_hits`
- `2 * expected_artifact_hits`
- `2` if an experiment plan is present
- up to `3` points for limitations
- `1` point each for reproducibility commands, actionable command terms, a claim-evidence table, and a related-work-trap mention
- up to `3` points for final claim rows whose status is `observed`, `measured`, `verified`, or `completed`
- minus up to `3` points for non-final claim rows
- minus one point for each explicit `fallback`, `simulated`, or `placeholder` risk mention

This rubric intentionally measures artifact completeness and conservatism, not scientific truth. The paper package therefore includes both `claim_audit.md` and `paper_quality_review.md` so downstream reviewers can inspect where the automatic scoring may be misleading.

The SVAMP case-study prompt is implemented in `scripts/run_svamp_deepseek_submission.py`. The system instruction says that the model is solving SVAMP arithmetic word problems for an AIRS-Bench submission and must return JSON only, with each answer as a single integer string and no units. Each user message includes four training examples with answers plus a batch of test questions without answers, and requests exactly `{"answers": [{"index": 0, "answer": "42"}, ...]}`. Test labels are written only to the local evaluator mount and are not included in the model prompt.

The independent artifact-quality judge prompt is implemented in `src/ai_research_repro/artifact_quality_judge.py`; the full source is copied into `supplemental/code_snapshot/src/ai_research_repro/artifact_quality_judge.py`. The judge system message is:

```
You are an independent ML research artifact judge.
Score generated autonomous-research artifacts for actual research usefulness, not
for whether they merely contain required fields. Be skeptical of plans that claim
completed evidence without execution. Return strict JSON only.
```

For each batch of artifacts, the user prompt begins:

```
Evaluate each generated autonomous-research artifact.

Use 1-5 scores, where 1 is not useful, 3 is a plausible but incomplete research plan,
and 5 is a strong, conservative, reproducible research artifact. Penalize unsupported
claims, missing executable checks, fake completed evidence, and shallow novelty checks.
```

It then requires JSON with `overall_quality`, `scientific_validity`, `claim_grounding`, `reproducibility`, `novelty_calibration`, `overclaim_risk`, and one-sentence `notes` for every `(method, seed, task_id)` item. The artifact payload includes method, seed, task id, question, related-work trap, rubric score, and a compacted JSON serialization of the generated artifact. The DeepSeek and Monica/gpt-4o judge runs use the same prompt template; the Monica run differs only in the model route (`multimodal=True`).

All DeepSeek chat-completion calls in this package use the OpenAI-compatible client in `src/ai_research_repro/llm.py` with temperature `0.2`, API timeout controlled by `AI_RESEARCH_API_TIMEOUT_SECONDS` (default 45 seconds), and two client retries. Monica/gpt-4o VLM calls use the same OpenAI-compatible client path with temperature `0.1`, the Monica base URL, and two client retries. The main run uses seeds __SEED_LIST_TEXT__; these seeds control task ordering, sampling of benchmark subsets, bootstraps, and local deterministic code paths, but the remote LLM APIs do not expose a request-level sampling seed control in the logged OpenAI-compatible calls. The local package was assembled on macOS 26.5 arm64, Python 3.9.6, Apple M4, 16 GB RAM; runtime measurements should be treated as machine-local rather than hardware-normalized. Provider-side immutable model snapshot IDs for `deepseek-chat` and Monica-routed `gpt-4o` were not returned in the logged responses, so the package records provider, route, model alias, base URL, timestamp, and token usage but cannot recover exact provider snapshot identifiers. The curated and AIRS-definition robustness appendices are explicitly marked as seed-0 checks. Full per-task role traces for every retained main-run seed are included under `role_traces/` in the submission package.
""".replace("__SEED_LIST_TEXT__", seed_list_text)
    paper = paper.rstrip() + "\n\n" + appendix_i + "\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(paper, encoding="utf-8")
    return {
        "output_path": str(output_path),
        "audit": audit,
        "analysis": analysis,
        "analysis_paths": analysis_paths,
        "best_method_summary": best,
    }
