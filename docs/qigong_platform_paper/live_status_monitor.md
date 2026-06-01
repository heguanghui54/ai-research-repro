# 当前实时状态监控

用途：把网页人工编码、投稿门槛、典型视频、评论审计和网站可访问性汇总到一个当前状态报告。它服务于研究生产管理，不是论文结果表。

注意：不带 `--refresh-web` 时，网页进度来自本地最近一次导出快照，可能落后于线上 Supabase；带 `--refresh-web` 时，才代表刷新后的线上提交状态。

## 离线状态

不刷新 Supabase，仅基于本地已有导出和审计文件生成状态，报告中会标记 `web_progress_source: local_snapshot`：

```bash
python3 scripts/build_qigong_live_status.py
```

输出：

- `runs/qigong_platform/formal_merge/live_status_current.md`
- `runs/qigong_platform/formal_merge/live_status_current.json`

## 刷新网页提交后再生成

只有本机环境已设置私有导出口令时使用：

```bash
python3 scripts/build_qigong_live_status.py --refresh-web
```

该命令会先运行 `scripts/build_qigong_web_coding_progress.py --refresh`，再刷新当前投稿门槛总表，报告中会标记 `web_progress_source: supabase_refreshed`。不要把导出口令写入命令历史、论文、GitHub 或群聊。

## 读取原则

- `web_primary_complete` 未达到 `120/120` 前，不能写人工编码变量分布。
- `web_double_complete` 未达到 `24/24` 前，不能写双编码一致性已经通过。
- `p0_nonpass` 非空时，不能称为投稿终稿。
- `video_ready_local_rights` 未达到至少 3 个本地授权视频前，不能写 SportsLabKit/姿态轨迹结果。
- `comment_audit_counts` 仍有 fail 时，只能写匿名评论近读，不能写评论频率结论。
