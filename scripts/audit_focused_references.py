#!/usr/bin/env python3
"""Audit related-work and focused-paper reference coverage.

This checks that the conference-style focused papers and supporting related-work
artifacts cover the method families, data sources, benchmark sources, and older
self-improvement line that the manuscript relies on.
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
    "self-referential learning",
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
    "PaperBench",
    "AIRS-Bench",
    "RExBench",
    "ReplicationBench",
    "SciVisAgentBench",
    "OpenReview",
    "FML-bench",
]

ZH_SELF_IMPROVEMENT_TERMS = [
    "Schmidhuber",
    "自指学习",
    "代码自我改进",
    "OOPS",
    "Gödel Machine",
    "POWERPLAY",
    "Darwin Gödel Machine",
    "Huxley-Gödel Machine",
    "人类 insight gate",
]

SELF_IMPROVEMENT_LINE_TERMS = [
    "Schmidhuber",
    "self-referential learning",
    "OOPS",
    "Gödel Machine",
    "POWERPLAY",
    "Darwin Gödel Machine",
    "Huxley-Gödel Machine",
    "self-improvement",
    "human-insight gates",
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
    "schmidhuber1987selfreferential",
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
    "paperbench",
    "airsbench",
    "rexbench",
    "replicationbench",
    "scivisagentbench",
    "OpenReview",
    "FML-bench",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _contains_all(text: str, terms: list[str]) -> dict[str, bool]:
    normalized_text = " ".join(text.split())
    return {term: term in normalized_text for term in terms}


def _contains(text: str, term: str) -> bool:
    return term in " ".join(text.split())


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    en_path = DOC_DIR / "paper_en_focused.md"
    zh_path = DOC_DIR / "paper_zh_focused.md"
    full_en_path = DOC_DIR / "paper_en.md"
    full_zh_path = DOC_DIR / "paper_zh.md"
    literature_matrix_path = DOC_DIR / "literature_matrix.md"
    coverage_map_path = DOC_DIR / "related_work_coverage_map.md"
    bib_path = DOC_DIR / "references.bib"
    manifest_path = DOC_DIR / "repro_manifest.json"

    en_text = en_path.read_text(encoding="utf-8")
    zh_text = zh_path.read_text(encoding="utf-8")
    full_en_text = full_en_path.read_text(encoding="utf-8")
    full_zh_text = full_zh_path.read_text(encoding="utf-8")
    literature_matrix_text = literature_matrix_path.read_text(encoding="utf-8")
    coverage_map_text = coverage_map_path.read_text(encoding="utf-8")
    bib_text = bib_path.read_text(encoding="utf-8")

    checks = {
        _rel(en_path): {
            "has_references_heading": "## References" in en_text,
            "has_key_terms": _contains_all(en_text, FOCUSED_PAPER_TERMS),
            "has_self_improvement_line": _contains_all(en_text, SELF_IMPROVEMENT_LINE_TERMS),
            "distinguishes_igre_from_whole_agent_self_rewrite": _contains(en_text, "rather than directly optimizing an autonomous agent's own source code"),
            "has_no_placeholder_citations": all(token not in en_text for token in ["[?]", "TODO citation", "citation needed"]),
        },
        _rel(zh_path): {
            "has_references_heading": "## 参考文献" in zh_text,
            "has_self_improvement_line": _contains_all(zh_text, ZH_SELF_IMPROVEMENT_TERMS),
            "distinguishes_igre_from_whole_agent_self_rewrite": _contains(zh_text, "不直接演化 autonomous agent 的完整源码"),
            "has_no_placeholder_citations": all(token not in zh_text for token in ["[?]", "TODO citation", "citation needed"]),
        },
        _rel(full_en_path): {
            "has_self_improvement_line": _contains_all(full_en_text, SELF_IMPROVEMENT_LINE_TERMS),
            "distinguishes_igre_from_recursive_self_improvement_claim": _contains(full_en_text, "does not claim to solve recursive self-improvement"),
        },
        _rel(full_zh_path): {
            "has_self_improvement_line": _contains_all(full_zh_text, ZH_SELF_IMPROVEMENT_TERMS),
            "distinguishes_igre_from_recursive_self_improvement_claim": _contains(full_zh_text, "不声称解决递归自我改进"),
        },
        _rel(literature_matrix_path): {
            "has_self_improvement_line": _contains_all(literature_matrix_text, SELF_IMPROVEMENT_LINE_TERMS),
            "has_bounded_auditable_boundary": _contains(literature_matrix_text, "bounded, auditable micro-evolution"),
        },
        _rel(coverage_map_path): {
            "has_self_improvement_line": _contains_all(coverage_map_text, SELF_IMPROVEMENT_LINE_TERMS),
            "has_distinction_column": _contains(coverage_map_text, "IGRE does not optimize the agent's whole source code"),
            "has_seed_links": all(
                term in coverage_map_text
                for term in [
                    "diploma1987ocr.pdf",
                    "cs/0309048",
                    "1112.5309",
                    "2505.22954",
                    "2510.21614",
                ]
            ),
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
            "This audit checks visible related-work coverage across the focused papers, "
            "full papers, literature matrix, coverage map, and BibTeX. It does not "
            "validate every bibliographic field or scientific claim."
        ),
    }

    json_path = AUDIT_DIR / "focused_references_audit.json"
    md_path = AUDIT_DIR / "focused_references_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Related-Work References Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        "",
        "## Focused English Key Terms",
        "",
    ]
    for term in FOCUSED_PAPER_TERMS:
        lines.append(f"- `{term}`")
    lines.extend(["", "## Self-Improvement Line Terms", ""])
    for term in SELF_IMPROVEMENT_LINE_TERMS:
        lines.append(f"- `{term}`")
    lines.extend(["", "## Chinese Self-Improvement Terms", ""])
    for term in ZH_SELF_IMPROVEMENT_TERMS:
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
