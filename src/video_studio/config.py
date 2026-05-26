from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


@dataclass
class Settings:
    app_name: str = "Viral Studio"
    secret_key: str = field(default_factory=lambda: _env("SECRET_KEY", "change-me-in-production"))
    database_url: str = field(default_factory=lambda: _env("DATABASE_URL", "sqlite:///./viral_studio.db"))
    data_dir: Path = field(default_factory=lambda: Path(_env("DATA_DIR", "./data")).resolve())
    upload_dir: Path = field(default_factory=lambda: Path(_env("UPLOAD_DIR", "./data/uploads")).resolve())
    render_dir: Path = field(default_factory=lambda: Path(_env("RENDER_DIR", "./data/renders")).resolve())
    static_dir: Path = field(default_factory=lambda: Path(_env("STATIC_DIR", "./static")).resolve())
    template_dir: Path = field(default_factory=lambda: Path(_env("TEMPLATE_DIR", "./templates")).resolve())

    deepseek_api_key: str = field(default_factory=lambda: _env("DEEPSEEK_API_KEY"))
    deepseek_base_url: str = field(default_factory=lambda: _env("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    deepseek_model: str = field(default_factory=lambda: _env("DEEPSEEK_MODEL", "deepseek-chat"))

    openai_api_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY"))
    openai_base_url: str = field(default_factory=lambda: _env("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    openai_whisper_model: str = field(default_factory=lambda: _env("OPENAI_WHISPER_MODEL", "whisper-1"))

    heygen_api_key: str = field(default_factory=lambda: _env("HEYGEN_API_KEY"))
    heygen_avatar_id: str = field(default_factory=lambda: _env("HEYGEN_AVATAR_ID"))
    heygen_voice_id: str = field(default_factory=lambda: _env("HEYGEN_VOICE_ID"))

    volcengine_ark_api_key: str = field(default_factory=lambda: _env("VOLCENGINE_ARK_API_KEY"))
    volcengine_ark_base_url: str = field(default_factory=lambda: _env("VOLCENGINE_ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"))
    volcengine_ark_model: str = field(default_factory=lambda: _env("VOLCENGINE_ARK_MODEL", "doubao-1-5-pro-32k-250115"))
    volcengine_video_model: str = field(default_factory=lambda: _env("VOLCENGINE_VIDEO_MODEL", "doubao-seedance-1-5-pro-251215"))
    volcengine_avatar_rtc_app_id: str = field(default_factory=lambda: _env("VOLCENGINE_AVATAR_RTC_APP_ID"))
    volcengine_avatar_access_key_id: str = field(default_factory=lambda: _env("VOLCENGINE_AVATAR_ACCESS_KEY_ID"))
    volcengine_avatar_secret_access_key: str = field(default_factory=lambda: _env("VOLCENGINE_AVATAR_SECRET_ACCESS_KEY"))
    volcengine_avatar_app_id: str = field(default_factory=lambda: _env("VOLCENGINE_AVATAR_APP_ID"))
    volcengine_avatar_token: str = field(default_factory=lambda: _env("VOLCENGINE_AVATAR_TOKEN"))
    volcengine_avatar_role: str = field(default_factory=lambda: _env("VOLCENGINE_AVATAR_ROLE"))
    volcengine_avatar_user_id: str = field(default_factory=lambda: _env("VOLCENGINE_AVATAR_USER_ID"))
    volcengine_avatar_background_url: str = field(default_factory=lambda: _env("VOLCENGINE_AVATAR_BACKGROUND_URL"))
    volcengine_avatar_video_bitrate: int = field(default_factory=lambda: int(_env("VOLCENGINE_AVATAR_VIDEO_BITRATE", "2000")))
    volcengine_avatar_region: str = field(default_factory=lambda: _env("VOLCENGINE_AVATAR_REGION", "cn-north-1"))
    volcengine_avatar_llm_endpoint_id: str = field(default_factory=lambda: _env("VOLCENGINE_AVATAR_LLM_ENDPOINT_ID"))
    volcengine_avatar_task_id: str = field(default_factory=lambda: _env("VOLCENGINE_AVATAR_TASK_ID"))
    volcengine_tts_app_id: str = field(default_factory=lambda: _env("VOLCENGINE_TTS_APP_ID"))
    volcengine_tts_access_key: str = field(default_factory=lambda: _env("VOLCENGINE_TTS_ACCESS_KEY"))
    volcengine_tts_resource_id: str = field(default_factory=lambda: _env("VOLCENGINE_TTS_RESOURCE_ID", "volc.service_type.10029"))
    volcengine_tts_speaker: str = field(default_factory=lambda: _env("VOLCENGINE_TTS_SPEAKER", "zh_female_qingxin_moon_bigtts"))

    multipost_api_base: str = field(default_factory=lambda: _env("MULTIPOST_API_BASE"))
    multipost_api_key: str = field(default_factory=lambda: _env("MULTIPOST_API_KEY"))

    default_admin_email: str = field(default_factory=lambda: _env("DEFAULT_ADMIN_EMAIL", "hgh54913"))
    default_admin_password: str = field(default_factory=lambda: _env("DEFAULT_ADMIN_PASSWORD", "Aaa.123456"))
    default_admin_display_name: str = field(default_factory=lambda: _env("DEFAULT_ADMIN_DISPLAY_NAME", "hgh54913"))

    app_host: str = field(default_factory=lambda: _env("APP_HOST", "127.0.0.1"))
    app_port: int = field(default_factory=lambda: int(_env("APP_PORT", "8000")))

    def ensure_dirs(self) -> None:
        for path in (self.data_dir, self.upload_dir, self.render_dir, self.static_dir, self.template_dir):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
