# 当前投稿闸门套件

本文件说明如何一键刷新当前论文包的关键闸门。它面向现在的 v0.9 工作流：网页人工编码、双编码可靠性、典型视频、结果回填、文本审计和目标完成度。

## 运行命令

先 dry run：

```bash
python3 scripts/run_qigong_current_submission_gate_suite.py --dry-run
```

正式刷新：

```bash
python3 scripts/run_qigong_current_submission_gate_suite.py
```

输出：

- `runs/qigong_platform/formal_merge/current_submission_gate_suite.md`
- `runs/qigong_platform/formal_merge/current_submission_gate_suite.json`

## 它会刷新什么

1. 当前投稿门槛总表。
2. v0.9 结果简报。
3. v0.9 门槛稿。
4. v0.9 文本审计。
5. v0.9 当前证据一致性审计。
6. 网页双编码可靠性门槛。
7. 典型视频文件预检。
8. 全目标完成度审计。

## 如何读结果

如果 `current_submission_gate_suite.md` 中 `artifacts_with_fail` 不是空，说明当前还不是投稿完成态。

现在最可能的非通过项是：

- 学生网页编码未完成。
- 双编码可靠性不足 24 条。
- 评论覆盖不足。
- TC0001-TC0003 本地视频未上传或未权利确认。
- Ubuntu 复现产物未生成。

## 投稿前才允许做的事

只有当前投稿总门槛无 warn/fail，且 v0.9 结果简报写出正式结果段落时，才可以把 `manuscript_draft_v0_9_gated_results.md` 作为投稿稿基础。

否则，该稿只是“当前证据稿”或“审计型结果回填稿”，不能直接投稿。
