#!/usr/bin/env python3
"""Refresh current submission gates for the qigong platform paper."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Step:
    name: str
    status: str
    command: list[str]
    returncode: int | None
    stdout_tail: str
    stderr_tail: str


def tail(text: str, limit: int = 1800) -> str:
    return text[-limit:] if len(text) > limit else text


def run_step(name: str, command: list[str], *, dry_run: bool) -> Step:
    if dry_run:
        return Step(name, "dry_run", command, None, "", "")
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return Step(name, "pass" if proc.returncode == 0 else "fail", command, proc.returncode, tail(proc.stdout), tail(proc.stderr))


def read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def status_counts(payload) -> dict[str, int]:
    rows = payload.get("gates", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        if isinstance(payload, dict) and {"web_ready", "reliability_ready", "comment_ready", "video_ready"} <= set(payload):
            fail = sum(
                1
                for key in ["web_ready", "reliability_ready", "comment_ready", "video_ready"]
                if not payload.get(key)
            )
            return {"pass": 4 - fail, "warn": 0, "fail": fail}
        if isinstance(payload, dict) and "summary" in payload and isinstance(payload.get("summary"), dict):
            summary = payload["summary"]
            if "ready" in summary:
                return {"pass": 1 if summary.get("ready") else 0, "warn": 0, "fail": 0 if summary.get("ready") else 1}
        return {"pass": 0, "warn": 0, "fail": 0}
    return {status: sum(1 for row in rows if isinstance(row, dict) and row.get("status") == status) for status in ["pass", "warn", "fail"]}


def write_report(path: Path, steps: list[Step], *, dry_run: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "current_submission_gate": "runs/qigong_platform/formal_merge/current_submission_gate.json",
        "manuscript_v0_9_text_audit": "runs/qigong_platform/formal_merge/manuscript_v0_9_text_audit.json",
        "manuscript_v0_9_result_gate": "runs/qigong_platform/formal_merge/manuscript_result_brief_v0_9_gate.json",
        "manuscript_v0_9_current_evidence_audit": "runs/qigong_platform/formal_merge/manuscript_v0_9_current_evidence_audit.json",
        "web_reliability_gate": "runs/qigong_platform/formal_merge/web_reliability_gate.json",
        "video_file_preflight": "runs/qigong_platform/formal_merge/video_file_preflight.json",
        "goal_completion_current": "runs/qigong_platform/formal_merge/goal_completion_current_audit.json",
    }
    loaded = {name: read_json(ROOT / rel) for name, rel in artifacts.items()}
    counts = {name: status_counts(payload) for name, payload in loaded.items()}
    summary = {
        "dry_run": dry_run,
        "steps": [asdict(step) for step in steps],
        "artifact_paths": artifacts,
        "artifact_status_counts": counts,
    }
    path.with_suffix(".json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    failish = {name: count for name, count in counts.items() if count.get("fail", 0)}
    lines = [
        "# 当前投稿闸门套件报告",
        "",
        "本报告统一刷新 v0.9 当前证据稿、网页人工编码、双编码可靠性、典型视频、目标完成度和投稿门槛。它不替代人工终审，只用于判断哪些结果可以写入论文。",
        "",
        f"- dry_run: {dry_run}",
        f"- failed_steps: {[step.name for step in steps if step.status == 'fail']}",
        f"- artifacts_with_fail: {failish}",
        "",
        "## Steps",
        "",
        "| Step | Status | Command |",
        "|---|---|---|",
    ]
    for step in steps:
        command = " ".join(step.command).replace("|", "\\|")
        lines.append(f"| {step.name} | {step.status} | `{command}` |")
    lines.extend(["", "## Artifact Counts", "", "| Artifact | pass | warn | fail |", "|---|---:|---:|---:|"])
    for name, count in counts.items():
        lines.append(f"| {name} | {count.get('pass', 0)} | {count.get('warn', 0)} | {count.get('fail', 0)} |")
    lines.extend(["", "## Decision", ""])
    current_gate = loaded.get("current_submission_gate")
    current_counts = counts.get("current_submission_gate", {})
    if current_counts.get("fail", 0) == 0 and current_counts.get("warn", 0) == 0:
        lines.append("当前投稿总门槛已通过，可进入人工终审和格式核验。")
    else:
        lines.append("当前仍不是投稿完成态。继续等待/补齐学生网页编码、本地典型视频、评论覆盖、Ubuntu 复现和最终人工终审。")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the current gate suite for the qigong platform paper.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/current_submission_gate_suite.md")
    args = parser.parse_args()
    py = sys.executable
    commands = [
        (
            "refresh_current_submission_gate",
            [py, "scripts/build_qigong_current_submission_gate.py"],
        ),
        (
            "create_v0_9_result_brief",
            [py, "scripts/create_qigong_v0_9_result_brief.py"],
        ),
        (
            "assemble_v0_9_manuscript",
            [py, "scripts/create_qigong_manuscript_v0_9_from_results.py"],
        ),
        (
            "audit_v0_9_text",
            [
                py,
                "scripts/audit_qigong_manuscript_text.py",
                "--manuscript",
                "docs/qigong_platform_paper/manuscript_draft_v0_9_gated_results.md",
                "--research-audit-json",
                "runs/qigong_platform/formal_merge/current_submission_gate.json",
                "--output-md",
                "runs/qigong_platform/formal_merge/manuscript_v0_9_text_audit.md",
                "--output-json",
                "runs/qigong_platform/formal_merge/manuscript_v0_9_text_audit.json",
            ],
        ),
        (
            "audit_v0_9_current_evidence",
            [
                py,
                "scripts/audit_qigong_current_evidence_manuscript.py",
                "--manuscript",
                "docs/qigong_platform_paper/manuscript_draft_v0_9_gated_results.md",
                "--output-md",
                "runs/qigong_platform/formal_merge/manuscript_v0_9_current_evidence_audit.md",
                "--output-json",
                "runs/qigong_platform/formal_merge/manuscript_v0_9_current_evidence_audit.json",
            ],
        ),
        (
            "audit_web_reliability_gate",
            [py, "scripts/audit_qigong_web_reliability_gate.py"],
        ),
        (
            "video_preflight",
            [py, "scripts/audit_qigong_video_files_preflight.py"],
        ),
        (
            "goal_completion_current",
            [
                py,
                "scripts/audit_qigong_goal_completion.py",
                "--manuscript",
                "docs/qigong_platform_paper/manuscript_draft_v0_9_gated_results.md",
                "--coding",
                "runs/qigong_platform/formal_merge/qigong_human_coding_from_web.csv",
                "--output-md",
                "runs/qigong_platform/formal_merge/goal_completion_current_audit.md",
                "--output-json",
                "runs/qigong_platform/formal_merge/goal_completion_current_audit.json",
            ],
        ),
        (
            "refresh_current_submission_gate_after_audits",
            [py, "scripts/build_qigong_current_submission_gate.py"],
        ),
    ]
    steps: list[Step] = []
    for name, command in commands:
        step = run_step(name, command, dry_run=args.dry_run)
        steps.append(step)
        if step.status == "fail":
            break
    write_report(ROOT / args.output_md, steps, dry_run=args.dry_run)
    print(ROOT / args.output_md)
    if any(step.status == "fail" for step in steps):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
