from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .llm import provider_status


def _git_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""


def _hardware_summary() -> dict[str, Any]:
    machine = {
        "processor": platform.processor(),
        "machine": platform.machine(),
    }
    if platform.system() == "Darwin":
        try:
            cpu = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
            mem = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()
            machine["cpu_brand"] = cpu
            machine["memory_bytes"] = int(mem)
        except Exception:
            pass
    return machine


def write_repro_manifest(
    *,
    workspace: Path,
    command: str,
    summary: dict[str, Any],
) -> dict[str, Any]:
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "python": sys.version,
        "platform": platform.platform(),
        "hardware": _hardware_summary(),
        "provider_status": provider_status(),
        "api_parameters": {
            "chat_completions": {
                "temperature": 0.2,
                "timeout_seconds": 45,
                "max_retries": 2,
            },
            "vision_chat_completions": {
                "temperature": 0.1,
                "timeout_seconds": 45,
                "max_retries": 2,
            },
            "provider_snapshot_note": "Provider-side immutable model snapshot IDs were not returned by the logged OpenAI-compatible responses.",
        },
        "git_commit": _git_output(["rev-parse", "HEAD"]),
        "git_branch": _git_output(["branch", "--show-current"]),
        "git_dirty": bool(_git_output(["status", "--short"])),
        "model": summary.get("model"),
        "role_mode": summary.get("role_mode"),
        "task_source": summary.get("task_source"),
        "task_ids": summary.get("task_ids", []),
        "seeds": summary.get("seeds", []),
        "method_count": len(summary.get("results", [])),
    }
    path = workspace / "repro_manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
