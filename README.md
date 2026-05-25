# Viral Studio

一个面向“爆款视频复刻与再创作”的全栈工作台。

目标不是简单做一个剪辑器，而是把“参考爆款链接 -> 结构分析 -> 生成相似但不同主题脚本 -> 数字人播报 -> 自动剪辑 -> 一键分发”串成一条可运营的流水线。

## 技术方案

### 核心原则

- 只参考结构，不搬运素材
- AI 负责结构化改写，FFmpeg 负责确定性渲染
- 先做可运行的 MVP，再接入高质量付费能力
- 用户数据、项目数据、任务数据都落在 Supabase Postgres
- HeyGen 走官方 `v3/videos` 生成与轮询接口
- OpenAI Whisper 走官方 `/v1/audio/transcriptions`
- 分发优先支持 `social-auto-upload` 的 `sau` CLI，MultiPost 走可配置 HTTP 适配器

### 组件选择

- 前端：FastAPI + Jinja2 + HTMX + 自定义 CSS
- 后端：FastAPI
- 数据库：Supabase Postgres
- 认证：应用内账号体系，后续可切 Supabase Auth
- 任务队列：内置线程池 + 数据库任务状态
- 文案/脚本：DeepSeek API
- 转写：本地 Whisper/Faster-Whisper 预留，默认可降级为参考链接元数据分析
- 数字人：HeyGen 作为高质量付费通道，CosyVoice 作为开源通道
- 剪辑：FFmpeg
- 分发：MultiPost / social-auto-upload 的适配层

### 付费项先说明

- `HeyGen`：付费，按秒计费，适合高质量数字人
- `OpenAI Whisper`：付费，按分钟计费
- `DeepSeek API`：按 token 计费，不是永久免费
- `Coze`：有免费额度，超过后要买 token
- `FFmpeg`：软件开源免费，但商用编译和分发要注意 LGPL/GPL 边界

### MVP 流程

1. 用户登录
2. 新建项目
3. 粘贴爆款参考链接
4. 输入目标主题、时长、平台
5. DeepSeek 生成改写脚本
6. 生成配音或数字人稿
7. FFmpeg 自动渲染成片
8. 生成多平台分发包
9. 进入发布队列

## 目录结构

```text
.
├── README.md
├── pyproject.toml
├── requirements.txt
├── supabase
│   └── migrations
│       └── 0001_init_viral_studio.sql
├── static
│   └── styles.css
├── templates
│   ├── base.html
│   ├── dashboard.html
│   ├── index.html
│   ├── job_detail.html
│   ├── login.html
│   ├── project_detail.html
│   ├── project_form.html
│   ├── register.html
│   └── settings.html
└── src
    └── video_studio
        ├── __init__.py
        ├── app.py
        ├── auth.py
        ├── config.py
        ├── crud.py
        ├── db.py
        ├── main.py
        ├── models.py
        ├── pipeline.py
        ├── security.py
        ├── schemas.py
        ├── services
        │   ├── __init__.py
        │   ├── deepseek.py
        │   ├── distributor.py
        │   ├── ffmpeg.py
        │   ├── whisper.py
        │   └── voice.py
        └── utils.py
```

## 本地运行

```bash
python3 -m pip install -r requirements.txt
export DATABASE_URL="sqlite:///./viral_studio.db"
uvicorn video_studio.main:app --reload
```

如果你要连 Supabase：

```bash
export DATABASE_URL="postgresql+psycopg2://USER:PASSWORD@db.PROJECT.supabase.co:5432/postgres?sslmode=require"
export DEEPSEEK_API_KEY="..."
export DEEPSEEK_MODEL="deepseek-chat"
```

## 需要你申请或准备的密钥

- `DEEPSEEK_API_KEY`
- `HEYGEN_API_KEY`，如果要启用高质量数字人
- `HEYGEN_AVATAR_ID` / `HEYGEN_VOICE_ID`，或在应用内 `HeyGen` 集成里写入 `extra settings JSON`
- `OPENAI_API_KEY`，如果要启用 OpenAI Whisper
- `MULTIPOST_API_BASE` / `MULTIPOST_API_KEY`，如果要接多平台分发 API
- `sau` CLI，如果要启用 `social-auto-upload` 发布

## 安全提醒

你当前 Supabase 项目里有很多现成表的 RLS 关闭了。这个仓库的新表会按“后端私有访问”的思路设计，但如果你打算把客户端直接连数据库，建议先单独做一版 RLS 策略，不要直接把 anon key 暴露给前端去读写核心表。
