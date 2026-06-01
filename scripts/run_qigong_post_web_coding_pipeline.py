#!/usr/bin/env python3
"""Run the post-student web-coding pipeline for the qigong paper."""

from __future__ import annotations

import argparse
import json
import os
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


def run_step(name: str, command: list[str], *, env: dict[str, str], dry_run: bool) -> Step:
    if dry_run:
        return Step(name, "dry_run", command, None, "", "")
    proc = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
    return Step(name, "pass" if proc.returncode == 0 else "fail", command, proc.returncode, tail(proc.stdout), tail(proc.stderr))


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {"rows": payload}


def write_report(path: Path, steps: list[Step], *, dry_run: bool) -> None:
    summary = {
        "dry_run": dry_run,
        "steps": [asdict(step) for step in steps],
        "web_export_summary": read_json(ROOT / "runs/qigong_platform/formal_merge/web_coding_submissions_export_summary.json"),
        "web_ingest_audit": read_json(ROOT / "runs/qigong_platform/formal_merge/web_coding_ingest_audit.json"),
        "current_submission_gate": read_json(ROOT / "runs/qigong_platform/formal_merge/current_submission_gate.json"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    json_path = path.with_suffix(".json")
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# 学生网页编码回收后处理流水线报告",
        "",
        f"- dry_run: {dry_run}",
        f"- step_count: {len(steps)}",
        f"- failed_steps: {[step.name for step in steps if step.status == 'fail']}",
        "",
        "## Steps",
        "",
        "| Step | Status | Command |",
        "|---|---|---|",
    ]
    for step in steps:
        command = " ".join(step.command).replace("|", "\\|")
        lines.append(f"| {step.name} | {step.status} | `{command}` |")

    web = summary["web_export_summary"]
    ingest = summary["web_ingest_audit"]
    lines.extend(
        [
            "",
            "## Current Data Gate",
            "",
            f"- 完整提交行数: {web.get('complete_rows', 'NA')}",
            f"- 主编码提交: {web.get('primary_submissions', 'NA')}",
            f"- 双编码提交: {web.get('double_check_submissions', 'NA')}",
            f"- 合并后完整主编码: {ingest.get('complete_main_rows_after_merge', 'NA')}",
            f"- ready_for_formal_audit: {ingest.get('ready_for_formal_audit', 'NA')}",
            "",
            "## Interpretation",
            "",
        ]
    )
    if ingest.get("ready_for_formal_audit"):
        lines.append("网页人工编码已经达到进入正式编码值审计和结果表生成的最低门槛。下一步检查双编码一致性和结果表。")
    else:
        lines.append("网页人工编码尚未达到正式结果写作门槛。论文仍应保持 v0.8 当前证据稿写法，不报告人工编码分布。")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export, ingest, audit, and gate Health Qigong web coding submissions.")
    parser.add_argument("--admin-code", default=os.environ.get("QIGONG_CODING_ADMIN_CODE"))
    parser.add_argument("--dry-run", action="store_true", help="Print and report the planned commands without contacting Supabase.")
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/post_web_coding_pipeline_report.md")
    args = parser.parse_args()

    env = os.environ.copy()
    if args.admin_code:
        env["QIGONG_CODING_ADMIN_CODE"] = args.admin_code
    elif not args.dry_run:
        raise SystemExit(
            "Missing QIGONG_CODING_ADMIN_CODE. Set it in the environment or pass --admin-code. "
            "Do not commit or paste the private admin code into public documents."
        )

    py = sys.executable
    commands = [
        (
            "export_web_submissions",
            [py, "scripts/export_qigong_web_coding_submissions.py"],
        ),
        (
            "ingest_web_submissions",
            [py, "scripts/ingest_qigong_web_coding_submissions.py", "--overwrite"],
        ),
        (
            "audit_human_coding_values",
            [
                py,
                "scripts/audit_qigong_coding_values.py",
                "--coding",
                "runs/qigong_platform/formal_merge/qigong_human_coding_from_web.csv",
                "--profile",
                "formal",
                "--output-md",
                "runs/qigong_platform/formal_merge/web_human_coding_values_audit.md",
                "--output-json",
                "runs/qigong_platform/formal_merge/web_human_coding_values_audit.json",
                "--output-errors",
                "runs/qigong_platform/formal_merge/web_human_coding_value_errors.csv",
            ],
        ),
        (
            "build_result_tables",
            [
                py,
                "scripts/build_qigong_result_tables.py",
                "--coding",
                "runs/qigong_platform/formal_merge/qigong_human_coding_from_web.csv",
                "--output-dir",
                "runs/qigong_platform/formal_merge/tables_from_web_coding",
            ],
        ),
        (
            "refresh_submission_gate",
            [py, "scripts/build_qigong_current_submission_gate.py"],
        ),
    ]

    steps: list[Step] = []
    for name, command in commands:
        step = run_step(name, command, env=env, dry_run=args.dry_run)
        steps.append(step)
        if step.status == "fail":
            break

    write_report(ROOT / args.output_md, steps, dry_run=args.dry_run)
    print(ROOT / args.output_md)
    if any(step.status == "fail" for step in steps):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
