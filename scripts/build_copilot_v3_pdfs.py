#!/usr/bin/env python3
"""Build simple bilingual PDFs for the Co-Pilot AI Scientist v3 manuscript.

This intentionally avoids a LaTeX dependency so the research package can render
on a fresh machine with only Python and reportlab installed.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
OUT_DIR = DOC_DIR / "build"


def _strip_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = text.replace("\\_", "_")
    return text


def _char_width(text: str, font: str, size: float) -> float:
    return pdfmetrics.stringWidth(text, font, size)


def _wrap_latin(text: str, font: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if _char_width(trial, font, size) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _wrap_cjk(text: str, font: str, size: float, max_width: float) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        trial = current + char
        if _char_width(trial, font, size) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = char
    if current or not lines:
        lines.append(current)
    return lines


def _wrap(text: str, font: str, size: float, max_width: float, cjk: bool) -> list[str]:
    if cjk:
        wrapped: list[str] = []
        for part in re.split(r"(\s+)", text):
            if not part.strip():
                if wrapped and wrapped[-1]:
                    wrapped[-1] += " "
                continue
            wrapped.extend(_wrap_cjk(part, font, size, max_width))
        return wrapped
    return _wrap_latin(text, font, size, max_width)


def _parse_markdown(path: Path) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    paragraph: list[str] = []
    in_code = False

    def flush() -> None:
        if paragraph:
            blocks.append(("p", _strip_markdown(" ".join(paragraph))))
            paragraph.clear()

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            flush()
            in_code = not in_code
            continue
        if in_code:
            blocks.append(("code", line))
            continue
        if not line.strip():
            flush()
            continue
        if line.startswith("# "):
            flush()
            blocks.append(("h1", _strip_markdown(line[2:].strip())))
        elif line.startswith("## "):
            flush()
            blocks.append(("h2", _strip_markdown(line[3:].strip())))
        elif re.match(r"^\d+\.\s+", line):
            flush()
            blocks.append(("li", _strip_markdown(line.strip())))
        elif line.startswith("- "):
            flush()
            blocks.append(("li", _strip_markdown("• " + line[2:].strip())))
        else:
            paragraph.append(line.strip())
    flush()
    return blocks


def build_pdf(markdown_path: Path, output_path: Path, language: str) -> None:
    cjk = language == "zh"
    if cjk:
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        body_font = "STSong-Light"
        bold_font = "STSong-Light"
    else:
        body_font = "Helvetica"
        bold_font = "Helvetica-Bold"

    page_width, page_height = A4
    left = 22 * mm
    right = 22 * mm
    top = 22 * mm
    bottom = 20 * mm
    max_width = page_width - left - right

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    y = page_height - top
    page_num = 1

    def new_page() -> None:
        nonlocal y, page_num
        pdf.setFont(body_font, 9)
        pdf.drawRightString(page_width - right, 12 * mm, str(page_num))
        pdf.showPage()
        page_num += 1
        y = page_height - top

    def ensure(space: float) -> None:
        if y - space < bottom:
            new_page()

    for kind, text in _parse_markdown(markdown_path):
        if kind == "h1":
            size = 17 if not cjk else 15
            leading = size + 5
            lines = _wrap(text, bold_font, size, max_width, cjk)
            ensure(leading * len(lines) + 8)
            pdf.setFont(bold_font, size)
            for line in lines:
                pdf.drawString(left, y, line)
                y -= leading
            y -= 5
        elif kind == "h2":
            size = 13 if not cjk else 12
            leading = size + 4
            lines = _wrap(text, bold_font, size, max_width, cjk)
            ensure(leading * len(lines) + 6)
            y -= 4
            pdf.setFont(bold_font, size)
            for line in lines:
                pdf.drawString(left, y, line)
                y -= leading
            y -= 2
        elif kind == "li":
            size = 10.5 if not cjk else 10
            leading = size + 4
            lines = _wrap(text, body_font, size, max_width - 6 * mm, cjk)
            ensure(leading * len(lines) + 2)
            pdf.setFont(body_font, size)
            for i, line in enumerate(lines):
                x = left + (0 if i == 0 else 6 * mm)
                pdf.drawString(x, y, line)
                y -= leading
            y -= 1
        elif kind == "code":
            size = 8
            leading = size + 3
            ensure(leading + 2)
            pdf.setFont("Courier", size)
            pdf.drawString(left, y, text[:110])
            y -= leading
        else:
            size = 10.5 if not cjk else 10
            leading = size + 4
            lines = _wrap(text, body_font, size, max_width, cjk)
            ensure(leading * len(lines) + 4)
            pdf.setFont(body_font, size)
            for line in lines:
                pdf.drawString(left, y, line)
                y -= leading
            y -= 4

    pdf.setFont(body_font, 9)
    pdf.drawRightString(page_width - right, 12 * mm, str(page_num))
    pdf.save()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Co-Pilot AI Scientist v3 PDFs.")
    parser.add_argument("--language", choices=["en", "zh", "both"], default="both")
    parser.add_argument(
        "--variant",
        choices=["full", "focused", "all"],
        default="full",
        help="Which manuscript variant to render.",
    )
    args = parser.parse_args()

    jobs = []
    if args.variant in {"full", "all"} and args.language in {"en", "both"}:
        jobs.append(("en", DOC_DIR / "paper_en.md", OUT_DIR / "co_pilot_ai_scientist_v3_en.pdf"))
    if args.variant in {"full", "all"} and args.language in {"zh", "both"}:
        jobs.append(("zh", DOC_DIR / "paper_zh.md", OUT_DIR / "co_pilot_ai_scientist_v3_zh.pdf"))
    if args.variant in {"focused", "all"} and args.language in {"en", "both"}:
        jobs.append(
            (
                "en",
                DOC_DIR / "paper_en_focused.md",
                OUT_DIR / "co_pilot_ai_scientist_v3_focused_en.pdf",
            )
        )
    if args.variant in {"focused", "all"} and args.language in {"zh", "both"}:
        jobs.append(
            (
                "zh",
                DOC_DIR / "paper_zh_focused.md",
                OUT_DIR / "co_pilot_ai_scientist_v3_focused_zh.pdf",
            )
        )

    for language, source, output in jobs:
        build_pdf(source, output, language)
        print(output)


if __name__ == "__main__":
    main()
