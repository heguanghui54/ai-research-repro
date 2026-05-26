# Viral Studio

一个面向“爆款视频复刻与再创作”的全栈工作台。

目标不是简单做一个剪辑器，而是把“参考爆款链接 -> 结构分析 -> 生成相似但不同主题脚本 -> 数字人播报 -> 自动剪辑 -> 一键分发”串成一条可运营的流水线。

## 技术方案

### 核心原则

- 只参考结构，不搬运素材
- AI 负责结构化改写，FFmpeg 负责确定性渲染
- 先做可运行的 MVP，再接入高质量付费能力
- 用户数据、项目数据、任务数据都落在 Supabase Postgres
- 火山方舟优先做低成本脚本/封面模型，火山语音优先做公版 TTS 或声音复刻
- 火山数字人优先走火山引擎实时会话链路，没配齐时自动降级为预览模式
- OpenAI Whisper 走官方 `/v1/audio/transcriptions`
- 分发优先支持 `social-auto-upload` 的 `sau` CLI，MultiPost 走可配置 HTTP 适配器

### 组件选择

- 前端：FastAPI + Jinja2 + HTMX + 自定义 CSS
- 后端：FastAPI
- 数据库：Supabase Postgres
- 认证：应用内账号体系，后续可切 Supabase Auth
- 任务队列：内置线程池 + 数据库任务状态
- 文案/脚本：火山方舟 Ark API，DeepSeek 作为兼容回退
- 转写：本地 Whisper/Faster-Whisper 预留，默认可降级为参考链接元数据分析
- 数字人：火山数字人作为优先高质量通道，CosyVoice 作为开源通道，火山语音作为低成本通道
- 剪辑：FFmpeg
- 分发：MultiPost / social-auto-upload 的适配层

### 付费项先说明

- `火山数字人`：需要开通 RTC / 数字人能力，适合高质量数字人和实时会话
- `OpenAI Whisper`：付费，按分钟计费
- `火山方舟 Ark`：有免费额度和低价模型，当前优先作为默认脚本/封面模型
- `火山语音`：公版 TTS 和声音复刻都比高阶数字人更省钱，适合批量播报
- `DeepSeek API`：按 token 计费，作为兼容回退
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
- `VOLCENGINE_AVATAR_ACCESS_KEY_ID` / `VOLCENGINE_AVATAR_SECRET_ACCESS_KEY` / `VOLCENGINE_AVATAR_RTC_APP_ID` / `VOLCENGINE_AVATAR_APP_ID`，如果要启用火山数字人
- `VOLCENGINE_AVATAR_TOKEN` / `VOLCENGINE_AVATAR_ROLE` / `VOLCENGINE_AVATAR_USER_ID`，如果你想直接走环境变量，不想每次都在页面里填
- 或在应用内 `火山方舟 / 豆包语音 / 火山数字人` 集成里写入 `extra settings JSON`
- `OPENAI_API_KEY`，如果要启用 OpenAI Whisper
- `VOLCENGINE_ARK_API_KEY`，如果要启用火山方舟低成本脚本/封面模型
- `VOLCENGINE_VIDEO_MODEL`，如果要切换 Seedance 视频生成模型
- `VOLCENGINE_TTS_APP_ID` / `VOLCENGINE_TTS_ACCESS_KEY`，如果要启用火山语音合成或声音复刻
- `MULTIPOST_API_BASE` / `MULTIPOST_API_KEY`，如果要接多平台分发 API
- `sau` CLI，如果要启用 `social-auto-upload` 发布

## 接入步骤

### 1. 火山数字人

1. 在火山引擎控制台先开通虚拟数字人 / RTC / 语音相关权限。
2. 到应用的 `Integrations` 页面，把 `volcengine` 的 API key 填进去。
3. 在同一页的 `Extra settings JSON` 里写入数字人相关字段：

```json
{
  "avatar_access_key_id": "你的 RTC Access Key ID",
  "avatar_secret_access_key": "你的 RTC Secret Access Key",
  "avatar_rtc_app_id": "你的 RTC AppId（如果和数字人 AppId 是同一个，也可以只填一个）",
  "avatar_app_id": "你的数字人 AppId",
  "avatar_token": "你的 AvatarToken",
  "avatar_role": "你的 AvatarRole",
  "avatar_user_id": "你的 AvatarUserId",
  "avatar_llm_endpoint_id": "你的 Ark EndPointId",
  "avatar_voice_mode": "volc_tts"
}
```

4. 如果你要更像真人声音，就把 `avatar_voice_mode` 改成 `volc_clone`，并在同一页补好 `tts_app_id` / `tts_access_key` / `tts_speaker`。
5. 如果你想直接走环境变量，也可以把 `VOLCENGINE_AVATAR_ACCESS_KEY_ID`、`VOLCENGINE_AVATAR_SECRET_ACCESS_KEY`、`VOLCENGINE_AVATAR_RTC_APP_ID`、`VOLCENGINE_AVATAR_APP_ID`、`VOLCENGINE_AVATAR_TOKEN`、`VOLCENGINE_AVATAR_ROLE` 和 `VOLCENGINE_AVATAR_USER_ID` 设好。
6. 火山数字人现在会优先走真实会话链路，没配齐时会自动降级为预览模式，方便你先看成片效果。

### 2. OpenAI Whisper

1. 在 OpenAI 平台申请 `OPENAI_API_KEY`。
2. 在应用 `Integrations` 页把 `openai` 的 API key 填进去。
3. `Base URL` 保持默认 `https://api.openai.com/v1`。
4. `Model` 可以先填 `whisper-1`，如果你想用新模型也可以换成 `gpt-4o-mini-transcribe`。
5. 如果你不想在页面里填，直接在系统环境变量里设 `OPENAI_API_KEY` 也可以，代码会优先读页面配置，页面没填时回退到环境变量。

### 3. 火山方舟 / 豆包语音

1. 在火山引擎控制台申请 Ark API Key。
2. 在应用 `Integrations` 页把 `volcengine` 的 API key 填进去。
3. `Base URL` 保持默认 `https://ark.cn-beijing.volces.com/api/v3`，`Model` 先用 `doubao-1-5-pro-32k-250115`。
4. `Extra settings JSON` 里默认已经预填了 `image_model=Doubao-Seedream-5.0-lite`、`tts_resource_id=volc.service_type.10029`。
5. 如果要用声音复刻，再把 `tts_app_id`、`tts_access_key` 和 `tts_speaker` 填进去，并把 `tts_resource_id` 改成 `seed-icl-2.0`。
6. 语音合成优先走公版音色，只有你需要真人声音克隆时才切复刻音色，这样成本最低。
7. 如果要启用视频模型，把 `video_model` 保持为 `doubao-seedance-1-5-pro-251215`，也可以在后台里换成你控制台里更便宜或更适合的版本。
8. 你还可以直接打开后台的 `火山连通性测试` 页面，一次看 Ark、TTS、公版音色、复刻音色、火山数字人和 Seedance 分别通不通。

### 4. social-auto-upload

1. 先安装 `sau` CLI，并确保终端里能直接运行 `sau --help`。
2. 用 `sau douyin login --account <account_name>` 之类的命令登录对应平台。
3. 在项目页的 Publish target 里把 `Adapter` 选成 `social-auto-upload`。
4. `Account / Handle` 填你登录时用的账号名。
5. 需要 Bilibili 时，可以在 `Extra settings JSON` 里放 `{"tid": 249}` 之类的参数。

### 5. MultiPost

1. 你可以把它当成 HTTP 分发适配器接到自己的后端。
2. 在 `Integrations` 页配置 `multipost` 的 `Base URL` 和 `API key`。
3. 当前仓库里的实现默认把它当成 `/publish` 风格的 JSON API；如果你的实际接口路径不同，把 `src/video_studio/services/distributor.py` 里的地址改成你的真实端点即可。

## 安全提醒

你当前 Supabase 项目里有很多现成表的 RLS 关闭了。这个仓库的新表会按“后端私有访问”的思路设计，但如果你打算把客户端直接连数据库，建议先单独做一版 RLS 策略，不要直接把 anon key 暴露给前端去读写核心表。
