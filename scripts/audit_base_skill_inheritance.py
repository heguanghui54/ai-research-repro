#!/usr/bin/env python3
"""Audit that Co-Pilot AI Scientist v3 inherits the user's AI Scientist-v2 loop.

This is an engineering and method-positioning audit. It checks that the v3
skill is not merely an unrelated six-gate prompt: the release, repository skill,
global installed skill, and migration guide must preserve the base
AI Scientist-v2 research-production loop and then add IGRE control gates.
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

BASE_SKILL = Path.home() / ".codex" / "skills" / "ai-scientist-v2" / "SKILL.md"
REPO_SKILL = ROOT / "skills" / "co-pilot-ai-scientist-v3" / "SKILL.md"
RELEASE_SKILL = ROOT / "release" / "co-pilot-ai-scientist-v3-skill" / "SKILL.md"
RELEASE_MIGRATION = ROOT / "release" / "co-pilot-ai-scientist-v3-skill" / "MIGRATION.md"
RELEASE_README = ROOT / "release" / "co-pilot-ai-scientist-v3-skill" / "README.md"
GLOBAL_SKILL = Path.home() / ".codex" / "skills" / "co-pilot-ai-scientist-v3" / "SKILL.md"
GLOBAL_MIGRATION = Path.home() / ".codex" / "skills" / "co-pilot-ai-scientist-v3" / "MIGRATION.md"


BASE_LOOP_STEPS = {
    "frame_problem": ["Frame The Research Problem", "concrete question"],
    "generate_candidates": ["Generate Multiple Candidate Ideas", "candidate"],
    "literature_novelty": ["Search Literature", "Remove Duplicates"],
    "benchmark_discovery": ["Discover Benchmarks", "Evaluation Targets"],
    "experiment_design": ["Design The Experiments", "baseline", "ablation"],
    "run_score_candidates": ["Run And Score Candidates", "Track logs"],
    "write_paper": ["Write The Paper", "standard paper"],
    "review_revise": ["Review And Revise", "claims"],
}

MIGRATION_STEP_LABELS = {
    "frame_problem": "Frame the research problem",
    "generate_candidates": "Generate multiple candidate ideas",
    "literature_novelty": "Search literature and remove duplicates",
    "benchmark_discovery": "Discover benchmarks and evaluation targets",
    "experiment_design": "Design experiments",
    "run_score_candidates": "Run and score candidates",
    "write_paper": "Write the paper",
    "review_revise": "Review and revise",
}

IGRE_GATES = [
    "scientific_taste_prior",
    "evaluator_stress_test",
    "frontier_steering",
    "verifiable_micro_evolution",
    "structured_feedback",
    "claim_calibration",
]

BASE_NON_NEGOTIABLES = [
    "Do not invent results",
    "Prefer narrow, defensible claims",
    "Run multiple candidate directions",
    "Make the final paper match the experiment log",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _contains_all(text: str, needles: list[str]) -> dict[str, bool]:
    lower_text = " ".join(text.lower().split())
    return {needle: " ".join(needle.lower().split()) in lower_text for needle in needles}


def _step_presence(text: str, required: dict[str, list[str]]) -> dict[str, dict[str, bool]]:
    return {step: _contains_all(text, needles) for step, needles in required.items()}


def _all_present(checks: dict[str, dict[str, bool]]) -> bool:
    return all(all(values.values()) for values in checks.values())


def _update_manifest(paths: list[Path], audit: dict[str, Any]) -> None:
    manifest = _load_json(MANIFEST_PATH)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["base_skill_inheritance_audit"] = {
        "status": audit["status"],
        "json": _rel(paths[0]),
        "markdown": _rel(paths[1]),
        "base_skill": str(BASE_SKILL),
        "base_loop_steps_preserved": audit["base_loop_steps_preserved"],
        "igre_gates_present": audit["igre_gates_present"],
        "claim_boundary": audit["claim_boundary"],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    warnings: list[str] = []

    required_files = [BASE_SKILL, REPO_SKILL, RELEASE_SKILL, RELEASE_MIGRATION, RELEASE_README, GLOBAL_SKILL]
    file_checks = {str(path): path.exists() and path.stat().st_size > 0 for path in required_files}
    for path, ok in file_checks.items():
        if not ok:
            errors.append(f"missing or empty required inheritance file: {path}")

    base_text = _read(BASE_SKILL)
    repo_text = _read(REPO_SKILL)
    release_text = _read(RELEASE_SKILL)
    migration_text = _read(RELEASE_MIGRATION)
    readme_text = _read(RELEASE_README)
    global_text = _read(GLOBAL_SKILL)
    global_migration_text = _read(GLOBAL_MIGRATION)

    base_loop_checks = _step_presence(base_text, BASE_LOOP_STEPS)
    if not _all_present(base_loop_checks):
        errors.append("base ai-scientist-v2 skill does not expose all expected loop markers")

    migration_mapping_checks = {
        step: {
            "base_step_label": label in migration_text,
            "extension_column": "IGRE extension" in migration_text,
            "log_column": "What to log" in migration_text,
        }
        for step, label in MIGRATION_STEP_LABELS.items()
    }
    if not _all_present(migration_mapping_checks):
        errors.append("migration guide does not map all AI Scientist-v2 steps into IGRE controls")

    skill_lineage_checks = {
        "repo_skill": _contains_all(
            repo_text,
            ["Base Skill Relationship", "ai-scientist-v2", "Preserve the base AI Scientist-v2 loop"],
        ),
        "release_skill": _contains_all(
            release_text,
            ["Base Skill Relationship", "ai-scientist-v2", "Preserve the base AI Scientist-v2 loop"],
        ),
        "global_skill": _contains_all(
            global_text,
            ["Base Skill Relationship", "ai-scientist-v2", "Preserve the base AI Scientist-v2 loop"],
        ),
        "release_readme": _contains_all(
            readme_text,
            ["Base Skill Lineage", "AI Scientist-v2-style research loop", "MIGRATION.md"],
        ),
    }
    for name, checks in skill_lineage_checks.items():
        missing = [term for term, present in checks.items() if not present]
        if missing:
            errors.append(f"{name} missing base-skill lineage terms: {missing}")

    gate_checks = {
        "repo_skill": _contains_all(repo_text, IGRE_GATES),
        "release_skill": _contains_all(release_text, IGRE_GATES),
        "global_skill": _contains_all(global_text, IGRE_GATES),
        "release_migration": _contains_all(migration_text, IGRE_GATES),
    }
    for name, checks in gate_checks.items():
        missing = [gate for gate, present in checks.items() if not present]
        if missing:
            errors.append(f"{name} missing IGRE gates: {missing}")

    nonnegotiable_checks = {
        "base_skill": _contains_all(base_text, BASE_NON_NEGOTIABLES),
        "release_migration": _contains_all(migration_text, ["do not invent results", "prefer narrow", "make the final paper match"]),
        "repo_skill": _contains_all(repo_text, ["Do not skip", "do not invent results", "make the final paper match"]),
        "global_skill": _contains_all(global_text, ["Do not skip", "do not invent results", "make the final paper match"]),
    }
    for name, checks in nonnegotiable_checks.items():
        missing = [term for term, present in checks.items() if not present]
        if missing:
            errors.append(f"{name} missing base non-negotiable terms: {missing}")

    if GLOBAL_MIGRATION.exists():
        global_migration_checks = _contains_all(
            global_migration_text,
            ["Migrating From `ai-scientist-v2`", "Base Loop Mapping", "scientific_taste_prior"],
        )
    else:
        global_migration_checks = {"global_migration_optional": False}
        warnings.append("global migration guide is absent; global skill still has lineage terms")

    base_loop_steps_preserved = _all_present(migration_mapping_checks)
    igre_gates_present = all(all(checks.values()) for checks in gate_checks.values())
    claim_boundary = (
        "This audit proves inheritance and packaging alignment: Co-Pilot AI Scientist v3 "
        "preserves the user's AI Scientist-v2 research-production loop and adds IGRE gates. "
        "It does not prove that the resulting workflow improves paper quality or benchmark "
        "performance."
    )
    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "base_skill": str(BASE_SKILL),
        "repo_skill": _rel(REPO_SKILL),
        "release_skill": _rel(RELEASE_SKILL),
        "global_skill": str(GLOBAL_SKILL),
        "file_checks": file_checks,
        "base_loop_checks": base_loop_checks,
        "migration_mapping_checks": migration_mapping_checks,
        "skill_lineage_checks": skill_lineage_checks,
        "gate_checks": gate_checks,
        "nonnegotiable_checks": nonnegotiable_checks,
        "global_migration_checks": global_migration_checks,
        "base_loop_steps_preserved": base_loop_steps_preserved,
        "igre_gates_present": igre_gates_present,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": claim_boundary,
    }

    json_path = AUDIT_DIR / "base_skill_inheritance_audit.json"
    md_path = AUDIT_DIR / "base_skill_inheritance_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Base Skill Inheritance Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Base skill: `{audit['base_skill']}`",
        f"- Release skill: `{audit['release_skill']}`",
        f"- Global skill: `{audit['global_skill']}`",
        f"- Base loop steps preserved: `{audit['base_loop_steps_preserved']}`",
        f"- IGRE gates present: `{audit['igre_gates_present']}`",
        "",
        "## AI Scientist-v2 Loop Mapping",
        "",
        "| Step | Base markers present | Migration mapping present |",
        "| --- | --- | --- |",
    ]
    for step in BASE_LOOP_STEPS:
        base_ok = all(base_loop_checks[step].values())
        migration_ok = all(migration_mapping_checks[step].values())
        lines.append(f"| `{step}` | `{base_ok}` | `{migration_ok}` |")
    lines.extend(["", "## IGRE Gate Coverage", "", "| Artifact | All gates present |", "| --- | --- |"])
    for name, checks in gate_checks.items():
        lines.append(f"| `{name}` | `{all(checks.values())}` |")
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", claim_boundary, ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    if args.update_manifest:
        _update_manifest([json_path, md_path], audit)

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
