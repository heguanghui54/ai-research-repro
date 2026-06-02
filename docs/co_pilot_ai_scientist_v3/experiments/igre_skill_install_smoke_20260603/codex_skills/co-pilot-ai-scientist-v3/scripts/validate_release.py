#!/usr/bin/env python3
"""Validate the standalone Co-Pilot AI Scientist v3 skill release scaffold."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []

    for rel in manifest["required_files"]:
        path = ROOT / rel
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing or empty required file: {rel}")

    skill = read(ROOT / "SKILL.md")
    readme = read(ROOT / "README.md")
    quickstart = read(ROOT / "QUICKSTART.md")
    positioning = read(ROOT / "POSITIONING.md")
    contributing = read(ROOT / "CONTRIBUTING.md")
    release_notes = read(ROOT / "RELEASE_NOTES.md")
    example_gate = json.loads((ROOT / "examples" / "example_gate_log.json").read_text(encoding="utf-8"))

    for gate in manifest["gates"]:
        if gate not in skill:
            errors.append(f"gate missing from SKILL.md: {gate}")
        if gate not in readme:
            warnings.append(f"gate not named in README.md: {gate}")

    required_terms = [
        "Insight-Gated Research Evolution",
        "human scientific taste",
        "OpenEvolve",
        "claim_calibration",
        "not scientific superiority",
    ]
    blob = "\n".join([skill, readme, quickstart, positioning, contributing, release_notes])
    for term in required_terms:
        if term not in blob:
            errors.append(f"required positioning term missing: {term}")

    publication_terms = [
        "academic-research-skills",
        "Engineering adoption is not scientific superiority",
        "Do not add fabricated benchmark numbers",
        "model-only reviews",
    ]
    for term in publication_terms:
        if term not in blob:
            errors.append(f"publication readiness term missing: {term}")

    if example_gate.get("gate_type") != "evaluator_stress_test":
        errors.append("example gate should demonstrate evaluator_stress_test")
    for field in ["attention_cost", "taste_insight", "human_decision", "rationale"]:
        if field not in example_gate:
            errors.append(f"example gate missing field: {field}")

    result = {
        "status": "pass" if not errors else "fail",
        "release_root": str(ROOT),
        "required_files_checked": len(manifest["required_files"]),
        "gates_checked": manifest["gates"],
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": manifest["claim_boundary"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
