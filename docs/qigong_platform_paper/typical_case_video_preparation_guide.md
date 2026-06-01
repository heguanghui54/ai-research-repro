# 典型案例视频准备指南

用途：为论文中的 SportsLabKit/视觉模型典型案例分析准备 3-5 个合法本地视频。该文件只说明数据准备和审计流程，不构成实证结果。

## 为什么必须准备本地授权视频

本论文的短视频传播论证可以使用公开元数据、标题、标签和匿名评论；但动作轨迹、姿态估计、帧级视觉编码属于对视频内容的本地计算分析，必须满足两个条件：

1. 视频文件已合法保存到本地。
2. `rights_status` 已由人工确认可用于本研究的本地分析。

未满足这两个条件的视频只能用于人工观看和语境记录，不能写入 SportsLabKit 姿态、轨迹、节奏或视觉模型结果。

## 当前典型案例设计

| video_id | 角色 | 功法 | 动作段 | 最低用途 |
|---|---|---|---|---|
| TC0001 | 标准参照 | 八段锦 | 左右开弓似射雕 | pose_feature_and_frame_coding |
| TC0002 | 平台变体 | 八段锦 | 左右开弓似射雕 | pose_feature_and_frame_coding |
| TC0003 | 平台变体 | 五禽戏 | 鸟戏 | pose_feature_and_frame_coding |
| TC0004 | 平台变体 | 六字诀 | 嘘字诀 | frame_coding_only |
| TC0005 | 平台变体 | 易筋经 | 韦驮献杵 | frame_coding_only |

最小可分析门槛：至少 3 个 `rights_confirmed` 且 `local_video_path` 存在的本地视频，其中应包含 1 个标准参照和至少 2 个平台变体。

## 文件放置与命名

将视频放入：

```text
data/private/qigong_typical_videos/
```

推荐文件名：

```text
TC0001.mp4
TC0002.mp4
TC0003.mp4
TC0004.mp4
TC0005.mp4
```

如果原文件不是 mp4，可以先保留原格式，但建议最终转为 mp4，便于 OpenCV/SportsLabKit 读取。不要在文件名中写作者昵称、主页、手机号、真实 URL 等可识别信息。

## 权利状态规则

| rights_status | 含义 | 可否本地计算 |
|---|---|---|
| `rights_confirmed` | 已确认可用于本研究本地分析 | 可以 |
| `manual_view_only` | 只能人工观看，不做本地计算分析 | 不可以 |
| `excluded` | 不纳入研究 | 不可以 |

注意：把视频下载到本地并不等于 `rights_confirmed`。必须经过人工权利和伦理确认后，才可把 manifest 中对应行改为 `rights_confirmed`。

## manifest 填写规则

文件：`data/qigong_video_manifest.csv`

必须检查这些字段：

| 字段 | 填写要求 |
|---|---|
| `video_id` | 保持 TC0001-TC0005 不变 |
| `local_video_path` | 填本地绝对路径或由脚本自动填入 |
| `source_dataset` | 标准参照可写 `official_standard`；平台样本写 `platform_sample` |
| `platform` | 平台变体需填写平台名；标准参照可空 |
| `url_hash` | 平台变体应关联匿名 URL 哈希；不要写原始 URL |
| `case_role` | `standard_reference` 或 `platform_variant` |
| `comparison_group` | `official` 或 `platform` |
| `routine` | 八段锦、五禽戏、六字诀、易筋经等 |
| `action_segment` | 尽量写具体动作段 |
| `rights_status` | 仅人工确认后填写 `rights_confirmed` |
| `expected_use` | 姿态分析写 `pose_feature_and_frame_coding`；只做帧级视觉编码写 `frame_coding_only` |

## 推荐操作顺序

快速流程可直接运行：

```bash
python3 scripts/run_qigong_post_video_upload_pipeline.py --dry-run
python3 scripts/run_qigong_post_video_upload_pipeline.py
```

若已完成所有上传视频的人工权利确认，可显式加入：

```bash
python3 scripts/run_qigong_post_video_upload_pipeline.py --mark-rights-confirmed
```

默认流程不会自动把视频改成 `rights_confirmed`，以避免把“本地文件存在”误写成“可计算分析证据”。

1. 准备标准参照视频 `TC0001.mp4`。

   可使用官方公开标准视频、机构授权视频，或自行录制的标准示范视频。若自行录制，应在 notes 中说明“self-recorded reference”。

2. 准备平台变体视频 `TC0002.mp4` 至 `TC0005.mp4`。

   优先选择已经在正式 120 样本中的视频，并确保其标题、平台、匿名哈希能与 `data/qigong_platform_metadata_coding_sample.csv` 对应。

3. 人工确认权利状态。

   对能本地分析的视频，将 `rights_status` 改为 `rights_confirmed`；对不能确认的，保持 `manual_view_only`。

4. 自动填充本地路径。

```bash
mkdir -p data/private/qigong_typical_videos
python scripts/fill_qigong_video_manifest_from_files.py --manifest data/qigong_video_manifest.csv --video-dir data/private/qigong_typical_videos --output-manifest data/qigong_video_manifest.csv --absolute-paths --replace-existing
```

5. 运行视频 manifest 与文件预检。

```bash
python scripts/audit_qigong_video_files_preflight.py --manifest data/qigong_video_manifest.csv --tasks-csv runs/qigong_platform/formal_merge/video_acquisition_tasks/video_acquisition_tasks.csv --video-dir data/private/qigong_typical_videos
python scripts/audit_qigong_video_manifest.py --manifest data/qigong_video_manifest.csv --metadata data/qigong_platform_metadata_formal.csv --profile formal --output-md runs/qigong_platform/audit/video_manifest_audit.md --output-json runs/qigong_platform/audit/video_manifest_audit.json
python scripts/audit_sportslabkit_environment.py --video-manifest data/qigong_video_manifest.csv --output-md runs/qigong_platform/audit/sportslabkit_environment_audit.md --output-json runs/qigong_platform/audit/sportslabkit_environment_audit.json
```

6. 通过预检后再抽帧和提取特征。

```bash
python scripts/sample_qigong_video_frames.py --manifest data/qigong_video_manifest.csv --output-root runs/qigong_platform/llm_frames --frame-index runs/qigong_platform/llm_frames_index.csv --max-frames 4
python scripts/extract_qigong_video_features.py --manifest data/qigong_video_manifest.csv --output runs/qigong_platform/features/video_features.csv
python scripts/create_qigong_vision_model_packets.py --manifest data/qigong_video_manifest.csv --frame-index runs/qigong_platform/llm_frames_index.csv --output-jsonl runs/qigong_platform/llm/vision_model_packets.jsonl --output-md runs/qigong_platform/llm/vision_model_packets.md
```

视觉分析方法部分只写具体模型名，例如 `gemini-2.5-pro` 或 `gpt-5`。

## 可以写入论文的边界

### 预检前可以写

1. 本研究设计了标准参照与平台变体的典型案例视频分析层。
2. SportsLabKit/MediaPipe/OpenCV 用于辅助呈现身体可见性、动作节奏和姿态轨迹。
3. 视频分析层是对人工编码和评论近读的补充，不替代传播学解释。

### 预检通过后才可以写

1. 已分析多少个本地授权视频。
2. 哪些动作段被抽帧和编码。
3. 哪些视频可进入姿态/轨迹或帧级视觉分析。

### 特征提取与审计通过后才可以写

1. 具体关节、姿态、节奏、运动幅度或轨迹差异。
2. 标准参照与平台变体之间的动作呈现差异。
3. 由视频特征支持的“身体经验消解”或“影像化规训”案例论证。

## 常见错误

1. 只有平台 URL，没有本地文件，却写 SportsLabKit 结果。
2. 本地文件存在，但 `rights_status` 仍是 `manual_view_only`。
3. 使用 HF/MultiSports 视频替代真实健身气功短视频。
4. 直接写原始 URL、用户名或主页信息。
5. 将视觉模型描述当作人工编码结果。
6. 只抽帧不做审计，就把帧级描述写成实证发现。

## 投稿前最低证据

正式稿中若要保留视频分析结果，至少需要：

1. `video_file_preflight.md` 显示 ready local rights-confirmed files >= 3。
2. `video_manifest_audit.md` 无 P0 失败。
3. `sportslabkit_environment_audit.md` 显示可用环境。
4. `llm_frames_index.csv` 存在且覆盖可分析视频。
5. `video_features.csv` 或视觉模型编码表存在并通过对应审计。
6. 论文只引用已通过审计的视频结论。

## 当前状态快照

截至 2026-06-01，已生成视频获取任务包：

- `runs/qigong_platform/formal_merge/video_acquisition_tasks/video_acquisition_tasks.csv`
- `runs/qigong_platform/formal_merge/video_acquisition_tasks/video_acquisition_candidates.csv`
- `runs/qigong_platform/formal_merge/video_acquisition_tasks/README.md`

当前预检显示本地权利确认视频为 `0/5`，最低门槛为 `3/5`。因此，论文目前只能写典型视频分析层的设计与边界，不能写 SportsLabKit 姿态或动作轨迹结果。
