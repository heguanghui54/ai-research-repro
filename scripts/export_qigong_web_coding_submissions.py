from __future__ import annotations

import argparse
import csv
import json
import os
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path


FIELDS = [
    "video_id",
    "priority",
    "platform",
    "keyword",
    "title",
    "student_code",
    "student_name",
    "task_role",
    "watched",
    "video_access_status",
    "dominant_frame",
    "body_visibility",
    "movement_tempo",
    "origin_reference",
    "supplement_mode",
    "binary_reversal",
    "visibility_centrality",
    "tempo_discipline",
    "efficacy_tagging",
    "image_trace_strength",
    "media_temporality",
    "meme_density",
    "embodied_dissolution",
    "trace_markers",
    "notes",
    "submitted_at",
    "updated_at",
]

CORE_FIELDS = [
    "dominant_frame",
    "body_visibility",
    "movement_tempo",
    "origin_reference",
    "supplement_mode",
    "binary_reversal",
    "visibility_centrality",
    "tempo_discipline",
    "efficacy_tagging",
    "image_trace_strength",
    "media_temporality",
    "meme_density",
    "embodied_dissolution",
]


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def request_json(url: str, key: str) -> list[dict[str, object]]:
    request = urllib.request.Request(
        url,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Supabase export failed: HTTP {exc.code}: {body}") from exc
    if not isinstance(payload, list):
        raise SystemExit(f"Unexpected Supabase payload: {payload!r}")
    return payload


def rpc_json(url: str, key: str, payload: dict[str, object]) -> list[dict[str, object]]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Supabase export failed: HTTP {exc.code}: {body}") from exc
    if not isinstance(data, list):
        raise SystemExit(f"Unexpected Supabase RPC payload: {data!r}")
    return data


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def summarize(rows: list[dict[str, object]], expected_tasks: int) -> dict[str, object]:
    complete_rows = [
        row for row in rows
        if all(clean(row.get(field)) for field in CORE_FIELDS) and str(row.get("watched")).lower() in {"true", "1"}
    ]
    by_student = Counter(clean(row.get("student_code")) or "missing" for row in rows)
    by_role = Counter(clean(row.get("task_role")) or "missing" for row in rows)
    return {
        "expected_primary_tasks": expected_tasks,
        "submission_rows": len(rows),
        "complete_rows": len(complete_rows),
        "primary_submissions": by_role.get("primary", 0),
        "double_check_submissions": by_role.get("double_check", 0),
        "students": dict(sorted(by_student.items())),
        "remaining_primary_lower_bound": max(0, expected_tasks - by_role.get("primary", 0)),
    }


def write_md(path: Path, summary: dict[str, object], csv_path: str) -> None:
    lines = [
        "# 健身气功网站人工编码导出审计",
        "",
        f"- 导出 CSV: `{csv_path}`",
        f"- 预期主编码任务: {summary['expected_primary_tasks']}",
        f"- 已提交总行数: {summary['submission_rows']}",
        f"- 完整提交行数: {summary['complete_rows']}",
        f"- 主编码提交: {summary['primary_submissions']}",
        f"- 复核编码提交: {summary['double_check_submissions']}",
        f"- 主编码剩余下限: {summary['remaining_primary_lower_bound']}",
        "",
        "## 按学生统计",
        "",
        "| 学生编号 | 提交数 |",
        "|---|---:|",
    ]
    for student, count in summary["students"].items():
        lines.append(f"| {student} | {count} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Health Qigong web coding submissions from Supabase REST API.")
    parser.add_argument("--supabase-url", default=os.environ.get("SUPABASE_URL", "https://onhfzpxxehumxmnvkxud.supabase.co"))
    parser.add_argument("--supabase-key", default=os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_eqOx34s8pYSS31I7aB55Yg_9JaZdfcS"))
    parser.add_argument("--admin-code", default=os.environ.get("QIGONG_CODING_ADMIN_CODE"))
    parser.add_argument("--output-csv", default="runs/qigong_platform/formal_merge/web_coding_submissions_export.csv")
    parser.add_argument("--summary-json", default="runs/qigong_platform/formal_merge/web_coding_submissions_export_summary.json")
    parser.add_argument("--summary-md", default="runs/qigong_platform/formal_merge/web_coding_submissions_export_summary.md")
    parser.add_argument("--expected-tasks", type=int, default=120)
    args = parser.parse_args()
    if not args.admin_code:
        raise SystemExit(
            "Missing export admin code. Set QIGONG_CODING_ADMIN_CODE or pass --admin-code. "
            "See the local private admin access note."
        )

    url = f"{args.supabase_url.rstrip('/')}/rest/v1/rpc/export_qigong_coding_submissions"
    rows = rpc_json(url, args.supabase_key, {"p_admin_code": args.admin_code})
    write_csv(Path(args.output_csv), rows, FIELDS)
    summary = summarize(rows, expected_tasks=args.expected_tasks)
    Path(args.summary_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary_json).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_md(Path(args.summary_md), summary, args.output_csv)
    print(args.output_csv)
    print(args.summary_json)
    print(args.summary_md)


if __name__ == "__main__":
    main()
