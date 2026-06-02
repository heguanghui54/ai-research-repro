#!/usr/bin/env python3
"""Install the Co-Pilot AI Scientist v3 skill into ~/.codex/skills and audit it."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
RELEASE_DIR = ROOT / "release" / "co-pilot-ai-scientist-v3-skill"
MANIFEST_PATH = DOC_DIR / "repro_manifest.json"
DEFAULT_SKILLS_DIR = Path.home() / ".codex" / "skills"
SKILL_NAME = "co-pilot-ai-scientist-v3"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "cmd": cmd,
        "cwd": _rel(cwd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _update_manifest(paths: list[Path], audit: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["global_copilot_skill_install"] = {
        "status": audit["status"],
        "skill_dir": audit["installed_dir"],
        "json": _rel(paths[0]),
        "markdown": _rel(paths[1]),
        "base_skill_lineage_checked": audit["base_skill_lineage_checked"],
        "claim_boundary": audit["claim_boundary"],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skills-dir", default=str(DEFAULT_SKILLS_DIR))
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    skills_dir = Path(args.skills_dir).expanduser().resolve()
    installed_dir = skills_dir / SKILL_NAME
    release_manifest = json.loads((RELEASE_DIR / "MANIFEST.json").read_text(encoding="utf-8"))

    env = os.environ.copy()
    env["CODEX_SKILLS_DIR"] = str(skills_dir)
    install_result = _run(["bash", "scripts/install_local.sh"], cwd=RELEASE_DIR, env=env)

    errors: list[str] = []
    warnings: list[str] = []
    if install_result["returncode"] != 0:
        errors.append("global install script returned non-zero status")
    if not installed_dir.exists():
        errors.append("installed global skill directory is missing")

    checked_files: list[str] = []
    for rel in release_manifest.get("required_files", []):
        path = installed_dir / rel
        checked_files.append(rel)
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing or empty installed global skill file: {rel}")

    validator_result = None
    validator_run = None
    validator_path = installed_dir / "scripts" / "validate_release.py"
    if validator_path.exists():
        validator_run = _run([sys.executable, "scripts/validate_release.py"], cwd=installed_dir)
        try:
            validator_result = json.loads(validator_run["stdout"])
        except json.JSONDecodeError:
            validator_result = {
                "status": "non_json",
                "stdout": validator_run["stdout"][:2000],
                "stderr": validator_run["stderr"][:2000],
            }
        if validator_run["returncode"] != 0 or validator_result.get("status") != "pass":
            errors.append("installed global skill validator did not pass")
    else:
        errors.append("installed global skill validator is missing")

    skill_text = (installed_dir / "SKILL.md").read_text(encoding="utf-8") if (installed_dir / "SKILL.md").exists() else ""
    migration_text = (installed_dir / "MIGRATION.md").read_text(encoding="utf-8") if (installed_dir / "MIGRATION.md").exists() else ""
    base_terms = [
        "ai-scientist-v2",
        "Base Skill Relationship",
        "AI Scientist-v2 research-production loop",
        "Migrating From `ai-scientist-v2` To Co-Pilot AI Scientist v3",
    ]
    base_skill_lineage_checked = all(term in f"{skill_text}\n{migration_text}" for term in base_terms)
    if not base_skill_lineage_checked:
        errors.append("installed global skill is missing ai-scientist-v2 lineage terms")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "skills_dir": str(skills_dir),
        "installed_dir": str(installed_dir),
        "release_dir": _rel(RELEASE_DIR),
        "required_files_checked": len(checked_files),
        "checked_files": checked_files,
        "install_result": install_result,
        "validator_result": validator_result,
        "validator_run": validator_run,
        "base_skill_lineage_checked": base_skill_lineage_checked,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "This audit verifies that Co-Pilot AI Scientist v3 is installed as a "
            "global reusable Codex skill derived from the release package. It is "
            "engineering reuse evidence, not scientific superiority evidence."
        ),
    }

    json_path = AUDIT_DIR / "global_copilot_skill_install_audit.json"
    md_path = AUDIT_DIR / "global_copilot_skill_install_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Global Co-Pilot AI Scientist v3 Skill Install Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Skills dir: `{audit['skills_dir']}`",
        f"- Installed dir: `{audit['installed_dir']}`",
        f"- Required files checked: `{audit['required_files_checked']}`",
        f"- Installed validator status: `{(validator_result or {}).get('status')}`",
        f"- Base skill lineage checked: `{audit['base_skill_lineage_checked']}`",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    if args.update_manifest:
        _update_manifest([json_path, md_path, Path(__file__)], audit)

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
