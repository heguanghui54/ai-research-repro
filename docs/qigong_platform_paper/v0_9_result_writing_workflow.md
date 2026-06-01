# v0.9 结果稿生成流程

本文件说明学生网页编码、双编码可靠性、评论和典型视频数据回收后，如何把结果表安全地写入论文。核心原则：脚本可以帮忙转写，但不能绕过证据门槛。

## 一、生成结果简报

```bash
python3 scripts/create_qigong_v0_9_result_brief.py
```

输出：

- `runs/qigong_platform/formal_merge/manuscript_result_brief_v0_9.md`
- `runs/qigong_platform/formal_merge/manuscript_result_brief_v0_9_gate.json`

如果网页人工编码、编码值审计或双编码可靠性没有通过，结果简报会自动写成“当前不报告正式经验结果”。这不是失败，而是防止论文提前写入无证据结果。

## 二、装配 v0.9 稿件

```bash
python3 scripts/create_qigong_manuscript_v0_9_from_results.py
```

输出：

- `docs/qigong_platform_paper/manuscript_draft_v0_9_gated_results.md`

该稿会把结果简报插入 v0.8 当前证据稿中。如果门槛未过，它仍然是“审计型结果回填状态稿”，不是投稿稿。

## 三、审计 v0.9 稿件

```bash
python3 scripts/audit_qigong_manuscript_text.py \
  --manuscript docs/qigong_platform_paper/manuscript_draft_v0_9_gated_results.md \
  --research-audit-json runs/qigong_platform/formal_merge/current_submission_gate.json \
  --output-md runs/qigong_platform/formal_merge/manuscript_v0_9_text_audit.md \
  --output-json runs/qigong_platform/formal_merge/manuscript_v0_9_text_audit.json
```

如果审计出现 `fail`，不能进入投稿版本。

## 四、可写入正式结果的最低条件

1. `web_coding_submissions_export_summary.json`：完整提交不少于 120，主编码不少于 120。
2. `web_coding_ingest_audit.json`：`ready_for_formal_audit=True`。
3. `web_human_coding_values_audit.json`：无 fail。
4. `web_reliability_gate.json`：所有门槛为 pass。
5. 评论若要写频率结论，`comment_audit.json` 无 fail；否则只能写质性近读。
6. 视频若要写姿态/轨迹/节奏结论，`video_file_preflight.json` 和视频特征表必须通过。

## 五、正式结果段落的边界

可以写：

> 网页人工编码结果显示，样本中的主导意义框架、可视性中心、节奏规训和功效标签化呈现出若干结构性分布。该分布经双编码一致性检验后进入正式分析。

不能写：

> 算法导致健身气功必然异化。

原因：本研究是平台样本的内容分析、评论近读和典型案例视频分析，不能直接证明因果。
