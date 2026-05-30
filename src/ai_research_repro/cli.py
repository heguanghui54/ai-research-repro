from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .artifact_quality_judge import judge_artifacts
from .benchmark_importers import import_airs_tasks
from .benchmark_tasks import save_task_template
from .claim_audit import audit_results_file
from .divergence_analysis import analyze_divergence
from .figure_critic import critique_figures
from .judge_comparison import compare_judges
from .llm import provider_status
from .orchestrator import PipelineConfig, run_pipeline
from .paper_builder import build_paper_from_results
from .paper_export import export_paper_package
from .paper_quality_review import review_paper_quality, save_paper_quality_review
from .policy_update_analysis import analyze_policy_updates
from .quality_gap_analysis import analyze_quality_gap
from .quality_primary_analysis import analyze_quality_primary
from .result_analysis import analyze_results_file
from .research_benchmark import (
    aggregate_result_scores,
    extend_research_benchmark_results,
    merge_research_benchmark_results,
    run_research_benchmark,
)
from .structured_memory_analysis import analyze_structured_memory
from .templates.nanogpt_lite import default_config, train_and_evaluate
from .reviewer import review_report
from .writer import save_report


def _cmd_run(args: argparse.Namespace) -> None:
    result = run_pipeline(
        PipelineConfig(
            workspace=Path(args.workspace),
            num_ideas=args.ideas,
            gpt_model=args.model,
            run_baseline=not args.no_baseline,
        )
    )
    print(json.dumps(
        {
            "workspace": result["workspace"],
            "summary_metrics": result["summary_metrics"],
            "report_path": result["report_path"],
            "review": result["review"],
        },
        indent=2,
    ))


def _cmd_baseline(args: argparse.Namespace) -> None:
    out_dir = Path(args.workspace) / "baseline"
    result = train_and_evaluate(default_config(), out_dir=out_dir)
    print(json.dumps(result["metrics"], indent=2))


def _cmd_review(args: argparse.Namespace) -> None:
    report = Path(args.report).read_text(encoding="utf-8")
    review = review_report(report, metrics={}, model=args.model)
    print(json.dumps(review, indent=2))


def _cmd_research_benchmark(args: argparse.Namespace) -> None:
    methods = args.methods.split(",") if args.methods else None
    seeds = [int(seed.strip()) for seed in args.seeds.split(",") if seed.strip()]
    result = run_research_benchmark(
        workspace=Path(args.workspace),
        methods=methods,
        model=args.model,
        seeds=seeds or None,
        task_file=Path(args.task_file) if args.task_file else None,
        command=" ".join(sys.argv),
        role_mode=args.role_mode,
    )
    print(json.dumps(
        {
            "workspace": args.workspace,
            "model": result["model"],
            "role_mode": result["role_mode"],
            "task_source": result["task_source"],
            "scores": aggregate_result_scores(result),
            "results_path": str(Path(args.workspace) / "research_benchmark_results.json"),
            "summary_path": str(Path(args.workspace) / "research_benchmark_summary.md"),
            "manifest_path": str(Path(args.workspace) / "repro_manifest.json"),
            "role_trace_index": str(Path(args.workspace) / "role_trace_index.md"),
        },
        indent=2,
    ))


def _cmd_merge_results(args: argparse.Namespace) -> None:
    result = merge_research_benchmark_results(
        base_results=Path(args.base_results),
        add_results=[Path(item) for item in args.add_results],
        workspace=Path(args.workspace),
        command=" ".join(sys.argv),
    )
    print(json.dumps(
        {
            "workspace": args.workspace,
            "model": result["model"],
            "role_mode": result["role_mode"],
            "task_source": result["task_source"],
            "scores": aggregate_result_scores(result),
            "results_path": str(Path(args.workspace) / "research_benchmark_results.json"),
            "summary_path": str(Path(args.workspace) / "research_benchmark_summary.md"),
            "manifest_path": str(Path(args.workspace) / "repro_manifest.json"),
            "role_trace_index": str(Path(args.workspace) / "role_trace_index.md"),
        },
        indent=2,
    ))


def _cmd_extend_results(args: argparse.Namespace) -> None:
    result = extend_research_benchmark_results(
        base_results=Path(args.base_results),
        add_results=[Path(item) for item in args.add_results],
        workspace=Path(args.workspace),
        command=" ".join(sys.argv),
    )
    print(json.dumps(
        {
            "workspace": args.workspace,
            "model": result["model"],
            "role_mode": result["role_mode"],
            "task_source": result["task_source"],
            "seeds": result["seeds"],
            "scores": aggregate_result_scores(result),
            "results_path": str(Path(args.workspace) / "research_benchmark_results.json"),
            "summary_path": str(Path(args.workspace) / "research_benchmark_summary.md"),
            "manifest_path": str(Path(args.workspace) / "repro_manifest.json"),
            "role_trace_index": str(Path(args.workspace) / "role_trace_index.md"),
        },
        indent=2,
    ))


def _cmd_write_task_template(args: argparse.Namespace) -> None:
    save_task_template(Path(args.output))
    print(json.dumps({"output": args.output}, indent=2))


def _cmd_import_airs_tasks(args: argparse.Namespace) -> None:
    result = import_airs_tasks(
        repo_dir=Path(args.repo_dir),
        output_path=Path(args.output),
        split=args.split,
        limit=args.limit,
        max_per_category=args.max_per_category,
    )
    print(json.dumps(result, indent=2))


def _cmd_critique_figures(args: argparse.Namespace) -> None:
    critique = critique_figures(
        image_paths=[Path(item) for item in args.images],
        claim_context=args.claim_context,
        model=args.model or None,
    )
    output_path = Path(args.output) if args.output else None
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(critique, encoding="utf-8")
    print(critique)


def _cmd_audit_claims(args: argparse.Namespace) -> None:
    audit = audit_results_file(Path(args.results))
    print(json.dumps(
        {
            "status": audit["status"],
            "error_count": audit["error_count"],
            "warning_count": audit["warning_count"],
            "paths": audit["paths"],
        },
        indent=2,
    ))


def _cmd_analyze_results(args: argparse.Namespace) -> None:
    analysis = analyze_results_file(Path(args.results))
    print(json.dumps(
        {
            "best_by_score": analysis["best_by_score"],
            "best_by_score_per_call": analysis["best_by_score_per_call"],
            "paths": analysis["paths"],
        },
        indent=2,
    ))


def _cmd_write_paper_from_results(args: argparse.Namespace) -> None:
    result = build_paper_from_results(
        results_path=Path(args.results),
        base_draft_path=Path(args.base_draft),
        output_path=Path(args.output),
    )
    print(json.dumps(result, indent=2))


def _cmd_export_paper_package(args: argparse.Namespace) -> None:
    result = export_paper_package(
        paper_markdown=Path(args.paper),
        output_dir=Path(args.output_dir),
        results_dir=Path(args.results_dir) if args.results_dir else None,
        references_path=Path(args.references) if args.references else None,
    )
    print(json.dumps(result, indent=2))


def _cmd_review_paper_quality(args: argparse.Namespace) -> None:
    review = review_paper_quality(
        paper_path=Path(args.paper),
        results_dir=Path(args.results_dir),
        model=args.model,
    )
    paths = save_paper_quality_review(review, Path(args.output_dir))
    print(json.dumps({"paths": paths, "review": review}, indent=2))


def _cmd_judge_artifacts(args: argparse.Namespace) -> None:
    result = judge_artifacts(
        results_path=Path(args.results),
        output_dir=Path(args.output_dir),
        model=args.model,
        batch_size=args.batch_size,
        multimodal=args.multimodal,
        output_prefix=args.output_prefix,
    )
    print(json.dumps(
        {
            "paths": result["paths"],
            "artifact_count": result["artifact_count"],
            "llm_call_count": result["llm_call_count"],
            "fallback_calls": result["fallback_calls"],
            "correlations": result["correlations"],
            "method_summary": result["method_summary"],
        },
        indent=2,
    ))


def _cmd_analyze_policy_updates(args: argparse.Namespace) -> None:
    result = analyze_policy_updates(
        results_path=Path(args.results),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(
        {
            "paths": result["paths"],
            "method": result["method"],
            "update_count": result["update_count"],
            "overall": result["overall"],
            "seed_summary": result["seed_summary"],
        },
        indent=2,
    ))


def _cmd_analyze_structured_memory(args: argparse.Namespace) -> None:
    result = analyze_structured_memory(
        results_path=Path(args.results),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(
        {
            "paths": result["paths"],
            "method": result["method"],
            "record_count": result["record_count"],
            "overall": result["overall"],
            "seed_summary": result["seed_summary"],
        },
        indent=2,
    ))


def _cmd_compare_judges(args: argparse.Namespace) -> None:
    result = compare_judges(
        judge_a_path=Path(args.judge_a),
        judge_b_path=Path(args.judge_b),
        output_dir=Path(args.output_dir),
        output_prefix=args.output_prefix,
    )
    print(json.dumps(
        {
            "paths": result["paths"],
            "matched_artifact_count": result["matched_artifact_count"],
            "pearson_quality": result["pearson_quality"],
            "spearman_quality": result["spearman_quality"],
            "mean_delta_b_minus_a": result["mean_delta_b_minus_a"],
            "method_summary": result["method_summary"],
        },
        indent=2,
    ))


def _cmd_analyze_quality_primary(args: argparse.Namespace) -> None:
    result = analyze_quality_primary(
        judge_a_path=Path(args.judge_a),
        judge_b_path=Path(args.judge_b),
        output_dir=Path(args.output_dir),
        output_prefix=args.output_prefix,
        baseline_method=args.baseline_method,
    )
    print(json.dumps(
        {
            "paths": result["paths"],
            "matched_artifact_count": result["matched_artifact_count"],
            "best_by_mean_quality": result["best_by_mean_quality"],
            "correlations": result["correlations"],
            "method_summary": result["method_summary"],
        },
        indent=2,
    ))


def _cmd_analyze_quality_gap(args: argparse.Namespace) -> None:
    result = analyze_quality_gap(
        results_path=Path(args.results),
        judge_a_path=Path(args.judge_a),
        judge_b_path=Path(args.judge_b),
        output_dir=Path(args.output_dir),
        output_prefix=args.output_prefix,
        baseline_method=args.baseline_method,
    )
    print(json.dumps(
        {
            "paths": result["paths"],
            "matched_artifact_count": result["matched_artifact_count"],
            "baseline_method": result["baseline_method"],
            "correlations_api_backed_only": result["correlations_api_backed_only"],
            "method_summary": result["method_summary"],
        },
        indent=2,
    ))


def _cmd_analyze_divergence(args: argparse.Namespace) -> None:
    result = analyze_divergence(
        results_path=Path(args.results),
        judge_a_path=Path(args.judge_a),
        judge_b_path=Path(args.judge_b),
        output_dir=Path(args.output_dir),
        output_prefix=args.output_prefix,
        baseline_method=args.baseline_method,
    )
    print(json.dumps(
        {
            "paths": result["paths"],
            "paired_record_count": result["paired_record_count"],
            "api_backed_paired_record_count": result["api_backed_paired_record_count"],
            "api_backed_delta_correlations": result["api_backed_delta_correlations"],
            "method_summary": result["method_summary"],
        },
        indent=2,
    ))


def _cmd_doctor(args: argparse.Namespace) -> None:
    status = provider_status()
    print(json.dumps(status, indent=2))
    if args.strict and not status["text_has_key"]:
        raise SystemExit(2)
    if args.require_vlm and not status["vlm_has_key"]:
        raise SystemExit(3)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-research-repro")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run the full idea-to-paper pipeline.")
    run.add_argument("--workspace", required=True)
    run.add_argument("--ideas", type=int, default=3)
    run.add_argument("--model", default="gpt-4o-mini")
    run.add_argument("--no-baseline", action="store_true")
    run.set_defaults(func=_cmd_run)

    baseline = sub.add_parser("baseline", help="Run the NanoGPT-lite baseline only.")
    baseline.add_argument("--workspace", required=True)
    baseline.set_defaults(func=_cmd_baseline)

    review = sub.add_parser("review", help="Review a report markdown file.")
    review.add_argument("--report", required=True)
    review.add_argument("--model", default="gpt-4o-mini")
    review.set_defaults(func=_cmd_review)

    research_benchmark = sub.add_parser("research-benchmark", help="Run the automated-research micro-benchmark.")
    research_benchmark.add_argument("--workspace", required=True)
    research_benchmark.add_argument("--model", default="deepseek-chat")
    research_benchmark.add_argument("--methods", default="")
    research_benchmark.add_argument("--seeds", default="0")
    research_benchmark.add_argument("--task-file", default="")
    research_benchmark.add_argument("--role-mode", choices=["metadata", "orchestrated"], default="metadata")
    research_benchmark.set_defaults(func=_cmd_research_benchmark)

    merge_results = sub.add_parser("merge-results", help="Merge compatible benchmark result files into a new workspace.")
    merge_results.add_argument("--workspace", required=True)
    merge_results.add_argument("--base-results", required=True)
    merge_results.add_argument("--add-results", nargs="+", required=True)
    merge_results.set_defaults(func=_cmd_merge_results)

    extend_results = sub.add_parser("extend-results", help="Append compatible new seeds/methods into an existing benchmark result set.")
    extend_results.add_argument("--workspace", required=True)
    extend_results.add_argument("--base-results", required=True)
    extend_results.add_argument("--add-results", nargs="+", required=True)
    extend_results.set_defaults(func=_cmd_extend_results)

    task_template = sub.add_parser("write-task-template", help="Write an external benchmark task JSON template.")
    task_template.add_argument("--output", default="research_artifacts/external_tasks_template.json")
    task_template.set_defaults(func=_cmd_write_task_template)

    import_airs = sub.add_parser("import-airs-tasks", help="Convert a local AIRS-Bench clone into this benchmark task schema.")
    import_airs.add_argument("--repo-dir", required=True, help="Path to a facebookresearch/airs-bench clone.")
    import_airs.add_argument("--output", default="research_artifacts/airs_official_tasks.json")
    import_airs.add_argument("--split", choices=["rad", "mlgym"], default="rad")
    import_airs.add_argument("--limit", type=int, default=0, help="Optional number of tasks to import after sorted task order.")
    import_airs.add_argument("--max-per-category", type=int, default=0, help="Optional cap per AIRS category before the global limit.")
    import_airs.set_defaults(func=_cmd_import_airs_tasks)

    critique_figures = sub.add_parser("critique-figures", help="Review generated figures with Monica/OpenAI-compatible VLM.")
    critique_figures.add_argument("images", nargs="+")
    critique_figures.add_argument("--claim-context", required=True)
    critique_figures.add_argument("--model", default="")
    critique_figures.add_argument("--output", default="")
    critique_figures.set_defaults(func=_cmd_critique_figures)

    audit_claims = sub.add_parser("audit-claims", help="Audit benchmark artifacts before using them as paper evidence.")
    audit_claims.add_argument("--results", required=True)
    audit_claims.set_defaults(func=_cmd_audit_claims)

    analyze = sub.add_parser("analyze-results", help="Compute statistical and cost-normalized result summaries.")
    analyze.add_argument("--results", required=True)
    analyze.set_defaults(func=_cmd_analyze_results)

    write_paper = sub.add_parser("write-paper-from-results", help="Insert benchmark results and audit findings into the paper draft.")
    write_paper.add_argument("--results", required=True)
    write_paper.add_argument("--base-draft", default="research_artifacts/paper_draft.md")
    write_paper.add_argument("--output", default="research_artifacts/paper_with_results.md")
    write_paper.set_defaults(func=_cmd_write_paper_from_results)

    export_paper = sub.add_parser("export-paper-package", help="Export paper markdown, LaTeX, figures, and evidence artifacts.")
    export_paper.add_argument("--paper", required=True)
    export_paper.add_argument("--output-dir", required=True)
    export_paper.add_argument("--results-dir", default="")
    export_paper.add_argument("--references", default="research_artifacts/references.bib")
    export_paper.set_defaults(func=_cmd_export_paper_package)

    review_quality = sub.add_parser("review-paper-quality", help="Run a structured final quality review of a paper and evidence package.")
    review_quality.add_argument("--paper", required=True)
    review_quality.add_argument("--results-dir", required=True)
    review_quality.add_argument("--output-dir", required=True)
    review_quality.add_argument("--model", default="deepseek-chat")
    review_quality.set_defaults(func=_cmd_review_paper_quality)

    judge_artifacts_cmd = sub.add_parser("judge-artifacts", help="Independently judge generated research artifacts for quality beyond rubric completeness.")
    judge_artifacts_cmd.add_argument("--results", required=True)
    judge_artifacts_cmd.add_argument("--output-dir", required=True)
    judge_artifacts_cmd.add_argument("--model", default="deepseek-chat")
    judge_artifacts_cmd.add_argument("--batch-size", type=int, default=5)
    judge_artifacts_cmd.add_argument("--multimodal", action="store_true", help="Route judge calls through the Monica/OpenAI-compatible multimodal provider.")
    judge_artifacts_cmd.add_argument("--output-prefix", default="artifact_quality_judge")
    judge_artifacts_cmd.set_defaults(func=_cmd_judge_artifacts)

    policy_updates = sub.add_parser("analyze-policy-updates", help="Analyze why artifact-evolution policy updates did or did not improve.")
    policy_updates.add_argument("--results", required=True)
    policy_updates.add_argument("--output-dir", required=True)
    policy_updates.set_defaults(func=_cmd_analyze_policy_updates)

    structured_memory = sub.add_parser("analyze-structured-memory", help="Analyze retrieved failure-memory records for structured artifact evolution.")
    structured_memory.add_argument("--results", required=True)
    structured_memory.add_argument("--output-dir", required=True)
    structured_memory.set_defaults(func=_cmd_analyze_structured_memory)

    compare_judge_cmd = sub.add_parser("compare-judges", help="Compare two artifact-quality judge outputs on matched artifacts.")
    compare_judge_cmd.add_argument("--judge-a", required=True)
    compare_judge_cmd.add_argument("--judge-b", required=True)
    compare_judge_cmd.add_argument("--output-dir", required=True)
    compare_judge_cmd.add_argument("--output-prefix", default="artifact_quality_judge_comparison")
    compare_judge_cmd.set_defaults(func=_cmd_compare_judges)

    quality_primary = sub.add_parser("analyze-quality-primary", help="Combine two judge outputs into a quality-primary paired method analysis.")
    quality_primary.add_argument("--judge-a", required=True)
    quality_primary.add_argument("--judge-b", required=True)
    quality_primary.add_argument("--output-dir", required=True)
    quality_primary.add_argument("--output-prefix", default="quality_primary_analysis")
    quality_primary.add_argument("--baseline-method", default="single_fixed")
    quality_primary.set_defaults(func=_cmd_analyze_quality_primary)

    quality_gap = sub.add_parser("analyze-quality-gap", help="Diagnose feature correlates of cross-judge artifact-quality gaps.")
    quality_gap.add_argument("--results", required=True)
    quality_gap.add_argument("--judge-a", required=True)
    quality_gap.add_argument("--judge-b", required=True)
    quality_gap.add_argument("--output-dir", required=True)
    quality_gap.add_argument("--output-prefix", default="quality_gap_analysis")
    quality_gap.add_argument("--baseline-method", default="single_fixed")
    quality_gap.set_defaults(func=_cmd_analyze_quality_gap)

    divergence = sub.add_parser("analyze-divergence", help="Test paired structural-score and judged-quality divergence with feature controls.")
    divergence.add_argument("--results", required=True)
    divergence.add_argument("--judge-a", required=True)
    divergence.add_argument("--judge-b", required=True)
    divergence.add_argument("--output-dir", required=True)
    divergence.add_argument("--output-prefix", default="divergence_analysis")
    divergence.add_argument("--baseline-method", default="single_fixed")
    divergence.set_defaults(func=_cmd_analyze_divergence)

    doctor = sub.add_parser("doctor", help="Show configured text and VLM providers without printing secrets.")
    doctor.add_argument("--strict", action="store_true", help="Exit non-zero when the text provider key is missing.")
    doctor.add_argument("--require-vlm", action="store_true", help="Exit non-zero when the VLM provider key is missing.")
    doctor.set_defaults(func=_cmd_doctor)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
