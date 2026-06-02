#!/usr/bin/env python3
"""Audit the end-to-end engineering chain for the global IGRE skill.

This audit intentionally separates engineering reuse evidence from scientific
validity evidence. A pass means the standalone release can be validated,
installed in isolation, installed globally, reused on a fresh task, copied into
a clean external temporary workspace, and tied to one executable toy
evaluator-stress smoke. It does not imply that the method improves paper
quality or outperforms autonomous AI Scientist-v2.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
MANIFEST_PATH = DOC_DIR / "repro_manifest.json"
RELEASE_DIR = ROOT / "release" / "co-pilot-ai-scientist-v3-skill"
GLOBAL_SKILL_DIR = Path.home() / ".codex" / "skills" / "co-pilot-ai-scientist-v3"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _contains(path: Path, needles: list[str]) -> dict[str, bool]:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    return {needle: needle in text for needle in needles}


def _file_ok(path: Path, min_bytes: int = 1) -> bool:
    return path.exists() and path.stat().st_size >= min_bytes


def _update_manifest(paths: list[Path], audit: dict[str, Any]) -> None:
    manifest = _load_json(MANIFEST_PATH)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["global_skill_engineering_chain_audit"] = {
        "status": audit["status"],
        "json": _rel(paths[0]),
        "markdown": _rel(paths[1]),
        "steps_passed": audit["steps_passed"],
        "steps_checked": audit["steps_checked"],
        "claim_boundary": audit["claim_boundary"],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    release_manifest_path = RELEASE_DIR / "MANIFEST.json"
    release_audit_path = AUDIT_DIR / "igre_skill_release_package_audit.json"
    isolated_install_path = DOC_DIR / "experiments" / "igre_skill_install_smoke_20260603" / "summary.json"
    global_install_path = AUDIT_DIR / "global_copilot_skill_install_audit.json"
    global_reuse_path = DOC_DIR / "experiments" / "global_skill_reuse_smoke_20260603" / "summary.json"
    external_clean_reuse_path = (
        DOC_DIR / "experiments" / "external_clean_skill_reuse_smoke_20260603" / "summary.json"
    )
    evaluator_path = DOC_DIR / "experiments" / "global_skill_metric_gaming_evaluator_20260603" / "summary.json"

    errors: list[str] = []
    warnings: list[str] = []
    required_paths = [
        release_manifest_path,
        release_audit_path,
        isolated_install_path,
        global_install_path,
        global_reuse_path,
        external_clean_reuse_path,
        evaluator_path,
        RELEASE_DIR / "MIGRATION.md",
        RELEASE_DIR / "SKILL.md",
        RELEASE_DIR / "scripts" / "install_local.sh",
        GLOBAL_SKILL_DIR / "SKILL.md",
        GLOBAL_SKILL_DIR / "MIGRATION.md",
    ]
    for path in required_paths:
        if not _file_ok(path):
            errors.append(f"missing or empty engineering-chain artifact: {_rel(path)}")

    release_manifest = _load_json(release_manifest_path) if release_manifest_path.exists() else {}
    release_audit = _load_json(release_audit_path) if release_audit_path.exists() else {}
    isolated_install = _load_json(isolated_install_path) if isolated_install_path.exists() else {}
    global_install = _load_json(global_install_path) if global_install_path.exists() else {}
    global_reuse = _load_json(global_reuse_path) if global_reuse_path.exists() else {}
    external_clean_reuse = _load_json(external_clean_reuse_path) if external_clean_reuse_path.exists() else {}
    evaluator = _load_json(evaluator_path) if evaluator_path.exists() else {}

    release_required_files = release_manifest.get("required_files", [])
    release_required_file_checks: dict[str, bool] = {}
    for rel in release_required_files:
        release_required_file_checks[rel] = _file_ok(RELEASE_DIR / rel)
    missing_release_files = [rel for rel, ok in release_required_file_checks.items() if not ok]
    if missing_release_files:
        errors.append(f"release manifest required files missing: {missing_release_files}")

    global_required_file_checks: dict[str, bool] = {}
    for rel in release_required_files:
        global_required_file_checks[rel] = _file_ok(GLOBAL_SKILL_DIR / rel)
    missing_global_files = [rel for rel, ok in global_required_file_checks.items() if not ok]
    if missing_global_files:
        errors.append(f"global installed skill missing release-required files: {missing_global_files}")

    lineage_checks = {
        _rel(RELEASE_DIR / "SKILL.md"): _contains(
            RELEASE_DIR / "SKILL.md",
            ["ai-scientist-v2", "Base Skill Relationship", "evaluator_stress_test", "claim_calibration"],
        ),
        _rel(RELEASE_DIR / "MIGRATION.md"): _contains(
            RELEASE_DIR / "MIGRATION.md",
            ["Migrating From `ai-scientist-v2`", "scientific_taste_prior", "verifiable_micro_evolution"],
        ),
        _rel(GLOBAL_SKILL_DIR / "SKILL.md"): _contains(
            GLOBAL_SKILL_DIR / "SKILL.md",
            ["ai-scientist-v2", "Base Skill Relationship", "evaluator_stress_test", "claim_calibration"],
        ),
        _rel(GLOBAL_SKILL_DIR / "MIGRATION.md"): _contains(
            GLOBAL_SKILL_DIR / "MIGRATION.md",
            ["Migrating From `ai-scientist-v2`", "scientific_taste_prior", "verifiable_micro_evolution"],
        ),
    }
    for path, checks in lineage_checks.items():
        missing = [term for term, present in checks.items() if not present]
        if missing:
            errors.append(f"{path} missing lineage/control terms: {missing}")

    steps = {
        "standalone_release_scaffold": release_manifest.get("status")
        in {"standalone_release_scaffold", "release_ready", "pass"}
        and release_audit.get("status") == "pass"
        and len(release_required_files) >= 10
        and not missing_release_files,
        "isolated_install_smoke": isolated_install.get("status") == "pass"
        and isolated_install.get("required_files_checked") == len(release_required_files)
        and not isolated_install.get("errors"),
        "global_install_audit": global_install.get("status") == "pass"
        and global_install.get("base_skill_lineage_checked") is True
        and not missing_global_files,
        "global_reuse_smoke": global_reuse.get("status") == "pass"
        and global_reuse.get("generated_from_global_install") is True
        and global_reuse.get("base_skill_lineage_checked") is True,
        "external_clean_reuse_smoke": external_clean_reuse.get("status") == "pass"
        and external_clean_reuse.get("generated_from_release_copy") is True
        and external_clean_reuse.get("generated_from_global_install") is False
        and external_clean_reuse.get("clean_external_environment") is True
        and external_clean_reuse.get("all_six_gates_present") is True
        and external_clean_reuse.get("six_gate_count") == 6,
        "toy_evaluator_stress_link": evaluator.get("status") == "pass"
        and evaluator.get("source_global_skill_reuse_smoke") == _rel(global_reuse_path)
        and evaluator.get("source_generated_from_global_install") is True
        and evaluator.get("source_gate_decision") == "guarded_evaluator"
        and evaluator.get("metric_gaming_incidents_reduced") == 1,
    }
    for step, ok in steps.items():
        if not ok:
            errors.append(f"engineering-chain step failed: {step}")

    if evaluator.get("primary_only_winner") != "metric_gaming_all_negative":
        warnings.append("toy evaluator primary-only winner changed; inspect the metric-gaming fixture")
    if evaluator.get("evaluator_stress_winner") != "guardrailed_utility_model":
        warnings.append("toy evaluator guarded winner changed; inspect the evaluator-stress fixture")

    claim_boundary = (
        "This audit verifies the engineering chain from standalone release scaffold "
        "through isolated install, global install, fresh global-skill reuse, clean "
        "external temporary reuse, and one toy evaluator-stress smoke. It is "
        "usability and reproducibility evidence, not independent human evidence, "
        "not an official benchmark result, and not proof that Co-Pilot AI Scientist "
        "v3 outperforms autonomous AI Scientist-v2."
    )
    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "steps": steps,
        "steps_checked": len(steps),
        "steps_passed": sum(1 for ok in steps.values() if ok),
        "release_required_files": release_required_files,
        "release_required_file_checks": release_required_file_checks,
        "global_required_file_checks": global_required_file_checks,
        "lineage_checks": lineage_checks,
        "source_artifacts": {
            "release_manifest": _rel(release_manifest_path),
            "release_audit": _rel(release_audit_path),
            "isolated_install_smoke": _rel(isolated_install_path),
            "global_install_audit": _rel(global_install_path),
            "global_reuse_smoke": _rel(global_reuse_path),
            "external_clean_reuse_smoke": _rel(external_clean_reuse_path),
            "toy_evaluator_stress": _rel(evaluator_path),
        },
        "external_clean_reuse_summary": {
            "external_root": external_clean_reuse.get("external_root"),
            "fresh_topic": external_clean_reuse.get("fresh_topic"),
            "six_gate_count": external_clean_reuse.get("six_gate_count"),
            "all_six_gates_present": external_clean_reuse.get("all_six_gates_present"),
        },
        "toy_evaluator_summary": {
            "primary_only_winner": evaluator.get("primary_only_winner"),
            "evaluator_stress_winner": evaluator.get("evaluator_stress_winner"),
            "metric_gaming_incidents_reduced": evaluator.get("metric_gaming_incidents_reduced"),
        },
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": claim_boundary,
    }

    json_path = AUDIT_DIR / "global_skill_engineering_chain_audit.json"
    md_path = AUDIT_DIR / "global_skill_engineering_chain_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Global Skill Engineering Chain Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Steps passed: `{audit['steps_passed']}/{audit['steps_checked']}`",
        "",
        "## Steps",
        "",
    ]
    for step, ok in steps.items():
        lines.append(f"- `{step}`: `{'pass' if ok else 'fail'}`")
    lines.extend(
        [
            "",
            "## Toy Evaluator Link",
            "",
            f"- Primary-only winner: `{audit['toy_evaluator_summary']['primary_only_winner']}`",
            f"- Evaluator-stress winner: `{audit['toy_evaluator_summary']['evaluator_stress_winner']}`",
            f"- Metric-gaming incidents reduced: `{audit['toy_evaluator_summary']['metric_gaming_incidents_reduced']}`",
            "",
            "## External Clean Reuse",
            "",
            f"- External root: `{audit['external_clean_reuse_summary']['external_root']}`",
            f"- Fresh topic: `{audit['external_clean_reuse_summary']['fresh_topic']}`",
            f"- Six gates present: `{audit['external_clean_reuse_summary']['all_six_gates_present']}`",
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for name, path in audit["source_artifacts"].items():
        lines.append(f"- `{name}`: `{path}`")
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", claim_boundary, ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    if args.update_manifest:
        _update_manifest([json_path, md_path, Path(__file__)], audit)

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
