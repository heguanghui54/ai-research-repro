from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def clean(value: str | None) -> str:
    return (value or "").strip()


def required_video_ids(value: str) -> set[str]:
    return {item.strip() for item in value.split(",") if item.strip()}


def expected_rows(manifest: list[dict[str, str]], tasks: list[dict[str, str]]) -> list[dict[str, str]]:
    if tasks:
        return tasks
    rows: list[dict[str, str]] = []
    for row in manifest:
        video_id = clean(row.get("video_id"))
        if not video_id:
            continue
        rows.append(
            {
                "video_id": video_id,
                "required_file_name": f"{video_id}.mp4",
                "case_role": clean(row.get("case_role")),
                "comparison_group": clean(row.get("comparison_group")),
                "routine": clean(row.get("routine")),
                "action_segment": clean(row.get("action_segment")),
                "expected_use": clean(row.get("expected_use")),
                "current_rights_status": clean(row.get("rights_status")),
                "target_rights_status": "rights_confirmed",
                "local_video_path_to_fill": f"data/private/qigong_typical_videos/{video_id}.mp4",
            }
        )
    return rows


def file_exists(path_text: str, video_dir: Path) -> bool:
    if not path_text:
        return False
    path = Path(path_text)
    if path.is_absolute():
        return path.exists()
    if path.exists():
        return True
    return (video_dir / path.name).exists()


def manifest_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {clean(row.get("video_id")): row for row in rows if clean(row.get("video_id"))}


def scan_unexpected_files(video_dir: Path, expected_names: set[str]) -> list[Path]:
    if not video_dir.exists():
        return []
    files = [path for path in video_dir.rglob("*") if path.is_file()]
    media_files = [path for path in files if path.suffix.lower() in VIDEO_SUFFIXES]
    return sorted(path for path in media_files if path.name not in expected_names)


def audit(args: argparse.Namespace) -> tuple[list[dict[str, object]], list[dict[str, str]], dict[str, object]]:
    video_dir = Path(args.video_dir)
    required_ids = required_video_ids(args.required_video_ids)
    manifest_rows = read_csv(Path(args.manifest))
    task_rows = expected_rows(manifest_rows, read_csv(Path(args.tasks_csv)))
    manifest_lookup = manifest_by_id(manifest_rows)
    issues: list[dict[str, str]] = []
    row_summaries: list[dict[str, object]] = []
    ready_local_rights = 0
    required_ready = 0

    for task in task_rows:
        video_id = clean(task.get("video_id"))
        required_case = video_id in required_ids
        manifest_row = manifest_lookup.get(video_id, {})
        required_name = clean(task.get("required_file_name")) or f"{video_id}.mp4"
        expected_path = video_dir / required_name
        manifest_local_path = clean(manifest_row.get("local_video_path"))
        task_local_path = clean(task.get("local_video_path_to_fill"))
        rights_status = clean(manifest_row.get("rights_status")) or clean(task.get("current_rights_status"))
        target_rights = clean(task.get("target_rights_status")) or "rights_confirmed"
        expected_use = clean(manifest_row.get("expected_use")) or clean(task.get("expected_use"))
        exists_by_required_name = expected_path.exists()
        exists_by_manifest = file_exists(manifest_local_path, video_dir)
        exists_by_task = file_exists(task_local_path, video_dir)
        has_local_file = exists_by_required_name or exists_by_manifest or exists_by_task
        suffix_ok = Path(required_name).suffix.lower() in VIDEO_SUFFIXES
        rights_ready = rights_status == "rights_confirmed"
        ready = has_local_file and suffix_ok and rights_ready
        if ready:
            ready_local_rights += 1
            if required_case:
                required_ready += 1

        if not video_id:
            issues.append({"video_id": "", "field": "video_id", "issue": "missing_video_id", "value": "", "fix": "Each acquisition task must have a video_id."})
        if video_id and video_id not in manifest_lookup:
            issues.append({"video_id": video_id, "field": "manifest", "issue": "missing_manifest_row", "value": video_id, "fix": "Add the typical case to data/qigong_video_manifest.csv."})
        if not suffix_ok:
            issues.append({"video_id": video_id, "field": "required_file_name", "issue": "unsupported_suffix", "value": required_name, "fix": "Use one of: " + ";".join(sorted(VIDEO_SUFFIXES))})
        if not has_local_file:
            issues.append({"video_id": video_id, "field": "local_video_path", "issue": "missing_local_file", "value": str(expected_path), "fix": "Place a rights-confirmed local file at this path, or keep the case as manual_view_only."})
        if has_local_file and not rights_ready:
            issues.append({"video_id": video_id, "field": "rights_status", "issue": "local_file_without_rights_confirmed", "value": rights_status, "fix": "Confirm permission first, then update rights_status=rights_confirmed in the manifest."})
        if target_rights != "rights_confirmed":
            issues.append({"video_id": video_id, "field": "target_rights_status", "issue": "non_rights_confirmed_target", "value": target_rights, "fix": "Local extraction requires target_rights_status=rights_confirmed."})
        if not expected_use:
            issues.append({"video_id": video_id, "field": "expected_use", "issue": "missing_expected_use", "value": "", "fix": "Specify pose_feature_and_frame_coding or frame_coding_only."})

        row_summaries.append(
            {
                "video_id": video_id,
                "required_file_name": required_name,
                "case_role": clean(task.get("case_role")) or clean(manifest_row.get("case_role")),
                "routine": clean(task.get("routine")) or clean(manifest_row.get("routine")),
                "rights_status": rights_status,
                "required_case": required_case,
                "has_local_file": has_local_file,
                "exists_by_required_name": exists_by_required_name,
                "exists_by_manifest_path": exists_by_manifest,
                "suffix_ok": suffix_ok,
                "ready_for_local_extraction": ready,
            }
        )

    expected_names = {clean(row.get("required_file_name")) for row in task_rows if clean(row.get("required_file_name"))}
    for path in scan_unexpected_files(video_dir, expected_names):
        issues.append({"video_id": "", "field": "video_dir", "issue": "unexpected_file", "value": str(path), "fix": "Keep only expected, rights-confirmed typical-case videos in the private folder."})

    role_counts = Counter(str(row.get("case_role", "")) for row in row_summaries if row.get("case_role"))
    required_issue_count = sum(1 for issue in issues if clean(issue.get("video_id")) in required_ids or not clean(issue.get("video_id")))
    missing_required_ids = sorted(
        video_id
        for video_id in required_ids
        if not any(row.get("video_id") == video_id and row.get("ready_for_local_extraction") for row in row_summaries)
    )
    summary = {
        "manifest": args.manifest,
        "tasks_csv": args.tasks_csv,
        "video_dir": args.video_dir,
        "task_rows": len(task_rows),
        "manifest_rows": len(manifest_rows),
        "ready_local_rights": ready_local_rights,
        "min_ready_local_rights": args.min_ready_local_rights,
        "required_video_ids": sorted(required_ids),
        "required_ready": required_ready,
        "missing_required_ids": missing_required_ids,
        "video_dir_exists": video_dir.exists(),
        "issue_count": len(issues),
        "required_issue_count": required_issue_count,
        "role_counts": dict(role_counts),
        "ready": ready_local_rights >= args.min_ready_local_rights and not missing_required_ids and required_issue_count == 0,
    }
    return row_summaries, issues, summary


def write_issues(path: Path, issues: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["video_id", "field", "issue", "value", "fix"]
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: issue.get(field, "") for field in fields} for issue in issues)


def write_markdown(path: Path, row_summaries: list[dict[str, object]], issues: list[dict[str, str]], summary: dict[str, object], issues_csv: str) -> None:
    counts = Counter(["pass" if summary["ready"] else "fail"])
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Typical-Case Video File Preflight",
        "",
        "This preflight checks whether rights-confirmed local video files are ready for the embodied video layer. It is a workflow gate, not empirical evidence.",
        "",
        f"- Manifest: `{summary['manifest']}`",
        f"- Task CSV: `{summary['tasks_csv']}`",
        f"- Video directory: `{summary['video_dir']}`",
        f"- Issue CSV: `{issues_csv}`",
        f"- Summary: pass={counts.get('pass', 0)}, fail={counts.get('fail', 0)}",
        f"- Ready local rights-confirmed files: {summary['ready_local_rights']}/{summary['task_rows']} (target >= {summary['min_ready_local_rights']})",
        f"- Required ready: {summary['required_ready']}/{len(summary['required_video_ids'])} ({', '.join(summary['required_video_ids'])})",
        f"- Missing required IDs: {summary['missing_required_ids']}",
        f"- Issue count: {summary['issue_count']}",
        f"- Required issue count: {summary['required_issue_count']}",
        "",
        "## Typical Cases",
        "",
        "| Video ID | Required | Required File | Case Role | Routine | Rights Status | Local File | Ready |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in row_summaries:
        lines.append(
            f"| {row['video_id']} | {row['required_case']} | `{row['required_file_name']}` | {row['case_role']} | {row['routine']} | {row['rights_status']} | {row['has_local_file']} | {row['ready_for_local_extraction']} |"
        )
    issue_counts = Counter(issue["issue"] for issue in issues)
    lines.extend(["", "## Issue Summary", ""])
    if issue_counts:
        for issue, count in sorted(issue_counts.items(), key=lambda pair: (-pair[1], pair[0])):
            lines.append(f"- `{issue}`: {count}")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Safe Next Commands",
            "",
            "```bash",
            "python scripts/fill_qigong_video_manifest_from_files.py --manifest data/qigong_video_manifest.csv --video-dir data/private/qigong_typical_videos --output-manifest data/qigong_video_manifest.csv --absolute-paths --replace-existing",
            "python scripts/audit_qigong_video_manifest.py --manifest data/qigong_video_manifest.csv --metadata data/qigong_platform_metadata_formal.csv --profile formal --output-md runs/qigong_platform/audit/video_manifest_audit.md --output-json runs/qigong_platform/audit/video_manifest_audit.json",
            "python scripts/audit_sportslabkit_environment.py --video-manifest data/qigong_video_manifest.csv --output-md runs/qigong_platform/audit/sportslabkit_environment_audit.md --output-json runs/qigong_platform/audit/sportslabkit_environment_audit.json",
            "python scripts/sample_qigong_video_frames.py --manifest data/qigong_video_manifest.csv --output-root runs/qigong_platform/llm_frames --frame-index runs/qigong_platform/llm_frames_index.csv --max-frames 4",
            "python scripts/extract_qigong_video_features.py --manifest data/qigong_video_manifest.csv --output runs/qigong_platform/features/video_features.csv",
            "```",
            "",
            "Only run local extraction after the relevant manifest rows already state `rights_status=rights_confirmed` based on human rights review.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preflight-check local files for the Health Qigong typical-case video analysis layer.")
    parser.add_argument("--manifest", default="data/qigong_video_manifest.csv")
    parser.add_argument("--tasks-csv", default="runs/qigong_platform/formal_merge/video_acquisition_tasks/video_acquisition_tasks.csv")
    parser.add_argument("--video-dir", default="data/private/qigong_typical_videos")
    parser.add_argument("--min-ready-local-rights", type=int, default=3)
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/video_file_preflight.md")
    parser.add_argument("--output-json", default="runs/qigong_platform/formal_merge/video_file_preflight.json")
    parser.add_argument("--issues-csv", default="runs/qigong_platform/formal_merge/video_file_preflight_issues.csv")
    parser.add_argument("--required-video-ids", default="TC0001,TC0002,TC0003")
    args = parser.parse_args()

    row_summaries, issues, summary = audit(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps({"summary": summary, "rows": row_summaries, "issues": issues}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_issues(Path(args.issues_csv), issues)
    write_markdown(Path(args.output_md), row_summaries, issues, summary, args.issues_csv)
    print(args.output_md)
    print(args.output_json)
    print(args.issues_csv)


if __name__ == "__main__":
    main()
