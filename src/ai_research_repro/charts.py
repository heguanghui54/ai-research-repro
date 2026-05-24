from __future__ import annotations

from pathlib import Path

from .templates.nanogpt_lite import plot_history


def save_learning_curve(history: dict, path: Path) -> None:
    plot_history(history, path)

