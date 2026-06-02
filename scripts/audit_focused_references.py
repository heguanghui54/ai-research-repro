#!/usr/bin/env python3
"""Audit focused-paper reference coverage.

This checks that the conference-style focused papers cite the method families,
data sources, and benchmark sources that the manuscript relies on.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"


FOCUSED_PAPER_TERMS = [
    "AI Co-Scientist",
    "The AI Scientist",
    "AI Scientist-v2",
    "AlphaTensor",
    "AlphaDev",
    "FunSearch",
    "AlphaEvolve",
    "OpenEvolve",
    "Schmidhuber",
    "OOPS",
    "Gödel Machine",
    "POWERPLAY",
    "Darwin Gödel Machine",
    "Huxley-Gödel Machine",
    "PromptBreeder",
    "EvoPrompting",
    "ReEvo",
    "Reflexion",
    "Self-Refine",
    "Voyager",
    "AutoGen",
    "MLAgentBench",
    "MLE-bench",
    "OpenReview",
    "FML-bench",
]

BIB_KEY_TERMS = [
    "aicoscientist",
    "aiscientistv2",
    "lu2024aiscientist",
    "alphaevolve",
    "alphatensor",
    "alphadev",
    "funsearch",
    "openevolve",
    "schmidhuber2004oops",
    "schmidhuber2003godel",
    "schmidhuber2011powerplay",
    "darwingodel",
    "huxleygodel",
    "promptbreeder",
    "evoprompting",
    "reevo",
    "reflexion",
    "selfrefine",
    "voyager",
    "autogen",
    "mlagentbench",
    "mlebench",
    "OpenReview",
    "FML-bench",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _contains_all(text: str, terms: list[str]) -> dict[str, bool]:
    return {term: term in text for term in terms}


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    en_path = DOC_DIR / "paper_en_focused.md"
    zh_path = DOC_DIR / "paper_zh_focused.md"
    bib_path = DOC_DIR / "references.bib"
    manifest_path = DOC_DIR / "repro_manifest.json"

    en_text = en_path.read_text(encoding="utf-8")
    bib_text = bib_path.read_text(encoding="utf-8")

    checks = {
        _rel(en_path): {
            "has_references_heading": "## References" in en_text,
            "has_key_terms": _contains_all(en_text, FOCUSED_PAPER_TERMS),
            "has_no_placeholder_citations": all(token not in en_text for token in ["[?]", "TODO citation", "citation needed"]),
        },
        _rel(bib_path): {
            "has_key_terms": _contains_all(bib_text, BIB_KEY_TERMS),
            "has_no_placeholder_citations": all(token not in bib_text for token in ["TODO", "citation needed"]),
        },
    }

    errors: list[str] = []
    for path, path_checks in checks.items():
        for name, value in path_checks.items():
            if isinstance(value, dict):
                missing = [term for term, ok in value.items() if not ok]
                if missing:
                    errors.append(f"{path} failed {name}: missing {missing}")
            elif not value:
                errors.append(f"{path} failed {name}")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "checks": checks,
        "errors": errors,
        "claim_boundary": (
            "This audit checks visible reference coverage for the focused English paper. "
            "It does not validate every bibliographic field or scientific claim."
        ),
    }

    json_path = AUDIT_DIR / "focused_references_audit.json"
    md_path = AUDIT_DIR / "focused_references_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Focused References Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        "",
        "## Key Terms",
        "",
    ]
    for term in FOCUSED_PAPER_TERMS:
        lines.append(f"- `{term}`")
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["focused_references_audit"] = {
        "status": audit["status"],
        "json": _rel(json_path),
        "markdown": _rel(md_path),
    }
    for path in [Path(__file__), json_path, md_path]:
        rel = _rel(path)
        if rel not in manifest["current_artifacts"]:
            manifest["current_artifacts"].append(rel)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
