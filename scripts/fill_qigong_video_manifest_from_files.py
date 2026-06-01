from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}


@dataclass
class FillVideoEvent:
    severity: str
    video_id: str
    file_path: str
    field: str
    message: str


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in rows)


def scan_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in VIDEO_SUFFIXES)


def match_file(video_id: str, files: list[Path]) -> Path | None:
    key = video_id.lower()
    exact = [path for path in files if path.stem.lower() == key]
    if exact:
        return exact[0]
    contains = [path for path in files if key and key in path.stem.lower()]
    if contains:
        return contains[0]
    return None


def append_note(existing: str, note: str) -> str:
    existing = (existing or "").strip()
    if not existing:
        return note
    parts = [part.strip() for part in existing.split(";") if part.strip()]
    if note in parts:
        return existing
    return existing + ";" + note


def fill_manifest(args: argparse.Namespace) -> tuple[list[str], list[dict[str, str]], list[FillVideoEvent], dict[str, object]]:
    manifest = Path(args.manifest)
    fieldnames, rows = read_csv(manifest)
    files = scan_files(Path(args.video_dir))
    events: list[FillVideoEvent] = []
    if not rows:
        events.append(FillVideoEvent("error", "", "", "manifest", f"Manifest is empty or missing: {manifest}"))
        return fieldnames, rows, events, {"matched_rows": 0, "video_files_found": len(files)}
    if "local_video_path" not in fieldnames:
        events.append(FillVideoEvent("error", "", "", "local_video_path", "Manifest lacks local_video_path column."))
        return fieldnames, rows, events, {"matched_rows": 0, "video_files_found": len(files)}

    matched = 0
    for row in rows:
        video_id = (row.get("video_id") or "").strip()
        if not video_id:
            continue
        current = (row.get("local_video_path") or "").strip()
        if current and Path(current).expanduser().exists() and not args.replace_existing:
            events.append(FillVideoEvent("info", video_id, current, "local_video_path", "Existing local path kept."))
            continue
        match = match_file(video_id, files)
        if match is None:
            events.append(FillVideoEvent("warning", video_id, "", "local_video_path", "No matching video file found by video_id."))
            continue
        path_value = str(match.resolve()) if args.absolute_paths else str(match)
        old = row.get("local_video_path", "")
        row["local_video_path"] = path_value
        matched += 1
        events.append(FillVideoEvent("change", video_id, path_value, "local_video_path", f"set: {old!r} -> {path_value!r}"))
        if args.set_rights_confirmed:
            old_rights = row.get("rights_status", "")
            row["rights_status"] = "rights_confirmed"
            if old_rights != "rights_confirmed":
                events.append(FillVideoEvent("change", video_id, path_value, "rights_status", f"set: {old_rights!r} -> 'rights_confirmed'"))
        if args.set_expected_use and not (row.get("expected_use") or "").strip():
            row["expected_use"] = args.set_expected_use
            events.append(FillVideoEvent("change", video_id, path_value, "expected_use", f"set: '' -> {args.set_expected_use!r}"))
        if "notes" in fieldnames:
            row["notes"] = append_note(row.get("notes", ""), f"local_file_matched_from={Path(args.video_dir)}")

    summary = {
        "manifest": str(manifest),
        "video_dir": args.video_dir,
        "video_files_found": len(files),
        "manifest_rows": len(rows),
        "matched_rows": matched,
        "replace_existing": bool(args.replace_existing),
        "absolute_paths": bool(args.absolute_paths),
        "event_counts": {
            severity: sum(1 for event in events if event.severity == severity)
            for severity in ["change", "info", "warning", "error"]
        },
    }
    return fieldnames, rows, events, summary


def write_report(path: Path, events: list[FillVideoEvent], summary: dict[str, object], output_manifest: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Fill Typical-Case Video Manifest From Files",
        "",
        "This report records a local-file matching step for typical-case videos. It is a workflow artifact, not empirical evidence.",
        "",
        f"- Manifest: `{summary.get('manifest')}`",
        f"- Video directory: `{summary.get('video_dir')}`",
        f"- Output manifest: `{output_manifest}`",
        f"- Video files found: {summary.get('video_files_found')}",
        f"- Matched rows: {summary.get('matched_rows')}/{summary.get('manifest_rows')}",
        f"- Event counts: {summary.get('event_counts')}",
        "",
        "## Next Commands",
        "",
        "```bash",
        f"python scripts/audit_qigong_video_manifest.py --manifest {output_manifest} --metadata data/qigong_platform_metadata_formal.csv --profile formal --output-md runs/qigong_platform/audit/video_manifest_audit.md --output-json runs/qigong_platform/audit/video_manifest_audit.json",
        f"python scripts/sample_qigong_video_frames.py --manifest {output_manifest} --output-root runs/qigong_platform/llm_frames --frame-index runs/qigong_platform/llm_frames_index.csv --max-frames 4",
        f"python scripts/extract_qigong_video_features.py --manifest {output_manifest} --output runs/qigong_platform/features/video_features.csv",
        "python scripts/refresh_qigong_readiness_dashboards.py",
        "```",
        "",
        "## Events",
        "",
        "| Severity | Video ID | Field | File | Message |",
        "|---|---|---|---|---|",
    ]
    for event in events[:500]:
        lines.append(f"| {event.severity} | {event.video_id} | {event.field} | `{event.file_path}` | {event.message} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill local_video_path values in a Health Qigong typical-case video manifest from a local video folder.")
    parser.add_argument("--manifest", default="data/qigong_video_manifest.csv")
    parser.add_argument("--video-dir", required=True)
    parser.add_argument("--output-manifest", default="runs/qigong_platform/formal_merge/qigong_video_manifest_filled_from_files.csv")
    parser.add_argument("--report-md", default="runs/qigong_platform/formal_merge/video_manifest_file_fill_report.md")
    parser.add_argument("--report-json", default="runs/qigong_platform/formal_merge/video_manifest_file_fill_report.json")
    parser.add_argument("--replace-existing", action="store_true")
    parser.add_argument("--absolute-paths", action="store_true")
    parser.add_argument("--set-rights-confirmed", action="store_true")
    parser.add_argument("--set-expected-use", default="")
    args = parser.parse_args()

    fieldnames, rows, events, summary = fill_manifest(args)
    output_manifest = Path(args.output_manifest)
    if rows and fieldnames:
        write_csv(output_manifest, fieldnames, rows)
    write_report(Path(args.report_md), events, summary, output_manifest)
    Path(args.report_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_json).write_text(
        json.dumps({"summary": summary, "events": [asdict(event) for event in events]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output_manifest)
    print(args.report_md)
    if any(event.severity == "error" for event in events):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
