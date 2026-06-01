# 石伟老师当前需要人工完成的事项

这份清单只列必须由人工完成或确认的工作。其余导入、审计、统计、图表和论文改写由脚本流程承担。

## 1. 组织学生完成网页人工编码

当前推荐入口已经从“前 20 条本地工作台”升级为网页分工填报：

`https://ai-research-repro.vercel.app`

请把学生编号 `STU01` 至 `STU10` 分给 10 名学生，并单独发送访问口令。学生登录后只填写系统分配给自己的任务。当前线上已经有 6 条主编码提交，说明网页流程可用；但还需要推进到 120 条主编码和 24 条复核编码。

学生填写时只需要遵守四条：

1. 每条任务先点击“打开视频”，看过画面、字幕、标签、动作节奏和平台语境后再填。
2. 不要只凭标题填写，也不要照抄 LLM 辅助建议。
3. 缺视频链接的任务显示为暂缓编码，不算学生未完成责任。
4. 备注只写匿名化观察，不写用户名、主页、手机号、评论者身份或原始链接。

网页分工说明见：

`docs/qigong_platform_paper/student_web_coding_distribution.md`

学生数据回收后，我会运行：

```bash
python3 scripts/run_qigong_post_web_coding_pipeline.py
```

该脚本会导出 Supabase 提交、转正式编码表、审计取值、计算双编码一致性、生成分歧复核表和刷新投稿门槛。

## 2. 准备 3-5 个典型视频文件

SportsLabKit/视觉模型分析需要本地视频文件。请准备：

- 1 个官方或专业标准八段锦/五禽戏/健身气功视频；
- 2-4 个平台改编、流变、年轻化、玩梗化或功效化典型视频；
- 每个视频都要能说明来源、用途和使用边界。

建议放到：

`data/private/qigong_typical_videos/`

文件名建议：

- `standard_baduanjin_01.mp4`
- `platform_variant_baduanjin_01.mp4`
- `platform_variant_wuqinxi_01.mp4`
- `platform_variant_cyber_wellness_01.mp4`

如果只有网页链接，先不要写入论文结果；等转成本地视频并完成权利确认后，我再跑预检、抽帧、SportsLabKit/MediaPipe/OpenCV 特征和视觉模型编码。

我已经准备好一键预检脚本。你放入视频文件后，我会运行：

```bash
python scripts/prepare_qigong_typical_videos.py
```

该脚本不会自动确认权利；只有 `data/qigong_video_manifest.csv` 中相应行已人工确认 `rights_status=rights_confirmed`，并且本地文件存在时，才会继续抽帧、特征提取和视觉模型包生成。

## 3. 不要手工改的东西

不用手工改论文正文、审计 JSON、结果表和图表。完成上面两项后告诉我，我会继续：

1. 导入人工编码；
2. 跑编码值审计；
3. 建立双编码信度；
4. 跑评论和视频证据审计；
5. 生成正式结果表；
6. 更新投稿稿件。
