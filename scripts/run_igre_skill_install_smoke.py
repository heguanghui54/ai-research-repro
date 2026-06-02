#!/usr/bin/env python3
"""Run an isolated install smoke test for the standalone IGRE skill package."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
RUN_ID = "igre_skill_install_smoke_20260603"
OUT_DIR = DOC_DIR / "experiments" / RUN_ID
RELEASE_DIR = ROOT / "release" / "co-pilot-ai-scientist-v3-skill"
MANIFEST_PATH = DOC_DIR / "repro_manifest.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_release_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
        "cwd": _rel(cwd) if cwd.is_relative_to(ROOT) else str(cwd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _update_manifest(paths: list[Path], summary: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["igre_skill_install_smoke"] = {
        "status": summary["status"],
        "run_id": summary["run_id"],
        "summary": _rel(OUT_DIR / "summary.json"),
        "markdown": _rel(OUT_DIR / "README.md"),
        "claim_boundary": summary["claim_boundary"],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    if not RELEASE_DIR.exists():
        raise SystemExit(f"Release directory missing: {RELEASE_DIR}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    install_root = OUT_DIR / "codex_skills"
    installed_dir = install_root / "co-pilot-ai-scientist-v3"
    if install_root.exists():
        shutil.rmtree(install_root)
    install_root.mkdir(parents=True)

    release_manifest = _load_release_manifest(RELEASE_DIR / "MANIFEST.json")
    env = os.environ.copy()
    env["CODEX_SKILLS_DIR"] = str(install_root)
    install_result = _run(["bash", "scripts/install_local.sh"], cwd=RELEASE_DIR, env=env)

    errors: list[str] = []
    warnings: list[str] = []
    if install_result["returncode"] != 0:
        errors.append("install script returned non-zero status")
    if not installed_dir.exists():
        errors.append("installed skill directory is missing")

    checked_files: list[str] = []
    for rel in release_manifest.get("required_files", []):
        path = installed_dir / rel
        checked_files.append(str(path.relative_to(installed_dir)))
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing or empty installed file: {rel}")

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
            errors.append("installed release validator did not pass")
    else:
        errors.append("installed validator script is missing")

    skill_text = _read(installed_dir / "SKILL.md") if (installed_dir / "SKILL.md").exists() else ""
    if "name: co-pilot-ai-scientist-v3" not in skill_text:
        errors.append("installed SKILL.md missing expected skill name")
    for gate in release_manifest.get("gates", []):
        if gate not in skill_text:
            errors.append(f"installed SKILL.md missing gate: {gate}")

    example_gate_path = installed_dir / "examples" / "example_gate_log.json"
    if example_gate_path.exists():
        example_gate = json.loads(example_gate_path.read_text(encoding="utf-8"))
        for field in ["attention_cost", "taste_insight", "human_decision", "rationale"]:
            if field not in example_gate:
                errors.append(f"installed example gate missing field: {field}")
    else:
        errors.append("installed example gate log missing")

    summary = {
        "run_id": RUN_ID,
        "created_at": _utc_now(),
        "status": "pass" if not errors else "fail",
        "release_dir": _rel(RELEASE_DIR),
        "install_root": _rel(install_root),
        "installed_dir": _rel(installed_dir),
        "required_files_checked": len(checked_files),
        "checked_files": checked_files,
        "install_result": install_result,
        "validator_result": validator_result,
        "validator_run": validator_run,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "This smoke test verifies isolated local installability and release "
            "self-validation for the IGRE skill. It is engineering evidence, not "
            "scientific evidence that IGRE improves automated research outcomes."
        ),
    }

    summary_path = OUT_DIR / "summary.json"
    readme_path = OUT_DIR / "README.md"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# IGRE Skill Install Smoke Test",
        "",
        f"- Run id: `{RUN_ID}`",
        f"- Created at: `{summary['created_at']}`",
        f"- Status: `{summary['status']}`",
        f"- Release dir: `{summary['release_dir']}`",
        f"- Install root: `{summary['install_root']}`",
        f"- Installed dir: `{summary['installed_dir']}`",
        f"- Required files checked: `{summary['required_files_checked']}`",
        f"- Installed validator status: `{(validator_result or {}).get('status')}`",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
            "",
        ]
    )
    readme_path.write_text("\n".join(lines), encoding="utf-8")

    if args.update_manifest:
        _update_manifest([Path(__file__), summary_path, readme_path], summary)

    print(json.dumps({"summary": _rel(summary_path), "markdown": _rel(readme_path), "status": summary["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
