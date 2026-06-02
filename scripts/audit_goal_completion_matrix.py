#!/usr/bin/env python3
"""Audit original user-goal completion for Co-Pilot AI Scientist v3.

This audit is deliberately stricter than artifact delivery checks. It maps the
full user objective to evidence in the current repository and separates
delivered artifacts from the still-unmet top-conference empirical bar.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _exists(path: Path, *, min_bytes: int = 1) -> bool:
    return path.exists() and path.stat().st_size >= min_bytes


def _contains(path: Path, terms: list[str]) -> bool:
    if not path.exists():
        return False
    text = _read(path)
    return all(term in text for term in terms)


def _remote_contains_branch(remote: str, branch: str) -> bool:
    result = subprocess.run(
        ["git", "ls-remote", "--heads", remote, branch],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return bool(result.stdout.strip())


def _requirement(
    key: str,
    requirement: str,
    status: str,
    evidence: list[str],
    gap: str,
    next_action: str,
) -> dict[str, Any]:
    return {
        "key": key,
        "requirement": requirement,
        "status": status,
        "evidence": evidence,
        "gap": gap,
        "next_action": next_action,
    }


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    branch = _git(["branch", "--show-current"])
    head = _git(["rev-parse", "HEAD"])
    remote_url = _git(["remote", "get-url", "origin"])

    manifest = _load_json(DOC_DIR / "repro_manifest.json")
    objective_delivery = _load_json(AUDIT_DIR / "objective_delivery_audit.json")
    package_consistency = _load_json(AUDIT_DIR / "package_consistency_audit.json")
    benchmark_coverage = _load_json(AUDIT_DIR / "benchmark_coverage_audit.json")
    deep_cases = _load_json(AUDIT_DIR / "deep_regeneration_cases_audit.json")
    human_packet = _load_json(AUDIT_DIR / "human_expert_blind_review_packet_audit.json")
    roadmap = _load_json(AUDIT_DIR / "top_conference_evidence_roadmap_audit.json")

    current_artifacts = manifest.get("current_artifacts", [])
    missing_manifest = [path for path in current_artifacts if not (ROOT / path).exists()]

    paper_en = DOC_DIR / "paper_en_focused.md"
    skill = ROOT / "skills" / "co-pilot-ai-scientist-v3" / "SKILL.md"
    deep_internal = DOC_DIR / "experiments" / "deep_case_internal_review_20260602_224500" / "summary.json"

    deep_summary = _load_json(deep_internal)
    remote_branch_pushed = _remote_contains_branch(remote_url, branch)
    benchmark_vector = benchmark_coverage.get("evidence_summary", {}).get("mlagentbench_vectorization", {})
    benchmark_cifar = benchmark_coverage.get("evidence_summary", {}).get("mlagentbench_cifar10_official", {})
    benchmark_cifar_multiseed = benchmark_coverage.get("evidence_summary", {}).get(
        "mlagentbench_cifar10_multiseed", {}
    )
    benchmark_ogbn_multiseed = benchmark_coverage.get("evidence_summary", {}).get(
        "mlagentbench_ogbn_arxiv_multiseed", {}
    )
    second_non_fml = benchmark_coverage.get("checks", {}).get("second_non_fml_priority_package_audited")
    second_non_fml_summary = benchmark_coverage.get("evidence_summary", {}).get(
        "open_data_multitask_evaluator_stress", {}
    )
    second_non_fml_audit_path = DOC_DIR / "audits" / "second_non_fml_priority_package_audit.md"
    non_fml_scored_complete = (
        benchmark_coverage.get("status") == "pass"
        and benchmark_vector.get("num_seeds") == 8
        and benchmark_vector.get("num_correct_best_programs") == 8
        and benchmark_vector.get("num_seeds_faster_than_starter") == 8
        and benchmark_vector.get("direct_rewrite_correct") is False
    )
    second_non_fml_official_like_complete = (
        second_non_fml is True
        and second_non_fml_summary.get("dataset_count") == 5
        and second_non_fml_summary.get("split_count") == 5
        and second_non_fml_summary.get("total_dataset_split_evaluations") == 25
    )
    official_cifar_complete = (
        benchmark_coverage.get("checks", {}).get("mlagentbench_cifar10_official_scored") is True
        and benchmark_cifar.get("candidate_score", 0) > benchmark_cifar.get("baseline_score", 1)
    )
    official_cifar_multiseed_complete = (
        benchmark_coverage.get("checks", {}).get("mlagentbench_cifar10_multiseed_scored") is True
        and benchmark_cifar_multiseed.get("seed_count", 0) >= 3
        and benchmark_cifar_multiseed.get("all_seeds_beat_baseline") is True
    )
    official_ogbn_multiseed_complete = (
        benchmark_coverage.get("checks", {}).get("mlagentbench_ogbn_arxiv_multiseed_scored") is True
        and benchmark_ogbn_multiseed.get("seed_count", 0) >= 3
        and min(benchmark_ogbn_multiseed.get("seed_scores", [0]))
        > benchmark_ogbn_multiseed.get("baseline_score", 1)
    )

    requirements = [
        _requirement(
            "paper_method_synthesis",
            "Write a paper that adapts AI Co-Scientist, AI Scientist-v2, AlphaEvolve/OpenEvolve into a distinct Co-Pilot AI Scientist v3 method.",
            "achieved",
            [
                _rel(paper_en),
                _rel(DOC_DIR / "architecture.md"),
            ],
            "The method synthesis is documented, but the paper remains a pilot/evidence-package draft rather than a final top-conference submission.",
            "Keep method naming centered on IGRE and remove any residual wording that sounds like a pasted combination of prior papers.",
        ),
        _requirement(
            "human_creative_gates",
            "Design human participation nodes at creative and key decision points.",
            "achieved",
            [
                _rel(skill),
                _rel(DOC_DIR / "experiment_protocol.md"),
                _rel(DOC_DIR / "audits" / "human_gate_attention_cost_audit.md"),
            ],
            "The gates are specified and logged, but large-scale live human-user traces are not available.",
            "Collect multi-researcher co-pilot traces only after ethics/privacy review and real deployment.",
        ),
        _requirement(
            "ai_scientist_v2_experiment_loop",
            "Use AI Scientist-v2-style hypothesis-to-experiment-to-paper production.",
            "partial",
            [
                _rel(DOC_DIR / "experiments" / "prospective_matched_fml_causality_20260602_000001" / "summary.json"),
                _rel(DOC_DIR / "experiments" / "online_full_gate_smoke_20260602_010521" / "trajectory.json"),
                _rel(DOC_DIR / "experiments" / "online_full_gate_smoke_20260602_010521" / "online_manuscript" / "co_pilot_online_full_gate_manuscript.md"),
                _rel(DOC_DIR / "experiments" / "online_full_gate_smoke_20260602_010521" / "online_manuscript" / "autonomous_online_comparator_manuscript.md"),
                _rel(DOC_DIR / "audits" / "end_to_end_paired_trajectory_audit.md"),
                _rel(DOC_DIR / "experiments" / "fml_matched_budget_comparison.md"),
            ],
            "There is now one same-run end-to-end smoke pair with co-pilot and autonomous manuscripts, but not enough full-scale matched tasks/seeds for a broad superiority claim.",
            "Repeat same-run end-to-end pairs across at least 3 tasks and independent manuscript reviews before claiming performance improvement.",
        ),
        _requirement(
            "alphaevolve_openevolve_search",
            "Use AlphaEvolve/OpenEvolve-style deep search on automatically evaluable subproblems.",
            "achieved",
            [
                _rel(DOC_DIR / "experiments" / "openevolve_5iter" / "README.md"),
                _rel(DOC_DIR / "experiments" / "mlagentbench_vectorization_openevolve_3iter_seed0" / "run" / "logs" / "openevolve_20260601_211855.log"),
                _rel(DOC_DIR / "experiments" / "maxcut_program_search_comparison.md"),
            ],
            "The evidence is micro-scale and demonstrates integration, not broad algorithm-discovery superiority.",
            "Extend OpenEvolve-style search to more machine-gradeable subproblems with matched baselines.",
        ),
        _requirement(
            "benchmark_selection",
            "Choose benchmarks based on the paper claim rather than limiting to FML-bench.",
            "achieved" if non_fml_scored_complete else "partial",
            [
                _rel(DOC_DIR / "benchmark_selection.md"),
                _rel(DOC_DIR / "benchmark_claim_matrix.md"),
                _rel(DOC_DIR / "audits" / "benchmark_coverage_audit.md"),
                _rel(second_non_fml_audit_path),
                _rel(DOC_DIR / "audits" / "mlagentbench_cifar10_official_audit.md"),
                _rel(DOC_DIR / "audits" / "mlagentbench_cifar10_multiseed_audit.md"),
                _rel(DOC_DIR / "audits" / "mlagentbench_ogbn_arxiv_multiseed_audit.md"),
            ],
            (
                "The package now includes a scored non-FML MLAgentBench vectorization comparison with 8/8 correct OpenEvolve-style best programs, "
                "all faster than the starter, and a failed direct-rewrite correctness baseline. It now also has a scored official MLAgentBench "
                f"CIFAR10/debug task with baseline {benchmark_cifar.get('baseline_score')} and co-pilot-selected score {benchmark_cifar.get('candidate_score')}, "
                f"delta {benchmark_cifar.get('delta')}; the three-seed robustness audit has mean {benchmark_cifar_multiseed.get('mean_score')}, "
                f"minimum {benchmark_cifar_multiseed.get('min_score')}, and sample std {benchmark_cifar_multiseed.get('sample_std')}. "
                f"OGBN-arxiv adds a second three-seed official-evaluator path with compatibility baseline {benchmark_ogbn_multiseed.get('baseline_score')}, "
                f"mean score {benchmark_ogbn_multiseed.get('mean_score')}, minimum {benchmark_ogbn_multiseed.get('min_score')}, "
                f"and sample std {benchmark_ogbn_multiseed.get('sample_std')}. "
                "The official-like open-data matched package adds 5 sklearn tasks, 5 split seeds, "
                "25 paired selections, and held-out trigger-policy transfer. This supports benchmark-portfolio coverage, but two narrow official-evaluator paths "
                "and one official-like package do not prove broad top-conference empirical sufficiency."
            )
            if non_fml_scored_complete
            and second_non_fml_official_like_complete
            and official_cifar_complete
            and official_cifar_multiseed_complete
            and official_ogbn_multiseed_complete
            else (
                "The package now includes a scored non-FML MLAgentBench vectorization comparison with 8/8 correct OpenEvolve-style best programs, "
                "all faster than the starter, and a failed direct-rewrite correctness baseline. It also has a scored official-like open-data "
                "matched package across 5 sklearn tasks, 5 split seeds, and 25 paired selections, with held-out trigger-policy transfer. "
                "This supports benchmark-portfolio coverage, but the official-like package is not broad official benchmark coverage."
            )
            if non_fml_scored_complete and second_non_fml_official_like_complete
            else (
                "The package now includes a scored non-FML MLAgentBench vectorization comparison with 8/8 correct OpenEvolve-style best programs, "
                "all faster than the starter, and a failed direct-rewrite correctness baseline. This supports benchmark-portfolio coverage, "
                "but it remains a narrow program-search subproblem rather than broad top-conference empirical sufficiency."
            )
            if non_fml_scored_complete
            else "The package considers FML-bench, MLAgentBench, OpenReview, OpenEvolve-style probes, and TFR, but a complete scored non-FML comparison is not yet proven.",
            "Add another scored official task or scale matched end-to-end co-pilot/autonomous trajectories; keep the open-data package labeled as official-like boundary evidence.",
        ),
        _requirement(
            "human_taste_and_insight_theory",
            "Emphasize that human participation can be harmful on average but may raise high-tail breakthrough probability through taste and insight.",
            "achieved",
            [
                _rel(DOC_DIR / "experiments" / "high_tail_power_analysis_20260602_233000" / "protocol.md"),
                _rel(DOC_DIR / "experiments" / "delayed_value_review_candidate_mining_20260603_001500" / "README.md"),
                _rel(DOC_DIR / "experiments" / "frontier_alignment_taxonomy_20260602_233000" / "README.md"),
                _rel(DOC_DIR / "experiments" / "frontier_vector_graph_20260602_234500" / "README.md"),
                _rel(DOC_DIR / "experiments" / "frontier_metric_disagreement_20260603_003000" / "README.md"),
                _rel(paper_en),
            ],
            "The high-tail theory is operationalized, but no positive delayed-value/high-tail case has been demonstrated yet.",
            "Prioritize delayed-value replay cases where historical review signals align with later frontier evidence.",
        ),
        _requirement(
            "deep_regeneration_cases",
            "Show concrete regenerated papers and data for several meaningful OpenReview cases.",
            "achieved",
            [
                _rel(DOC_DIR / "deep_regeneration_casebook.md"),
                _rel(DOC_DIR / "build" / "deep_regeneration_cases" / "summary.json"),
                _rel(deep_internal),
                _rel(DOC_DIR / "experiments" / "frontier_vector_graph_20260602_234500" / "summary.json"),
                _rel(DOC_DIR / "experiments" / "frontier_metric_disagreement_20260603_003000" / "summary.json"),
            ],
            f"Internal review is positive ({deep_summary.get('six_gate_hybrid_wins')}/3 six-gate wins, mean delta {deep_summary.get('mean_delta_six_gate_minus_raw')}), but it is deterministic internal review rather than human expert review.",
            "Use the prepared blind packet for future expert validation; keep current result labeled as internal evidence.",
        ),
        _requirement(
            "english_paper_pdfs",
            "Produce the English paper PDF.",
            "achieved",
            [
                _rel(DOC_DIR / "build" / "co_pilot_ai_scientist_v3_focused_en.pdf"),
            ],
            "The English PDF exists and is audited; final camera-ready paper still depends on stronger evidence.",
            "Rebuild PDFs after any substantive manuscript revision.",
        ),
        _requirement(
            "bilingual_usage",
            "Produce English and Chinese usage/runbook documentation.",
            "achieved",
            [
                _rel(DOC_DIR / "usage_en.md"),
                _rel(DOC_DIR / "usage_zh.md"),
                _rel(DOC_DIR / "RUNBOOK_EN.md"),
                _rel(DOC_DIR / "RUNBOOK_ZH.md"),
            ],
            "Usage is complete for the current package shape.",
            "Keep commands synchronized with new experiment scripts.",
        ),
        _requirement(
            "reusable_codex_skill",
            "Generate a reusable Codex skill for Co-Pilot AI Scientist v3.",
            "achieved",
            [
                _rel(skill),
                _rel(ROOT / "skills" / "co-pilot-ai-scientist-v3" / "templates" / "task_spec_template.md"),
                _rel(ROOT / "skills" / "co-pilot-ai-scientist-v3" / "templates" / "human_gate_log_template.json"),
                _rel(DOC_DIR / "experiments" / "external_clean_skill_reuse_smoke_20260603" / "summary.json"),
            ],
            "Skill is packaged, globally installed, smoke-audited, and copied into a clean external temporary environment on a fresh scientific-visualization topic; real external researcher or community reuse is not yet observed.",
            "Collect an independently run external example or community issue/PR before claiming community transfer.",
        ),
        _requirement(
            "github_push",
            "Push the project to the user's GitHub.",
            "achieved" if remote_branch_pushed else "partial",
            [remote_url, branch, head],
            "Branch is pushed if remote branch lookup succeeds; publication as a PR/release is separate.",
            "Create a release or PR only when the user wants a public submission package.",
        ),
        _requirement(
            "ssh_ubuntu_experiments",
            "Run experiments on the SSH-controlled Ubuntu computer where relevant.",
            "partial",
            [
                _rel(DOC_DIR / "experiments" / "online_full_gate_smoke_20260602_010521" / "README.md"),
                _rel(DOC_DIR / "experiments" / "prospective_matched_fml_causality_20260602_000001" / "co_pilot_trajectory.json"),
                _rel(DOC_DIR / "experiments" / "mlagentbench_house_price_setup_probe" / "README.md"),
            ],
            "Several Ubuntu traces exist, but some official benchmark attempts hit data/auth/setup blockers.",
            "Pre-cache datasets or choose official tasks with open data to complete non-FML scored comparisons.",
        ),
        _requirement(
            "model_selection_monica",
            "Use Monica-routed GPT/Gemini/Anthropic models when useful for paper quality.",
            "achieved",
            [
                _rel(DOC_DIR / "audits" / "focused_paper_quality_reviews" / "summary.json"),
                _rel(DOC_DIR / "audits" / "focused_paper_quality_reviews" / "gpt-4o-mini.md"),
                _rel(DOC_DIR / "audits" / "focused_paper_quality_reviews" / "gemini-2.5-flash.md"),
                _rel(DOC_DIR / "audits" / "focused_paper_quality_reviews" / "claude-3-7-sonnet-latest.md"),
            ],
            "Model reviews help audit quality but do not count as independent human expert review.",
            "Use model reviews for iteration; use human experts only as future supplementary validation.",
        ),
        _requirement(
            "author_record",
            "Record author as He Shi, NUS School of Computing undergraduate.",
            "achieved",
            [_rel(DOC_DIR / "paper_en_focused.md")],
            "Author metadata is recorded in the paper package.",
            "Keep author information synchronized in any final submission template.",
        ),
        _requirement(
            "top_conference_quality",
            "Reach top-conference paper quality.",
            "incomplete",
            [
                _rel(DOC_DIR / "audits" / "objective_delivery_audit.md"),
                _rel(DOC_DIR / "top_conference_evidence_roadmap.md"),
                _rel(DOC_DIR / "audits" / "top_conference_evidence_roadmap_audit.md"),
            ],
            "Current evidence is a strong pilot/reproducibility package, but top-conference empirical sufficiency remains unproven: no independent human expert ratings, limited matched tasks/seeds, and limited full end-to-end trajectories.",
            "Treat the next research phase as evidence collection: matched multi-task runs, complete non-FML benchmark, and independent review when feasible.",
        ),
    ]

    status_counts: dict[str, int] = {}
    for item in requirements:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1

    errors: list[str] = []
    warnings: list[str] = []
    if missing_manifest:
        errors.append(f"manifest lists {len(missing_manifest)} missing artifacts")
    if objective_delivery.get("status") != "pass_artifact_delivery_with_empirical_gaps":
        errors.append("objective delivery audit is not at the expected pass-with-gaps status")
    if package_consistency.get("status") != "pass":
        errors.append("package consistency audit is not passing")
    if benchmark_coverage.get("status") != "pass":
        errors.append("benchmark coverage audit is not passing")
    if deep_cases.get("status") != "pass":
        errors.append("deep regeneration audit is not passing")
    if human_packet.get("status") != "pass_prepared_no_human_ratings":
        errors.append("human expert packet must remain prepared without ratings for the current evidence boundary")
    if roadmap.get("status") != "pass":
        errors.append("top-conference roadmap audit is not passing")
    if not _exists(deep_internal):
        errors.append("deep internal review summary is missing")
    if not _contains(paper_en, ["We do not claim", "top-conference-level proof of co-pilot superiority"]):
        errors.append("English paper is missing conservative top-conference boundary wording")
    if not _contains(skill, ["Co-Pilot AI Scientist v3", "Insight-Gated Research Evolution", "Monica-routed"]):
        errors.append("Reusable skill is missing core method terms")
    if not remote_branch_pushed:
        warnings.append("current branch was not found on origin")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass_with_top_conference_gap" if not errors else "fail",
        "head": head,
        "branch": branch,
        "remote_url": remote_url,
        "remote_branch_pushed": remote_branch_pushed,
        "manifest_artifacts": len(current_artifacts),
        "missing_manifest_artifacts": len(missing_manifest),
        "requirement_count": len(requirements),
        "status_counts": status_counts,
        "requirements": requirements,
        "errors": errors,
        "warnings": warnings,
        "largest_current_gap": (
            "Top-conference empirical sufficiency remains incomplete: the package has "
            "auditable artifacts, internal/model reviews, and pilot experiments, but not "
            "independent expert ratings, large matched benchmark evidence, or broad "
            "multi-researcher online traces."
        ),
        "next_best_action": (
            "Run a compact but complete non-FML matched benchmark or a multi-case "
            "delayed-value replay before polishing the manuscript further."
        ),
        "claim_boundary": (
            "This audit maps objective completion. It does not mark the active goal "
            "complete because the original top-conference empirical target is not yet proven."
        ),
    }

    json_path = AUDIT_DIR / "goal_completion_matrix.json"
    md_path = AUDIT_DIR / "goal_completion_matrix.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Goal Completion Matrix",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- HEAD: `{head}`",
        f"- Branch: `{branch}`",
        f"- Remote branch pushed: `{remote_branch_pushed}`",
        f"- Manifest artifacts: `{len(current_artifacts)}`",
        f"- Missing manifest artifacts: `{len(missing_manifest)}`",
        f"- Requirement count: `{len(requirements)}`",
        f"- Status counts: `{json.dumps(status_counts, ensure_ascii=False)}`",
        "",
        "## Largest Current Gap",
        "",
        audit["largest_current_gap"],
        "",
        "## Requirement Matrix",
        "",
        "| Key | Status | Evidence | Gap | Next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in requirements:
        evidence = "<br>".join(f"`{entry}`" for entry in item["evidence"])
        lines.append(
            "| {key} | {status} | {evidence} | {gap} | {next_action} |".format(
                key=item["key"],
                status=item["status"],
                evidence=evidence,
                gap=item["gap"].replace("|", "/"),
                next_action=item["next_action"].replace("|", "/"),
            )
        )
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
