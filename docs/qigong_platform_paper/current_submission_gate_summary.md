# 当前投稿门槛总表摘要

更新时间：2026-06-01

本摘要来自：

```bash
python3 scripts/build_qigong_current_submission_gate.py
```

输出文件：

- `runs/qigong_platform/formal_merge/current_submission_gate.md`
- `runs/qigong_platform/formal_merge/current_submission_gate.json`

## 总体判断

当前研究包仍是“当前证据约束下的研究生产包”，还不是《武汉体育学院学报》投稿终稿。可以继续推进理论框架、方法设计、人工编码平台和视频分析管道，但不能把未完成的人工编码、评论频率或 SportsLabKit 结果写成正式发现。

当前门槛统计：

| 类型 | 数量 |
|---|---:|
| pass | 4 |
| warn | 6 |
| fail | 0 |

虽然没有脚本级 fail，但仍有 4 个 P0 non-pass 门槛，因此不能标记目标完成。

## 已通过的 P0

| 门槛 | 当前证据 |
|---|---|
| 作者身份与署名 | 稿件和元数据保留石伟、西南科技大学体育学院、副教授、中国科学技术大学博士 |
| 公开稿件模型命名 | 未发现聚合平台、私有 API 路由或自动科研工作流署名等公开稿件禁用表述；稿件出现具体模型名 `deepseek-chat` |
| 真实短视频样本池 | `metadata_rows=628`，`included=185`，覆盖 bilibili、douyin、kuaishou、xiaohongshu |

## 未通过的 P0

| 门槛 | 当前证据 | 下一步 |
|---|---|---|
| 网页人工编码提交 | `complete_rows=0`，`primary_submissions=0` | 让 STU01-STU10 完成网页编码 |
| 网页提交转正式编码表 | `dominant_frame_filled=0/120` | 学生提交后运行 export + ingest + formal coding audit |
| 典型视频本地权利与文件预检 | `ready_local_rights=0/5`，目标至少 `3/5` | 上传并确认 `TC0001.mp4`、`TC0002.mp4`、`TC0003.mp4` |
| 全目标完成度审计 | 当前仍有视觉模型、Ubuntu 复现、投稿终审等缺口 | P0 输入齐备后重跑全目标审计 |

## P1 风险

| 门槛 | 当前证据 | 写作边界 |
|---|---|---|
| 评论语料审计 | 评论数、覆盖率、单视频评论数仍未达标 | 只能写匿名评论近读，不能写频率结论 |
| SportsLabKit/OpenCV 环境 | 当前本机 `sportslabkit=False`，`opencv_motion=True`，本地视频 0 | 未跑通前不能写 SportsLabKit 结果 |
| HF/benchmark 边界 | 已通过 | HF/MultiSports 只作为基线和校准，不替代真实短视频平台样本 |

## 下一步优先级

1. 学生完成网页人工编码，先解决 `0/120`。
2. 上传至少 3 个本地授权典型视频，先解决 `0/5`。
3. 补齐评论覆盖或明确降级为近读材料。
4. 在 Ubuntu 上跑正式复现实验包。
5. 用通过审计的数据更新 v0.7 稿件结果部分。
