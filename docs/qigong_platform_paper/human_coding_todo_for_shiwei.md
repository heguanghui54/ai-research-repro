# 健身气功短视频论文人工编码 TODO

用途：完成《平台/短视频如何重塑健身气功的意义生成与身体经验》论文的正式 120 条人工编码。LLM 预填只能作为提示，不能直接作为论文结果。

## 现在推荐的做法：用网页让学生分工填写

1. 给 10 名学生分配编号 `STU01` 至 `STU10`。
2. 把网页填写入口、学生编号和访问口令分别发给学生。访问口令不要写进公开论文材料。
3. 学生登录后只填写系统分配给自己的任务；缺视频链接的条目会显示“缺视频链接，暂缓编码”，不要要求学生硬填。
4. 每条任务必须点击“打开视频”并人工观看后填写。LLM 辅助建议只能用于提示，不能替代人工判断。
5. 学生完成后，研究者运行导出脚本，检查完整提交数、缺失字段、复核任务和异常值。
6. 网页提交导出后会用 `scripts/ingest_qigong_web_coding_submissions.py` 转成正式编码表，再进入正式审计和论文结果表。

网页分工细则见 `student_web_coding_distribution.md`，论文方法写法见 `web_human_coding_method_note.md`。

## 备用做法：本地表格/HTML 工作台

1. 先读 `human_coding_quick_card.md`，再需要时查 `human_coding_manual.md`。
2. 前 20 条优先打开 `data/private/qigong_first20_coding_workbench_with_links.html`，这是中文界面并带视频链接的本地私有工作台。
3. 逐条点击“打开视频”，看完标题、标签、画面、字幕/口令、剪辑节奏和可见的评论/平台语境后再填。不要只凭标题或 LLM 建议填。
4. 没有视频链接的条目先暂缓编码；缺失清单见 `data/private/qigong_first20_missing_video_links_todo.csv`。
5. 前 20 条通过导入和审计后，再继续后续 100 条。

如果你想用 Excel 全量工作簿，也可以打开 `runs/qigong_platform/formal_merge/qigong_human_coding_workbook.xlsx`，但它不负责展示私有视频链接；前 20 条建议仍以私有 HTML 工作台为准。

## 每条视频要填的正式字段

请人工确认并填写以下字段：

- `dominant_frame`
- `body_visibility`
- `movement_tempo`
- `origin_reference`
- `supplement_mode`
- `binary_reversal`
- `visibility_centrality`
- `tempo_discipline`
- `efficacy_tagging`
- `image_trace_strength`
- `media_temporality`
- `meme_density`
- `embodied_dissolution`
- `coder_id`

`coder_id` 统一填 `coder_main`。证据不足时填 `unclear`，不要硬判。

## 可以参考但不能直接当结果的列

Excel 工作簿中的 `llm_` 列、评论信号列，以及 Batch 表中 `suggested_` 开头的列和 `llm_` 开头的列，都是辅助提示：

- 可以帮助你快速定位可能的意义框架、身体可见性、节奏、功效化、玩梗化等特征。
- 必须经过你人工观看、核验标题/标签/画面/评论线索后，才能填入正式字段。
- 如果你不同意建议值，以人工判断为准，并在 `notes` 简短说明。

## 不要写入表格的内容

- 不要写原始 URL。
- 不要写用户名、主页、联系方式。
- 不要复制评论者身份信息。
- `notes` 和 `trace_markers` 只写匿名化观察，例如：`标题强调完整版与呼吸口令，画面为正面跟练，未见玩梗化标签。`

## 文件位置

- 推荐 Excel 工作簿: `runs/qigong_platform/formal_merge/qigong_human_coding_workbook.xlsx`
- 前20条中文私有链接工作台: `data/private/qigong_first20_coding_workbench_with_links.html`
- 前20条缺失链接清单: `data/private/qigong_first20_missing_video_links_todo.csv`
- Excel 预检报告: `runs/qigong_platform/formal_merge/qigong_human_coding_xlsx_preflight.md`
- Batch 01: `runs/qigong_platform/formal_merge/human_coding_batches/human_coding_batch_01.csv`
- Batch 02: `runs/qigong_platform/formal_merge/human_coding_batches/human_coding_batch_02.csv`
- Batch 03: `runs/qigong_platform/formal_merge/human_coding_batches/human_coding_batch_03.csv`
- Batch 04: `runs/qigong_platform/formal_merge/human_coding_batches/human_coding_batch_04.csv`
- Batch 05: `runs/qigong_platform/formal_merge/human_coding_batches/human_coding_batch_05.csv`
- Batch 06: `runs/qigong_platform/formal_merge/human_coding_batches/human_coding_batch_06.csv`

## 你完成前 20 条后我会做什么

如果你填的是 Excel 工作簿，我会运行：

```bash
python scripts/audit_qigong_human_coding_xlsx.py --workbook runs/qigong_platform/formal_merge/qigong_human_coding_workbook.xlsx
python scripts/ingest_qigong_human_coding_xlsx.py --workbook runs/qigong_platform/formal_merge/qigong_human_coding_workbook.xlsx
python scripts/audit_qigong_coding_values.py --coding runs/qigong_platform/formal_merge/qigong_human_coding_from_xlsx.csv --profile formal
python scripts/build_qigong_human_coding_progress.py
python scripts/refresh_qigong_readiness_dashboards.py
```

如果你填的是 Batch 01 CSV，我会运行：

```bash
python scripts/ingest_qigong_human_coding_batch.py --batch-csv runs/qigong_platform/formal_merge/human_coding_batches/human_coding_batch_01.csv --output-coding runs/qigong_platform/formal_merge/human_coding_batch_01_merged.csv
python scripts/audit_qigong_coding_values.py --coding runs/qigong_platform/formal_merge/human_coding_batch_01_merged.csv --profile formal
python scripts/build_qigong_human_coding_progress.py
python scripts/refresh_qigong_readiness_dashboards.py
```

如果前 20 条通过，就继续后续批次；全部完成后再做双编码信度、评论证据、典型视频 SportsLabKit/视觉模型分析和正式论文结果表。
