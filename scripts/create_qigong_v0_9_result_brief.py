#!/usr/bin/env python3
"""Create a gated v0.9 result brief from formal qigong artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


KEY_FIELDS = [
    "dominant_frame",
    "visibility_centrality",
    "tempo_discipline",
    "efficacy_tagging",
    "image_trace_strength",
    "media_temporality",
    "embodied_dissolution",
]

FIELD_CN = {
    "dominant_frame": "主导意义框架",
    "visibility_centrality": "可视性中心",
    "tempo_discipline": "节奏规训",
    "efficacy_tagging": "功效标签化",
    "image_trace_strength": "影像痕迹强度",
    "media_temporality": "媒介时间性",
    "embodied_dissolution": "具身消解程度",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def gate_pass(rows) -> bool:
    if not isinstance(rows, list) or not rows:
        return False
    return all(isinstance(row, dict) and row.get("status") == "pass" for row in rows)


def gate_has_no_fail(rows) -> bool:
    if not isinstance(rows, list) or not rows:
        return False
    return not any(isinstance(row, dict) and row.get("status") == "fail" for row in rows)


def web_coding_ready(summary: dict | None, ingest: dict | None, values_gate, reliability_gate) -> bool:
    if not isinstance(summary, dict) or not isinstance(ingest, dict):
        return False
    return (
        int(summary.get("complete_rows", 0) or 0) >= 120
        and int(summary.get("primary_submissions", 0) or 0) >= 120
        and bool(ingest.get("ready_for_formal_audit"))
        and gate_has_no_fail(values_gate)
        and gate_pass(reliability_gate)
    )


def comment_ready(comment_audit) -> bool:
    if not isinstance(comment_audit, list):
        return False
    return gate_has_no_fail(comment_audit)


def video_ready(video_preflight: dict | None) -> bool:
    if not isinstance(video_preflight, dict):
        return False
    summary = video_preflight.get("summary", {})
    return bool(summary.get("ready")) and int(summary.get("ready_local_rights", 0) or 0) >= int(summary.get("min_ready_local_rights", 3) or 3)


def top_counts(rows: list[dict[str, str]], field: str, limit: int = 3) -> list[tuple[str, int]]:
    counts = Counter((row.get(field) or "missing").strip() or "missing" for row in rows)
    return counts.most_common(limit)


def pct(count: int, total: int) -> str:
    if total <= 0:
        return "0.0%"
    return f"{count / total * 100:.1f}%"


def format_top(items: list[tuple[str, int]], total: int) -> str:
    if not items:
        return "暂无可报告分布"
    return "；".join(f"{value} {count} 条（{pct(count, total)}）" for value, count in items)


def reliability_summary(rows: list[dict[str, str]]) -> str:
    by_field = {row.get("field", ""): row for row in rows}
    parts = []
    for field in KEY_FIELDS:
        row = by_field.get(field, {})
        status = row.get("status", "missing")
        kappa = row.get("cohen_kappa", "")
        alpha = row.get("krippendorff_alpha_nominal", "")
        parts.append(f"{FIELD_CN[field]}：{status}（kappa={kappa or 'NA'}，alpha={alpha or 'NA'}）")
    return "；".join(parts)


def build_ready_result(coding_rows: list[dict[str, str]], reliability_rows: list[dict[str, str]]) -> str:
    total = len(coding_rows)
    lines = [
        "## 5 实证结果：平台化身体的编码分布与机制证据",
        "",
        f"网页人工编码共形成 {total} 条正式样本记录。双编码一致性检验显示：{reliability_summary(reliability_rows)}。以下结果仅报告通过编码值审计与可靠性门槛的变量。",
        "",
        "### 5.1 主导意义框架与身体呈现",
        "",
        f"主导意义框架分布显示：{format_top(top_counts(coding_rows, 'dominant_frame'), total)}。身体可见性分布为：{format_top(top_counts(coding_rows, 'body_visibility'), total)}。这些结果用于说明平台如何把健身气功重新组织为教学身体、疗愈身体、文化身体、景观身体、社交身体或商业身体。",
        "",
        "### 5.2 影像化规训变量",
        "",
        f"可视性中心分布为：{format_top(top_counts(coding_rows, 'visibility_centrality'), total)}。节奏规训分布为：{format_top(top_counts(coding_rows, 'tempo_discipline'), total)}。功效标签化分布为：{format_top(top_counts(coding_rows, 'efficacy_tagging'), total)}。这些变量共同指向短视频平台对身体外形、观看节奏和健康功效话语的重排。",
        "",
        "### 5.3 延异、痕迹与具身消解",
        "",
        f"影像痕迹强度分布为：{format_top(top_counts(coding_rows, 'image_trace_strength'), total)}。媒介时间性分布为：{format_top(top_counts(coding_rows, 'media_temporality'), total)}。具身消解程度分布为：{format_top(top_counts(coding_rows, 'embodied_dissolution'), total)}。在正式稿中，这些结果应与评论近读和典型视频身体证据结合解释，避免把单一频数直接写成因果结论。",
    ]
    return "\n".join(lines)


def build_pending_result(args: argparse.Namespace, states: dict[str, object]) -> str:
    lines = [
        "## 5 结果回填状态：当前不报告正式经验结果",
        "",
        "当前工作包尚未满足 v0.9 正式结果写作门槛。以下内容用于审稿前自检和后续回填，不应作为投稿正文中的经验发现。",
        "",
        "### 5.1 网页人工编码状态",
        "",
        f"- web_coding_ready: {states['web_ready']}",
        f"- complete_rows: {states['web_summary'].get('complete_rows', 'NA') if isinstance(states['web_summary'], dict) else 'NA'}",
        f"- primary_submissions: {states['web_summary'].get('primary_submissions', 'NA') if isinstance(states['web_summary'], dict) else 'NA'}",
        f"- ingest_ready_for_formal_audit: {states['web_ingest'].get('ready_for_formal_audit', 'NA') if isinstance(states['web_ingest'], dict) else 'NA'}",
        "",
        "论文写法：只能写“网页人工编码平台已建立、学生编码正在进行”，不能写“编码结果显示”。",
        "",
        "### 5.2 双编码可靠性状态",
        "",
        f"- reliability_gate_pass: {states['reliability_ready']}",
        f"- reliability_gate_fail_count: {states['reliability_fail_count']}",
        "",
        "论文写法：可靠性未通过前，不报告主导意义框架、可视性中心、节奏规训等变量分布。",
        "",
        "### 5.3 评论与典型视频状态",
        "",
        f"- comment_ready: {states['comment_ready']}",
        f"- video_ready: {states['video_ready']}",
        "",
        "论文写法：评论未达标时只作近读；视频未达标时只写典型视频分析层设计与边界。",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a gated v0.9 result brief for the qigong manuscript.")
    parser.add_argument("--coding", default="runs/qigong_platform/formal_merge/qigong_human_coding_from_web.csv")
    parser.add_argument("--reliability", default="runs/qigong_platform/formal_merge/web_reliability/coding_reliability.csv")
    parser.add_argument("--web-summary", default="runs/qigong_platform/formal_merge/web_coding_submissions_export_summary.json")
    parser.add_argument("--web-ingest", default="runs/qigong_platform/formal_merge/web_coding_ingest_audit.json")
    parser.add_argument("--coding-values-gate", default="runs/qigong_platform/formal_merge/web_human_coding_values_audit.json")
    parser.add_argument("--reliability-gate", default="runs/qigong_platform/formal_merge/web_reliability_gate.json")
    parser.add_argument("--comment-audit", default="runs/qigong_platform/formal_merge/comment_audit.json")
    parser.add_argument("--video-preflight", default="runs/qigong_platform/formal_merge/video_file_preflight.json")
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/manuscript_result_brief_v0_9.md")
    parser.add_argument("--output-json", default="runs/qigong_platform/formal_merge/manuscript_result_brief_v0_9_gate.json")
    args = parser.parse_args()

    coding_rows = read_csv(Path(args.coding))
    reliability_rows = read_csv(Path(args.reliability))
    web_summary = read_json(Path(args.web_summary))
    web_ingest = read_json(Path(args.web_ingest))
    values_gate = read_json(Path(args.coding_values_gate))
    reliability_gate = read_json(Path(args.reliability_gate))
    comment_audit = read_json(Path(args.comment_audit))
    video_preflight = read_json(Path(args.video_preflight))

    web_ready = web_coding_ready(web_summary, web_ingest, values_gate, reliability_gate)
    states = {
        "web_ready": web_ready,
        "web_summary": web_summary or {},
        "web_ingest": web_ingest or {},
        "reliability_ready": gate_pass(reliability_gate),
        "reliability_fail_count": sum(1 for row in reliability_gate or [] if isinstance(row, dict) and row.get("status") == "fail"),
        "comment_ready": comment_ready(comment_audit),
        "video_ready": video_ready(video_preflight),
        "coding_rows": len(coding_rows),
        "reliability_rows": len(reliability_rows),
    }
    brief = build_ready_result(coding_rows, reliability_rows) if web_ready else build_pending_result(args, states)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(brief + "\n", encoding="utf-8")
    output_json.write_text(json.dumps(states, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_md)


if __name__ == "__main__":
    main()
