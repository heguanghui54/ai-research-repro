#!/usr/bin/env python3
"""Audit the MLAgentBench CIFAR10/debug multi-seed official evidence."""

from __future__ import annotations

import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
RUN_DIR = DOC_DIR / "experiments" / "mlagentbench_cifar10_debug_multiseed_20260603"
BASELINE_JSON = DOC_DIR / "experiments" / "mlagentbench_cifar10_debug_official_20260603" / "baseline" / "eval.json"
MANIFEST_PATH = DOC_DIR / "repro_manifest.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def update_manifest(paths: list[Path], summary: dict) -> None:
    manifest = load_json(MANIFEST_PATH)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        r = rel(path)
        if r not in artifacts:
            artifacts.append(r)
    manifest["mlagentbench_cifar10_multiseed_audit"] = {
        "status": summary["status"],
        "json": rel(AUDIT_DIR / "mlagentbench_cifar10_multiseed_audit.json"),
        "markdown": rel(AUDIT_DIR / "mlagentbench_cifar10_multiseed_audit.md"),
        "experiment_dir": rel(RUN_DIR),
        "evidence_class": "scored_official_mlagentbench_non_fml_multiseed_task",
        "seed_count": summary["seed_count"],
        "baseline_score": summary["baseline_score"],
        "mean_score": summary["mean_score"],
        "min_score": summary["min_score"],
        "sample_std": summary["sample_std"],
        "mean_delta_vs_baseline": summary["mean_delta_vs_baseline"],
        "all_seeds_beat_baseline": summary["all_seeds_beat_baseline"],
        "claim_boundary": (
            "Three co-pilot-selected seeds for one official MLAgentBench CIFAR10/debug task; "
            "still not broad benchmark coverage, independent human evidence, or paper-quality superiority."
        ),
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    seed_rows: list[dict] = []
    required_paths: list[Path] = []

    baseline = load_json(BASELINE_JSON)
    if "final_score" in baseline:
        baseline_score = float(baseline["final_score"])
    else:
        baseline_records = list(baseline.values())
        baseline_score = float(baseline_records[0]["final_score"]) if baseline_records else math.nan

    for seed in [20260603, 20260604, 20260605]:
        seed_dir = RUN_DIR / f"seed_{seed}"
        summary_path = seed_dir / "summary.json"
        train_path = seed_dir / "train.py"
        log_path = seed_dir / "train.stdout.log"
        required_paths.extend([summary_path, train_path, log_path])
        if not summary_path.exists() or not train_path.exists() or not log_path.exists():
            errors.append(f"missing seed artifact for {seed}")
            continue
        summary = load_json(summary_path)
        score = float(summary["official_eval_score"])
        log = log_path.read_text(encoding="utf-8", errors="replace")
        completed = "Epoch [8/8]" in log and "Done in" in log
        seed_rows.append(
            {
                "seed": seed,
                "score": score,
                "delta_vs_baseline": score - baseline_score,
                "completed": completed,
                "run_dir": summary.get("run_dir"),
            }
        )
        if not completed:
            errors.append(f"seed {seed} training log does not show completion")
        if score <= baseline_score:
            errors.append(f"seed {seed} score {score:.4f} does not beat baseline {baseline_score:.4f}")

    scores = [row["score"] for row in seed_rows]
    mean_score = statistics.mean(scores) if scores else math.nan
    sample_std = statistics.stdev(scores) if len(scores) > 1 else 0.0
    min_score = min(scores) if scores else math.nan
    max_score = max(scores) if scores else math.nan
    all_seeds_beat_baseline = bool(scores) and all(score > baseline_score for score in scores)

    audit = {
        "audit_date": utc_now(),
        "status": "pass" if not errors else "fail",
        "evidence_class": "scored_official_mlagentbench_non_fml_multiseed_task",
        "task": "MLAgentBench debug / cifar10",
        "metric": "CIFAR10 test accuracy; higher is better",
        "baseline_score": baseline_score,
        "seed_count": len(seed_rows),
        "seeds": seed_rows,
        "mean_score": mean_score,
        "min_score": min_score,
        "max_score": max_score,
        "sample_std": sample_std,
        "mean_delta_vs_baseline": mean_score - baseline_score if scores else math.nan,
        "min_delta_vs_baseline": min_score - baseline_score if scores else math.nan,
        "all_seeds_beat_baseline": all_seeds_beat_baseline,
        "errors": errors,
        "claim_boundary": (
            "This is a three-seed robustness check for one official MLAgentBench CIFAR10/debug task. "
            "It strengthens the non-FML evidence slice but remains one task and does not prove broad "
            "co-pilot superiority, paper-quality improvement, or independent human benefit."
        ),
    }

    json_path = AUDIT_DIR / "mlagentbench_cifar10_multiseed_audit.json"
    md_path = AUDIT_DIR / "mlagentbench_cifar10_multiseed_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# MLAgentBench CIFAR10 Multi-Seed Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Evidence class: `{audit['evidence_class']}`",
        f"- Task: `{audit['task']}`",
        f"- Metric: `{audit['metric']}`",
        f"- Baseline score: `{baseline_score:.4f}`",
        f"- Seed count: `{audit['seed_count']}`",
        f"- Mean co-pilot-selected score: `{mean_score:.4f}`",
        f"- Min co-pilot-selected score: `{min_score:.4f}`",
        f"- Max co-pilot-selected score: `{max_score:.4f}`",
        f"- Sample std: `{sample_std:.6f}`",
        f"- Mean delta vs baseline: `{audit['mean_delta_vs_baseline']:.4f}`",
        f"- Min delta vs baseline: `{audit['min_delta_vs_baseline']:.4f}`",
        f"- All seeds beat baseline: `{all_seeds_beat_baseline}`",
        "",
        "## Seed Results",
        "",
        "| Seed | Official score | Delta vs baseline | Completed |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in seed_rows:
        lines.append(
            f"| `{row['seed']}` | `{row['score']:.4f}` | `{row['delta_vs_baseline']:.4f}` | `{row['completed']}` |"
        )
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {err}" for err in errors] if errors else ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    update_manifest(required_paths + [json_path, md_path], audit)
    print(json.dumps({"json": rel(json_path), "markdown": rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
