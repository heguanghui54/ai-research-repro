# SportsLabKit 典型视频证据层当前状态

更新时间：2026-06-01

## 研究用途

本层用于补强论文中的“身体经验”证据：在真实平台样本与人工编码之外，选取少量典型视频进行本地抽帧、身体可见性、动作节奏、姿态/轨迹或帧级视觉分析。该层不替代传播学解释，也不替代学生人工编码；它只用于说明短视频影像技术如何改变健身气功动作呈现、身体可见性和节奏结构。

## 当前设计

`data/qigong_video_manifest.csv` 已设计 5 个典型案例：

| video_id | 角色 | 组别 | 功法 | 动作段 | 计划用途 | 当前权利状态 | 本地文件 |
|---|---|---|---|---|---|---|---|
| TC0001 | 标准参照 | official | 八段锦 | 左右开弓似射雕 | pose_feature_and_frame_coding | rights_confirmed | 缺 |
| TC0002 | 平台变体 | platform | 八段锦 | 左右开弓似射雕 | pose_feature_and_frame_coding | manual_view_only | 缺 |
| TC0003 | 平台变体 | platform | 五禽戏 | 鸟戏 | pose_feature_and_frame_coding | manual_view_only | 缺 |
| TC0004 | 平台变体 | platform | 六字诀 | 嘘字诀 | frame_coding_only | manual_view_only | 缺 |
| TC0005 | 平台变体 | platform | 易筋经 | 韦驮献杵 | frame_coding_only | manual_view_only | 缺 |

## 当前预检结果

已运行：

```bash
python3 scripts/create_qigong_video_acquisition_task_pack.py --manifest data/qigong_video_manifest.csv --metadata data/qigong_platform_metadata_coding_sample.csv --video-dir data/private/qigong_typical_videos --output-dir runs/qigong_platform/formal_merge/video_acquisition_tasks
python3 scripts/audit_qigong_video_files_preflight.py --manifest data/qigong_video_manifest.csv --tasks-csv runs/qigong_platform/formal_merge/video_acquisition_tasks/video_acquisition_tasks.csv --video-dir data/private/qigong_typical_videos --output-md runs/qigong_platform/formal_merge/video_file_preflight.md --output-json runs/qigong_platform/formal_merge/video_file_preflight.json --issues-csv runs/qigong_platform/formal_merge/video_file_preflight_issues.csv
```

当前结果：

- 典型案例任务数：5
- 平台候选视频行：32
- 本地权利确认可分析视频：0/5
- 最低可分析门槛：至少 3 个本地文件且 `rights_status=rights_confirmed`
- 当前问题：5 个 `missing_local_file`

因此，论文目前不能报告 SportsLabKit、姿态估计、动作轨迹、运动幅度或节奏特征结果。只能写“已设计典型视频分析层和预检管道”。

## 需要上传/准备的视频

将视频放入：

```text
data/private/qigong_typical_videos/
```

文件名必须为：

```text
TC0001.mp4
TC0002.mp4
TC0003.mp4
TC0004.mp4
TC0005.mp4
```

最低先准备 3 个即可进入初步分析：`TC0001.mp4`、`TC0002.mp4`、`TC0003.mp4`。其中 `TC0001` 应为官方/标准/自录授权的八段锦标准参照；`TC0002` 与 `TC0003` 应为平台变体，并且需要人工确认可用于本研究本地分析。

## 上传后操作

1. 人工确认每个本地视频的权利状态。
2. 将可本地分析的视频在 `data/qigong_video_manifest.csv` 中设为 `rights_confirmed`。
3. 运行：

```bash
python3 scripts/fill_qigong_video_manifest_from_files.py --manifest data/qigong_video_manifest.csv --video-dir data/private/qigong_typical_videos --output-manifest data/qigong_video_manifest.csv --absolute-paths --replace-existing
python3 scripts/audit_qigong_video_files_preflight.py --manifest data/qigong_video_manifest.csv --tasks-csv runs/qigong_platform/formal_merge/video_acquisition_tasks/video_acquisition_tasks.csv --video-dir data/private/qigong_typical_videos
python3 scripts/audit_qigong_video_manifest.py --manifest data/qigong_video_manifest.csv --metadata data/qigong_platform_metadata_formal.csv --profile formal --output-md runs/qigong_platform/audit/video_manifest_audit.md --output-json runs/qigong_platform/audit/video_manifest_audit.json
python3 scripts/audit_sportslabkit_environment.py --video-manifest data/qigong_video_manifest.csv --output-md runs/qigong_platform/audit/sportslabkit_environment_audit.md --output-json runs/qigong_platform/audit/sportslabkit_environment_audit.json
```

预检通过后，才运行抽帧和特征提取：

```bash
python3 scripts/sample_qigong_video_frames.py --manifest data/qigong_video_manifest.csv --output-root runs/qigong_platform/llm_frames --frame-index runs/qigong_platform/llm_frames_index.csv --max-frames 4
python3 scripts/extract_qigong_video_features.py --manifest data/qigong_video_manifest.csv --output runs/qigong_platform/features/video_features.csv
```

## 论文写作边界

当前可写：

- 研究设计了“标准参照-平台变体”的典型视频身体证据层。
- SportsLabKit/OpenCV/视觉模型只作为身体可见性与动作节奏分析工具。
- 本地视频分析必须通过权利确认、文件预检和环境审计。

当前不可写：

- 不可写已经获得姿态轨迹或动作偏离结果。
- 不可写平台变体相对标准参照的量化差异。
- 不可把 HF/MultiSports 等通用数据集替代真实健身气功平台视频。

## 投稿总门槛中的位置

`scripts/build_qigong_current_submission_gate.py` 已将典型视频本地权利与文件预检列为 P0 门槛。当前状态为 `ready_local_rights=0/5`，目标至少为 `3/5`。因此，SportsLabKit/视觉模型部分目前只能保留为方法设计和待执行管道，不能进入正式结果或摘要。
