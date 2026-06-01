# 学生网页编码回收后的处理流程

本文件用于把 STU01-STU10 的网页人工编码提交转成论文可用的正式结果表。它是数据采集方法的一部分，也是一条证据纪律线：只有通过本流程，网页填写结果才可以进入《武汉体育学院学报》投稿稿的结果部分。

## 一、运行前条件

1. 学生已经在网页系统完成自己的主编码任务。
2. 至少 120 条主编码任务完整提交。
3. 双编码复核任务已经完成，后续可做一致性检验。
4. 本机私有环境中已设置 `QIGONG_CODING_ADMIN_CODE`。不要把该 code 写入论文、GitHub、微信群或公开文档。

可先做 dry run 检查将要执行的命令：

```bash
python3 scripts/run_qigong_post_web_coding_pipeline.py --dry-run
```

正式运行：

```bash
QIGONG_CODING_ADMIN_CODE=本机私有导出码 python3 scripts/run_qigong_post_web_coding_pipeline.py
```

## 二、流水线会生成什么

运行脚本会依次执行：

1. 从 Supabase 导出网页编码提交：
   `runs/qigong_platform/formal_merge/web_coding_submissions_export.csv`
2. 汇总学生提交状态：
   `runs/qigong_platform/formal_merge/web_coding_submissions_export_summary.md`
3. 合并网页主编码到正式人工编码表：
   `runs/qigong_platform/formal_merge/qigong_human_coding_from_web.csv`
4. 导出双编码复核表：
   `runs/qigong_platform/formal_merge/qigong_double_coding_from_web.csv`
5. 运行正式编码值审计：
   `runs/qigong_platform/formal_merge/web_human_coding_values_audit.md`
6. 生成初步结果表：
   `runs/qigong_platform/formal_merge/tables_from_web_coding/`
7. 刷新当前投稿门槛总表：
   `runs/qigong_platform/formal_merge/current_submission_gate.md`
8. 生成本次流水线报告：
   `runs/qigong_platform/formal_merge/post_web_coding_pipeline_report.md`

## 三、结果能否写进论文的判断

可以写入正式结果的最低条件：

1. `web_coding_submissions_export_summary.md` 中 `完整提交行数 >= 120`。
2. `web_coding_ingest_audit.md` 中 `ready_for_formal_audit: True`。
3. `web_human_coding_values_audit.md` 中正式编码值审计无 fail。
4. `current_submission_gate.md` 中“网页人工编码提交”和“网页提交转正式编码表”均为 pass。

如果上述任一条件没有满足，论文仍保持 v0.8 当前证据稿写法，只能写“网页人工编码平台已建立、学生编码正在进行”，不能写“编码结果显示”。

## 四、论文方法部分可写法

待流水线通过后，可在方法部分写：

> 本研究建立网页人工编码系统，将 120 条正式样本分配给 10 名学生编码员，并设置双编码复核任务。编码员依据统一中文编码手册观看视频，填写主导意义框架、身体可见性、动作节奏、影像痕迹强度、媒介时间性和具身消解程度等变量。网页提交经导出、合并、值域审计和一致性检验后进入正式统计分析。

待流水线未通过时，只能写：

> 本研究已建立网页人工编码系统，并完成任务分配；当前版本仅报告方法设计和证据边界，不报告尚未完成的人工编码结果。

## 五、后续仍需完成

- 双编码一致性：基于 `qigong_double_coding_from_web.csv` 计算一致性，并生成分歧复核表。
- 评论补采：按 `comment_collection_targets.md` 补齐评论覆盖率。
- 典型视频：上传 TC0001-TC0003 后重跑视频预检和 SportsLabKit/后备视频分析。
- 稿件更新：只有数据门槛通过后，才把 v0.8 当前证据稿升级为正式结果稿。
