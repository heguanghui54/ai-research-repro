# 典型视频上传后的处理流程

本文件用于把本地上传的 TC0001-TC0005 典型视频转成论文可用的视频分析证据。它强调一个底线：本地视频文件存在，不等于可以写 SportsLabKit 或姿态估计结果；必须先通过权利确认、文件预检和工具环境审计。

## 一、上传位置与命名

把视频放入：

```text
data/private/qigong_typical_videos/
```

最低需要：

```text
TC0001.mp4  # 官方/标准参照，八段锦“左右开弓似射雕”
TC0002.mp4  # 平台变体，八段锦同动作段或相近动作段
TC0003.mp4  # 平台变体，五禽戏“鸟戏”或相近传统身体动作
```

可选：

```text
TC0004.mp4  # 六字诀
TC0005.mp4  # 易筋经
```

文件名不要包含作者昵称、主页、手机号、真实 URL 或其他可识别信息。

## 二、权利确认规则

默认流水线只会自动填 `local_video_path`，不会自动把 `rights_status` 改成 `rights_confirmed`。原因是：下载到本地并不等于拥有本地计算分析许可。

只有在人工确认某个视频可用于本研究本地分析后，才可以把对应 manifest 行设为：

```text
rights_status=rights_confirmed
```

若确认全部上传视频均可用于本地分析，可运行：

```bash
python3 scripts/run_qigong_post_video_upload_pipeline.py --mark-rights-confirmed
```

如果尚未完成权利确认，运行默认命令即可；它会保守地停止在预检阶段，不会产出可误写成结果的姿态分析。

## 三、dry run

先检查命令链：

```bash
python3 scripts/run_qigong_post_video_upload_pipeline.py --dry-run
```

正式运行：

```bash
python3 scripts/run_qigong_post_video_upload_pipeline.py
```

## 四、流水线会生成什么

1. 填入本地路径后的 manifest：
   `runs/qigong_platform/formal_merge/qigong_video_manifest_filled_from_files.csv`
2. 视频文件预检：
   `runs/qigong_platform/formal_merge/video_file_preflight.md`
3. SportsLabKit/OpenCV/MediaPipe 环境审计：
   `runs/qigong_platform/formal_merge/sportslabkit_environment_audit.md`
4. 若预检通过，抽帧索引：
   `runs/qigong_platform/formal_merge/typical_video_frames_index.csv`
5. 若预检通过，视频特征表：
   `runs/qigong_platform/formal_merge/video_features_from_typical_cases.csv`
6. 本次流水线报告：
   `runs/qigong_platform/formal_merge/post_video_upload_pipeline_report.md`

## 五、结果能否写进论文

可写入视频分析结果的最低条件：

1. `video_file_preflight.md` 显示 `ready_local_rights >= 3`。
2. 必需视频 `TC0001`、`TC0002`、`TC0003` 均显示 `ready_for_local_extraction=True`。
3. `sportslabkit_environment_audit.md` 明确工具链状态。
4. 若使用 SportsLabKit，必须在 Ubuntu 上实际跑通并保留日志。
5. 若只使用 OpenCV/MediaPipe 后备链路，论文中必须写成 OpenCV/MediaPipe，不得写成 SportsLabKit 结果。
6. `video_features_from_typical_cases.csv` 存在且不含 smoke/synthetic 标记。

说明：`TC0004`、`TC0005` 是可选扩展案例。它们缺失时会在预检中显示为待补充，但不应阻止 `TC0001`-`TC0003` 三个必需视频进入最低视频证据层。

未通过时，论文只能写：

> 本研究设计了典型视频身体证据层，用于后续比较标准示范与平台变体在身体可见性、动作连续性和节奏切分上的差异；当前版本不报告视频特征结果。

通过后，论文可以谨慎写：

> 在权利确认的典型案例视频中，研究使用 SportsLabKit 或 OpenCV/MediaPipe 后备链路提取运动能量、节奏变化、镜头切换和姿态可见性指标，用于辅助解释短视频影像化规训如何影响健身气功的身体呈现。

## 六、与学生人工编码的关系

视频分析层只是辅助身体证据，不替代学生人工编码。正式稿的结果写作顺序应是：

1. 真实平台样本与人工编码分布。
2. 评论近读或频率结果。
3. 典型视频身体证据。
4. 三者合流解释“传播延异-影像痕迹”机制。
