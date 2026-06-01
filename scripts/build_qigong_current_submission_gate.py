from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Gate:
    priority: str
    gate: str
    status: str
    evidence: str
    next_action: str


FORBIDDEN_PUBLIC_PATTERNS = [
    r"\bMonica\b",
    r"AI\s*Scientist",
    r"ai[-\s]?scientist",
]

AUTHOR_TERMS = ["石伟", "西南科技大学体育学院", "副教授", "中国科学技术大学博士"]


def read_json(path: Path) -> object:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def status(ok: bool, *, warn: bool = False) -> str:
    if ok:
        return "pass"
    return "warn" if warn else "fail"


def count_nonempty(rows: list[dict[str, str]], field: str) -> int:
    return sum(1 for row in rows if (row.get(field) or "").strip())


def audit_status_counts(payload: object) -> dict[str, int]:
    rows = payload.get("gates", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return {"pass": 0, "warn": 0, "fail": 0}
    return {key: sum(1 for row in rows if isinstance(row, dict) and row.get("status") == key) for key in ["pass", "warn", "fail"]}


def audit_fail_names(payload: object) -> list[str]:
    rows = payload.get("gates", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return []
    names = []
    for row in rows:
        if isinstance(row, dict) and row.get("status") == "fail":
            names.append(str(row.get("gate") or row.get("category") or row.get("requirement") or "unnamed"))
    return names


def build_gates(args: argparse.Namespace) -> list[Gate]:
    manuscript_text = read_text(Path(args.manuscript))
    author_text = read_text(Path(args.author_metadata))
    web_summary = read_json(Path(args.web_summary))
    web_ingest = read_json(Path(args.web_ingest_audit))
    web_coding_rows = read_csv(Path(args.web_coding))
    comment_audit = read_json(Path(args.comment_audit))
    video_preflight = read_json(Path(args.video_preflight))
    sports_env = read_json(Path(args.sports_env))
    goal_audit = read_json(Path(args.goal_audit))
    hf_inventory = read_csv(Path(args.hf_inventory))
    hf_probe = read_csv(Path(args.hf_probe))
    metadata = read_csv(Path(args.metadata))

    gates: list[Gate] = []

    author_ok = all(term in manuscript_text + author_text for term in AUTHOR_TERMS)
    gates.append(
        Gate(
            "P0",
            "作者身份与署名",
            status(author_ok),
            "required=" + json.dumps(AUTHOR_TERMS, ensure_ascii=False),
            "正式稿首页和作者元数据必须保持石伟、单位与博士身份，不得署 AI 工作流。",
        )
    )

    forbidden_hits = [pat for pat in FORBIDDEN_PUBLIC_PATTERNS if re.search(pat, manuscript_text, re.I)]
    concrete_model_hit = any(name in manuscript_text.lower() for name in ["deepseek-chat", "gemini-2.5-pro", "gpt-5"])
    gates.append(
        Gate(
            "P0",
            "公开稿件模型命名",
            status(not forbidden_hits and concrete_model_hit, warn=not forbidden_hits),
            f"forbidden_hits={forbidden_hits}, concrete_model_hit={concrete_model_hit}",
            "公开稿件只写具体模型名，不写聚合平台、私有 API 或 AI Scientist 作者身份。",
        )
    )

    included = sum(1 for row in metadata if (row.get("include_status") or "").strip() == "included")
    platforms = sorted({(row.get("platform") or "").strip() for row in metadata if (row.get("include_status") or "").strip() == "included"})
    gates.append(
        Gate(
            "P0",
            "真实短视频样本池",
            status(len(metadata) >= 300 and included >= 120 and len(platforms) >= 4, warn=bool(metadata)),
            f"metadata_rows={len(metadata)}, included={included}, platforms={platforms}",
            "继续保持真实平台样本为核心；HF/MultiSports 只能作基线与校准。",
        )
    )

    complete_rows = int((web_summary or {}).get("complete_rows", 0)) if isinstance(web_summary, dict) else 0
    primary = int((web_summary or {}).get("primary_submissions", 0)) if isinstance(web_summary, dict) else 0
    gates.append(
        Gate(
            "P0",
            "网页人工编码提交",
            status(complete_rows >= 120 and primary >= 120, warn=exists(Path(args.web_summary))),
            f"complete_rows={complete_rows}, primary_submissions={primary}",
            "让 STU01-STU10 完成有链接任务；导出后必须有 120 条主编码完整提交。",
        )
    )

    ingested_complete = int((web_ingest or {}).get("complete_main_rows_after_merge", 0)) if isinstance(web_ingest, dict) else 0
    field_filled = count_nonempty(web_coding_rows, "dominant_frame")
    gates.append(
        Gate(
            "P0",
            "网页提交转正式编码表",
            status(ingested_complete >= 120 and field_filled >= 120, warn=exists(Path(args.web_ingest_audit))),
            f"ingested_complete={ingested_complete}, dominant_frame_filled={field_filled}/120",
            "运行 export + ingest + formal coding audit，生成可进入统计的正式人工编码表。",
        )
    )

    comment_counts = audit_status_counts(comment_audit)
    comment_fails = audit_fail_names(comment_audit)
    gates.append(
        Gate(
            "P1",
            "评论语料审计",
            status(comment_counts["fail"] == 0 and sum(comment_counts.values()) > 0, warn=sum(comment_counts.values()) > 0),
            f"counts={comment_counts}, fail_gates={comment_fails}",
            "补齐评论数和覆盖率；未达标前只写近读，不写频率结论。",
        )
    )

    video_summary = (video_preflight or {}).get("summary", {}) if isinstance(video_preflight, dict) else {}
    ready_videos = int(video_summary.get("ready_local_rights", 0) or 0)
    min_ready = int(video_summary.get("min_ready_local_rights", 3) or 3)
    gates.append(
        Gate(
            "P0",
            "典型视频本地权利与文件预检",
            status(ready_videos >= min_ready and bool(video_summary.get("ready")), warn=exists(Path(args.video_preflight))),
            f"ready_local_rights={ready_videos}/{video_summary.get('task_rows', 0)}, target>={min_ready}, issue_count={video_summary.get('issue_count')}",
            "上传并确认至少 TC0001-TC0003 三个本地视频，更新 manifest 后重跑预检。",
        )
    )

    sports_payload = sports_env if isinstance(sports_env, dict) else {}
    gates.append(
        Gate(
            "P1",
            "SportsLabKit/OpenCV 环境",
            status(bool(sports_payload.get("sportslabkit_ready")) and ready_videos >= min_ready, warn=exists(Path(args.sports_env))),
            f"sportslabkit={sports_payload.get('sportslabkit_ready')}, opencv_motion={sports_payload.get('opencv_only_motion_ready')}, existing_videos={sports_payload.get('existing_local_videos')}",
            "Ubuntu 上安装/验证 SportsLabKit；若只用 OpenCV 后备，论文必须如实写 OpenCV/MediaPipe 后备链路。",
        )
    )

    hf_probe_pass = sum(1 for row in hf_probe if (row.get("status") or "") == "pass")
    hf_bad_claims = [row.get("repo_id", "") for row in hf_inventory if (row.get("can_support_platform_differance_claim") or "").strip().lower() not in {"no", "false", "0"}]
    gates.append(
        Gate(
            "P1",
            "HF/benchmark 边界",
            status(len(hf_inventory) >= 6 and hf_probe_pass >= 4 and not hf_bad_claims, warn=bool(hf_inventory)),
            f"hf_rows={len(hf_inventory)}, probe_pass={hf_probe_pass}, bad_platform_claims={hf_bad_claims}",
            "HF 数据集只进入方法边界和工具基线，不替代真实短视频样本。",
        )
    )

    goal_counts = audit_status_counts(goal_audit)
    goal_fails = audit_fail_names(goal_audit)
    gates.append(
        Gate(
            "P0",
            "全目标完成度审计",
            status(goal_counts["fail"] == 0 and goal_counts["warn"] == 0 and sum(goal_counts.values()) > 0, warn=sum(goal_counts.values()) > 0),
            f"counts={goal_counts}, fail_gates={goal_fails}",
            "所有 P0/P1 输入齐备后再运行全目标审计；仍有 fail 时不能标记目标完成。",
        )
    )

    return gates


def write_outputs(gates: list[Gate], output_md: Path, output_json: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    counts = {key: sum(1 for gate in gates if gate.status == key) for key in ["pass", "warn", "fail"]}
    p0_nonpass = [gate.gate for gate in gates if gate.priority == "P0" and gate.status != "pass"]
    lines = [
        "# 当前投稿门槛总表",
        "",
        "本表面向《武汉体育学院学报》投稿目标，汇总网页人工编码、评论、典型视频、HF/benchmark、稿件署名与模型命名等关键证据层。它不是结果报告，而是决定哪些内容可以写入正式稿的闸门。",
        "",
        f"Summary: pass={counts['pass']}, warn={counts['warn']}, fail={counts['fail']}",
        f"P0 non-pass: {p0_nonpass}",
        "",
        "| Priority | Gate | Status | Evidence | Next Action |",
        "|---|---|---|---|---|",
    ]
    for gate in gates:
        lines.append(f"| {gate.priority} | {gate.gate} | {gate.status} | {gate.evidence} | {gate.next_action} |")
    lines.extend(["", "## Decision", ""])
    if not p0_nonpass and counts["fail"] == 0:
        lines.append("P0 gates are clear. The paper can move from evidence collection toward formal result writing, while resolving remaining P1 warnings.")
    else:
        lines.append("The package is not submission-ready. Keep the manuscript as a current-evidence draft and do not report unverified artificial coding, video, or frequency results.")
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    output_json.write_text(json.dumps([asdict(gate) for gate in gates], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the current submission gate for the Health Qigong short-video paper.")
    parser.add_argument("--manuscript", default="docs/qigong_platform_paper/manuscript_draft_v0_8_current_evidence.md")
    parser.add_argument("--author-metadata", default="docs/qigong_platform_paper/author_metadata.json")
    parser.add_argument("--metadata", default="data/qigong_platform_metadata_formal.csv")
    parser.add_argument("--web-summary", default="runs/qigong_platform/formal_merge/web_coding_submissions_export_summary.json")
    parser.add_argument("--web-ingest-audit", default="runs/qigong_platform/formal_merge/web_coding_ingest_audit.json")
    parser.add_argument("--web-coding", default="runs/qigong_platform/formal_merge/qigong_human_coding_from_web.csv")
    parser.add_argument("--comment-audit", default="runs/qigong_platform/formal_merge/comment_audit.json")
    parser.add_argument("--video-preflight", default="runs/qigong_platform/formal_merge/video_file_preflight.json")
    parser.add_argument("--sports-env", default="runs/qigong_platform/formal_merge/sportslabkit_environment_audit.json")
    parser.add_argument("--hf-inventory", default="runs/qigong_platform/hf_dataset_inventory.csv")
    parser.add_argument("--hf-probe", default="runs/qigong_platform/hf_dataset_viewer_probe.csv")
    parser.add_argument("--goal-audit", default="runs/qigong_platform/formal_merge/goal_completion_current_audit.json")
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/current_submission_gate.md")
    parser.add_argument("--output-json", default="runs/qigong_platform/formal_merge/current_submission_gate.json")
    args = parser.parse_args()
    gates = build_gates(args)
    write_outputs(gates, Path(args.output_md), Path(args.output_json))
    print(args.output_md)
    print(args.output_json)


if __name__ == "__main__":
    main()
