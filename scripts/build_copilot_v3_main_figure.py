#!/usr/bin/env python3
"""Build the main IGRE/frontier-evaluation figure for the focused paper."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
FIG_DIR = DOC_DIR / "figures"
DISAGREE = DOC_DIR / "experiments" / "frontier_metric_disagreement_20260603_003000" / "summary.json"
VECTOR = DOC_DIR / "experiments" / "frontier_vector_graph_20260602_234500" / "summary.json"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if path and Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), trial, font=font)[2] <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    title: str,
    body: str,
    fill: str,
    outline: str,
) -> None:
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=14, fill=fill, outline=outline, width=3)
    draw.text((x1 + 18, y1 + 16), title, font=_font(26, bold=True), fill="#111827")
    y = y1 + 58
    for line in _wrap(draw, body, _font(20), x2 - x1 - 36):
        draw.text((x1 + 18, y), line, font=_font(20), fill="#334155")
        y += 27


def _arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = "#334155") -> None:
    draw.line([start, end], fill=color, width=5)
    x1, y1 = start
    x2, y2 = end
    if x2 >= x1:
        pts = [(x2, y2), (x2 - 18, y2 - 10), (x2 - 18, y2 + 10)]
    else:
        pts = [(x2, y2), (x2 + 18, y2 - 10), (x2 + 18, y2 + 10)]
    draw.polygon(pts, fill=color)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    disagree = json.loads(DISAGREE.read_text(encoding="utf-8"))
    vector = json.loads(VECTOR.read_text(encoding="utf-8"))

    img = Image.new("RGB", (1800, 1080), "#ffffff")
    draw = ImageDraw.Draw(img)

    draw.text((70, 52), "Co-Pilot AI Scientist v3: Insight-Gated Research Evolution", font=_font(42, True), fill="#0f172a")
    draw.text((72, 105), "Humans are modeled as high-variance scientific search operators, not generic approvers.", font=_font(24), fill="#475569")

    boxes = [
        ((80, 180, 405, 370), "AI Co-Scientist", "Generate hypotheses, debate directions, organize evidence.", "#e0f2fe", "#0284c7"),
        ((475, 180, 800, 370), "AI Scientist-v2", "Turn hypotheses into experiments, benchmarks, and manuscripts.", "#ecfdf5", "#059669"),
        ((870, 180, 1195, 370), "OpenEvolve Loop", "Search machine-gradeable code subproblems under evaluators.", "#fff7ed", "#ea580c"),
        ((1265, 180, 1700, 370), "Audited Paper", "Claim-calibrated English paper, runbooks, reusable Codex skill.", "#f5f3ff", "#7c3aed"),
    ]
    for box in boxes:
        _box(draw, *box)
    for sx, ex in [((405, 275), (475, 275)), ((800, 275), (870, 275)), ((1195, 275), (1265, 275))]:
        _arrow(draw, sx, ex)

    draw.text((80, 430), "Six Human Insight Gates", font=_font(30, True), fill="#111827")
    gates = [
        "Scientific-taste prior",
        "Evaluator stress test",
        "Frontier steering",
        "Verifiable micro-evolution",
        "Structured feedback",
        "Claim calibration",
    ]
    x, y = 80, 475
    for i, gate in enumerate(gates):
        gx = x + (i % 3) * 390
        gy = y + (i // 3) * 92
        draw.rounded_rectangle((gx, gy, gx + 335, gy + 58), radius=12, fill="#f8fafc", outline="#94a3b8", width=2)
        draw.text((gx + 18, gy + 16), gate, font=_font(22, True), fill="#1f2937")

    draw.rounded_rectangle((80, 690, 1700, 1010), radius=18, fill="#f8fafc", outline="#cbd5e1", width=3)
    draw.text((110, 725), "Frontier-aware evaluation: compare movement, not just local score", font=_font(30, True), fill="#111827")
    draw.text((110, 775), "Vector space dimensions: safety/reliability, mechanism/theory, efficiency, long-horizon search, evaluation shift, deployment value.", font=_font(22), fill="#475569")

    # Vector sketch.
    ox, oy = 270, 925
    draw.ellipse((ox - 10, oy - 10, ox + 10, oy + 10), fill="#64748b")
    draw.text((ox - 58, oy + 20), "original o", font=_font(20), fill="#475569")
    frontier = (625, 805)
    raw = (510, 900)
    six = (590, 850)
    for point, label, color in [(frontier, "frontier f", "#111827"), (raw, "raw review", "#2563eb"), (six, "six-gate", "#dc2626")]:
        _arrow(draw, (ox, oy), point, color)
        px, py = point
        draw.ellipse((px - 11, py - 11, px + 11, py + 11), fill=color)
        draw.text((px + 14, py - 10), label, font=_font(20, True), fill=color)

    metric_x = 820
    draw.text((metric_x, 825), f"Internal review: six-gate wins {disagree['metric_win_counts']['internal_review']['six_gate_hybrid']}/3", font=_font(24, True), fill="#111827")
    draw.text((metric_x, 865), f"Lexical frontier: six-gate wins {disagree['metric_win_counts']['lexical_frontier']['six_gate_hybrid']}/3", font=_font(24, True), fill="#111827")
    draw.text((metric_x, 905), f"Vector projection: six-gate wins {disagree['metric_win_counts']['vector_projection']['six_gate_hybrid']}/3", font=_font(24, True), fill="#111827")
    draw.text((metric_x, 945), f"Frontier cosine: six-gate wins {disagree['metric_win_counts']['frontier_cosine']['six_gate_hybrid']}/3", font=_font(24, True), fill="#111827")
    draw.text((1290, 865), f"Disagreement rate: {disagree['disagreement_rate']}", font=_font(30, True), fill="#b91c1c")
    draw.text((1290, 910), f"Mean projection gain: {vector['mean_six_minus_raw_projection_gain']}", font=_font(24), fill="#334155")
    draw.text((1290, 946), f"Mean cosine gain: {vector['mean_six_minus_raw_cosine_gain']}", font=_font(24), fill="#334155")

    out = FIG_DIR / "igre_frontier_main_figure.png"
    img.save(out)
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
