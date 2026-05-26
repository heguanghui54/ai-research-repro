from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_CJK_FONTS = [
    ("/System/Library/Fonts/PingFang.ttc", "PingFang SC"),
    ("/System/Library/Fonts/STHeiti Medium.ttc", "STHeiti"),
    ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "Arial Unicode MS"),
    ("/Library/Fonts/Arial Unicode.ttf", "Arial Unicode MS"),
]


@lru_cache(maxsize=32)
def load_cjk_font(size: int):
    for path, _name in _CJK_FONTS:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


@lru_cache(maxsize=1)
def primary_cjk_font_name() -> str:
    for path, name in _CJK_FONTS:
        if Path(path).exists():
            return name
    return "Arial Unicode MS"


@lru_cache(maxsize=1)
def _measure_draw():
    return ImageDraw.Draw(Image.new("RGB", (1, 1)))


def wrap_cjk_text(text: str, font, max_width: int) -> list[str]:
    draw = _measure_draw()
    lines: list[str] = []
    for paragraph in (text or "").splitlines() or [""]:
        if not paragraph.strip():
            lines.append("")
            continue
        current = ""
        for ch in paragraph:
            candidate = current + ch
            if not current or draw.textlength(candidate, font=font) <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines or [""]


def wrap_cjk_text_limited(text: str, font, max_width: int, max_lines: int = 2) -> list[str]:
    lines = wrap_cjk_text(text, font, max_width)
    if len(lines) <= max_lines:
        return lines
    limited = lines[:max_lines]
    if limited[-1] and not limited[-1].endswith("…"):
        limited[-1] = limited[-1].rstrip("。．. ") + "…"
    return limited
