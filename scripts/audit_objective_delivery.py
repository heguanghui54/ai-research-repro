#!/usr/bin/env python3
"""Audit explicit objective-level deliverables for Co-Pilot AI Scientist v3.

This is not a scientific-validity audit. It checks whether the concrete
deliverables requested in the project objective exist and whether the package
still marks top-conference empirical support as incomplete when evidence is
insufficient.
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


def _file_status(path: Path, *, min_bytes: int = 1) -> dict[str, Any]:
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    return {
        "path": _rel(path),
        "exists": exists,
        "bytes": size,
        "ok": exists and size >= min_bytes,
    }


def _contains(path: Path, needles: list[str]) -> dict[str, bool]:
    text = _read(path)
    return {needle: needle in text for needle in needles}


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    branch = _git(["branch", "--show-current"])
    head = _git(["rev-parse", "HEAD"])
    remote_url = _git(["remote", "get-url", "origin"])

    manifest_path = DOC_DIR / "repro_manifest.json"
    readiness_path = AUDIT_DIR / "top_conference_readiness_audit.json"
    claim_path = AUDIT_DIR / "claim_evidence_audit.json"
    lhtg_path = AUDIT_DIR / "lhtg_dvrs_audit.json"
    prospective_path = AUDIT_DIR / "prospective_matched_budget_package_audit.json"
    package_path = AUDIT_DIR / "package_consistency_audit.json"
    focused_review_path = AUDIT_DIR / "focused_paper_quality_review_summary.json"
    roadmap_audit_path = AUDIT_DIR / "top_conference_evidence_roadmap_audit.json"

    manifest = _load_json(manifest_path)
    readiness = _load_json(readiness_path)
    claim = _load_json(claim_path)
    lhtg = _load_json(lhtg_path)
    prospective = _load_json(prospective_path)
    package = _load_json(package_path)
    focused_review = _load_json(focused_review_path)
    roadmap_audit = _load_json(roadmap_audit_path)

    current_artifacts = manifest.get("current_artifacts", [])
    missing_manifest = [path for path in current_artifacts if not (ROOT / path).exists()]

    pdfs = {
        "english_pdf": DOC_DIR / "build" / "co_pilot_ai_scientist_v3_en.pdf",
        "chinese_pdf": DOC_DIR / "build" / "co_pilot_ai_scientist_v3_zh.pdf",
        "focused_english_pdf": DOC_DIR / "build" / "co_pilot_ai_scientist_v3_focused_en.pdf",
        "focused_chinese_pdf": DOC_DIR / "build" / "co_pilot_ai_scientist_v3_focused_zh.pdf",
    }
    docs = {
        "root_readme": ROOT / "README.md",
        "english_submission_card": DOC_DIR / "submission_card_en.md",
        "chinese_submission_card": DOC_DIR / "submission_card_zh.md",
        "top_conference_evidence_roadmap": DOC_DIR / "top_conference_evidence_roadmap.md",
        "top_conference_evidence_roadmap_json": DOC_DIR / "top_conference_evidence_roadmap.json",
        "english_usage": DOC_DIR / "usage_en.md",
        "chinese_usage": DOC_DIR / "usage_zh.md",
        "english_runbook": DOC_DIR / "RUNBOOK_EN.md",
        "chinese_runbook": DOC_DIR / "RUNBOOK_ZH.md",
        "reusable_skill": ROOT / "skills" / "co-pilot-ai-scientist-v3" / "SKILL.md",
        "task_template": ROOT / "skills" / "co-pilot-ai-scientist-v3" / "templates" / "task_spec_template.md",
        "gate_template": ROOT / "skills" / "co-pilot-ai-scientist-v3" / "templates" / "human_gate_log_template.json",
    }

    paper_checks = {
        _rel(DOC_DIR / "paper_en_focused.md"): _contains(
            DOC_DIR / "paper_en_focused.md",
            [
                "Insight-Gated Research Evolution",
                "AI Scientist-v2",
                "AI Co-Scientist",
                "OpenEvolve",
                "Long-Horizon Taste Gate",
                "We do not claim",
            ],
        ),
        _rel(DOC_DIR / "paper_zh_focused.md"): _contains(
            DOC_DIR / "paper_zh_focused.md",
            [
                "Insight-Gated Research Evolution",
                "AI Scientist-v2",
                "AI Co-Scientist",
                "OpenEvolve",
                "长期科研品味门控",
                "不能",
            ],
        ),
    }

    skill_checks = {
        _rel(docs["root_readme"]): _contains(
            docs["root_readme"],
            [
                "Co-Pilot AI Scientist v3",
                "submission_card_en.md",
                "submission_card_zh.md",
                "top_conference_evidence_roadmap.md",
                "External Verification Entry Point",
                "audit_top_conference_evidence_roadmap.py",
                "pass_artifact_delivery_with_empirical_gaps",
                "top-conference empirical target is not yet satisfied",
            ],
        ),
        _rel(docs["english_submission_card"]): _contains(
            docs["english_submission_card"],
            [
                "Insight-Gated Research Evolution",
                "Long-Horizon Taste Gate",
                "Delayed-Value Review Signal",
                "AI Scientist-v2",
                "AI Co-Scientist",
                "OpenEvolve",
                "Do not claim",
                "External Verification",
            ],
        ),
        _rel(docs["chinese_submission_card"]): _contains(
            docs["chinese_submission_card"],
            [
                "Insight-Gated Research Evolution",
                "长期科研品味门控",
                "延迟价值评议信号",
                "AI Scientist-v2",
                "AI Co-Scientist",
                "OpenEvolve",
                "不能声称",
                "外部复现入口",
            ],
        ),
        _rel(docs["top_conference_evidence_roadmap"]): _contains(
            docs["top_conference_evidence_roadmap"],
            [
                "Blind Human Expert Review",
                "Matched Autonomous Versus Human-Gated Runs",
                "Long-Horizon Taste Gate",
                "Live Multi-Researcher Co-Pilot Trace Data",
                "Non-FML Official Benchmark Check",
                "not empirical superiority over autonomous AI Scientist-v2",
            ],
        ),
        _rel(docs["reusable_skill"]): _contains(
            docs["reusable_skill"],
            [
                "AI Scientist-v2",
                "AI Co-Scientist",
                "OpenEvolve",
                "Long-Horizon Taste Gate",
                "human",
            ],
        )
    }

    explicit_requirements = {
        "bilingual_pdfs": all(_file_status(path, min_bytes=1_000)["ok"] for path in pdfs.values()),
        "bilingual_usage": all(_file_status(path, min_bytes=100)["ok"] for path in docs.values()),
        "reusable_codex_skill": _file_status(docs["reusable_skill"], min_bytes=100)["ok"],
        "github_branch_pushed": _remote_contains_branch("origin", branch),
        "author_recorded": manifest.get("author") == "He Shi, School of Computing, National University of Singapore",
        "manifest_complete": len(current_artifacts) > 0 and not missing_manifest,
        "package_consistency_pass": package.get("status") == "pass",
        "prospective_package_audit_pass": prospective.get("overall_status") == "pass",
        "top_conference_roadmap_audit_pass": roadmap_audit.get("status") == "pass",
        "lhtg_operationalized": lhtg.get("status") == "pass_with_no_positive_dvrs"
        and lhtg.get("reusable_workflow_terms_present") is True,
        "top_conference_boundary_kept": readiness.get("top_conference_empirical_support", {}).get("status")
        == "not_supported_yet",
        "unsupported_superiority_claims_kept_unsupported": "outperforms autonomous AI Scientist-v2"
        in json.dumps(readiness.get("unsupported_performance_requirements", []), ensure_ascii=False)
        or "full co-pilot v3 system outperforms" in json.dumps(manifest.get("unverified_claims", []), ensure_ascii=False),
    }

    missing_text_terms = []
    for path, checks in {**paper_checks, **skill_checks}.items():
        for term, present in checks.items():
            if not present:
                missing_text_terms.append(f"{path}: {term}")

    errors: list[str] = []
    warnings: list[str] = []
    for name, ok in explicit_requirements.items():
        if not ok:
            errors.append(f"objective requirement failed: {name}")
    if missing_manifest:
        errors.append(f"manifest has missing artifacts: {len(missing_manifest)}")
    if missing_text_terms:
        errors.append(f"missing required method/boundary terms: {missing_text_terms}")
    if lhtg.get("delayed_value_positive_cases") != 0:
        warnings.append("LHTG positive delayed-value case count changed; update claim boundary manually")
    if len(focused_review.get("successful_reviews", {})) < 1:
        warnings.append("focused paper quality review has no successful model reviews")

    artifact_status = {name: _file_status(path, min_bytes=1_000 if name.endswith("pdf") else 100) for name, path in {**pdfs, **docs}.items()}

    audit = {
        "audit_date": _utc_now(),
        "status": "pass_artifact_delivery_with_empirical_gaps" if not errors else "fail",
        "head": head,
        "branch": branch,
        "remote_url": remote_url,
        "explicit_requirements": explicit_requirements,
        "artifact_status": artifact_status,
        "paper_checks": paper_checks,
        "skill_checks": skill_checks,
        "manifest_artifacts": len(current_artifacts),
        "missing_manifest_artifacts": len(missing_manifest),
        "manifest_coverage_ratio": f"{len(current_artifacts) - len(missing_manifest)}/{len(current_artifacts)}",
        "top_conference_empirical_support_status": readiness.get("top_conference_empirical_support", {}).get("status"),
        "unverified_claims": manifest.get("unverified_claims", []),
        "next_required_evidence": manifest.get("next_required_evidence", []),
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "The requested artifact pipeline is delivered and auditable, but the original "
            "top-conference empirical target remains incomplete until independent human "
            "ratings, larger matched benchmark runs, and broader end-to-end trajectories "
            "are collected."
        ),
    }

    json_path = AUDIT_DIR / "objective_delivery_audit.json"
    md_path = AUDIT_DIR / "objective_delivery_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Objective Delivery Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- HEAD: `{head}`",
        f"- Branch: `{branch}`",
        f"- Remote: `{remote_url}`",
        f"- Manifest artifacts: `{audit['manifest_artifacts']}`",
        f"- Missing manifest artifacts: `{audit['missing_manifest_artifacts']}`",
        f"- Manifest coverage: `{audit['manifest_coverage_ratio']}`",
        "",
        "## Explicit Requirements",
        "",
    ]
    for name, ok in explicit_requirements.items():
        lines.append(f"- `{name}`: `{'pass' if ok else 'fail'}`")
    lines.extend(["", "## Artifact Status", ""])
    for name, status in artifact_status.items():
        lines.append(f"- `{name}`: `{'pass' if status['ok'] else 'fail'}` ({status['bytes']} bytes) - `{status['path']}`")
    lines.extend(["", "## Remaining Evidence Gap", ""])
    for item in audit["next_required_evidence"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    manifest["objective_delivery_audit"] = {
        "status": audit["status"],
        "json": _rel(json_path),
        "markdown": _rel(md_path),
        "head": head,
        "branch": branch,
        "manifest_artifacts": len(current_artifacts),
        "missing_manifest_artifacts": len(missing_manifest),
        "claim_boundary": audit["claim_boundary"],
    }
    for path in [
        json_path,
        md_path,
        Path(__file__),
        ROOT / "scripts" / "audit_top_conference_evidence_roadmap.py",
        AUDIT_DIR / "top_conference_evidence_roadmap_audit.json",
        AUDIT_DIR / "top_conference_evidence_roadmap_audit.md",
        docs["root_readme"],
        docs["english_submission_card"],
        docs["chinese_submission_card"],
        docs["top_conference_evidence_roadmap"],
        docs["top_conference_evidence_roadmap_json"],
    ]:
        rel = _rel(path)
        if rel not in manifest["current_artifacts"]:
            manifest["current_artifacts"].append(rel)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
