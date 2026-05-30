from __future__ import annotations

from pathlib import Path
from typing import Any

from .templates.nanogpt_lite import plot_history


METHOD_LABELS = {
    "fixed_template": "Fixed\nTemplate",
    "single_fixed": "Single\nFixed",
    "single_reflection": "Single\nReflect",
    "single_self_consistency": "Single\nConsist",
    "multi_fixed": "Multi\nFixed",
    "multi_artifact_evolution": "Multi\nEvolve",
}


def save_learning_curve(history: dict, path: Path) -> None:
    plot_history(history, path)


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def save_bar_chart(
    *,
    rows: list[dict[str, Any]],
    metric: str,
    title: str,
    ylabel: str,
    path: Path,
    width: int = 920,
    height: int = 420,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    margin_left = 90
    margin_right = 30
    margin_top = 56
    margin_bottom = 88
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    values = [float(row.get(metric, 0) or 0) for row in rows]
    max_value = max(values + [1.0])
    min_value = min(values + [0.0])
    if min_value > 0:
        min_value = 0.0
    span = max(max_value - min_value, 1.0)
    bar_gap = 18
    bar_w = max(28, (plot_w - bar_gap * (len(rows) + 1)) / max(len(rows), 1))
    zero_y = margin_top + plot_h - ((0 - min_value) / span) * plot_h
    palette = ["#2f6fbb", "#43a047", "#f39c12", "#8e44ad", "#d35400", "#16a085"]

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width / 2:.1f}" y="28" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="700">{_esc(title)}</text>',
        f'<text x="18" y="{margin_top + plot_h / 2:.1f}" transform="rotate(-90 18 {margin_top + plot_h / 2:.1f})" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">{_esc(ylabel)}</text>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" stroke="#333" stroke-width="1"/>',
        f'<line x1="{margin_left}" y1="{zero_y:.1f}" x2="{margin_left + plot_w}" y2="{zero_y:.1f}" stroke="#333" stroke-width="1"/>',
    ]
    for tick in range(5):
        value = min_value + span * tick / 4
        y = margin_top + plot_h - ((value - min_value) / span) * plot_h
        svg.append(f'<line x1="{margin_left - 5}" y1="{y:.1f}" x2="{margin_left + plot_w}" y2="{y:.1f}" stroke="#e5e5e5" stroke-width="1"/>')
        svg.append(f'<text x="{margin_left - 10}" y="{y + 4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11" fill="#555">{value:.2f}</text>')

    for idx, row in enumerate(rows):
        value = float(row.get(metric, 0) or 0)
        x = margin_left + bar_gap + idx * (bar_w + bar_gap)
        y = margin_top + plot_h - ((value - min_value) / span) * plot_h
        bar_y = min(y, zero_y)
        bar_h = abs(zero_y - y)
        color = palette[idx % len(palette)]
        method = str(row.get("method", "method"))
        label = METHOD_LABELS.get(method, method).replace("_", "\n")
        label_lines = label.splitlines()
        svg.append(f'<rect x="{x:.1f}" y="{bar_y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{color}"/>')
        svg.append(f'<text x="{x + bar_w / 2:.1f}" y="{bar_y - 6:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#222">{value:.2f}</text>')
        label_y = height - 52
        svg.append(f'<text x="{x + bar_w / 2:.1f}" y="{label_y}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#222">')
        for line_idx, line in enumerate(label_lines):
            dy = 0 if line_idx == 0 else 13
            svg.append(f'<tspan x="{x + bar_w / 2:.1f}" dy="{dy}">{_esc(line)}</tspan>')
        svg.append("</text>")
    svg.append("</svg>")
    path.write_text("\n".join(svg), encoding="utf-8")
