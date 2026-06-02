#!/usr/bin/env python3
"""Audit the Frontier Alignment Vector Graph protocol and artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
FAVG_DIR = DOC_DIR / "experiments" / "frontier_vector_graph_20260602_234500"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(_read(path))


def _contains(path: Path, needles: list[str]) -> dict[str, bool]:
    text = _read(path)
    return {needle: needle in text for needle in needles}


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = FAVG_DIR / "summary.json"
    readme_path = FAVG_DIR / "README.md"
    protocol_path = DOC_DIR / "frontier_alignment_vector_graph_protocol.md"
    script_path = ROOT / "scripts" / "build_frontier_vector_graph.py"
    skill_path = ROOT / "skills" / "co-pilot-ai-scientist-v3" / "SKILL.md"
    paper_en_path = DOC_DIR / "paper_en_focused.md"
    paper_zh_path = DOC_DIR / "paper_zh_focused.md"

    summary = _load_json(summary_path)
    errors: list[str] = []
    warnings: list[str] = []

    required_files = [
        protocol_path,
        script_path,
        summary_path,
        readme_path,
        FAVG_DIR / "openreview_sample_1_vector_graph.svg",
        FAVG_DIR / "openreview_sample_2_vector_graph.svg",
        FAVG_DIR / "openreview_sample_17_vector_graph.svg",
    ]
    file_status = {}
    for path in required_files:
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        ok = exists and size > 20
        file_status[_rel(path)] = {"exists": exists, "bytes": size, "ok": ok}
        if not ok:
            errors.append(f"missing or too small FAVG artifact: {_rel(path)}")

    if summary.get("method_abbreviation") != "FAVG":
        errors.append("frontier vector summary must name method_abbreviation FAVG")
    if summary.get("status") != "pass":
        errors.append("frontier vector summary status must be pass")
    if summary.get("case_count") != 3:
        errors.append("FAVG pilot should include 3 deep cases")
    if summary.get("mean_six_minus_raw_projection_gain") != 0.1668:
        errors.append("unexpected FAVG mean projection gain")
    if summary.get("mean_six_minus_raw_cosine_gain") != -0.0641:
        errors.append("unexpected FAVG mean cosine gain")
    if "not a claim" not in summary.get("claim_boundary", ""):
        errors.append("FAVG summary claim boundary must prevent SOTA/value overclaim")

    required_terms = {
        _rel(protocol_path): [
            "Frontier Alignment Vector Graph",
            "FAVG",
            "delayed-value",
            "orthogonal novelty",
            "Claim Boundary",
        ],
        _rel(readme_path): [
            "Frontier Alignment Vector Graph",
            "FAVG",
            "frontier_projection_gain",
            "orthogonal_novelty_norm",
        ],
        _rel(skill_path): [
            "Frontier Alignment Vector Graph",
            "FAVG",
            "frontier_steering",
        ],
        _rel(paper_en_path): [
            "Frontier Alignment Vector Graph",
            "FAVG",
            "frontier-vector graph",
        ],
        _rel(paper_zh_path): [
            "前沿对齐向量图",
            "FAVG",
            "前沿向量图",
        ],
    }
    term_status = {
        rel: _contains(ROOT / rel, needles)
        for rel, needles in required_terms.items()
    }
    for rel, checks in term_status.items():
        missing = [term for term, ok in checks.items() if not ok]
        if missing:
            errors.append(f"{rel} missing FAVG terms: {missing}")

    projection = summary.get("mean_six_minus_raw_projection_gain")
    cosine = summary.get("mean_six_minus_raw_cosine_gain")
    if projection is not None and cosine is not None and projection > 0 and cosine < 0:
        warnings.append(
            "FAVG detects mixed directionality: positive projection gain with negative direct cosine gain."
        )

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "method": "Frontier Alignment Vector Graph",
        "abbreviation": "FAVG",
        "summary": _rel(summary_path),
        "case_count": summary.get("case_count"),
        "mean_six_minus_raw_projection_gain": projection,
        "mean_six_minus_raw_cosine_gain": cosine,
        "file_status": file_status,
        "term_status": term_status,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "This audit verifies that FAVG is documented, runnable, and bounded. "
            "It does not convert the pilot vector metrics into a proof of top-conference-level superiority."
        ),
    }

    json_path = AUDIT_DIR / "frontier_alignment_vector_graph_audit.json"
    md_path = AUDIT_DIR / "frontier_alignment_vector_graph_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Frontier Alignment Vector Graph Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Case count: `{audit['case_count']}`",
        f"- Mean projection gain: `{audit['mean_six_minus_raw_projection_gain']}`",
        f"- Mean cosine gain: `{audit['mean_six_minus_raw_cosine_gain']}`",
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
