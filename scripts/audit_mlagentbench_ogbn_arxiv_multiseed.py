#!/usr/bin/env python3
"""Audit the MLAgentBench OGBN-arxiv multi-seed compatibility evidence."""

from __future__ import annotations

import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments" / "mlagentbench_ogbn_arxiv_official_compat_20260603"
AUDIT_DIR = DOC_DIR / "audits"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = EXP_DIR / "summary.json"
    summary = _load_json(summary_path)
    baseline_score = float(summary["baseline"]["score"])
    multiseed = summary["co_pilot_multiseed"]
    seeds = multiseed["seeds"]
    scores = [float(seed["score"]) for seed in seeds]

    required_files = [summary_path, EXP_DIR / "README.md"]
    for seed in seeds:
        required_files.extend(
            [
                ROOT / seed["train_script"],
                ROOT / seed["train_log"],
                ROOT / seed["eval_log"],
            ]
        )
    missing = [_rel(path) for path in required_files if not path.exists()]

    per_seed_checks = []
    for seed in seeds:
        train_log = _read(ROOT / seed["train_log"]) if (ROOT / seed["train_log"]).exists() else ""
        eval_log = _read(ROOT / seed["eval_log"]) if (ROOT / seed["eval_log"]).exists() else ""
        expected_score = str(seed["score"])
        per_seed_checks.append(
            {
                "seed": seed["seed"],
                "train_completed": "done best_val=" in train_log,
                "eval_score_present": expected_score in eval_log,
                "score_beats_baseline": seed["score"] > baseline_score,
            }
        )

    computed = {
        "seed_count": len(seeds),
        "mean_score": statistics.mean(scores),
        "min_score": min(scores),
        "max_score": max(scores),
        "sample_std": statistics.stdev(scores),
        "mean_delta_vs_baseline": statistics.mean(scores) - baseline_score,
    }
    checks = {
        "all_required_files_present": not missing,
        "seed_count_at_least_three": len(seeds) >= 3,
        "all_train_logs_completed": all(item["train_completed"] for item in per_seed_checks),
        "all_eval_logs_match_summary": all(item["eval_score_present"] for item in per_seed_checks),
        "all_seeds_beat_baseline": all(item["score_beats_baseline"] for item in per_seed_checks),
        "mean_score_matches_summary": _close(computed["mean_score"], multiseed["mean_score"]),
        "min_score_matches_summary": _close(computed["min_score"], multiseed["min_score"]),
        "sample_std_matches_summary": _close(computed["sample_std"], multiseed["sample_std"]),
        "compatibility_boundary_recorded": "compatibility" in multiseed["claim_boundary"].lower()
        and "not broad MLAgentBench superiority" in multiseed["claim_boundary"],
    }
    errors = [name for name, ok in checks.items() if not ok]
    if missing:
        errors.append(f"missing_files: {missing}")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "evidence_class": "three_seed_scored_official_mlagentbench_ogbn_arxiv_compatibility_path",
        "task": summary["task"],
        "metric": summary["metric"],
        "baseline_score": baseline_score,
        "seed_scores": scores,
        **computed,
        "per_seed_checks": per_seed_checks,
        "checks": checks,
        "errors": errors,
        "claim_boundary": multiseed["claim_boundary"],
    }

    json_path = AUDIT_DIR / "mlagentbench_ogbn_arxiv_multiseed_audit.json"
    md_path = AUDIT_DIR / "mlagentbench_ogbn_arxiv_multiseed_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# MLAgentBench OGBN-arxiv Multi-Seed Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Evidence class: `{audit['evidence_class']}`",
        f"- Task: `{audit['task']}`",
        f"- Metric: `{audit['metric']}`",
        f"- Compatibility baseline score: `{baseline_score}`",
        f"- Seed scores: `{scores}`",
        f"- Mean score: `{computed['mean_score']}`",
        f"- Min score: `{computed['min_score']}`",
        f"- Sample std: `{computed['sample_std']}`",
        f"- Mean delta vs baseline: `{computed['mean_delta_vs_baseline']}`",
        "",
        "## Per-Seed Checks",
        "",
    ]
    for item in per_seed_checks:
        lines.append(
            f"- Seed `{item['seed']}`: train completed `{'pass' if item['train_completed'] else 'fail'}`, "
            f"eval log match `{'pass' if item['eval_score_present'] else 'fail'}`, "
            f"beats baseline `{'pass' if item['score_beats_baseline'] else 'fail'}`"
        )
    lines.extend(["", "## Checks", ""])
    for name, ok in checks.items():
        lines.append(f"- `{name}`: `{'pass' if ok else 'fail'}`")
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in [json_path, md_path, Path(__file__), *required_files]:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["current_artifacts"] = sorted(artifacts)
    manifest["mlagentbench_ogbn_arxiv_multiseed_audit"] = {
        "status": audit["status"],
        "json": _rel(json_path),
        "markdown": _rel(md_path),
        "experiment_dir": _rel(EXP_DIR),
        "evidence_class": audit["evidence_class"],
        "baseline_score": baseline_score,
        "mean_score": computed["mean_score"],
        "min_score": computed["min_score"],
        "sample_std": computed["sample_std"],
        "mean_delta_vs_baseline": computed["mean_delta_vs_baseline"],
        "claim_boundary": audit["claim_boundary"],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
