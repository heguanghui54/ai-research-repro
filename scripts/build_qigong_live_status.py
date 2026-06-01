#!/usr/bin/env python3
"""Build one current live-status report for the Health Qigong paper package."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> object:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def run(command: list[str], *, env: dict[str, str]) -> dict[str, object]:
    proc = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-1600:],
        "stderr_tail": proc.stderr[-1600:],
    }


def site_probe(url: str) -> dict[str, object]:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return {
                "url": url,
                "ok": 200 <= response.status < 400,
                "status": response.status,
                "etag": response.headers.get("etag", ""),
                "age": response.headers.get("age", ""),
                "date": response.headers.get("date", ""),
            }
    except urllib.error.HTTPError as exc:
        return {"url": url, "ok": False, "status": exc.code, "error": str(exc)}
    except urllib.error.URLError as exc:
        return {"url": url, "ok": False, "status": None, "error": str(exc)}


def gate_counts(current_gate: object) -> dict[str, int]:
    rows = current_gate if isinstance(current_gate, list) else []
    return {status: sum(1 for row in rows if isinstance(row, dict) and row.get("status") == status) for status in ["pass", "warn", "fail"]}


def p0_nonpass(current_gate: object) -> list[str]:
    rows = current_gate if isinstance(current_gate, list) else []
    return [
        str(row.get("gate"))
        for row in rows
        if isinstance(row, dict) and row.get("priority") == "P0" and row.get("status") != "pass"
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a live status report for the qigong paper production package.")
    parser.add_argument("--refresh-web", action="store_true", help="Refresh Supabase web-coding export before building status.")
    parser.add_argument("--admin-code", default=os.environ.get("QIGONG_CODING_ADMIN_CODE"))
    parser.add_argument("--site-url", default="https://ai-research-repro.vercel.app")
    parser.add_argument("--output-json", default="runs/qigong_platform/formal_merge/live_status_current.json")
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/live_status_current.md")
    args = parser.parse_args()

    env = os.environ.copy()
    if args.admin_code:
        env["QIGONG_CODING_ADMIN_CODE"] = args.admin_code

    steps: list[dict[str, object]] = []
    if args.refresh_web:
        if not args.admin_code:
            raise SystemExit("Missing QIGONG_CODING_ADMIN_CODE for --refresh-web. Run without --refresh-web for an offline status report.")
        steps.append(run([sys.executable, "scripts/build_qigong_web_coding_progress.py", "--refresh"], env=env))
    else:
        steps.append(run([sys.executable, "scripts/build_qigong_web_coding_progress.py"], env=env))

    steps.append(run([sys.executable, "scripts/build_qigong_current_submission_gate.py"], env=env))

    progress = read_json(ROOT / "runs/qigong_platform/formal_merge/web_coding_student_progress.json")
    current_gate = read_json(ROOT / "runs/qigong_platform/formal_merge/current_submission_gate.json")
    video_preflight = read_json(ROOT / "runs/qigong_platform/formal_merge/video_file_preflight.json")
    comment_audit = read_json(ROOT / "runs/qigong_platform/formal_merge/comment_audit.json")
    reliability_gate = read_json(ROOT / "runs/qigong_platform/formal_merge/web_reliability_gate.json")
    probe = site_probe(args.site_url)

    video_summary = video_preflight.get("summary", {}) if isinstance(video_preflight, dict) else {}
    comment_rows = comment_audit if isinstance(comment_audit, list) else []
    reliability_rows = reliability_gate if isinstance(reliability_gate, list) else []
    payload = {
        "steps": steps,
        "web_progress_source": "supabase_refreshed" if args.refresh_web else "local_snapshot",
        "site_probe": probe,
        "web_progress": progress or {},
        "current_gate_counts": gate_counts(current_gate),
        "p0_nonpass": p0_nonpass(current_gate),
        "video_preflight_summary": video_summary,
        "comment_audit_counts": gate_counts(comment_rows),
        "web_reliability_counts": gate_counts(reliability_rows),
    }

    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    progress_dict = progress if isinstance(progress, dict) else {}
    lines = [
        "# 健身气功论文当前实时状态",
        "",
        f"- web_progress_source: {payload['web_progress_source']}",
        f"- site_url: `{args.site_url}`",
        f"- site_http_ok: {probe.get('ok')} (status={probe.get('status')}, age={probe.get('age')})",
        f"- web_primary_complete: {progress_dict.get('primary_complete', 'NA')}/{progress_dict.get('primary_target', 'NA')}",
        f"- web_double_complete: {progress_dict.get('double_check_complete', 'NA')}/{progress_dict.get('double_target', 'NA')}",
        f"- web_ready_for_result_writing: {progress_dict.get('ready_for_result_writing', 'NA')}",
        f"- current_gate_counts: {payload['current_gate_counts']}",
        f"- p0_nonpass: {payload['p0_nonpass']}",
        f"- video_ready_local_rights: {video_summary.get('ready_local_rights', 'NA')}/{video_summary.get('task_rows', 'NA')}",
        f"- comment_audit_counts: {payload['comment_audit_counts']}",
        f"- web_reliability_counts: {payload['web_reliability_counts']}",
        "",
        "## 学生编码",
        "",
        "| 学生 | 主完成 | 主剩余 | 复核完成 | 复核剩余 | 最后更新时间 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for student, stats in dict(progress_dict.get("students") or {}).items():
        lines.append(
            f"| {student} | {stats.get('primary_complete', 0)} | {stats.get('primary_remaining', 0)} | "
            f"{stats.get('double_complete', 0)} | {stats.get('double_remaining', 0)} | {stats.get('last_updated_at', '')} |"
        )
    lines.extend(
        [
            "",
            "## 写作判断",
            "",
        ]
    )
    if progress_dict.get("ready_for_result_writing") and not payload["p0_nonpass"]:
        lines.append("网页人工编码和 P0 门槛已具备进入正式结果写作的条件。")
    else:
        lines.append("当前仍不能写正式结果；继续等待学生编码、典型视频和其他 P0 门槛通过。")
    output_md = ROOT / args.output_md
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.output_json)
    print(args.output_md)


if __name__ == "__main__":
    main()
