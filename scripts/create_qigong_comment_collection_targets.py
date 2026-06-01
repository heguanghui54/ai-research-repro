#!/usr/bin/env python3
"""Create a prioritized worksheet for supplementing qigong comment evidence."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "runs" / "qigong_platform" / "formal_merge"
DOC_DIR = ROOT / "docs" / "qigong_platform_paper"


SAMPLE_PATH = DATA_DIR / "qigong_platform_metadata_coding_sample.csv"
COMMENTS_PATH = DATA_DIR / "qigong_comments_formal.csv"
OUT_CSV = OUT_DIR / "qigong_comment_collection_targets.csv"
OUT_JSON = OUT_DIR / "qigong_comment_collection_targets.json"
OUT_MD = DOC_DIR / "comment_collection_targets.md"


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def int_or_zero(value: str | None) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def main() -> None:
    sample = read_rows(SAMPLE_PATH)
    comments = read_rows(COMMENTS_PATH) if COMMENTS_PATH.exists() else []
    counts = Counter(row.get("video_id", "") for row in comments)

    targets: list[dict] = []
    for row in sample:
        video_id = row.get("video_id", "")
        current = counts.get(video_id, 0)
        target_min = 5
        need = max(0, target_min - current)
        comment_count = int_or_zero(row.get("comment_count"))
        has_public_comments = comment_count > 0
        if need == 0:
            priority = "covered"
        elif has_public_comments and current == 0:
            priority = "P0_no_collected_comments"
        elif has_public_comments:
            priority = "P1_top_up_to_five"
        else:
            priority = "P2_mark_unavailable_or_find_alternative"
        targets.append(
            {
                "video_id": video_id,
                "platform": row.get("platform", ""),
                "keyword": row.get("keyword", ""),
                "title": row.get("title", ""),
                "search_rank": row.get("search_rank", ""),
                "metadata_comment_count": row.get("comment_count", ""),
                "collected_comment_rows": current,
                "target_min_comments": target_min,
                "additional_comments_needed": need,
                "priority": priority,
                "student_or_assistant_action": (
                    "补采公开视频评论，去除用户名、头像、主页、评论链接等身份信息"
                    if need and has_public_comments
                    else "若平台显示无评论或不可访问，记录 unavailable_reason"
                    if need
                    else "无需补采"
                ),
                "ethics_note": "只采公开评论文本；不保存用户名、主页、头像、账号ID或评论直链；如含个人隐私需改写或剔除。",
            }
        )

    targets.sort(
        key=lambda x: (
            {"P0_no_collected_comments": 0, "P1_top_up_to_five": 1, "P2_mark_unavailable_or_find_alternative": 2, "covered": 3}.get(x["priority"], 9),
            -int_or_zero(x["metadata_comment_count"]),
            x["video_id"],
        )
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(targets[0].keys()))
        writer.writeheader()
        writer.writerows(targets)

    summary = {
        "sample_videos": len(sample),
        "comment_rows": len(comments),
        "covered_videos": sum(1 for row in targets if row["collected_comment_rows"] > 0),
        "videos_with_at_least_five_comments": sum(1 for row in targets if row["collected_comment_rows"] >= 5),
        "p0_no_collected_comments": sum(1 for row in targets if row["priority"] == "P0_no_collected_comments"),
        "p1_top_up_to_five": sum(1 for row in targets if row["priority"] == "P1_top_up_to_five"),
        "p2_unavailable_or_alternative": sum(1 for row in targets if row["priority"] == "P2_mark_unavailable_or_find_alternative"),
        "additional_comments_needed_to_reach_five_each": sum(row["additional_comments_needed"] for row in targets),
    }
    OUT_JSON.write_text(json.dumps({"summary": summary, "targets": targets}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    top = [row for row in targets if row["priority"] != "covered"][:40]
    lines = [
        "# 评论补采目标表",
        "",
        "本表用于把评论语料从“定性近读”推进到可支撑频率描述的状态。补采时只保存匿名化公开评论文本，不保存用户身份信息。",
        "",
        "## 当前摘要",
        "",
        f"- 样本视频：{summary['sample_videos']}",
        f"- 已收评论：{summary['comment_rows']}",
        f"- 已覆盖视频：{summary['covered_videos']}/{summary['sample_videos']}",
        f"- 已达到每视频至少 5 条评论：{summary['videos_with_at_least_five_comments']}/{summary['sample_videos']}",
        f"- 仍需补采评论条数（按每条视频 5 条估算）：{summary['additional_comments_needed_to_reach_five_each']}",
        "",
        "## 优先补采前 40 条",
        "",
        "| Priority | Video ID | Platform | Keyword | 已收 | 需补 | 元数据评论数 | Title |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in top:
        title = row["title"].replace("|", "｜")[:42]
        lines.append(
            f"| {row['priority']} | {row['video_id']} | {row['platform']} | {row['keyword']} | "
            f"{row['collected_comment_rows']} | {row['additional_comments_needed']} | {row['metadata_comment_count']} | {title} |"
        )
    lines.extend(
        [
            "",
            "## 助研操作规则",
            "",
            "1. 优先处理 `P0_no_collected_comments`：这些视频元数据中有评论，但正式评论表尚未覆盖。",
            "2. 其次处理 `P1_top_up_to_five`：这些视频已有少量评论，但不足以支撑单视频近读。",
            "3. 对 `P2_mark_unavailable_or_find_alternative`，若平台确实无评论或不可访问，只记录不可采原因，不强行补造。",
            "4. 每条评论进入正式表前必须匿名化：不保存用户名、主页、头像、账号 ID、评论直链。",
            "5. 在未通过评论审计前，论文中只能写评论近读或示例，不写总体比例结论。",
            "",
            f"完整 CSV：`{OUT_CSV}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
