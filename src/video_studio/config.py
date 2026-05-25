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
    multipost_api_base: str = field(default_factory=lambda: _env("MULTIPOST_API_BASE"))
    multipost_api_key: str = field(default_factory=lambda: _env("MULTIPOST_API_KEY"))

    app_host: str = field(default_factory=lambda: _env("APP_HOST", "127.0.0.1"))
    app_port: int = field(default_factory=lambda: int(_env("APP_PORT", "8000")))

    def ensure_dirs(self) -> None:
        for path in (self.data_dir, self.upload_dir, self.render_dir, self.static_dir, self.template_dir):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()

