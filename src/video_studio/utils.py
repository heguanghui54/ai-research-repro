from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def slugify(value: str) -> str:
    keep = []
    for ch in value.lower():
        if ch.isalnum():
            keep.append(ch)
        elif keep and keep[-1] != "-":
            keep.append("-")
    return "".join(keep).strip("-") or "item"


def ensure_path(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_dt(value: datetime | None) -> str:
    if not value:
        return "-"
    return value.strftime("%Y-%m-%d %H:%M:%S")


def split_bullets(text: str) -> List[str]:
    lines = []
    for raw in text.splitlines():
        line = raw.strip(" -•\t")
        if line:
            lines.append(line)
    return lines

