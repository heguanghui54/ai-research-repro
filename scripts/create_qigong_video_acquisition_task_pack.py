from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


VIDEO_SUFFIX = ".mp4"
FALSE_POSITIVE_TERMS = ["英语", "语法", "单词", "四六级", "考研英语", "基础教学 p", "合集片头"]
QIGONG_CONTEXT_TERMS = ["健身", "气功", "养生", "运动", "锻炼", "功法", "导引", "传统", "国家体育总局", "跟练"]


@dataclass
class VideoTask:
    video_id: str
    required_file_name: str
    case_role: str
    comparison_group: str
    routine: str
    action_segment: str
    expected_use: str
    current_rights_status: str
    target_rights_status: str
    acquisition_status: str
    local_video_path_to_fill: str
    candidate_platform_video_id: str
    candidate_url_hash: str
    candidate_title: str
    notes: str


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def score_metadata(row: dict[str, str], routine: str, action_segment: str) -> tuple[float, list[str], bool]:
    title = row.get("title", "")
    hashtags = row.get("hashtags", "")
    text = f"{title} {hashtags}"
    if any(term in text for term in FALSE_POSITIVE_TERMS) and not any(term in text for term in QIGONG_CONTEXT_TERMS):
        return 0.0, ["excluded_false_positive"], False
    score = 0.0
    reasons: list[str] = []
    matched_target = False
    if routine and routine in text:
        score += 10
        reasons.append(f"routine={routine}")
        matched_target = True
    if action_segment and action_segment in text:
        score += 8
        reasons.append(f"segment={action_segment}")
        matched_target = True
    for cue, amount in [("八段锦", 2), ("五禽戏", 2), ("六字诀", 2), ("易筋经", 2), ("健身气功", 1)]:
        if cue in text:
            score += amount
    for field, weight in [("view_count", 0.000001), ("like_count", 0.00001), ("comment_count", 0.0001)]:
        try:
            score += float(row.get(field) or 0) * weight
        except ValueError:
            pass
    if not reasons and score > 0:
        reasons.append("qigong_keyword_or_engagement")
    return score, reasons, matched_target


def candidate_rows(metadata_rows: list[dict[str, str]], manifest_rows: list[dict[str, str]], per_task: int) -> list[dict[str, str]]:
    included = [row for row in metadata_rows if (row.get("include_status") or "").strip().lower() == "included"]
    by_task: list[dict[str, str]] = []
    for task in manifest_rows:
        if (task.get("case_role") or "").strip() != "platform_variant":
            continue
        routine = (task.get("routine") or "").strip()
        action_segment = (task.get("action_segment") or "").strip()
        exact_scored = []
        fallback_scored = []
        for row in included:
            score, reasons, matched_target = score_metadata(row, routine, action_segment)
            if score <= 0:
                continue
            if matched_target or not (routine or action_segment):
                exact_scored.append((score, reasons, row))
            else:
                fallback_scored.append((score, reasons, row))
        scored = exact_scored or fallback_scored
        scored.sort(key=lambda item: (-item[0], item[2].get("video_id", "")))
        for rank, (score, reasons, row) in enumerate(scored[:per_task], start=1):
            by_task.append({
                "task_video_id": task.get("video_id", ""),
                "candidate_rank": str(rank),
                "candidate_video_id": row.get("video_id", ""),
                "platform": row.get("platform", ""),
                "url_hash": row.get("url_hash", ""),
                "keyword": row.get("keyword", ""),
                "title": row.get("title", ""),
                "hashtags": row.get("hashtags", ""),
                "view_count": row.get("view_count", ""),
                "like_count": row.get("like_count", ""),
                "comment_count": row.get("comment_count", ""),
                "download_permission": row.get("download_permission", ""),
                "comment_collection_status": row.get("comment_collection_status", ""),
                "candidate_score": f"{score:.4f}",
                "candidate_reason": ";".join(reasons),
                "selection_rule": "candidate_only_requires_manual_rights_confirmation",
            })
    return by_task


def build_tasks(manifest_rows: list[dict[str, str]], candidates: list[dict[str, str]], video_dir: Path) -> list[VideoTask]:
    first_candidate: dict[str, dict[str, str]] = {}
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        grouped[row.get("task_video_id", "")].append(row)
    for key, rows in grouped.items():
        rows.sort(key=lambda row: int(row.get("candidate_rank") or 9999))
        if rows:
            first_candidate[key] = rows[0]

    tasks: list[VideoTask] = []
    for row in manifest_rows:
        video_id = (row.get("video_id") or "").strip()
        if not video_id:
            continue
        candidate = first_candidate.get(video_id, {})
        required_file = f"{video_id}{VIDEO_SUFFIX}"
        local_path = video_dir / required_file
        case_role = (row.get("case_role") or "").strip()
        target_rights = "rights_confirmed" if case_role in {"standard_reference", "platform_variant"} else (row.get("rights_status") or "").strip()
        tasks.append(
            VideoTask(
                video_id=video_id,
                required_file_name=required_file,
                case_role=case_role,
                comparison_group=row.get("comparison_group", ""),
                routine=row.get("routine", ""),
                action_segment=row.get("action_segment", ""),
                expected_use=row.get("expected_use", ""),
                current_rights_status=row.get("rights_status", ""),
                target_rights_status=target_rights,
                acquisition_status="needs_local_file" if not row.get("local_video_path") else "check_existing_file",
                local_video_path_to_fill=str(local_path),
                candidate_platform_video_id=candidate.get("candidate_video_id", ""),
                candidate_url_hash=candidate.get("url_hash", ""),
                candidate_title=candidate.get("title", ""),
                notes="standard case may use an official/self-recorded rights-confirmed reference" if case_role == "standard_reference" else "candidate must be manually verified and rights-confirmed before local analysis",
            )
        )
    return tasks


def write_readme(path: Path, *, video_dir: Path, manifest: Path, task_csv: Path, candidate_csv: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Typical-Case Video Acquisition Task Pack",
        "",
        "This pack prepares the embodied sports-video evidence layer. It does not create empirical video results; it defines what must be legally acquired before SportsLabKit/OpenCV/MediaPipe extraction can be run.",
        "",
        "## Targets",
        "",
        f"- Manifest: `{manifest}`",
        f"- Video directory: `{video_dir}`",
        f"- Task sheet: `{task_csv}`",
        f"- Candidate sheet: `{candidate_csv}`",
        f"- Required task rows: {summary['task_rows']}",
        f"- Platform candidate rows: {summary['candidate_rows']}",
        "",
        "## File Rules",
        "",
        "- Put only rights-confirmed local files in the video directory.",
        "- Name files exactly as `TC0001.mp4`, `TC0002.mp4`, etc. so `fill_qigong_video_manifest_from_files.py` can match them automatically.",
        "- Do not download or store videos when permission is unclear; keep those rows as `manual_view_only`.",
        "- Platform candidate rows are suggestions for manual selection, not authorization to download.",
        "",
        "## After Files Are Ready",
        "",
        "```bash",
        f"python scripts/audit_qigong_video_files_preflight.py --manifest {manifest} --tasks-csv {task_csv} --video-dir {video_dir}",
        f"python scripts/fill_qigong_video_manifest_from_files.py --manifest {manifest} --video-dir {video_dir} --output-manifest {manifest} --absolute-paths --replace-existing",
        f"python scripts/audit_qigong_video_manifest.py --manifest {manifest} --metadata data/qigong_platform_metadata_formal.csv --profile formal --output-md runs/qigong_platform/audit/video_manifest_audit.md --output-json runs/qigong_platform/audit/video_manifest_audit.json",
        f"python scripts/audit_sportslabkit_environment.py --video-manifest {manifest} --output-md runs/qigong_platform/audit/sportslabkit_environment_audit.md --output-json runs/qigong_platform/audit/sportslabkit_environment_audit.json",
        f"python scripts/sample_qigong_video_frames.py --manifest {manifest} --output-root runs/qigong_platform/llm_frames --frame-index runs/qigong_platform/llm_frames_index.csv --max-frames 4",
        f"python scripts/extract_qigong_video_features.py --manifest {manifest} --output runs/qigong_platform/features/video_features.csv",
        "python scripts/refresh_qigong_readiness_dashboards.py",
        "```",
        "",
        "Do not use a script flag to mark rights automatically. Confirm permissions first, then update `rights_status=rights_confirmed` in the manifest before local frame sampling or SportsLabKit/OpenCV extraction.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a rights-confirmed typical-case video acquisition task pack.")
    parser.add_argument("--manifest", default="data/qigong_video_manifest.csv")
    parser.add_argument("--metadata", default="data/qigong_platform_metadata_coding_sample.csv")
    parser.add_argument("--video-dir", default="data/private/qigong_typical_videos")
    parser.add_argument("--output-dir", default="runs/qigong_platform/formal_merge/video_acquisition_tasks")
    parser.add_argument("--per-task-candidates", type=int, default=8)
    args = parser.parse_args()

    manifest = Path(args.manifest)
    metadata = Path(args.metadata)
    output_dir = Path(args.output_dir)
    video_dir = Path(args.video_dir)
    manifest_rows = read_csv(manifest)
    candidates = candidate_rows(read_csv(metadata), manifest_rows, args.per_task_candidates)
    tasks = build_tasks(manifest_rows, candidates, video_dir)

    task_csv = output_dir / "video_acquisition_tasks.csv"
    candidate_csv = output_dir / "video_acquisition_candidates.csv"
    summary_json = output_dir / "video_acquisition_summary.json"
    readme = output_dir / "README.md"
    task_rows = [asdict(task) for task in tasks]
    task_fields = list(task_rows[0].keys()) if task_rows else [
        "video_id",
        "required_file_name",
        "case_role",
        "comparison_group",
        "routine",
        "action_segment",
        "expected_use",
        "current_rights_status",
        "target_rights_status",
        "acquisition_status",
        "local_video_path_to_fill",
        "candidate_platform_video_id",
        "candidate_url_hash",
        "candidate_title",
        "notes",
    ]
    candidate_fields = [
        "task_video_id",
        "candidate_rank",
        "candidate_video_id",
        "platform",
        "url_hash",
        "keyword",
        "title",
        "hashtags",
        "view_count",
        "like_count",
        "comment_count",
        "download_permission",
        "comment_collection_status",
        "candidate_score",
        "candidate_reason",
        "selection_rule",
    ]
    summary = {
        "manifest": str(manifest),
        "metadata": str(metadata),
        "video_dir": str(video_dir),
        "task_rows": len(task_rows),
        "candidate_rows": len(candidates),
        "target_rights_confirmed_rows": sum(1 for row in task_rows if row.get("target_rights_status") == "rights_confirmed"),
        "required_file_names": [row.get("required_file_name") for row in task_rows],
    }
    write_csv(task_csv, task_rows, task_fields)
    write_csv(candidate_csv, candidates, candidate_fields)
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_readme(readme, video_dir=video_dir, manifest=manifest, task_csv=task_csv, candidate_csv=candidate_csv, summary=summary)
    print(readme)
    print(task_csv)
    print(candidate_csv)
    print(summary_json)


if __name__ == "__main__":
    main()
