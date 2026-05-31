from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def clean(value: object) -> str:
    return str(value or "").strip()


def hash_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def load_url_map(patterns: list[str]) -> tuple[dict[str, dict[str, str]], list[str]]:
    url_by_hash: dict[str, dict[str, str]] = {}
    sources: list[str] = []
    for pattern in patterns:
        for source in sorted(glob.glob(pattern, recursive=True)):
            path = Path(source)
            if not path.is_file():
                continue
            rows = read_csv(path)
            if not rows or "url" not in rows[0]:
                continue
            sources.append(source)
            for row in rows:
                url = clean(row.get("url"))
                if not url or url.lower() == "nan":
                    continue
                url_by_hash.setdefault(
                    hash_url(url),
                    {
                        "video_url": url,
                        "private_url_source": source,
                        "private_source_video_id": clean(row.get("video_id")),
                    },
                )
    return url_by_hash, sources


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    platform_counts: dict[str, Counter[str]] = defaultdict(Counter)
    keyword_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        matched = "matched" if clean(row.get("video_url")) else "missing"
        platform_counts[clean(row.get("platform")) or "missing"][matched] += 1
        keyword_counts[clean(row.get("keyword")) or "missing"][matched] += 1
    return {
        "total_rows": len(rows),
        "matched": sum(1 for row in rows if clean(row.get("video_url"))),
        "missing": sum(1 for row in rows if not clean(row.get("video_url"))),
        "platform_counts": {platform: dict(counts) for platform, counts in sorted(platform_counts.items())},
        "keyword_counts": {keyword: dict(counts) for keyword, counts in sorted(keyword_counts.items())},
    }


def write_md(path: Path, summary: dict[str, object], *, link_map: str, missing_csv: str) -> None:
    lines = [
        "# 健身气功正式编码样本私有链接覆盖报告",
        "",
        "这份报告只统计链接覆盖情况，不展示原始 URL。原始 URL 只保存在 `data/private/` 中，用于本地人工编码核验。",
        "",
        f"- 样本总数: {summary['total_rows']}",
        f"- 已匹配私有视频链接: {summary['matched']}",
        f"- 缺失私有视频链接: {summary['missing']}",
        f"- 私有链接映射表: `{link_map}`",
        f"- 缺失链接待补表: `{missing_csv}`",
        "",
        "## 按平台统计",
        "",
        "| 平台 | 已匹配 | 缺失 | 合计 |",
        "|---|---:|---:|---:|",
    ]
    for platform, counts in summary["platform_counts"].items():
        matched = int(counts.get("matched", 0))
        missing = int(counts.get("missing", 0))
        lines.append(f"| {platform} | {matched} | {missing} | {matched + missing} |")
    lines.extend(["", "## 方法边界", ""])
    lines.extend(
        [
            "- 已匹配链接的样本可以进入人工观看与编码流程。",
            "- 缺失链接的样本不能仅凭标题、标签或 LLM 建议完成编码。",
            "- 缺失链接可以通过人工补充原始平台 URL、替换为可核验样本，或在论文方法中标记为待补/不可观看样本。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build private video-link coverage files for the Health Qigong formal coding sample.")
    parser.add_argument("--metadata", default="data/qigong_platform_metadata_coding_sample.csv")
    parser.add_argument("--private-url-glob", action="append", default=["data/private/**/*urls*.csv"])
    parser.add_argument("--output-map", default="data/private/qigong_coding_sample_video_link_map_private.csv")
    parser.add_argument("--output-missing", default="data/private/qigong_coding_sample_missing_video_links_todo.csv")
    parser.add_argument("--output-json", default="runs/qigong_platform/formal_merge/private_video_link_coverage.json")
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/private_video_link_coverage.md")
    args = parser.parse_args()

    metadata_rows = read_csv(Path(args.metadata))
    url_by_hash, sources = load_url_map(args.private_url_glob)
    rows: list[dict[str, str]] = []
    for row in metadata_rows:
        url_hash = clean(row.get("url_hash"))
        match = url_by_hash.get(url_hash, {})
        rows.append(
            {
                "video_id": clean(row.get("video_id")),
                "platform": clean(row.get("platform")),
                "keyword": clean(row.get("keyword")),
                "title": clean(row.get("title")),
                "url_hash": url_hash,
                "video_url": clean(match.get("video_url")),
                "link_status": "matched_private_url" if match else "missing_private_url",
                "private_url_source": clean(match.get("private_url_source")),
                "private_source_video_id": clean(match.get("private_source_video_id")),
            }
        )

    fieldnames = [
        "video_id",
        "platform",
        "keyword",
        "title",
        "url_hash",
        "video_url",
        "link_status",
        "private_url_source",
        "private_source_video_id",
    ]
    write_csv(Path(args.output_map), rows, fieldnames)
    missing_rows = [row for row in rows if not clean(row.get("video_url"))]
    write_csv(Path(args.output_missing), missing_rows, fieldnames)

    summary = summarize(rows)
    summary["metadata"] = args.metadata
    summary["private_url_sources"] = sources
    summary["output_map"] = args.output_map
    summary["output_missing"] = args.output_missing
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_md(Path(args.output_md), summary, link_map=args.output_map, missing_csv=args.output_missing)
    print(args.output_map)
    print(args.output_missing)
    print(args.output_json)
    print(args.output_md)


if __name__ == "__main__":
    main()
