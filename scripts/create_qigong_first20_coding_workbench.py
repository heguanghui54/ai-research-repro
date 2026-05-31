from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import html
import json
from pathlib import Path


FORMAL_FIELDS = [
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
    "coder_id",
    "trace_markers",
    "notes",
]

SELECT_OPTIONS = {
    "dominant_frame": ["", "instructional_body", "therapeutic_body", "cultural_body", "spectacular_body", "social_body", "commercial_body", "unclear"],
    "body_visibility": ["", "full_body", "upper_body", "partial", "close_up", "unclear"],
    "movement_tempo": ["", "slow_continuous", "segmented_teaching", "fast_montage", "mixed", "unclear"],
    "origin_reference": ["", "none", "official_routine", "master_teacher", "ancient_tradition", "national_culture", "medical_health", "unclear"],
    "supplement_mode": ["", "none", "caption", "caption_explanation", "music_reframing", "comment_interaction", "hashtag_recontextualization", "commercial_linkage", "mixed", "unclear"],
    "binary_reversal": ["", "0", "1", "none", "teaching_performance", "tradition_modern", "inner_outer", "health_traffic", "slow_fast", "unclear"],
    "visibility_centrality": ["", "low", "medium", "high", "unclear"],
    "tempo_discipline": ["", "slow_media", "balanced", "accelerated", "montage", "unclear"],
    "efficacy_tagging": ["", "none", "mild_health", "strong_health", "medicalized", "anxiety_marketing", "unclear"],
    "image_trace_strength": ["", "none", "weak", "moderate", "strong", "unclear"],
    "media_temporality": ["", "continuous", "fragmented", "looped", "hot_trend", "live_stream", "mixed", "unclear"],
    "meme_density": ["", "none", "low", "medium", "high", "unclear"],
    "embodied_dissolution": ["", "none", "weak", "moderate", "strong", "unclear"],
}

SUGGESTION_MAP = {
    "dominant_frame": "suggested_dominant_frame",
    "body_visibility": "suggested_body_visibility",
    "movement_tempo": "suggested_movement_tempo",
    "origin_reference": "suggested_origin_reference",
    "efficacy_tagging": "suggested_efficacy_tagging",
    "embodied_dissolution": "suggested_embodied_dissolution",
}

FIELD_LABELS = {
    "dominant_frame": "主导身体框架",
    "body_visibility": "身体可见性",
    "movement_tempo": "动作节奏",
    "origin_reference": "来源/正统性引用",
    "supplement_mode": "平台补充方式",
    "binary_reversal": "二元反转/张力结构",
    "visibility_centrality": "可视性中心化",
    "tempo_discipline": "节奏规训",
    "efficacy_tagging": "功效标签化",
    "image_trace_strength": "影像痕迹强度",
    "media_temporality": "媒介时间性",
    "meme_density": "玩梗密度",
    "embodied_dissolution": "具身消解",
    "coder_id": "编码员编号",
    "trace_markers": "证据标记",
    "notes": "备注",
}

OPTION_LABELS = {
    "": "空白",
    "instructional_body": "教学身体",
    "therapeutic_body": "疗愈/健康身体",
    "cultural_body": "文化身体",
    "spectacular_body": "景观/表演身体",
    "social_body": "社交身体",
    "commercial_body": "商业身体",
    "unclear": "无法判断",
    "full_body": "全身可见",
    "upper_body": "上半身为主",
    "partial": "局部身体",
    "close_up": "特写",
    "slow_continuous": "慢速连续",
    "segmented_teaching": "分段教学",
    "fast_montage": "快速剪辑",
    "mixed": "混合",
    "none": "无",
    "official_routine": "官方套路/标准功法",
    "master_teacher": "名师/师承",
    "ancient_tradition": "古法/传统",
    "national_culture": "民族/国家文化",
    "medical_health": "医学/健康话语",
    "caption": "字幕补充",
    "caption_explanation": "字幕解释",
    "music_reframing": "音乐再语境化",
    "comment_interaction": "评论互动",
    "hashtag_recontextualization": "标签再语境化",
    "commercial_linkage": "商业链接",
    "0": "无明显反转",
    "1": "有明显反转",
    "teaching_performance": "教学/表演反转",
    "tradition_modern": "传统/现代反转",
    "inner_outer": "内在气感/外在形态反转",
    "health_traffic": "健康/流量反转",
    "slow_fast": "慢练/快节奏反转",
    "low": "低",
    "medium": "中",
    "high": "高",
    "slow_media": "慢媒体/慢教学",
    "balanced": "相对均衡",
    "accelerated": "加速",
    "montage": "剪辑化",
    "mild_health": "温和养生",
    "strong_health": "强功效健康",
    "medicalized": "医学化/治疗化",
    "anxiety_marketing": "焦虑营销",
    "weak": "弱",
    "moderate": "中等",
    "strong": "强",
    "continuous": "连续",
    "fragmented": "碎片化",
    "looped": "循环播放",
    "hot_trend": "热点/挑战化",
    "live_stream": "直播化",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in rows)


def hash_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def clean(value: object) -> str:
    return str(value or "").strip()


def load_private_url_map(patterns: list[str]) -> tuple[dict[str, dict[str, str]], list[str]]:
    url_by_hash: dict[str, dict[str, str]] = {}
    sources: list[str] = []
    for pattern in patterns:
        for source in sorted(glob.glob(pattern, recursive=True)):
            path = Path(source)
            if not path.is_file():
                continue
            fields, rows = read_csv(path)
            if "url" not in fields:
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


def attach_private_links(rows: list[dict[str, str]], metadata_csv: Path, private_url_patterns: list[str]) -> tuple[int, list[str]]:
    metadata_fields, metadata_rows = read_csv(metadata_csv)
    if not metadata_rows or "url_hash" not in metadata_fields:
        return 0, []
    metadata_by_video_id = {clean(row.get("video_id")): row for row in metadata_rows}
    url_by_hash, sources = load_private_url_map(private_url_patterns)
    matched = 0
    for row in rows:
        metadata = metadata_by_video_id.get(clean(row.get("video_id")), {})
        url_hash = clean(metadata.get("url_hash"))
        row["url_hash"] = url_hash
        private_match = url_by_hash.get(url_hash)
        if private_match:
            row.update(private_match)
            row["link_status"] = "matched_private_url"
            matched += 1
        else:
            row.setdefault("video_url", "")
            row.setdefault("private_url_source", "")
            row.setdefault("private_source_video_id", "")
            row["link_status"] = "missing_private_url"
    return matched, sources


def render_html(rows: list[dict[str, str]], fieldnames: list[str], export_name: str, workbench_title: str) -> str:
    payload = json.dumps(rows, ensure_ascii=False)
    fields = json.dumps(fieldnames, ensure_ascii=False)
    formal_fields = json.dumps(FORMAL_FIELDS, ensure_ascii=False)
    select_options = json.dumps(SELECT_OPTIONS, ensure_ascii=False)
    suggestion_map = json.dumps(SUGGESTION_MAP, ensure_ascii=False)
    field_labels = json.dumps(FIELD_LABELS, ensure_ascii=False)
    option_labels = json.dumps(OPTION_LABELS, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(workbench_title)}</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #17202a; background: #fff; }}
    header {{ position: sticky; top: 0; z-index: 4; background: #fff; border-bottom: 1px solid #d7dde5; padding: 14px 18px; }}
    h1 {{ font-size: 20px; margin: 0 0 8px; letter-spacing: 0; }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    button {{ border: 1px solid #b8c2cc; background: #fff; border-radius: 6px; padding: 7px 10px; cursor: pointer; }}
    button.primary {{ background: #1f6feb; color: #fff; border-color: #1f6feb; }}
    a.video-link {{ display: inline-flex; align-items: center; text-decoration: none; border: 1px solid #1f6feb; color: #1f6feb; border-radius: 6px; padding: 5px 8px; margin-right: 8px; }}
    main {{ padding: 16px 18px 60px; }}
    .card {{ border: 1px solid #d7dde5; border-radius: 8px; padding: 12px; margin: 0 0 14px; }}
    .meta {{ display: grid; grid-template-columns: 90px 1fr; gap: 4px 10px; font-size: 13px; }}
    .meta b {{ color: #5e6b78; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(160px, 1fr)); gap: 10px; margin-top: 12px; }}
    label {{ display: grid; gap: 4px; font-size: 12px; color: #5e6b78; }}
    select, input, textarea {{ width: 100%; box-sizing: border-box; border: 1px solid #c7d0da; border-radius: 6px; padding: 7px; font: inherit; }}
    textarea {{ min-height: 74px; grid-column: span 2; }}
    .suggestion {{ color: #5e6b78; font-size: 12px; min-height: 16px; line-height: 1.45; }}
    .done {{ border-color: #2da44e; background: #f0fff4; }}
    .warn {{ color: #8a5a00; }}
    .muted {{ color: #5e6b78; line-height: 1.55; }}
    .private-note {{ color: #7a4b00; background: #fff8c5; border: 1px solid #eac54f; border-radius: 6px; padding: 7px 9px; margin-top: 8px; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} textarea {{ grid-column: span 1; }} .meta {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(workbench_title)}</h1>
    <div class="toolbar">
      <button onclick="copySuggestions()">将可用建议填入空白字段</button>
      <button onclick="markCoder()">coder_id 填 coder_main</button>
      <button class="primary" onclick="downloadCsv()">导出已填 CSV</button>
      <span id="progress" class="muted"></span>
    </div>
    <div class="muted">LLM 建议只作提示。请先打开视频核验，再填写或采用建议。导出后把 CSV 交给我导入审计；未核验时不要当论文结果。</div>
    <div class="private-note">如本页显示“打开视频”，链接仅用于本地人工编码核验，不写入公开论文和公开交付包。</div>
  </header>
  <main id="app"></main>
  <script>
    const rows = {payload};
    const fieldnames = {fields};
    const formalFields = {formal_fields};
    const selectOptions = {select_options};
    const suggestionMap = {suggestion_map};
    const fieldLabels = {field_labels};
    const optionLabels = {option_labels};
    const exportName = {json.dumps(export_name)};

    const app = document.getElementById('app');

    function esc(s) {{
      return String(s ?? '').replace(/[&<>"']/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
    }}

    function labelForField(field) {{
      return fieldLabels[field] || field;
    }}

    function labelForOption(option) {{
      if (!option) return '空白';
      return (optionLabels[option] || option) + '（' + option + '）';
    }}

    function fieldControl(rowIndex, field) {{
      const value = rows[rowIndex][field] || '';
      const suggestionField = suggestionMap[field];
      const suggestion = suggestionField ? (rows[rowIndex][suggestionField] || '') : '';
      const options = selectOptions[field];
      if (options) {{
        return `<label>${{labelForField(field)}}<select data-row="${{rowIndex}}" data-field="${{field}}" onchange="updateValue(this)">${{options.map(opt => `<option value="${{esc(opt)}}" ${{opt===value?'selected':''}}>${{esc(labelForOption(opt))}}</option>`).join('')}}</select><span class="suggestion">${{suggestion ? '建议：' + esc(labelForOption(suggestion)) : ''}}</span></label>`;
      }}
      if (field === 'notes' || field === 'trace_markers') {{
        return `<label>${{labelForField(field)}}<textarea data-row="${{rowIndex}}" data-field="${{field}}" oninput="updateValue(this)">${{esc(value)}}</textarea><span class="suggestion">${{field==='notes' ? esc(rows[rowIndex].llm_rationale || '') : ''}}</span></label>`;
      }}
      return `<label>${{labelForField(field)}}<input data-row="${{rowIndex}}" data-field="${{field}}" value="${{esc(value)}}" oninput="updateValue(this)"><span class="suggestion">${{suggestion ? '建议：' + esc(suggestion) : ''}}</span></label>`;
    }}

    function render() {{
      app.innerHTML = rows.map((row, i) => {{
        const required = formalFields.filter(f => f !== 'trace_markers' && f !== 'notes');
        const done = required.every(f => String(row[f] || '').trim());
        const videoUrl = String(row.video_url || '').trim();
        const linkHtml = videoUrl
          ? `<a class="video-link" target="_blank" rel="noopener noreferrer" href="${{esc(videoUrl)}}">打开视频</a><span class="muted">${{esc(row.link_status || '')}}</span>`
          : `<span class="warn">未找到可直开的私有链接。请按标题/平台搜索，或补充 URL 后再编码。</span>`;
        return `<section class="card ${{done ? 'done' : ''}}">
          <div class="meta">
            <b>Excel 行</b><span>${{i + 2}}</span>
            <b>视频</b><span>${{esc(row.video_id)}} | ${{esc(row.platform)}} | ${{esc(row.keyword)}}</span>
            <b>链接</b><span>${{linkHtml}}</span>
            <b>标题</b><span>${{esc(row.title)}}</span>
            <b>标签</b><span>${{esc(row.hashtags || '')}}</span>
            <b>建议/理由</b><span>${{esc(row.suggested_dominant_frame || '')}}; ${{esc(row.llm_rationale || '')}}</span>
          </div>
          <div class="grid">${{formalFields.map(f => fieldControl(i, f)).join('')}}</div>
        </section>`;
      }}).join('');
      updateProgress();
    }}

    function updateValue(el) {{
      rows[Number(el.dataset.row)][el.dataset.field] = el.value;
      updateProgress();
    }}

    function copySuggestions() {{
      rows.forEach(row => {{
        for (const [field, suggestionField] of Object.entries(suggestionMap)) {{
          if (!String(row[field] || '').trim() && row[suggestionField]) row[field] = row[suggestionField];
        }}
      }});
      render();
    }}

    function markCoder() {{
      rows.forEach(row => {{ if (!String(row.coder_id || '').trim()) row.coder_id = 'coder_main'; }});
      render();
    }}

    function updateProgress() {{
      const required = formalFields.filter(f => f !== 'trace_markers' && f !== 'notes');
      const done = rows.filter(row => required.every(f => String(row[f] || '').trim())).length;
      document.getElementById('progress').textContent = `${{done}} / ${{rows.length}} 已完成`;
    }}

    function csvEscape(value) {{
      const s = String(value ?? '');
      return /[",\\n\\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
    }}

    function downloadCsv() {{
      const csv = [fieldnames.join(',')].concat(rows.map(row => fieldnames.map(f => csvEscape(row[f] || '')).join(','))).join('\\n');
      const blob = new Blob(['\\ufeff' + csv], {{type: 'text/csv;charset=utf-8'}});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = exportName;
      a.click();
      URL.revokeObjectURL(a.href);
    }}

    render();
  </script>
</body>
</html>
"""


def write_md(path: Path, html_path: Path, template_path: Path) -> None:
    lines = [
        "# 前20条人工编码浏览器工作台",
        "",
        "这个工作台只用于前20条样本的人工编码。只有在导出、导入、审计通过之后，才可以作为论文证据。",
        "",
        f"- HTML: `{html_path}`",
        f"- 导出模板: `{template_path}`",
        "- 在浏览器打开 HTML，先看视频，再填写字段，最后导出 CSV，并告诉 Codex 导入。",
        "",
        "Recommended ingest after export:",
        "",
        "```bash",
        "python scripts/ingest_qigong_first20_export.py --export-csv qigong_first20_human_coding_export.csv",
        "```",
        "",
        "If the export lands in `~/Downloads`, the path can be omitted:",
        "",
        "```bash",
        "python scripts/ingest_qigong_first20_export.py",
        "```",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a browser workbench for the first 20 Health Qigong human-coding rows.")
    parser.add_argument("--batch", default="runs/qigong_platform/formal_merge/human_coding_batches/human_coding_batch_01.csv")
    parser.add_argument("--output-html", default="runs/qigong_platform/formal_merge/manual_action_pack/first20_coding_workbench.html")
    parser.add_argument("--output-template", default="runs/qigong_platform/formal_merge/manual_action_pack/first20_coding_export_template.csv")
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/manual_action_pack/first20_coding_workbench.md")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--export-name", default="qigong_first20_human_coding_export.csv")
    parser.add_argument("--title", default="健身气功短视频前20条人工编码工作台")
    parser.add_argument("--metadata", default="data/qigong_platform_metadata_coding_sample.csv")
    parser.add_argument("--include-private-links", action="store_true", help="Attach raw private video URLs for local human coding only.")
    parser.add_argument(
        "--private-url-glob",
        action="append",
        default=[],
        help="Glob for private URL CSV files. Can be repeated. Defaults to data/private/**/*urls*.csv when --include-private-links is used.",
    )
    args = parser.parse_args()

    fieldnames, rows = read_csv(Path(args.batch))
    rows = rows[: args.limit]
    if args.include_private_links:
        private_patterns = args.private_url_glob or ["data/private/**/*urls*.csv"]
        matched, sources = attach_private_links(rows, Path(args.metadata), private_patterns)
        for extra_field in ["url_hash", "video_url", "link_status", "private_url_source", "private_source_video_id"]:
            if extra_field not in fieldnames:
                fieldnames.append(extra_field)
        print(f"private_links_matched={matched}/{len(rows)}")
        print(f"private_url_sources={len(sources)}")
    output_template = Path(args.output_template)
    output_html = Path(args.output_html)
    output_md = Path(args.output_md)
    write_csv(output_template, rows, fieldnames)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(render_html(rows, fieldnames, args.export_name, args.title), encoding="utf-8")
    write_md(output_md, output_html, output_template)
    print(output_html)
    print(output_template)
    print(output_md)


if __name__ == "__main__":
    main()
