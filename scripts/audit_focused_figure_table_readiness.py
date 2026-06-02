#!/usr/bin/env python3
"""Audit focused-paper figure and evidence-table readiness."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
MANIFEST_PATH = DOC_DIR / "repro_manifest.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _image_refs(markdown: str) -> list[dict[str, str]]:
    pattern = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)")
    return [match.groupdict() for match in pattern.finditer(markdown)]


def _table_count(markdown: str) -> int:
    return sum(1 for line in markdown.splitlines() if re.match(r"^\|\s*-{3,}", line))


def _image_check(paper_path: Path, ref: dict[str, str]) -> dict[str, Any]:
    src = ref["src"]
    path = (paper_path.parent / src).resolve()
    item: dict[str, Any] = {
        "src": src,
        "path": _rel(path) if path.exists() else str(path),
        "alt_chars": len(ref["alt"]),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
        "width": None,
        "height": None,
    }
    if path.exists() and path.stat().st_size > 0:
        with Image.open(path) as image:
            item["width"], item["height"] = image.size
    return item


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _write_manifest(manifest: dict[str, Any], artifacts: list[str]) -> None:
    current = manifest.setdefault("current_artifacts", [])
    for artifact in artifacts:
        if artifact not in current:
            current.append(artifact)
    manifest["current_artifacts"] = sorted(current)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    en_path = DOC_DIR / "paper_en_focused.md"
    zh_path = DOC_DIR / "paper_zh_focused.md"
    en = en_path.read_text(encoding="utf-8")
    zh = zh_path.read_text(encoding="utf-8")

    required_en_markers = [
        "Review utility map",
        "Gate-structure ablation",
        "Held-out review-gate validation",
        "Prospective matched packages",
        "Prospective attention/taste instrumentation",
        "Open-data evaluator-stress pilot",
        "Evaluator-stress trigger-policy transfer",
        "MLAgentBench vectorization",
        "Sklearn diabetes tabular probe",
        "Paper claim",
        "Claim boundary",
    ]
    required_zh_markers = [
        "Review utility map",
        "Prospective matched packages",
        "Prospective attention/taste instrumentation",
        "Open-data evaluator-stress pilot",
        "Evaluator-stress trigger-policy transfer",
        "MLAgentBench vectorization",
    ]
    stale_markers = [
        "3 co-pilot or human-selected wins",
        "6 packages; SSH Max-Cut delta",
        "co-pilot 或人类选分支胜 3 次",
        "6 个 package；SSH Max-Cut delta",
    ]

    en_images = [_image_check(en_path, ref) for ref in _image_refs(en)]
    zh_images = [_image_check(zh_path, ref) for ref in _image_refs(zh)]
    en_marker_checks = {marker: marker in en for marker in required_en_markers}
    zh_marker_checks = {marker: marker in zh for marker in required_zh_markers}
    stale_hits = {marker: marker in en or marker in zh for marker in stale_markers}

    errors: list[str] = []
    if not en_images:
        errors.append("English focused paper has no image references")
    if not zh_images:
        errors.append("Chinese focused paper has no image references")
    for label, images in [("English", en_images), ("Chinese", zh_images)]:
        for image in images:
            if not image["exists"] or image["bytes"] <= 1000:
                errors.append(f"{label} image reference is missing or tiny: {image['src']}")
            if not image["width"] or not image["height"]:
                errors.append(f"{label} image reference has no readable dimensions: {image['src']}")
            if image["alt_chars"] < 30:
                errors.append(f"{label} image alt text is too short: {image['src']}")
    for marker, present in en_marker_checks.items():
        if not present:
            errors.append(f"English focused paper missing evidence marker: {marker}")
    for marker, present in zh_marker_checks.items():
        if not present:
            errors.append(f"Chinese focused paper missing evidence marker: {marker}")
    for marker, present in stale_hits.items():
        if present:
            errors.append(f"Focused papers still contain stale evidence marker: {marker}")
    if _table_count(en) < 2:
        errors.append("English focused paper has fewer than two markdown tables")
    if _table_count(zh) < 1:
        errors.append("Chinese focused paper has fewer than one markdown table")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "english_paper": _rel(en_path),
        "chinese_paper": _rel(zh_path),
        "english_table_count": _table_count(en),
        "chinese_table_count": _table_count(zh),
        "english_images": en_images,
        "chinese_images": zh_images,
        "english_marker_checks": en_marker_checks,
        "chinese_marker_checks": zh_marker_checks,
        "stale_marker_hits": stale_hits,
        "errors": errors,
        "claim_boundary": (
            "This audit checks whether the focused papers expose the main figure, "
            "evidence table, claim-boundary table, and current prospective-package "
            "counts. It does not judge whether the evidence is top-conference sufficient."
        ),
    }

    json_path = AUDIT_DIR / "focused_figure_table_readiness_audit.json"
    md_path = AUDIT_DIR / "focused_figure_table_readiness_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Focused Figure and Table Readiness Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- English paper: `{audit['english_paper']}`",
        f"- Chinese paper: `{audit['chinese_paper']}`",
        f"- English markdown tables: `{audit['english_table_count']}`",
        f"- Chinese markdown tables: `{audit['chinese_table_count']}`",
        "",
        "## Figure Checks",
        "",
    ]
    for label, images in [("English", en_images), ("Chinese", zh_images)]:
        for image in images:
            lines.append(
                f"- {label} `{image['src']}`: exists `{image['exists']}`, "
                f"bytes `{image['bytes']}`, size `{image['width']}x{image['height']}`, "
                f"alt chars `{image['alt_chars']}`"
            )
    lines.extend(["", "## Evidence Markers", ""])
    lines.extend([f"- English `{marker}`: `{'pass' if present else 'fail'}`" for marker, present in en_marker_checks.items()])
    lines.extend([f"- Chinese `{marker}`: `{'pass' if present else 'fail'}`" for marker, present in zh_marker_checks.items()])
    lines.extend(["", "## Stale Marker Scan", ""])
    lines.extend([f"- `{marker}`: `{'present' if present else 'absent'}`" for marker, present in stale_hits.items()])
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    _write_manifest(_load_manifest(), [_rel(json_path), _rel(md_path), "scripts/audit_focused_figure_table_readiness.py"])

    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
