#!/usr/bin/env python3
"""Audit the standalone IGRE skill release scaffold."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
RELEASE_DIR = ROOT / "release" / "co-pilot-ai-scientist-v3-skill"
INSTALL_SMOKE_SUMMARY = (
    DOC_DIR / "experiments" / "igre_skill_install_smoke_20260603" / "summary.json"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = RELEASE_DIR / "MANIFEST.json"
    if not manifest_path.exists():
        errors.append("release MANIFEST.json is missing")
        manifest = {"required_files": [], "gates": []}
    else:
        manifest = _load_json(manifest_path)

    checked_files = []
    for rel in manifest.get("required_files", []):
        path = RELEASE_DIR / rel
        checked_files.append(_rel(path))
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing or empty release file: {rel}")

    validator_result = None
    if (RELEASE_DIR / "scripts" / "validate_release.py").exists():
        proc = subprocess.run(
            [sys.executable, "scripts/validate_release.py"],
            cwd=RELEASE_DIR,
            text=True,
            capture_output=True,
            check=False,
        )
        try:
            validator_result = json.loads(proc.stdout)
        except json.JSONDecodeError:
            validator_result = {"status": "non_json", "stdout": proc.stdout[:2000], "stderr": proc.stderr[:2000]}
        if proc.returncode != 0 or validator_result.get("status") != "pass":
            errors.append("standalone release validator did not pass")
    else:
        errors.append("standalone release validator missing")

    readme = _read(RELEASE_DIR / "README.md") if (RELEASE_DIR / "README.md").exists() else ""
    release_positioning = _read(RELEASE_DIR / "POSITIONING.md") if (RELEASE_DIR / "POSITIONING.md").exists() else ""
    release_contributing = _read(RELEASE_DIR / "CONTRIBUTING.md") if (RELEASE_DIR / "CONTRIBUTING.md").exists() else ""
    release_notes = _read(RELEASE_DIR / "RELEASE_NOTES.md") if (RELEASE_DIR / "RELEASE_NOTES.md").exists() else ""
    strategy = _read(DOC_DIR / "skill_engineering_release_strategy.md")
    root_readme = _read(ROOT / "README.md")
    project_readme = _read(DOC_DIR / "README.md")
    roadmap = _read(DOC_DIR / "top_conference_evidence_roadmap.md")

    required_positioning = [
        "six-gate",
        "not scientific superiority",
        "matched benchmarks",
        "blind expert review",
        "academic-research-skills",
        "PaperOrchestra",
        "Engineering adoption is not scientific superiority",
        "Do not add fabricated benchmark numbers",
        "model-only reviews",
    ]
    positioning_blob = "\n".join(
        [
            readme,
            release_positioning,
            release_contributing,
            release_notes,
            strategy,
            root_readme,
            project_readme,
            roadmap,
        ]
    )
    for term in required_positioning:
        if term not in positioning_blob:
            errors.append(f"release positioning missing term: {term}")

    if "Engineering adoption can support the systems story" not in project_readme:
        errors.append("project README missing two-track engineering/science boundary")
    if "does not replace blind expert review or matched benchmark evidence" not in roadmap:
        errors.append("roadmap missing engineering-adoption boundary")

    install_script = RELEASE_DIR / "scripts" / "install_local.sh"
    if not install_script.exists():
        errors.append("local install script missing")
    else:
        install_text = _read(install_script)
        if "CODEX_SKILLS_DIR" not in install_text or ".codex/skills" not in install_text:
            errors.append("install script does not target Codex skills directory")

    install_smoke_result = None
    if INSTALL_SMOKE_SUMMARY.exists():
        install_smoke_result = _load_json(INSTALL_SMOKE_SUMMARY)
        if install_smoke_result.get("status") != "pass":
            errors.append("isolated install smoke test did not pass")
        if "not scientific evidence" not in install_smoke_result.get("claim_boundary", ""):
            errors.append("install smoke test missing engineering/science claim boundary")
    else:
        errors.append("isolated install smoke test summary is missing")

    publication_files = [
        "POSITIONING.md",
        "CONTRIBUTING.md",
        "LICENSE",
        "RELEASE_NOTES.md",
    ]
    for rel in publication_files:
        if not (RELEASE_DIR / rel).exists():
            errors.append(f"publication file missing: {rel}")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "release_dir": _rel(RELEASE_DIR),
        "required_files_checked": len(checked_files),
        "checked_files": checked_files,
        "validator_result": validator_result,
        "engineering_track_status": "standalone_release_scaffold_prepared",
        "publication_files_checked": publication_files,
        "install_script": _rel(install_script),
        "install_smoke_status": (install_smoke_result or {}).get("status"),
        "install_smoke_summary": _rel(INSTALL_SMOKE_SUMMARY),
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "This audit verifies engineering release readiness for a standalone "
            "skill scaffold. It is not scientific evidence that IGRE improves "
            "automated research outcomes."
        ),
    }

    json_path = AUDIT_DIR / "igre_skill_release_package_audit.json"
    md_path = AUDIT_DIR / "igre_skill_release_package_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# IGRE Skill Release Package Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Release dir: `{audit['release_dir']}`",
        f"- Required files checked: `{audit['required_files_checked']}`",
        f"- Engineering track status: `{audit['engineering_track_status']}`",
        f"- Standalone validator status: `{(validator_result or {}).get('status')}`",
        f"- Install smoke status: `{audit['install_smoke_status']}`",
        "",
        "## Errors",
        "",
    ]
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
