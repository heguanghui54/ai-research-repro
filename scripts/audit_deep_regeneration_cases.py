#!/usr/bin/env python3
"""Audit deep regeneration and six-gate hybrid-review case artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
AUDIT_DIR = DOC_DIR / "audits"
DEEP_RUN = EXP_DIR / "deep_regeneration_cases_20260602_203000"
HYBRID_RUN = EXP_DIR / "six_gate_hybrid_review_cases_20260602_211500"
INTERNAL_REVIEW_RUN = EXP_DIR / "deep_case_internal_review_20260602_224500"
PDF_SUMMARY = DOC_DIR / "build" / "deep_regeneration_cases" / "summary.json"

REQUIRED_GATES = {
    "scientific_taste_prior",
    "evaluator_stress_test",
    "frontier_steering",
    "verifiable_micro_evolution",
    "structured_feedback",
    "claim_calibration",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_ok(path: Path, min_bytes: int = 10) -> bool:
    return path.exists() and path.stat().st_size >= min_bytes


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    warnings: list[str] = []

    casebook_path = DOC_DIR / "deep_regeneration_casebook.md"
    deep_summary_path = DEEP_RUN / "summary.json"
    hybrid_summary_path = HYBRID_RUN / "summary.json"
    internal_review_summary_path = INTERNAL_REVIEW_RUN / "summary.json"

    for path in [casebook_path, deep_summary_path, hybrid_summary_path, internal_review_summary_path, PDF_SUMMARY]:
        if not _file_ok(path):
            errors.append(f"missing required artifact: {_rel(path)}")

    deep_summary = _load_json(deep_summary_path) if deep_summary_path.exists() else {}
    hybrid_summary = _load_json(hybrid_summary_path) if hybrid_summary_path.exists() else {}
    internal_review_summary = _load_json(internal_review_summary_path) if internal_review_summary_path.exists() else {}
    pdf_summary = _load_json(PDF_SUMMARY) if PDF_SUMMARY.exists() else {}

    deep_cases = deep_summary.get("cases", [])
    hybrid_cases = hybrid_summary.get("cases", [])
    if len(deep_cases) < 3:
        errors.append("deep case package has fewer than 3 cases")
    if len(hybrid_cases) < 3:
        errors.append("six-gate hybrid package has fewer than 3 cases")
    if set(hybrid_summary.get("gates", [])) != REQUIRED_GATES:
        errors.append("six-gate hybrid package does not contain the required gate set")
    if pdf_summary.get("pdf_count") != 6:
        errors.append("deep case PDF package does not contain 6 PDFs")
    if internal_review_summary.get("case_count") != 3:
        errors.append("internal deep-case review does not contain 3 cases")
    if internal_review_summary.get("six_gate_hybrid_wins") != 3:
        errors.append("internal deep-case review should report 3 six-gate wins")
    if "not replace future human expert blind review" not in internal_review_summary.get("claim_boundary", ""):
        errors.append("internal deep-case review missing human-review boundary")

    case_checks = []
    for case in deep_cases:
        case_dir = ROOT / case["case_dir"]
        required_files = [
            "original_paper.md",
            "human_reviews.md",
            "regenerated_artifacts.md",
            "short_term_scores.md",
            "future_frontier_evidence.md",
            "case_analysis.md",
            "case_summary.json",
        ]
        missing = [name for name in required_files if not _file_ok(case_dir / name)]
        if missing:
            errors.append(f"{case['paper_id']} missing deep case files: {missing}")
        case_checks.append({"paper_id": case["paper_id"], "case_dir": _rel(case_dir), "missing_files": missing})

    hybrid_checks = []
    for case in hybrid_cases:
        case_dir = ROOT / case["case_dir"]
        required_files = [
            "optimized_hybrid_review.md",
            "gate_optimized_regeneration.md",
            "six_gate_routing.json",
            "optimized_hybrid_review.json",
            "gate_optimized_regeneration.json",
            "case_comparison.json",
        ]
        missing = [name for name in required_files if not _file_ok(case_dir / name)]
        if missing:
            errors.append(f"{case['paper_id']} missing six-gate case files: {missing}")
        proxy = case.get("proxy_metrics", {})
        if proxy.get("six_gate_action_count", 0) < 3:
            warnings.append(f"{case['paper_id']} has fewer than 3 gates with routed evidence")
        hybrid_checks.append(
            {
                "paper_id": case["paper_id"],
                "case_dir": _rel(case_dir),
                "missing_files": missing,
                "proxy_metrics": proxy,
            }
        )

    pdf_checks = []
    for case in pdf_summary.get("cases", []):
        missing_pdfs = []
        for key in ["review_guided_pdf", "six_gate_hybrid_pdf"]:
            rel = case.get(key)
            if not rel or not _file_ok(ROOT / rel, min_bytes=1_000):
                missing_pdfs.append(rel or key)
        if missing_pdfs:
            errors.append(f"{case.get('paper_id')} missing PDF outputs: {missing_pdfs}")
        pdf_checks.append({"paper_id": case.get("paper_id"), "missing_pdfs": missing_pdfs})

    internal_review_checks = []
    for case in internal_review_summary.get("cases", []):
        missing = []
        for suffix in ["json", "md"]:
            path = INTERNAL_REVIEW_RUN / f"{case.get('paper_id')}.{suffix}"
            if not _file_ok(path):
                missing.append(_rel(path))
        if missing:
            errors.append(f"{case.get('paper_id')} missing internal review files: {missing}")
        internal_review_checks.append(
            {
                "paper_id": case.get("paper_id"),
                "winner": case.get("winner"),
                "delta": case.get("overall_delta_six_gate_minus_raw"),
                "missing_files": missing,
            }
        )

    casebook_text = casebook_path.read_text(encoding="utf-8") if casebook_path.exists() else ""
    for term in [
        "LLM Refusal And Reliability",
        "Conditional Graph Generation And Molecular Design",
        "Knowledge Unlearning And Privacy Risk",
        "Minimum Future Deep-Case Artifact",
    ]:
        if term not in casebook_text:
            errors.append(f"casebook missing term: {term}")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "casebook": _rel(casebook_path),
        "deep_run": _rel(DEEP_RUN),
        "hybrid_run": _rel(HYBRID_RUN),
        "internal_review_run": _rel(INTERNAL_REVIEW_RUN),
        "deep_case_count": len(deep_cases),
        "hybrid_case_count": len(hybrid_cases),
        "internal_review_case_count": internal_review_summary.get("case_count"),
        "internal_review_six_gate_wins": internal_review_summary.get("six_gate_hybrid_wins"),
        "internal_review_mean_delta": internal_review_summary.get("mean_delta_six_gate_minus_raw"),
        "pdf_count": pdf_summary.get("pdf_count"),
        "required_gates": sorted(REQUIRED_GATES),
        "hybrid_gates": hybrid_summary.get("gates", []),
        "case_checks": case_checks,
        "hybrid_checks": hybrid_checks,
        "internal_review_checks": internal_review_checks,
        "pdf_checks": pdf_checks,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "A pass means the package exposes concrete paper-level replay cases and "
            "six-gate optimized hybrid-review proxies. It does not mean the deep "
            "benchmark reruns, human expert reviews, or long-horizon innovation "
            "claims are completed."
        ),
    }

    json_path = AUDIT_DIR / "deep_regeneration_cases_audit.json"
    md_path = AUDIT_DIR / "deep_regeneration_cases_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Deep Regeneration Cases Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Casebook: `{audit['casebook']}`",
        f"- Deep cases: `{audit['deep_case_count']}`",
        f"- Six-gate hybrid cases: `{audit['hybrid_case_count']}`",
        f"- Internal review cases: `{audit['internal_review_case_count']}`",
        f"- Internal six-gate wins: `{audit['internal_review_six_gate_wins']}`",
        f"- Internal mean delta: `{audit['internal_review_mean_delta']}`",
        f"- Viewable mini-paper PDFs: `{audit['pdf_count']}`",
        f"- Gates: `{', '.join(audit['hybrid_gates'])}`",
        "",
        "## Deep Case Checks",
        "",
    ]
    for check in case_checks:
        lines.append(f"- `{check['paper_id']}`: missing `{check['missing_files']}`")
    lines.extend(["", "## Hybrid Case Checks", ""])
    for check in hybrid_checks:
        lines.append(
            f"- `{check['paper_id']}`: missing `{check['missing_files']}`, "
            f"gates with evidence `{check['proxy_metrics'].get('six_gate_action_count')}`"
        )
    lines.extend(["", "## Internal Review Checks", ""])
    for check in internal_review_checks:
        lines.append(
            f"- `{check['paper_id']}`: winner `{check['winner']}`, "
            f"delta `{check['delta']}`, missing `{check['missing_files']}`"
        )
    lines.extend(["", "## PDF Checks", ""])
    for check in pdf_checks:
        lines.append(f"- `{check['paper_id']}`: missing `{check['missing_pdfs']}`")
    lines.extend(["", "## Errors", ""])
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
