# 网页人工编码双编码一致性计划

本文件说明学生网页人工编码如何满足《武汉体育学院学报》投稿所需的编码可信度要求。它不报告结果，只规定门槛。

## 当前最低门槛

- 正式主编码样本：120 条。
- 双编码比例：不少于 20%。
- 最低双编码条数：24 条。
- 核心变量：`dominant_frame`、`visibility_centrality`、`tempo_discipline`、`efficacy_tagging`、`image_trace_strength`、`media_temporality`、`embodied_dissolution`。
- 统计指标：percent agreement、Cohen's kappa、nominal Krippendorff's alpha。

## 当前风险

网页系统当前已经设置了少量复核任务，但若只有 6 条复核任务，则不足以支撑投稿级一致性声明。6 条可以作为流程测试或编码员训练反馈，不能作为正式可靠性证据。

## 数据回收后运行

```bash
python3 scripts/run_qigong_post_web_coding_pipeline.py
```

该流水线会生成：

- `runs/qigong_platform/formal_merge/web_reliability/coding_reliability.csv`
- `runs/qigong_platform/formal_merge/web_reliability/coding_reliability_report.md`
- `runs/qigong_platform/formal_merge/web_reliability/coding_reconciliation.csv`
- `runs/qigong_platform/formal_merge/web_reliability_gate.md`

## 通过标准

1. `web_reliability_gate.md` 中 `double_coding_rows` 为 pass。
2. `web_reliability_gate.md` 中 `key_field_reliability_present` 为 pass。
3. 核心变量不能出现 `poor` 或 `insufficient`。
4. 若核心变量为 `weak`，需先进入分歧复核和编码手册修订，不能直接写成正式统计发现。

## 论文写法

通过后可写：

> 本研究对不少于 20% 的正式样本设置双编码复核，计算百分比一致率、Cohen's kappa 与 nominal Krippendorff's alpha。对低一致性变量，研究者依据分歧复核表修订编码说明并进行人工协商，最终仅报告达到可靠性门槛的变量结果。

未通过时只能写：

> 当前版本已建立双编码复核流程，但一致性分析尚未达到正式结果报告门槛，因此不报告人工编码变量分布。
