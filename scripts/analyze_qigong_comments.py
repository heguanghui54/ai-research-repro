from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


LEXICONS = {
    "meme_play": ["功德", "哈哈", "笑死", "鬼畜", "保命", "赛博", "玄学", "整活", "抽象", "打卡", "收藏了"],
    "embodiment_deferral": ["收藏", "先收藏", "等于练", "明天练", "下次练", "已经会了", "眼睛会了", "身体不会"],
    "authority_contest": ["正宗", "标准", "错了", "不对", "误导", "老师", "大师", "官方", "求指正", "打脸", "科普", "辟谣"],
    "health_anxiety": ["颈椎", "腰痛", "失眠", "焦虑", "亚健康", "上班族", "程序员", "减肥", "变瘦", "气血"],
    "practice_intention": ["跟练", "练起来", "每天", "坚持", "打卡", "有效", "舒服", "放松", "呼吸", "动作"],
    "commercial_suspicion": ["卖课", "割韭菜", "链接", "课程", "私教", "直播间", "付费", "收费", "下单"],
}


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def contains_any(text: str, terms: list[str]) -> int:
    return int(any(term in text for term in terms))


def tokenize_chineseish(text: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fffA-Za-z0-9#_+]+", text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Health Qigong short-video comments for meme, deferral, and authority-contest signals.")
    parser.add_argument("--comments", required=True)
    parser.add_argument("--output-dir", default="runs/qigong_platform/comments")
    args = parser.parse_args()

    rows = read_rows(Path(args.comments))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    by_video: dict[str, Counter[str]] = defaultdict(Counter)
    overall = Counter()
    top_terms = Counter()
    for row in rows:
        video_id = row.get("video_id", "").strip() or "missing"
        text = row.get("comment_text", "")
        if not text:
            continue
        for category, terms in LEXICONS.items():
            hit = contains_any(text, terms)
            by_video[video_id][category] += hit
            overall[category] += hit
        for token in tokenize_chineseish(text):
            if len(token) >= 2:
                top_terms[token] += 1

    video_out = output_dir / "comment_signal_by_video.csv"
    with video_out.open("w", newline="", encoding="utf-8") as f:
        fields = ["video_id", "comment_count", *LEXICONS.keys()]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        counts = Counter(row.get("video_id", "").strip() or "missing" for row in rows if row.get("comment_text", ""))
        for video_id in sorted(counts):
            out = {"video_id": video_id, "comment_count": counts[video_id]}
            out.update({category: by_video[video_id][category] for category in LEXICONS})
            writer.writerow(out)

    overall_out = output_dir / "comment_signal_overall.csv"
    with overall_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "hit_count"])
        for category in LEXICONS:
            writer.writerow([category, overall[category]])

    terms_out = output_dir / "comment_top_terms.csv"
    with terms_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "count"])
        for term, count in top_terms.most_common(100):
            writer.writerow([term, count])

    print(output_dir)


if __name__ == "__main__":
    main()
