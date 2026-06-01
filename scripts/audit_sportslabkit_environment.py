from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import platform
import sys
from importlib import metadata
from pathlib import Path


PACKAGES = [
    ("sportslabkit", "sportslabkit"),
    ("opencv-python", "cv2"),
    ("mediapipe", "mediapipe"),
    ("numpy", "numpy"),
    ("pandas", "pandas"),
]


def package_status(package_name: str, import_name: str) -> dict[str, str]:
    spec = importlib.util.find_spec(import_name)
    installed = spec is not None
    version = ""
    if installed:
        try:
            version = metadata.version(package_name)
        except metadata.PackageNotFoundError:
            try:
                version = metadata.version(import_name)
            except metadata.PackageNotFoundError:
                version = "unknown"
    return {
        "package": package_name,
        "import_name": import_name,
        "installed": str(installed),
        "version": version,
    }


def mediapipe_pose_api_available() -> bool:
    if importlib.util.find_spec("mediapipe") is None:
        return False
    try:
        import mediapipe as mp  # type: ignore
    except Exception:
        return False
    solutions = getattr(mp, "solutions", None)
    pose_module = getattr(solutions, "pose", None) if solutions is not None else None
    return getattr(pose_module, "Pose", None) is not None


def count_manifest_videos(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    listed = 0
    existing = 0
    for row in rows:
        local_path = (row.get("local_video_path") or "").strip()
        if not local_path:
            continue
        listed += 1
        if Path(local_path).expanduser().exists():
            existing += 1
    return listed, existing


def write_markdown(
    *,
    output: Path,
    package_rows: list[dict[str, str]],
    manifest_path: Path,
    listed_videos: int,
    existing_videos: int,
    pose_api_ready: bool,
) -> None:
    sportslabkit_installed = next(row for row in package_rows if row["package"] == "sportslabkit")["installed"] == "True"
    opencv_installed = next(row for row in package_rows if row["package"] == "opencv-python")["installed"] == "True"
    mediapipe_installed = next(row for row in package_rows if row["package"] == "mediapipe")["installed"] == "True"
    lines = [
        "# SportsLabKit Environment Audit",
        "",
        f"- Python: `{sys.version.split()[0]}`",
        f"- Platform: `{platform.platform()}`",
        f"- Video manifest: `{manifest_path}`",
        f"- Listed local videos: `{listed_videos}`",
        f"- Existing local videos: `{existing_videos}`",
        "",
        "| Package | Import | Installed | Version |",
        "|---|---|---:|---|",
    ]
    for row in package_rows:
        lines.append(f"| {row['package']} | {row['import_name']} | {row['installed']} | {row['version']} |")
    lines.extend(["", "## Method Decision", ""])
    if sportslabkit_installed and existing_videos >= 3:
        lines.append("SportsLabKit is installed and rights-confirmed local videos are available; the formal typical-case sports-video analysis layer can run after execution logs are generated.")
    elif sportslabkit_installed:
        lines.append("SportsLabKit is installed and importable, but rights-confirmed local videos are not yet available. Report the environment as prepared only; do not claim pose, trajectory, or body-keypoint results until local video execution logs exist.")
    elif opencv_installed and mediapipe_installed and pose_api_ready:
        lines.append("SportsLabKit is not fully ready, but the OpenCV/MediaPipe fallback can still extract body-visibility and rhythm indicators. Do not describe fallback outputs as SportsLabKit results.")
    elif opencv_installed:
        if mediapipe_installed and not pose_api_ready:
            lines.append("OpenCV is available and MediaPipe is installed, but the MediaPipe pose API is unavailable in this environment. Use only motion, smoothness, tempo-change, and shot-change features unless SportsLabKit or another pose stack is installed and actually used.")
        else:
            lines.append("OpenCV is available for motion, smoothness, tempo-change, and shot-change smoke checks, but MediaPipe/SportsLabKit is still required before claiming pose or body-visibility evidence.")
    else:
        lines.append("The video-analysis environment is incomplete. Install SportsLabKit or the OpenCV/MediaPipe fallback before claiming embodied video evidence.")
    lines.extend([
        "",
        "## Reporting Rule",
        "",
        "- If SportsLabKit is installed and used, report it as the sports-CV toolkit layer.",
        "- If the fallback extractor is used, report it explicitly as OpenCV/MediaPipe, not SportsLabKit.",
        "- In either case, connect outputs only to body visibility, rhythm, fragmentation, and typical-case embodied evidence, not to platform cultural meaning by itself.",
    ])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit SportsLabKit and fallback video-analysis environment readiness.")
    parser.add_argument("--video-manifest", default="data/qigong_video_manifest.csv")
    parser.add_argument("--output-md", default="runs/qigong_platform/audit/sportslabkit_environment_audit.md")
    parser.add_argument("--output-json", default="runs/qigong_platform/audit/sportslabkit_environment_audit.json")
    args = parser.parse_args()

    package_rows = [package_status(package, import_name) for package, import_name in PACKAGES]
    manifest_path = Path(args.video_manifest)
    listed_videos, existing_videos = count_manifest_videos(manifest_path)
    pose_api_ready = mediapipe_pose_api_available()
    opencv_ready = any(row["package"] == "opencv-python" and row["installed"] == "True" for row in package_rows)
    payload = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "video_manifest": str(manifest_path),
        "listed_local_videos": listed_videos,
        "existing_local_videos": existing_videos,
        "packages": package_rows,
        "opencv_only_motion_ready": opencv_ready,
        "mediapipe_pose_api_ready": pose_api_ready,
        "pose_fallback_ready": opencv_ready and pose_api_ready,
        "sportslabkit_ready": any(row["package"] == "sportslabkit" and row["installed"] == "True" for row in package_rows),
    }

    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(
        output=output_md,
        package_rows=package_rows,
        manifest_path=manifest_path,
        listed_videos=listed_videos,
        existing_videos=existing_videos,
        pose_api_ready=pose_api_ready,
    )
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_md)
    print(output_json)


if __name__ == "__main__":
    main()
