#!/usr/bin/env python3
"""Run the post-upload typical-video pipeline for the qigong paper."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO_DIR = "data/private/qigong_typical_videos"
FILLED_MANIFEST = "runs/qigong_platform/formal_merge/qigong_video_manifest_filled_from_files.csv"
PREFLIGHT_JSON = ROOT / "runs/qigong_platform/formal_merge/video_file_preflight.json"


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


def run_command(name: str, command: list[str], *, dry_run: bool) -> Step:
    if dry_run:
        return Step(name, "dry_run", command, None, "", "")
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return Step(name, "pass" if proc.returncode == 0 else "fail", command, proc.returncode, tail(proc.stdout), tail(proc.stderr))


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {"rows": payload}


def preflight_ready() -> bool:
    payload = read_json(PREFLIGHT_JSON)
    summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
    return bool(summary.get("ready")) and int(summary.get("ready_local_rights", 0) or 0) >= int(summary.get("min_ready_local_rights", 3) or 3)


def write_report(path: Path, steps: list[Step], *, dry_run: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    preflight = read_json(PREFLIGHT_JSON)
    sports_env = read_json(ROOT / "runs/qigong_platform/formal_merge/sportslabkit_environment_audit.json")
    summary = {
        "dry_run": dry_run,
        "steps": [asdict(step) for step in steps],
        "video_file_preflight": preflight,
        "sportslabkit_environment": sports_env,
    }
    path.with_suffix(".json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    preflight_summary = preflight.get("summary", {}) if isinstance(preflight, dict) else {}
    lines = [
        "# 典型视频上传后处理流水线报告",
        "",
        f"- dry_run: {dry_run}",
        f"- step_count: {len(steps)}",
        f"- failed_steps: {[step.name for step in steps if step.status == 'fail']}",
        f"- ready_local_rights: {preflight_summary.get('ready_local_rights', 'NA')}/{preflight_summary.get('task_rows', 'NA')}",
        f"- ready: {preflight_summary.get('ready', 'NA')}",
        "",
        "## Steps",
        "",
        "| Step | Status | Command |",
        "|---|---|---|",
    ]
    for step in steps:
        command = " ".join(step.command).replace("|", "\\|")
        lines.append(f"| {step.name} | {step.status} | `{command}` |")
    lines.extend(["", "## Interpretation", ""])
    if preflight_summary.get("ready"):
        lines.append("典型视频已经达到本地权利确认与文件预检门槛；若特征提取和环境审计也通过，可以进入典型案例身体证据写作。")
    else:
        lines.append("典型视频尚未达到身体证据写作门槛。论文仍只能写视频分析层的设计、边界和待完成任务。")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill, preflight, and analyze uploaded local typical-case qigong videos.")
    parser.add_argument("--video-dir", default=DEFAULT_VIDEO_DIR)
    parser.add_argument("--manifest", default="data/qigong_video_manifest.csv")
    parser.add_argument("--filled-manifest", default=FILLED_MANIFEST)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--mark-rights-confirmed", action="store_true", help="Only use after human rights review confirms local analysis permission.")
    parser.add_argument("--skip-extraction-if-not-ready", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/post_video_upload_pipeline_report.md")
    args = parser.parse_args()

    py = sys.executable
    fill_cmd = [
        py,
        "scripts/fill_qigong_video_manifest_from_files.py",
        "--manifest",
        args.manifest,
        "--video-dir",
        args.video_dir,
        "--output-manifest",
        args.filled_manifest,
        "--absolute-paths",
        "--replace-existing",
    ]
    if args.mark_rights_confirmed:
        fill_cmd.append("--set-rights-confirmed")

    commands_before_gate = [
        ("fill_manifest_from_files", fill_cmd),
        (
            "video_file_preflight",
            [
                py,
                "scripts/audit_qigong_video_files_preflight.py",
                "--manifest",
                args.filled_manifest,
                "--tasks-csv",
                "runs/qigong_platform/formal_merge/video_acquisition_tasks/video_acquisition_tasks.csv",
                "--video-dir",
                args.video_dir,
            ],
        ),
        (
            "audit_sportslabkit_environment",
            [
                py,
                "scripts/audit_sportslabkit_environment.py",
                "--video-manifest",
                args.filled_manifest,
                "--output-md",
                "runs/qigong_platform/formal_merge/sportslabkit_environment_audit.md",
                "--output-json",
                "runs/qigong_platform/formal_merge/sportslabkit_environment_audit.json",
            ],
        ),
    ]
    commands_after_gate = [
        (
            "sample_video_frames",
            [
                py,
                "scripts/sample_qigong_video_frames.py",
                "--manifest",
                args.filled_manifest,
                "--output-root",
                "runs/qigong_platform/formal_merge/typical_video_frames",
                "--frame-index",
                "runs/qigong_platform/formal_merge/typical_video_frames_index.csv",
                "--max-frames",
                "4",
            ],
        ),
        (
            "extract_video_features",
            [
                py,
                "scripts/extract_qigong_video_features.py",
                "--manifest",
                args.filled_manifest,
                "--output",
                "runs/qigong_platform/formal_merge/video_features_from_typical_cases.csv",
            ],
        ),
        ("refresh_submission_gate", [py, "scripts/build_qigong_current_submission_gate.py"]),
    ]

    steps: list[Step] = []
    for name, command in commands_before_gate:
        step = run_command(name, command, dry_run=args.dry_run)
        steps.append(step)
        if step.status == "fail":
            write_report(ROOT / args.output_md, steps, dry_run=args.dry_run)
            raise SystemExit(1)

    should_extract = args.dry_run or not args.skip_extraction_if_not_ready or preflight_ready()
    if should_extract:
        for name, command in commands_after_gate:
            step = run_command(name, command, dry_run=args.dry_run)
            steps.append(step)
            if step.status == "fail":
                write_report(ROOT / args.output_md, steps, dry_run=args.dry_run)
                raise SystemExit(1)
    else:
        steps.append(Step("skip_frame_and_feature_extraction", "skipped", [], None, "", "preflight not ready"))
        step = run_command("refresh_submission_gate", [py, "scripts/build_qigong_current_submission_gate.py"], dry_run=args.dry_run)
        steps.append(step)

    write_report(ROOT / args.output_md, steps, dry_run=args.dry_run)
    print(ROOT / args.output_md)


if __name__ == "__main__":
    main()
