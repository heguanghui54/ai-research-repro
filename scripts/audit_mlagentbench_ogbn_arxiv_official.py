#!/usr/bin/env python3
"""Audit the MLAgentBench OGBN-arxiv official-evaluator compatibility run."""

from __future__ import annotations

import json
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


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = EXP_DIR / "summary.json"
    summary = _load_json(summary_path)
    baseline = summary["baseline"]
    candidate = summary["co_pilot_selected"]

    required_files = [
        EXP_DIR / "README.md",
        summary_path,
        ROOT / baseline["train_script"],
        ROOT / baseline["train_log"],
        ROOT / baseline["eval_log"],
        ROOT / candidate["train_script"],
        ROOT / candidate["train_log"],
        ROOT / candidate["eval_log"],
    ]
    missing = [_rel(path) for path in required_files if not path.exists()]

    baseline_train_log = _read(ROOT / baseline["train_log"])
    baseline_eval_log = _read(ROOT / baseline["eval_log"])
    candidate_train_log = _read(ROOT / candidate["train_log"])
    candidate_eval_log = _read(ROOT / candidate["eval_log"])

    checks = {
        "all_required_files_present": not missing,
        "official_prepared_data": summary.get("official_prepared_data") is True,
        "official_eval_script": summary.get("official_eval_script") is True,
        "baseline_train_completed": "done seconds=" in baseline_train_log
        and baseline.get("train_exit_code") == 0,
        "baseline_eval_completed": str(baseline.get("score")) in baseline_eval_log
        and baseline.get("eval_exit_code") == 0,
        "candidate_train_completed": "done best_val=" in candidate_train_log
        and candidate.get("train_exit_code") == 0,
        "candidate_eval_completed": str(candidate.get("score")) in candidate_eval_log
        and candidate.get("eval_exit_code") == 0,
        "candidate_beats_baseline": candidate.get("score", 0) > baseline.get("score", 1),
        "compatibility_boundary_recorded": "compatibility" in summary.get("claim_boundary", "").lower()
        and "unmodified NeighborLoader starter" in summary.get("claim_boundary", ""),
        "no_broad_superiority_claim": "broad MLAgentBench superiority" in summary.get("claim_boundary", ""),
    }
    errors = [name for name, ok in checks.items() if not ok]
    if missing:
        errors.append(f"missing_files: {missing}")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "evidence_class": summary.get("evidence_class"),
        "task": summary.get("task"),
        "metric": summary.get("metric"),
        "baseline_score": baseline.get("score"),
        "candidate_score": candidate.get("score"),
        "delta": summary.get("delta"),
        "baseline_name": baseline.get("name"),
        "candidate_name": candidate.get("name"),
        "remote_run_root": summary.get("remote_run_root"),
        "checks": checks,
        "errors": errors,
        "claim_boundary": summary.get("claim_boundary"),
    }

    json_path = AUDIT_DIR / "mlagentbench_ogbn_arxiv_official_audit.json"
    md_path = AUDIT_DIR / "mlagentbench_ogbn_arxiv_official_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# MLAgentBench OGBN-arxiv Official-Evaluator Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Evidence class: `{audit['evidence_class']}`",
        f"- Task: `{audit['task']}`",
        f"- Metric: `{audit['metric']}`",
        f"- Baseline: `{audit['baseline_name']}` score `{audit['baseline_score']}`",
        f"- Co-pilot selected: `{audit['candidate_name']}` score `{audit['candidate_score']}`",
        f"- Delta: `{audit['delta']}`",
        "",
        "## Checks",
        "",
    ]
    for name, ok in checks.items():
        lines.append(f"- `{name}`: `{'pass' if ok else 'fail'}`")
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in [
        json_path,
        md_path,
        Path(__file__),
        *required_files,
    ]:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["current_artifacts"] = sorted(artifacts)
    manifest["mlagentbench_ogbn_arxiv_official_audit"] = {
        "status": audit["status"],
        "json": _rel(json_path),
        "markdown": _rel(md_path),
        "experiment_dir": _rel(EXP_DIR),
        "evidence_class": audit["evidence_class"],
        "baseline_score": audit["baseline_score"],
        "candidate_score": audit["candidate_score"],
        "delta": audit["delta"],
        "claim_boundary": audit["claim_boundary"],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
