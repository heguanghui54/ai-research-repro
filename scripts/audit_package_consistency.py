#!/usr/bin/env python3
"""Audit cross-artifact consistency for the Co-Pilot AI Scientist v3 package.

This is a reproducibility hygiene audit. It checks that the manuscript,
manifest, readiness audit, claim-evidence audit, clean-clone audit, and key
experiment summaries agree on the current artifact count and latest TFR
candidate-frontier validation metrics.
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


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _git_is_shallow() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return result.stdout.strip().lower() == "true"


def _git_is_ancestor(ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def _contains(path: Path, needles: list[str]) -> dict[str, bool]:
    text = path.read_text(encoding="utf-8")
    return {needle: needle in text for needle in needles}


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    head = _git_head()
    manifest_path = DOC_DIR / "repro_manifest.json"
    clean_path = AUDIT_DIR / "clean_clone_reproducibility_audit.json"
    readiness_path = AUDIT_DIR / "top_conference_readiness_audit.json"
    claim_path = AUDIT_DIR / "claim_evidence_audit.json"
    objective_path = AUDIT_DIR / "objective_delivery_audit.json"
    validation_path = DOC_DIR / "experiments" / "delayed_value_candidate_frontier_validation_20260603_011500" / "summary.json"
    tfr_path = AUDIT_DIR / "temporal_frontier_replay_audit.json"

    manifest = _load_json(manifest_path)
    clean = _load_json(clean_path)
    readiness = _load_json(readiness_path)
    claim = _load_json(claim_path)
    objective = _load_json(objective_path)
    validation = _load_json(validation_path)
    tfr = _load_json(tfr_path)

    artifacts = manifest.get("current_artifacts", [])
    missing = [path for path in artifacts if not (ROOT / path).exists()]
    duplicate_artifacts = sorted({path for path in artifacts if artifacts.count(path) > 1})
    manifest_count = len(artifacts)
    clean_checks = clean.get("checks", {})
    validation_agg = validation.get("aggregate", {})

    errors: list[str] = []
    warnings: list[str] = []
    is_shallow_repository = _git_is_shallow()

    if missing:
        errors.append(f"manifest lists {len(missing)} missing artifacts")
    if duplicate_artifacts:
        warnings.append(f"manifest has duplicate artifact entries: {len(duplicate_artifacts)}")
    audited_commit = clean.get("commit", "")
    clean_commit_is_head = audited_commit == head
    clean_commit_is_ancestor = bool(audited_commit and _git_is_ancestor(audited_commit, head))
    if clean_checks.get("manifest_artifacts_checked") != manifest_count:
        message = "clean-clone manifest_artifacts_checked does not match manifest current_artifacts length"
        if clean_commit_is_head:
            errors.append(message)
        else:
            warnings.append(message + " because clean-clone audit targets an ancestor commit")
    if clean_checks.get("missing_manifest_artifacts") != 0:
        errors.append("clean-clone audit reports missing manifest artifacts")
    if validation_agg.get("scored_count") != clean_checks.get("candidate_frontier_scored_reviews"):
        errors.append("candidate-frontier scored count disagrees between clean audit and summary")
    if validation_agg.get("delayed_minus_control_mean_score") != clean_checks.get("delayed_minus_control_mean_score"):
        errors.append("candidate-frontier delta disagrees between clean audit and summary")
    if tfr.get("status") != clean_checks.get("temporal_frontier_replay_audit_status"):
        errors.append("TFR audit status disagrees with clean-clone audit")
    if audited_commit and not clean_commit_is_ancestor:
        message = "clean-clone audited commit is not an ancestor of current HEAD"
        if is_shallow_repository and audited_commit != head:
            warnings.append(message + " in this shallow checkout")
        else:
            errors.append(message)

    current_counts = readiness.get("current_counts", {})
    if current_counts.get("delayed_value_candidate_frontier_validation_scored_reviews") != validation_agg.get(
        "scored_count"
    ):
        errors.append("readiness current_counts has stale candidate-frontier scored count")
    if readiness.get("clean_clone_reproducibility", {}).get("manifest_artifacts_checked") != manifest_count:
        message = "readiness clean-clone manifest count is stale"
        if clean_commit_is_head:
            errors.append(message)
        else:
            warnings.append(message + " because clean-clone audit targets an ancestor commit")

    claim_text = json.dumps(claim, ensure_ascii=False)
    if "delayed_value_candidate_frontier_validation_20260603_011500" not in claim_text:
        errors.append("claim-evidence audit does not reference candidate-frontier validation")

    focused_en = DOC_DIR / "paper_en_focused.md"
    readiness_md = AUDIT_DIR / "top_conference_readiness_audit.md"
    claim_md = AUDIT_DIR / "claim_evidence_audit.md"
    objective_md = AUDIT_DIR / "objective_delivery_audit.md"
    clean_short = audited_commit[:9] if audited_commit else ""
    manifest_ratio = f"{manifest_count}/{manifest_count}"
    clean_ratio = f"{clean_checks.get('manifest_artifacts_checked')}/{clean_checks.get('manifest_artifacts_checked')}"
    stale_tokens = ["dc8f35be7", "dc8f35be", "603/603", '"manifest_artifacts_checked": 603']
    stale_scan_paths = [
        manifest_path,
        readiness_path,
        AUDIT_DIR / "top_conference_readiness_audit.md",
        AUDIT_DIR / "claim_evidence_audit.md",
    ]
    stale_hits = {}
    for path in stale_scan_paths:
        text = path.read_text(encoding="utf-8")
        hits = [token for token in stale_tokens if token in text]
        if hits:
            stale_hits[_rel(path)] = hits
    if stale_hits:
        errors.append(f"stale clean-clone or manifest-count tokens found: {stale_hits}")

    text_checks = {
        _rel(focused_en): _contains(focused_en, ["+0.064", "Candidate-frontier validation"]),
        _rel(readiness_md): _contains(readiness_md, [clean_short, clean_ratio, "+0.064"]),
        _rel(claim_md): _contains(claim_md, [clean_ratio, "candidate-frontier validation"]),
        _rel(objective_md): _contains(objective_md, [head[:9], manifest_ratio, "top-conference empirical target remains incomplete"]),
    }
    for path, checks in text_checks.items():
        for needle, present in checks.items():
            if not present:
                errors.append(f"{path} missing consistency marker: {needle}")

    pdfs = {
        "focused_en": DOC_DIR / "build" / "co_pilot_ai_scientist_v3_focused_en.pdf",
    }
    pdf_bytes = {}
    for name, path in pdfs.items():
        if not path.exists() or path.stat().st_size <= 0:
            errors.append(f"missing or empty PDF: {_rel(path)}")
        else:
            pdf_bytes[name] = path.stat().st_size

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "head": head,
        "clean_clone_audited_commit": audited_commit,
        "clean_clone_commit_is_head": clean_commit_is_head,
        "clean_clone_commit_is_head_ancestor": clean_commit_is_ancestor,
        "git_repository_is_shallow": is_shallow_repository,
        "manifest_artifacts": manifest_count,
        "missing_manifest_artifacts": len(missing),
        "duplicate_manifest_artifacts": len(duplicate_artifacts),
        "candidate_frontier_validation": {
            "scored_count": validation_agg.get("scored_count"),
            "delayed_minus_control_mean_score": validation_agg.get("delayed_minus_control_mean_score"),
            "not_scored_count": validation_agg.get("not_scored_count"),
        },
        "tfr_status": tfr.get("status"),
        "objective_delivery_status": objective.get("status"),
        "pdf_bytes": pdf_bytes,
        "text_checks": text_checks,
        "stale_token_hits": stale_hits,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "This audit checks package consistency, not scientific correctness or "
            "top-conference sufficiency. A pass means the artifact metadata agree."
        ),
    }

    json_path = AUDIT_DIR / "package_consistency_audit.json"
    md_path = AUDIT_DIR / "package_consistency_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Package Consistency Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- HEAD: `{audit['head']}`",
        f"- Clean-clone audited commit: `{audit['clean_clone_audited_commit']}`",
        f"- Clean-clone commit is HEAD ancestor: `{audit['clean_clone_commit_is_head_ancestor']}`",
        f"- Manifest artifacts: `{audit['manifest_artifacts']}`",
        f"- Missing manifest artifacts: `{audit['missing_manifest_artifacts']}`",
        f"- Candidate-frontier scored reviews: `{audit['candidate_frontier_validation']['scored_count']}`",
        f"- Candidate-frontier delayed-control delta: `{audit['candidate_frontier_validation']['delayed_minus_control_mean_score']}`",
        f"- TFR status: `{audit['tfr_status']}`",
        "",
        "## PDF Bytes",
        "",
    ]
    for name, size in pdf_bytes.items():
        lines.append(f"- `{name}`: `{size}`")
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
