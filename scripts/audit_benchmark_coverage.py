#!/usr/bin/env python3
"""Audit benchmark coverage and claim boundaries for Co-Pilot AI Scientist v3.

This audit checks whether the package uses a benchmark portfolio rather than a
single convenient benchmark. It treats successful scored probes, boundary
conditions, and blocked official setups as different kinds of evidence.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
AUDIT_DIR = DOC_DIR / "audits"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _contains_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def _mentions_fml_benchmark(entry: dict[str, Any]) -> bool:
    joined = " ".join(
        [
            entry.get("claim_family", ""),
            entry.get("benchmark_or_probe", ""),
            entry.get("current_evidence", ""),
        ]
    )
    return re.search(r"(?<![Nn]on-)FML(?:-bench|_|\b)", joined) is not None


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    matrix_path = DOC_DIR / "benchmark_claim_matrix.json"
    selection_path = DOC_DIR / "benchmark_selection.md"
    vector_path = EXP_DIR / "mlagentbench_vectorization_multiseed_summary.json"
    maxcut_path = EXP_DIR / "maxcut_program_search_comparison.json"
    knapsack_openevolve_path = EXP_DIR / "knapsack_openevolve_5iter" / "summary.json"
    knapsack_direct_path = EXP_DIR / "knapsack_direct_baseline" / "summary.json"
    sklearn_path = EXP_DIR / "sklearn_diabetes_tabular_summary.json"
    cifar_path = EXP_DIR / "mlagentbench_cifar10_debug_setup_probe" / "summary.json"
    cifar_refresh_path = EXP_DIR / "mlagentbench_cifar10_debug_refresh_probe_20260602" / "summary.json"
    cifar_official_path = AUDIT_DIR / "mlagentbench_cifar10_official_audit.json"
    cifar_multiseed_path = AUDIT_DIR / "mlagentbench_cifar10_multiseed_audit.json"
    imdb_path = EXP_DIR / "mlagentbench_imdb_setup_probe" / "summary.json"
    clrs_path = EXP_DIR / "mlagentbench_clrs_baseline_smoke_20260602" / "summary.json"
    clrs_reduced_path = EXP_DIR / "mlagentbench_clrs_reduced_smoke_20260602" / "summary.json"
    house_price_path = EXP_DIR / "mlagentbench_house_price_setup_probe" / "summary.json"
    ogbn_path = EXP_DIR / "mlagentbench_ogbn_arxiv_setup_probe_20260603" / "summary.json"
    science_path = EXP_DIR / "scienceagentbench_metadata_setup_probe" / "summary.json"
    open_data_path = (
        EXP_DIR
        / "prospective_matched_open_data_multitask_20260603"
        / "remote_metrics.json"
    )
    trigger_policy_path = (
        EXP_DIR
        / "prospective_matched_open_data_multitask_20260603"
        / "evaluator_stress_trigger_policy_summary.json"
    )
    open_data_holdout_path = (
        EXP_DIR
        / "prospective_matched_open_data_multitask_holdout_20260603"
        / "remote_metrics.json"
    )
    trigger_policy_holdout_path = (
        EXP_DIR
        / "prospective_matched_open_data_multitask_holdout_20260603"
        / "evaluator_stress_trigger_policy_summary.json"
    )
    trigger_policy_transfer_path = (
        EXP_DIR
        / "evaluator_trigger_policy_transfer_20260603"
        / "summary.json"
    )
    second_non_fml_priority_path = AUDIT_DIR / "second_non_fml_priority_package_audit.json"

    matrix = _load_json(matrix_path)
    selection_text = _read(selection_path)
    matrix_text = json.dumps(matrix, ensure_ascii=False)
    entries = matrix.get("entries", [])

    vector = _load_json(vector_path)
    maxcut = _load_json(maxcut_path)
    knapsack_openevolve = _load_json(knapsack_openevolve_path)
    knapsack_direct = _load_json(knapsack_direct_path)
    sklearn = _load_json(sklearn_path)
    cifar = _load_json(cifar_path)
    cifar_refresh = _load_json(cifar_refresh_path)
    cifar_official = _load_json(cifar_official_path)
    cifar_multiseed = _load_json(cifar_multiseed_path)
    imdb = _load_json(imdb_path)
    clrs = _load_json(clrs_path)
    clrs_reduced = _load_json(clrs_reduced_path)
    house_price = _load_json(house_price_path)
    ogbn = _load_json(ogbn_path)
    science = _load_json(science_path)
    open_data = _load_json(open_data_path)
    trigger_policy = _load_json(trigger_policy_path)
    open_data_holdout = _load_json(open_data_holdout_path)
    trigger_policy_holdout = _load_json(trigger_policy_holdout_path)
    trigger_policy_transfer = _load_json(trigger_policy_transfer_path)
    second_non_fml_priority = _load_json(second_non_fml_priority_path)
    open_data_total = open_data.get("total_dataset_split_evaluations")
    open_data_expected_total = (
        open_data.get("dataset_count", 0) * open_data.get("split_count", 0)
        if isinstance(open_data.get("dataset_count"), int)
        and isinstance(open_data.get("split_count"), int)
        else None
    )
    open_data_outcome_total = (
        open_data.get("co_pilot_dataset_wins", 0)
        + open_data.get("autonomous_dataset_wins", 0)
        + open_data.get("dataset_ties", 0)
    )

    vector_agg = vector.get("aggregate", {})
    starter_runtime = vector.get("controlled_starter_runtime_seconds")
    direct_rewrite = vector.get("direct_deepseek_rewrite", {})
    maxcut_delta = maxcut.get("deltas", {}).get("openevolve_minus_direct")
    knapsack_open_score = knapsack_openevolve.get("best_score")
    knapsack_direct_score = knapsack_direct.get("metrics", {}).get("score")
    sklearn_initial = sklearn.get("initial_mean_predictor", {}).get("mean_rmse")
    sklearn_direct = sklearn.get("direct_deepseek_rewrite", {}).get("mean_rmse")
    sklearn_median = sklearn.get("openevolve_3iter", {}).get("median_rmse")

    fml_entries = [entry for entry in entries if _mentions_fml_benchmark(entry)]
    non_fml_entries = [entry for entry in entries if not _mentions_fml_benchmark(entry)]

    official_blockers = {
        "mlagentbench_cifar10": {
            "status": cifar.get("status"),
            "official_score_reported": cifar.get("official_score_reported"),
            "blocker": cifar.get("blocker", {}),
            "path": _rel(cifar_path),
        },
        "mlagentbench_cifar10_refresh": {
            "status": cifar_refresh.get("status"),
            "official_score_reported": cifar_refresh.get("official_score_reported"),
            "blocker": cifar_refresh.get("blocker", {}),
            "partial_download_bytes": cifar_refresh.get("absolute_python_attempt", {}).get("partial_download_bytes"),
            "archive_bytes": cifar_refresh.get("absolute_python_attempt", {}).get("archive_bytes"),
            "path": _rel(cifar_refresh_path),
        },
        "mlagentbench_imdb": {
            "status": imdb.get("status"),
            "official_score_reported": imdb.get("official_score_reported"),
            "blocker": imdb.get("blocker", {}),
            "path": _rel(imdb_path),
        },
        "mlagentbench_clrs": {
            "status": clrs.get("status"),
            "official_score_reported": clrs.get("official_score_reported"),
            "dependency_status": clrs.get("dependency_status"),
            "runner_reached_task_prompt": clrs.get("runner_reached_task_prompt"),
            "train_py_launched": clrs.get("train_py_launched"),
            "runner_exit_code": clrs.get("runner_exit_code"),
            "checkpoint_produced": clrs.get("checkpoint_produced"),
            "blocker": clrs.get("blocker", {}),
            "path": _rel(clrs_path),
        },
        "mlagentbench_clrs_reduced": {
            "status": clrs_reduced.get("status"),
            "mode": clrs_reduced.get("mode"),
            "official_score_reported": clrs_reduced.get("official_score_reported"),
            "train_exit_code": clrs_reduced.get("train_exit_code"),
            "checkpoint_produced": clrs_reduced.get("checkpoint_produced"),
            "spec_list_produced": clrs_reduced.get("spec_list_produced"),
            "direct_eval_error": clrs_reduced.get("direct_eval_error"),
            "path": _rel(clrs_reduced_path),
        },
        "mlagentbench_house_price": {
            "status": house_price.get("status"),
            "official_score_reported": house_price.get("official_score_reported"),
            "blocker": house_price.get("blocker", {}),
            "path": _rel(house_price_path),
        },
        "mlagentbench_ogbn_arxiv": {
            "status": ogbn.get("status"),
            "mode": ogbn.get("mode"),
            "official_score_reported": ogbn.get("official_score_reported"),
            "data_download_completed": ogbn.get("data_access", {}).get("download_completed"),
            "prepare_torch_compat_status": ogbn.get("prepare_torch_compat", {}).get("status"),
            "baseline_failure_type": ogbn.get("baseline_train", {}).get("failure_type"),
            "required_backend": ogbn.get("baseline_train", {}).get("required_backend"),
            "path": _rel(ogbn_path),
        },
        "scienceagentbench": {
            "status": science.get("status"),
            "score_reported": science.get("score_reported"),
            "missing_verified_artifacts": science.get("missing_verified_artifacts", []),
            "path": _rel(science_path),
        },
    }

    checks = {
        "benchmark_claim_matrix_has_entries": len(entries) >= 10,
        "fml_evidence_represented": len(fml_entries) >= 2,
        "non_fml_evidence_represented": len(non_fml_entries) >= 5,
        "matrix_records_boundaries": _contains_any(matrix_text, ["does_not_prove", "not prove"]),
        "selection_mentions_beyond_fml": "beyond FML-bench" in selection_text or "Non-FML" in selection_text,
        "mlagentbench_vectorization_scored_multiseed": vector_agg.get("num_seeds") == 8,
        "mlagentbench_vectorization_all_correct": vector_agg.get("num_correct_best_programs") == 8,
        "mlagentbench_vectorization_all_faster_than_starter": vector_agg.get("num_seeds_faster_than_starter")
        == 8,
        "mlagentbench_direct_rewrite_failed_correctness": direct_rewrite.get("correct") is False,
        "mlagentbench_median_runtime_beats_starter": vector_agg.get("median_runtime_seconds", 10**9)
        < starter_runtime,
        "knapsack_openevolve_beats_direct": knapsack_open_score is not None
        and knapsack_direct_score is not None
        and knapsack_open_score > knapsack_direct_score,
        "maxcut_openevolve_beats_direct": maxcut_delta is not None and maxcut_delta > 0,
        "sklearn_boundary_direct_matches_or_beats_openevolve": sklearn_initial is not None
        and sklearn_direct is not None
        and sklearn_median is not None
        and sklearn_direct <= sklearn_median + 1e-9
        and sklearn_direct < sklearn_initial,
        "open_data_multitask_evaluator_stress_scored": open_data.get("dataset_count") == 5
        and open_data.get("split_count", 0) >= 5
        and open_data_total == open_data_expected_total
        and open_data_outcome_total == open_data_total
        and open_data.get("candidate_count_per_dataset") == 8
        and isinstance(open_data.get("delta_mean_test_balanced_accuracy"), (int, float))
        and open_data.get("selection_changed_count", 0) >= 1,
        "evaluator_stress_trigger_policy_scored": trigger_policy.get("status") == "pass"
        and trigger_policy.get("total_dataset_split_evaluations") == open_data_total
        and trigger_policy.get("best_policy") == "class_imbalance_trigger_0_94"
        and trigger_policy.get("policies", {})
        .get("class_imbalance_trigger_0_94", {})
        .get("losses_vs_autonomous")
        == 0
        and trigger_policy.get("policies", {})
        .get("class_imbalance_trigger_0_94", {})
        .get("delta_vs_autonomous_mean", 0)
        > trigger_policy.get("policies", {})
        .get("always_on_evaluator_stress", {})
        .get("delta_vs_autonomous_mean", 0),
        "evaluator_stress_trigger_policy_heldout_scored": trigger_policy_holdout.get("status")
        == "pass"
        and open_data_holdout.get("total_dataset_split_evaluations") == 25
        and trigger_policy_holdout.get("best_policy") == "class_imbalance_trigger_0_94"
        and trigger_policy_holdout.get("policies", {})
        .get("class_imbalance_trigger_0_94", {})
        .get("losses_vs_autonomous")
        == 0
        and trigger_policy_holdout.get("policies", {})
        .get("class_imbalance_trigger_0_94", {})
        .get("delta_vs_autonomous_mean", 0)
        > trigger_policy_holdout.get("policies", {})
        .get("always_on_evaluator_stress", {})
        .get("delta_vs_autonomous_mean", 0),
        "evaluator_stress_trigger_policy_transfer_validated": trigger_policy_transfer.get("status")
        == "pass"
        and trigger_policy_transfer.get("selected_policy") == "class_imbalance_trigger_0_94"
        and trigger_policy_transfer.get("heldout_transfer_checks", {}).get(
            "frozen_policy_delta_beats_always_on_delta"
        )
        is True
        and trigger_policy_transfer.get("heldout_transfer_checks", {}).get(
            "frozen_policy_has_no_losses"
        )
        is True
        and trigger_policy_transfer.get("heldout_transfer_checks", {}).get("always_on_has_losses")
        is True,
        "second_non_fml_priority_package_audited": second_non_fml_priority.get("status") == "pass"
        and second_non_fml_priority.get("evidence_class")
        in {
            "scored_official_mlagentbench_non_fml_plus_official_like_package",
            "scored_official_like_non_fml_matched_package_not_official_benchmark",
        }
        and second_non_fml_priority.get("official_blockers")
        and (
            second_non_fml_priority.get("official_mlagentbench_cifar10")
            or "not a second scored official" in second_non_fml_priority.get("claim_boundary", "")
        ),
        "mlagentbench_cifar10_official_scored": cifar_official.get("status") == "pass"
        and cifar_official.get("evidence_class") == "scored_official_mlagentbench_non_fml_task"
        and cifar_official.get("candidate_score", 0) > cifar_official.get("baseline_score", 1),
        "mlagentbench_cifar10_multiseed_scored": cifar_multiseed.get("status") == "pass"
        and cifar_multiseed.get("evidence_class")
        == "scored_official_mlagentbench_non_fml_multiseed_task"
        and cifar_multiseed.get("seed_count", 0) >= 3
        and cifar_multiseed.get("all_seeds_beat_baseline") is True
        and cifar_multiseed.get("min_score", 0) > cifar_multiseed.get("baseline_score", 1),
        "blocked_official_tasks_logged": all(
            official_blockers[name].get("status") for name in official_blockers
        ),
        "remaining_blocked_tasks_do_not_report_scores": imdb.get("official_score_reported") is False
        and clrs.get("official_score_reported") is False
        and clrs_reduced.get("official_score_reported") is False
        and house_price.get("official_score_reported") is False
        and ogbn.get("official_score_reported") is False
        and science.get("score_reported") is False,
        "mlagentbench_clrs_dependency_repaired_but_unscored": clrs.get("dependency_status") == "repaired"
        and clrs.get("runner_reached_task_prompt") is True
        and clrs.get("train_py_launched") is True
        and clrs.get("runner_exit_code") == 124
        and clrs.get("checkpoint_produced") is False
        and clrs.get("official_score_reported") is False,
        "mlagentbench_clrs_reduced_kept_non_official_and_unscored": clrs_reduced.get("mode")
        == "reduced_feasibility_not_official"
        and clrs_reduced.get("train_exit_code") == 124
        and clrs_reduced.get("checkpoint_produced") is False
        and clrs_reduced.get("spec_list_produced") is False
        and clrs_reduced.get("official_score_reported") is False,
        "mlagentbench_house_price_credential_blocker_logged": house_price.get("status")
        == "setup_blocked_by_missing_kaggle_cli_and_competition_consent"
        and house_price.get("official_score_reported") is False
        and house_price.get("blocker", {}).get("missing_tool") == "kaggle"
        and house_price.get("blocker", {}).get("requires_kaggle_competition_consent") is True,
        "mlagentbench_ogbn_arxiv_data_ready_but_unscored": ogbn.get("status")
        == "setup_repaired_data_ready_but_sampler_dependency_blocked"
        and ogbn.get("data_access", {}).get("download_completed") is True
        and ogbn.get("prepare_torch_compat", {}).get("status") == "pass"
        and ogbn.get("baseline_train", {}).get("submission_csv_produced") is False
        and ogbn.get("baseline_train", {}).get("failure_type") == "missing_pyg_neighbor_sampler_backend"
        and ogbn.get("official_score_reported") is False,
        "stretch_targets_kept_future": _contains_any(matrix_text, ["MLE-bench Lite", "PaperBench", "AIRS-Bench"])
        and "Not run in the current budget" in matrix_text,
    }

    errors = [name for name, ok in checks.items() if not ok]
    warnings: list[str] = []
    if vector_agg.get("max_runtime_seconds", 0) > 1:
        warnings.append("MLAgentBench vectorization speedups are positive but seed-sensitive.")
    if maxcut_delta is not None and maxcut_delta < 0.02:
        warnings.append("Max-Cut OpenEvolve advantage is small and single-seed.")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "checks": checks,
        "evidence_summary": {
            "fml_entry_count": len(fml_entries),
            "non_fml_entry_count": len(non_fml_entries),
            "mlagentbench_vectorization": {
                "num_seeds": vector_agg.get("num_seeds"),
                "num_correct_best_programs": vector_agg.get("num_correct_best_programs"),
                "num_seeds_faster_than_starter": vector_agg.get("num_seeds_faster_than_starter"),
                "median_runtime_seconds": vector_agg.get("median_runtime_seconds"),
                "starter_runtime_seconds": starter_runtime,
                "median_speedup_over_starter": vector_agg.get("median_speedup_over_starter"),
                "direct_rewrite_correct": direct_rewrite.get("correct"),
                "path": _rel(vector_path),
            },
            "mlagentbench_cifar10_official": {
                "task": cifar_official.get("task"),
                "metric": cifar_official.get("metric"),
                "baseline_score": cifar_official.get("baseline_score"),
                "candidate_score": cifar_official.get("candidate_score"),
                "delta": cifar_official.get("delta"),
                "path": _rel(cifar_official_path),
            },
            "mlagentbench_cifar10_multiseed": {
                "task": cifar_multiseed.get("task"),
                "metric": cifar_multiseed.get("metric"),
                "baseline_score": cifar_multiseed.get("baseline_score"),
                "seed_count": cifar_multiseed.get("seed_count"),
                "mean_score": cifar_multiseed.get("mean_score"),
                "min_score": cifar_multiseed.get("min_score"),
                "max_score": cifar_multiseed.get("max_score"),
                "sample_std": cifar_multiseed.get("sample_std"),
                "mean_delta_vs_baseline": cifar_multiseed.get("mean_delta_vs_baseline"),
                "min_delta_vs_baseline": cifar_multiseed.get("min_delta_vs_baseline"),
                "all_seeds_beat_baseline": cifar_multiseed.get("all_seeds_beat_baseline"),
                "path": _rel(cifar_multiseed_path),
            },
            "algorithmic_program_search": {
                "knapsack_openevolve_score": knapsack_open_score,
                "knapsack_direct_score": knapsack_direct_score,
                "maxcut_openevolve_minus_direct": maxcut_delta,
                "paths": [_rel(knapsack_openevolve_path), _rel(knapsack_direct_path), _rel(maxcut_path)],
            },
            "boundary_condition": {
                "sklearn_initial_rmse": sklearn_initial,
                "sklearn_direct_rmse": sklearn_direct,
                "sklearn_openevolve_median_rmse": sklearn_median,
                "path": _rel(sklearn_path),
            },
            "open_data_multitask_evaluator_stress": {
                "dataset_count": open_data.get("dataset_count"),
                "split_count": open_data.get("split_count"),
                "total_dataset_split_evaluations": open_data.get("total_dataset_split_evaluations"),
                "candidate_count_per_dataset": open_data.get("candidate_count_per_dataset"),
                "co_pilot_mean_test_balanced_accuracy": open_data.get("co_pilot_variant", {}).get(
                    "mean_test_balanced_accuracy"
                ),
                "autonomous_mean_test_balanced_accuracy": open_data.get("autonomous_baseline", {}).get(
                    "mean_test_balanced_accuracy"
                ),
                "delta_mean_test_balanced_accuracy": open_data.get("delta_mean_test_balanced_accuracy"),
                "co_pilot_dataset_wins": open_data.get("co_pilot_dataset_wins"),
                "autonomous_dataset_wins": open_data.get("autonomous_dataset_wins"),
                "dataset_ties": open_data.get("dataset_ties"),
                "selection_changed_count": open_data.get("selection_changed_count"),
                "path": _rel(open_data_path),
            },
            "evaluator_stress_trigger_policy": {
                "best_policy": trigger_policy.get("best_policy"),
                "always_on": trigger_policy.get("policies", {}).get("always_on_evaluator_stress"),
                "best_policy_summary": trigger_policy.get("policies", {}).get(
                    trigger_policy.get("best_policy", "")
                ),
                "path": _rel(trigger_policy_path),
            },
            "evaluator_stress_trigger_policy_holdout": {
                "best_policy": trigger_policy_holdout.get("best_policy"),
                "open_data_delta": open_data_holdout.get("delta_mean_test_balanced_accuracy"),
                "always_on": trigger_policy_holdout.get("policies", {}).get(
                    "always_on_evaluator_stress"
                ),
                "best_policy_summary": trigger_policy_holdout.get("policies", {}).get(
                    trigger_policy_holdout.get("best_policy", "")
                ),
                "path": _rel(trigger_policy_holdout_path),
            },
            "evaluator_stress_trigger_policy_transfer": {
                "selected_policy": trigger_policy_transfer.get("selected_policy"),
                "train_package": trigger_policy_transfer.get("train_package"),
                "heldout_package": trigger_policy_transfer.get("heldout_package"),
                "heldout_frozen_policy": trigger_policy_transfer.get("heldout_frozen_policy"),
                "heldout_always_on": trigger_policy_transfer.get("heldout_always_on"),
                "transfer_checks": trigger_policy_transfer.get("heldout_transfer_checks"),
                "path": _rel(trigger_policy_transfer_path),
            },
            "official_setup_blockers": official_blockers,
            "mlagentbench_ogbn_arxiv_repair_probe": {
                "status": ogbn.get("status"),
                "data_download_completed": ogbn.get("data_access", {}).get("download_completed"),
                "prepare_torch_compat_status": ogbn.get("prepare_torch_compat", {}).get("status"),
                "baseline_failure_type": ogbn.get("baseline_train", {}).get("failure_type"),
                "official_score_reported": ogbn.get("official_score_reported"),
                "path": _rel(ogbn_path),
            },
        },
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "Benchmark coverage now includes FML feasibility evidence, non-FML scored "
            "program-search probes, an open-data multi-task evaluator-stress pilot, "
            "a scored official multi-seed MLAgentBench CIFAR10/debug task, a direct-editing "
            "boundary condition, an OGBN-arxiv repaired setup probe, and logged "
            "remaining official benchmark blockers. "
            "This supports selective workflow design, not whole-paper "
            "superiority over autonomous AI Scientist-v2."
        ),
    }

    json_path = AUDIT_DIR / "benchmark_coverage_audit.json"
    md_path = AUDIT_DIR / "benchmark_coverage_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Benchmark Coverage Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- FML entries: `{len(fml_entries)}`",
        f"- Non-FML entries: `{len(non_fml_entries)}`",
        "",
        "## Positive Scored Evidence",
        "",
        (
            "- MLAgentBench vectorization: "
            f"`{vector_agg.get('num_correct_best_programs')}/{vector_agg.get('num_seeds')}` "
            "correct best programs; median runtime "
            f"`{vector_agg.get('median_runtime_seconds')}` seconds versus starter "
            f"`{starter_runtime}` seconds; direct rewrite correctness "
            f"`{direct_rewrite.get('correct')}`."
        ),
        (
            "- MLAgentBench CIFAR10/debug official task: baseline score "
            f"`{cifar_official.get('baseline_score')}` versus co-pilot selected score "
            f"`{cifar_official.get('candidate_score')}`, delta "
            f"`{cifar_official.get('delta')}`."
        ),
        (
            "- MLAgentBench CIFAR10/debug multi-seed official check: "
            f"`{cifar_multiseed.get('seed_count')}` co-pilot-selected seeds; mean score "
            f"`{cifar_multiseed.get('mean_score'):.4f}`, min score "
            f"`{cifar_multiseed.get('min_score'):.4f}`, sample std "
            f"`{cifar_multiseed.get('sample_std'):.6f}`, mean delta vs baseline "
            f"`{cifar_multiseed.get('mean_delta_vs_baseline'):.4f}`."
        ),
        (
            "- Program search subproblems: knapsack OpenEvolve "
            f"`{knapsack_open_score}` versus direct `{knapsack_direct_score}`; "
            f"Max-Cut OpenEvolve-minus-direct `{maxcut_delta}`."
        ),
        (
            "- Open-data evaluator-stress pilot: "
            f"`{open_data.get('dataset_count')}` sklearn tasks, "
            f"`{open_data.get('split_count')}` split seeds, "
            f"`{open_data.get('total_dataset_split_evaluations')}` paired selections, "
            f"`{open_data.get('candidate_count_per_dataset')}` candidates each, "
            f"co-pilot mean balanced accuracy "
            f"`{open_data.get('co_pilot_variant', {}).get('mean_test_balanced_accuracy')}` "
            f"versus autonomous `{open_data.get('autonomous_baseline', {}).get('mean_test_balanced_accuracy')}`, "
            f"delta `{open_data.get('delta_mean_test_balanced_accuracy')}`; "
            f"selection changed in `{open_data.get('selection_changed_count')}` paired selections."
        ),
        (
            "- Evaluator-stress trigger policy: best policy "
            f"`{trigger_policy.get('best_policy')}` with delta "
            f"`{trigger_policy.get('policies', {}).get(trigger_policy.get('best_policy', ''), {}).get('delta_vs_autonomous_mean')}` "
            "versus always-on delta "
            f"`{trigger_policy.get('policies', {}).get('always_on_evaluator_stress', {}).get('delta_vs_autonomous_mean')}`."
        ),
        (
            "- Held-out trigger-policy validation: best policy "
            f"`{trigger_policy_holdout.get('best_policy')}` with delta "
            f"`{trigger_policy_holdout.get('policies', {}).get(trigger_policy_holdout.get('best_policy', ''), {}).get('delta_vs_autonomous_mean')}` "
            "versus held-out always-on delta "
            f"`{trigger_policy_holdout.get('policies', {}).get('always_on_evaluator_stress', {}).get('delta_vs_autonomous_mean')}`."
        ),
        (
            "- Frozen trigger-policy transfer: discovery selected "
            f"`{trigger_policy_transfer.get('selected_policy')}`; held-out frozen delta "
            f"`{trigger_policy_transfer.get('heldout_frozen_policy', {}).get('delta_vs_autonomous_mean')}` "
            "versus held-out always-on delta "
            f"`{trigger_policy_transfer.get('heldout_always_on', {}).get('delta_vs_autonomous_mean')}`, "
            "with held-out losses "
            f"`{trigger_policy_transfer.get('heldout_frozen_policy', {}).get('losses_vs_autonomous')}` "
            "versus always-on losses "
            f"`{trigger_policy_transfer.get('heldout_always_on', {}).get('losses_vs_autonomous')}`."
        ),
        (
            "- Second non-FML priority package audit: "
            f"`{second_non_fml_priority.get('evidence_class')}`; "
            "CIFAR10/debug is now scored, while remaining blocked official tasks stay unscored."
        ),
        (
            "- MLAgentBench OGBN-arxiv setup repair: data download completed "
            f"`{ogbn.get('data_access', {}).get('download_completed')}`, prepare with PyTorch "
            f"compatibility `{ogbn.get('prepare_torch_compat', {}).get('status')}`, baseline "
            f"failure `{ogbn.get('baseline_train', {}).get('failure_type')}`; no official score."
        ),
        "",
        "## Boundary And Blocked Evidence",
        "",
        (
            "- sklearn diabetes boundary: direct rewrite RMSE "
            f"`{sklearn_direct}` matches or beats OpenEvolve median `{sklearn_median}`, "
            "so program search should be gated rather than automatic."
        ),
    ]
    for name, blocker in official_blockers.items():
        lines.append(f"- `{name}`: `{blocker.get('status')}`; no official score reported.")
    lines.append(
        "- `mlagentbench_cifar10_official`: "
        f"`{cifar_official.get('status')}`; official score reported with delta `{cifar_official.get('delta')}`."
    )
    lines.append(
        "- `mlagentbench_cifar10_multiseed`: "
        f"`{cifar_multiseed.get('status')}`; `{cifar_multiseed.get('seed_count')}` official "
        f"co-pilot-selected seeds with minimum score `{cifar_multiseed.get('min_score')}`."
    )
    lines.extend(["", "## Checks", ""])
    for name, ok in checks.items():
        lines.append(f"- `{name}`: `{'pass' if ok else 'fail'}`")
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
