#!/usr/bin/env python3
"""Build a per-student progress report for the Health Qigong web coding task."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE_FIELDS = [
    "dominant_frame",
    "body_visibility",
    "body_count",
    "movement_tempo",
    "camera_relation",
    "text_occlusion",
    "breath_cue",
    "mind_cue",
    "qi_meridian_cue",
    "risk_cue",
    "call_to_action",
    "platform_trace",
    "origin_reference",
    "supplement_mode",
    "binary_reversal",
    "recontextualization_scene",
    "visibility_centrality",
    "tempo_discipline",
    "efficacy_tagging",
    "image_trace_strength",
    "media_temporality",
    "cyber_wellness_symbol",
    "meme_density",
    "embodied_dissolution",
]


def clean(value: object) -> str:
    return str(value or "").strip()


def normalize_role(value: object) -> str:
    role = clean(value).lower()
    if role in {"double", "double_check", "double-check", "secondary", "review"}:
        return "double_check"
    return role or "missing"


def watched(row: dict[str, str]) -> bool:
    return clean(row.get("watched")).lower() in {"true", "1", "yes", "y"}


def complete(row: dict[str, str]) -> bool:
    return watched(row) and all(clean(row.get(field)) for field in CORE_FIELDS)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def run_export(admin_code: str | None) -> None:
    env = os.environ.copy()
    if admin_code:
        env["QIGONG_CODING_ADMIN_CODE"] = admin_code
    command = [sys.executable, "scripts/export_qigong_web_coding_submissions.py"]
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def task_counts(seed_summary: dict[str, object]) -> dict[str, dict[str, int]]:
    students = {f"STU{i:02d}": {"primary_expected": 0, "double_expected": 0} for i in range(1, 11)}
    for student, count in dict(seed_summary.get("primary_tasks_by_student") or {}).items():
        if student in students:
            students[student]["primary_expected"] = int(count)
    for student, count in dict(seed_summary.get("double_tasks_by_student") or {}).items():
        if student in students:
            students[student]["double_expected"] = int(count)
    return students


def build_progress(rows: list[dict[str, str]], expected: dict[str, dict[str, int]]) -> dict[str, object]:
    students = {
        student: {
            **counts,
            "primary_submitted": 0,
            "primary_complete": 0,
            "double_submitted": 0,
            "double_complete": 0,
            "last_updated_at": "",
        }
        for student, counts in expected.items()
    }
    role_totals: dict[str, int] = defaultdict(int)
    role_complete: dict[str, int] = defaultdict(int)

    for row in rows:
        student = clean(row.get("student_code")) or "missing"
        role = normalize_role(row.get("task_role"))
        is_complete = complete(row)
        role_totals[role] += 1
        if is_complete:
            role_complete[role] += 1
        if student not in students:
            students[student] = {
                "primary_expected": 0,
                "double_expected": 0,
                "primary_submitted": 0,
                "primary_complete": 0,
                "double_submitted": 0,
                "double_complete": 0,
                "last_updated_at": "",
            }
        if role == "double_check":
            students[student]["double_submitted"] += 1
            if is_complete:
                students[student]["double_complete"] += 1
        elif role == "primary":
            students[student]["primary_submitted"] += 1
            if is_complete:
                students[student]["primary_complete"] += 1
        updated = clean(row.get("updated_at") or row.get("submitted_at"))
        if updated and updated > students[student]["last_updated_at"]:
            students[student]["last_updated_at"] = updated

    for stats in students.values():
        stats["primary_remaining"] = max(0, stats["primary_expected"] - stats["primary_complete"])
        stats["double_remaining"] = max(0, stats["double_expected"] - stats["double_complete"])
        stats["total_expected"] = stats["primary_expected"] + stats["double_expected"]
        stats["total_complete"] = stats["primary_complete"] + stats["double_complete"]
        stats["total_remaining"] = max(0, stats["total_expected"] - stats["total_complete"])

    primary_target = sum(stats["primary_expected"] for stats in students.values())
    double_target = sum(stats["double_expected"] for stats in students.values())
    primary_complete = sum(stats["primary_complete"] for stats in students.values())
    double_complete = sum(stats["double_complete"] for stats in students.values())
    return {
        "primary_target": primary_target,
        "double_target": double_target,
        "total_target": primary_target + double_target,
        "submission_rows": len(rows),
        "primary_submissions": role_totals.get("primary", 0),
        "double_check_submissions": role_totals.get("double_check", 0),
        "primary_complete": primary_complete,
        "double_check_complete": double_complete,
        "total_complete": primary_complete + double_complete,
        "ready_for_result_writing": primary_complete >= primary_target and double_complete >= double_target,
        "students": dict(sorted(students.items())),
    }


def write_markdown(path: Path, progress: dict[str, object], *, export_csv: str) -> None:
    lines = [
        "# 学生网页编码进度监控",
        "",
        f"- Export CSV: `{export_csv}`",
        f"- 主编码完成: {progress['primary_complete']}/{progress['primary_target']}",
        f"- 复核编码完成: {progress['double_check_complete']}/{progress['double_target']}",
        f"- 总完成: {progress['total_complete']}/{progress['total_target']}",
        f"- ready_for_result_writing: {progress['ready_for_result_writing']}",
        "",
        "## 按学生统计",
        "",
        "| 学生 | 主任务 | 主完成 | 主剩余 | 复核任务 | 复核完成 | 复核剩余 | 最后更新时间 |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for student, stats in progress["students"].items():
        lines.append(
            "| {student} | {primary_expected} | {primary_complete} | {primary_remaining} | "
            "{double_expected} | {double_complete} | {double_remaining} | {last_updated_at} |".format(
                student=student,
                **stats,
            )
        )
    lines.extend(
        [
            "",
            "## 解释边界",
            "",
            "- 未达到 120 条主编码与 24 条复核编码前，论文不能报告正式人工编码结果。",
            "- 复核编码用于一致性分析，不替代主编码。",
            "- 若某学生长时间无更新时间，优先单独提醒该学生完成有视频链接的任务。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build per-student progress for the qigong web coding collection.")
    parser.add_argument("--refresh", action="store_true", help="Refresh web export before building progress.")
    parser.add_argument("--admin-code", default=os.environ.get("QIGONG_CODING_ADMIN_CODE"))
    parser.add_argument("--web-export", default="runs/qigong_platform/formal_merge/web_coding_submissions_export.csv")
    parser.add_argument("--seed-summary", default="runs/qigong_platform/formal_merge/coding_web_seed_summary.json")
    parser.add_argument("--output-json", default="runs/qigong_platform/formal_merge/web_coding_student_progress.json")
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/web_coding_student_progress.md")
    args = parser.parse_args()

    if args.refresh:
        run_export(args.admin_code)

    expected = task_counts(read_json(ROOT / args.seed_summary))
    progress = build_progress(read_csv(ROOT / args.web_export), expected)
    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(ROOT / args.output_md, progress, export_csv=args.web_export)
    print(args.output_json)
    print(args.output_md)


if __name__ == "__main__":
    main()
