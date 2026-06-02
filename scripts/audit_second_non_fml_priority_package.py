#!/usr/bin/env python3
"""Audit the second non-FML priority benchmark package.

This audit separates three evidence classes that are easy to blur:

1. MLAgentBench vectorization is the first scored non-FML result.
2. MLAgentBench CIFAR10/debug is now a scored official non-FML task.
3. MLAgentBench OGBN-arxiv now has a scored official-evaluator compatibility run.
4. The open-data sklearn package is a scored, official-like matched package
   with held-out trigger-policy transfer.
5. Larger remaining official MLAgentBench/ScienceAgentBench tasks remain blocked and
   must not be reported as scored.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
AUDIT_DIR = DOC_DIR / "audits"

TRAIN_PACKAGE = "prospective_matched_open_data_multitask_20260603"
HELDOUT_PACKAGE = "prospective_matched_open_data_multitask_holdout_20260603"
TRANSFER_PACKAGE = "evaluator_trigger_policy_transfer_20260603"
SELECTED_TRIGGER_POLICY = "class_imbalance_trigger_0_94"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _add_manifest_artifacts(paths: list[Path], payload: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    if not manifest_path.exists():
        return
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in [*paths, Path(__file__)]:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["second_non_fml_priority_package_audit"] = payload
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _metric_checks(metrics: dict[str, Any]) -> dict[str, bool]:
    total = metrics.get("total_dataset_split_evaluations")
    expected_total = metrics.get("dataset_count", 0) * metrics.get("split_count", 0)
    outcomes = (
        metrics.get("co_pilot_dataset_wins", 0)
        + metrics.get("autonomous_dataset_wins", 0)
        + metrics.get("dataset_ties", 0)
    )
    return {
        "five_open_datasets": metrics.get("dataset_count") == 5,
        "five_split_seeds": metrics.get("split_count") == 5,
        "twenty_five_paired_selections": total == 25 and expected_total == 25,
        "all_outcomes_accounted": outcomes == total,
        "eight_shared_candidates": metrics.get("candidate_count_per_dataset") == 8,
        "matched_selectors_present": bool(metrics.get("autonomous_selector"))
        and bool(metrics.get("co_pilot_selector")),
        "numeric_delta_present": isinstance(metrics.get("delta_mean_test_balanced_accuracy"), (int, float)),
        "selection_changes_present": metrics.get("selection_changed_count", 0) >= 1,
    }


def _trigger_checks(summary: dict[str, Any], metrics: dict[str, Any]) -> dict[str, bool]:
    policies = summary.get("policies", {})
    selected = policies.get(SELECTED_TRIGGER_POLICY, {})
    always = policies.get("always_on_evaluator_stress", {})
    return {
        "summary_pass": summary.get("status") == "pass",
        "total_matches_metrics": summary.get("total_dataset_split_evaluations")
        == metrics.get("total_dataset_split_evaluations"),
        "selected_policy_matches": summary.get("best_policy") == SELECTED_TRIGGER_POLICY,
        "selected_policy_has_no_losses": selected.get("losses_vs_autonomous") == 0,
        "selected_delta_beats_always_on": selected.get("delta_vs_autonomous_mean", 0)
        > always.get("delta_vs_autonomous_mean", 0),
        "selected_policy_triggers_nonzero": selected.get("triggered_count", 0) > 0,
    }


def _official_blocker_checks() -> dict[str, dict[str, Any]]:
    blockers = {
        "mlagentbench_cifar10_refresh": EXP_DIR
        / "mlagentbench_cifar10_debug_refresh_probe_20260602"
        / "summary.json",
        "mlagentbench_imdb": EXP_DIR / "mlagentbench_imdb_setup_probe" / "summary.json",
        "mlagentbench_clrs": EXP_DIR / "mlagentbench_clrs_baseline_smoke_20260602" / "summary.json",
        "mlagentbench_clrs_reduced": EXP_DIR
        / "mlagentbench_clrs_reduced_smoke_20260602"
        / "summary.json",
        "mlagentbench_house_price": EXP_DIR / "mlagentbench_house_price_setup_probe" / "summary.json",
        "scienceagentbench": EXP_DIR / "scienceagentbench_metadata_setup_probe" / "summary.json",
    }
    results: dict[str, dict[str, Any]] = {}
    for name, path in blockers.items():
        payload = _load_json(path)
        score_flag = payload.get("official_score_reported", payload.get("score_reported"))
        results[name] = {
            "path": _rel(path),
            "status": payload.get("status"),
            "score_reported": bool(score_flag),
            "kept_unscored": score_flag is False,
        }
    return results


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    train_metrics_path = EXP_DIR / TRAIN_PACKAGE / "remote_metrics.json"
    heldout_metrics_path = EXP_DIR / HELDOUT_PACKAGE / "remote_metrics.json"
    train_trigger_path = EXP_DIR / TRAIN_PACKAGE / "evaluator_stress_trigger_policy_summary.json"
    heldout_trigger_path = EXP_DIR / HELDOUT_PACKAGE / "evaluator_stress_trigger_policy_summary.json"
    transfer_path = EXP_DIR / TRANSFER_PACKAGE / "summary.json"
    cifar_official_path = AUDIT_DIR / "mlagentbench_cifar10_official_audit.json"
    cifar_multiseed_path = AUDIT_DIR / "mlagentbench_cifar10_multiseed_audit.json"
    ogbn_official_path = AUDIT_DIR / "mlagentbench_ogbn_arxiv_official_audit.json"

    train_metrics = _load_json(train_metrics_path)
    heldout_metrics = _load_json(heldout_metrics_path)
    train_trigger = _load_json(train_trigger_path)
    heldout_trigger = _load_json(heldout_trigger_path)
    transfer = _load_json(transfer_path)
    cifar_official = _load_json(cifar_official_path)
    cifar_multiseed = _load_json(cifar_multiseed_path)
    ogbn_official = _load_json(ogbn_official_path)

    train_metric_checks = _metric_checks(train_metrics)
    heldout_metric_checks = _metric_checks(heldout_metrics)
    train_trigger_checks = _trigger_checks(train_trigger, train_metrics)
    heldout_trigger_checks = _trigger_checks(heldout_trigger, heldout_metrics)
    official_blockers = _official_blocker_checks()

    transfer_checks = {
        "transfer_pass": transfer.get("status") == "pass",
        "selected_policy_frozen": transfer.get("selected_policy") == SELECTED_TRIGGER_POLICY,
        "heldout_frozen_policy_has_no_losses": transfer.get("heldout_frozen_policy", {}).get(
            "losses_vs_autonomous"
        )
        == 0,
        "heldout_delta_beats_always_on": transfer.get("heldout_transfer_checks", {}).get(
            "frozen_policy_delta_beats_always_on_delta"
        )
        is True,
        "heldout_delta_positive": transfer.get("heldout_frozen_policy", {}).get(
            "delta_vs_autonomous_mean", 0
        )
        > 0,
    }
    official_cifar_checks = {
        "official_cifar_audit_pass": cifar_official.get("status") == "pass",
        "official_cifar_scored": cifar_official.get("evidence_class")
        == "scored_official_mlagentbench_non_fml_task",
        "official_cifar_candidate_beats_baseline": cifar_official.get("candidate_score", 0)
        > cifar_official.get("baseline_score", 1),
        "official_cifar_multiseed_audit_pass": cifar_multiseed.get("status") == "pass",
        "official_cifar_multiseed_all_beat_baseline": cifar_multiseed.get("all_seeds_beat_baseline")
        is True,
        "official_cifar_multiseed_seed_count": cifar_multiseed.get("seed_count", 0) >= 3,
    }
    official_ogbn_checks = {
        "official_ogbn_audit_pass": ogbn_official.get("status") == "pass",
        "official_ogbn_scored_compatibility": ogbn_official.get("evidence_class")
        == "scored_official_mlagentbench_non_fml_task_with_compatibility_baseline",
        "official_ogbn_candidate_beats_baseline": ogbn_official.get("candidate_score", 0)
        > ogbn_official.get("baseline_score", 1),
        "official_ogbn_boundary_recorded": "compatibility" in ogbn_official.get(
            "claim_boundary", ""
        ).lower(),
    }

    official_blockers_kept_unscored = all(item["kept_unscored"] for item in official_blockers.values())
    checks = {
        "train_metric_checks": train_metric_checks,
        "heldout_metric_checks": heldout_metric_checks,
        "train_trigger_checks": train_trigger_checks,
        "heldout_trigger_checks": heldout_trigger_checks,
        "transfer_checks": transfer_checks,
        "official_cifar_checks": official_cifar_checks,
        "official_ogbn_checks": official_ogbn_checks,
        "official_blockers_kept_unscored": official_blockers_kept_unscored,
    }
    errors: list[str] = []
    for group, group_checks in checks.items():
        if isinstance(group_checks, dict):
            for name, passed in group_checks.items():
                if isinstance(passed, dict):
                    continue
                if not passed:
                    errors.append(f"{group}.{name} failed")
        elif not group_checks:
            errors.append(f"{group} failed")
    if not official_blockers_kept_unscored:
        errors.append("one or more blocked official tasks report a score")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "head": _git_head(),
        "evidence_class": "two_scored_official_mlagentbench_paths_plus_official_like_package",
        "priority_queue_item": "Second scored non-FML benchmark package",
        "official_mlagentbench_cifar10": {
            "audit_path": _rel(cifar_official_path),
            "multiseed_audit_path": _rel(cifar_multiseed_path),
            "task": cifar_official.get("task"),
            "metric": cifar_official.get("metric"),
            "baseline_score": cifar_official.get("baseline_score"),
            "candidate_score": cifar_official.get("candidate_score"),
            "delta": cifar_official.get("delta"),
            "seed_count": cifar_multiseed.get("seed_count"),
            "mean_score": cifar_multiseed.get("mean_score"),
            "min_score": cifar_multiseed.get("min_score"),
            "sample_std": cifar_multiseed.get("sample_std"),
            "mean_delta_vs_baseline": cifar_multiseed.get("mean_delta_vs_baseline"),
        },
        "official_mlagentbench_ogbn_arxiv": {
            "audit_path": _rel(ogbn_official_path),
            "task": ogbn_official.get("task"),
            "metric": ogbn_official.get("metric"),
            "baseline_score": ogbn_official.get("baseline_score"),
            "candidate_score": ogbn_official.get("candidate_score"),
            "delta": ogbn_official.get("delta"),
            "baseline_name": ogbn_official.get("baseline_name"),
            "candidate_name": ogbn_official.get("candidate_name"),
            "claim_boundary": ogbn_official.get("claim_boundary"),
        },
        "official_like_package": {
            "train_package": TRAIN_PACKAGE,
            "heldout_package": HELDOUT_PACKAGE,
            "transfer_package": TRANSFER_PACKAGE,
        },
        "train_package": TRAIN_PACKAGE,
        "heldout_package": HELDOUT_PACKAGE,
        "transfer_package": TRANSFER_PACKAGE,
        "train_metrics_path": _rel(train_metrics_path),
        "heldout_metrics_path": _rel(heldout_metrics_path),
        "selected_trigger_policy": SELECTED_TRIGGER_POLICY,
        "train_summary": {
            "mean_delta": train_metrics.get("delta_mean_test_balanced_accuracy"),
            "wins": train_metrics.get("co_pilot_dataset_wins"),
            "losses": train_metrics.get("autonomous_dataset_wins"),
            "ties": train_metrics.get("dataset_ties"),
            "selection_changed_count": train_metrics.get("selection_changed_count"),
        },
        "heldout_transfer_summary": {
            "frozen_policy_delta": transfer.get("heldout_frozen_policy", {}).get(
                "delta_vs_autonomous_mean"
            ),
            "frozen_policy_wins": transfer.get("heldout_frozen_policy", {}).get(
                "wins_vs_autonomous"
            ),
            "frozen_policy_losses": transfer.get("heldout_frozen_policy", {}).get(
                "losses_vs_autonomous"
            ),
            "frozen_policy_ties": transfer.get("heldout_frozen_policy", {}).get(
                "ties_vs_autonomous"
            ),
        },
        "checks": checks,
        "official_blockers": official_blockers,
        "errors": errors,
        "claim_boundary": (
            "This closes a low-cost official-like non-FML matched-package gap: "
            "the package is scored, open-data, matched, held-out, and auditable; "
            "it also adds a three-seed scored official MLAgentBench CIFAR10/debug result "
            "and a scored OGBN-arxiv official-evaluator compatibility run. The OGBN "
            "baseline is a compatibility translation, so this is still not broad "
            "MLAgentBench superiority evidence, independent human evidence, or "
            "paper-quality proof."
        ),
    }

    json_path = AUDIT_DIR / "second_non_fml_priority_package_audit.json"
    md_path = AUDIT_DIR / "second_non_fml_priority_package_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Second Non-FML Priority Package Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Evidence class: `{audit['evidence_class']}`",
        f"- Priority queue item: `{audit['priority_queue_item']}`",
        f"- Official MLAgentBench CIFAR10 baseline score: `{audit['official_mlagentbench_cifar10']['baseline_score']}`",
        f"- Official MLAgentBench CIFAR10 co-pilot selected score: `{audit['official_mlagentbench_cifar10']['candidate_score']}`",
        f"- Official MLAgentBench CIFAR10 delta: `{audit['official_mlagentbench_cifar10']['delta']}`",
        f"- Official MLAgentBench CIFAR10 multi-seed mean score: `{audit['official_mlagentbench_cifar10']['mean_score']}`",
        f"- Official MLAgentBench CIFAR10 multi-seed min score: `{audit['official_mlagentbench_cifar10']['min_score']}`",
        f"- Official MLAgentBench CIFAR10 multi-seed sample std: `{audit['official_mlagentbench_cifar10']['sample_std']}`",
        f"- Official MLAgentBench OGBN-arxiv compatibility baseline score: `{audit['official_mlagentbench_ogbn_arxiv']['baseline_score']}`",
        f"- Official MLAgentBench OGBN-arxiv co-pilot selected score: `{audit['official_mlagentbench_ogbn_arxiv']['candidate_score']}`",
        f"- Official MLAgentBench OGBN-arxiv delta: `{audit['official_mlagentbench_ogbn_arxiv']['delta']}`",
        f"- Train package: `{audit['train_package']}`",
        f"- Held-out package: `{audit['heldout_package']}`",
        f"- Selected trigger policy: `{audit['selected_trigger_policy']}`",
        "",
        "## Train Summary",
        "",
        f"- Mean delta: `{audit['train_summary']['mean_delta']}`",
        f"- Wins/losses/ties: `{audit['train_summary']['wins']}` / `{audit['train_summary']['losses']}` / `{audit['train_summary']['ties']}`",
        f"- Selection changes: `{audit['train_summary']['selection_changed_count']}`",
        "",
        "## Held-Out Frozen Policy",
        "",
        f"- Frozen-policy delta: `{audit['heldout_transfer_summary']['frozen_policy_delta']}`",
        f"- Wins/losses/ties: `{audit['heldout_transfer_summary']['frozen_policy_wins']}` / `{audit['heldout_transfer_summary']['frozen_policy_losses']}` / `{audit['heldout_transfer_summary']['frozen_policy_ties']}`",
        "",
        "## Official Benchmark Boundary",
        "",
    ]
    for name, item in official_blockers.items():
        lines.append(
            f"- `{name}`: status `{item['status']}`, score reported `{item['score_reported']}`"
        )
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    _add_manifest_artifacts([json_path, md_path], audit)
    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
