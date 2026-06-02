#!/usr/bin/env python3
"""Audit focused-paper accessibility revisions after model-review feedback."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _contains(text: str, terms: list[str]) -> dict[str, bool]:
    return {term: term in text for term in terms}


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    en_path = DOC_DIR / "paper_en_focused.md"
    zh_path = DOC_DIR / "paper_zh_focused.md"
    en = en_path.read_text(encoding="utf-8")
    zh = zh_path.read_text(encoding="utf-8")

    required_en_terms = [
        "A concrete run looks as follows",
        "evaluator-repair direction",
        "balanced-utility guardrail",
        "IGRE is intended to generalize across domains",
        "wet-lab or biomedical settings",
        "social science",
        "theoretical work",
        "ethical and governance obligations",
        "require consent",
        "repository stars",
    ]
    required_zh_terms = [
        "一个具体运行例子如下",
        "evaluator-repair 方向",
        "balanced-utility guardrail",
        "跨领域扩展",
        "湿实验或生物医学场景",
        "社会科学",
        "理论研究",
        "伦理和治理要求",
        "实时轨迹收集取得同意",
        "GitHub star",
    ]

    en_checks = _contains(en, required_en_terms)
    zh_checks = _contains(zh, required_zh_terms)
    errors = []
    for term, present in en_checks.items():
        if not present:
            errors.append(f"English focused paper missing accessibility term: {term}")
    for term, present in zh_checks.items():
        if not present:
            errors.append(f"Chinese focused paper missing accessibility term: {term}")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "english_paper": _rel(en_path),
        "chinese_paper": _rel(zh_path),
        "english_checks": en_checks,
        "chinese_checks": zh_checks,
        "errors": errors,
        "claim_boundary": (
            "This audit checks that the paper addresses presentation, running-example, "
            "ethics, and scalability revision requests. It does not judge empirical strength."
        ),
    }

    json_path = AUDIT_DIR / "focused_accessibility_revision_audit.json"
    md_path = AUDIT_DIR / "focused_accessibility_revision_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Focused Accessibility Revision Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- English paper: `{audit['english_paper']}`",
        f"- Chinese paper: `{audit['chinese_paper']}`",
        "",
        "## English Checks",
        "",
    ]
    lines.extend([f"- `{term}`: `{'pass' if present else 'fail'}`" for term, present in en_checks.items()])
    lines.extend(["", "## Chinese Checks", ""])
    lines.extend([f"- `{term}`: `{'pass' if present else 'fail'}`" for term, present in zh_checks.items()])
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
