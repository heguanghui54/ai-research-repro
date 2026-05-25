from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    reference_url: str = ""
    niche: str = ""
    target_platforms: list[str] = Field(default_factory=lambda: ["douyin", "xiaohongshu", "bilibili", "youtube", "tiktok"])


class JobCreate(BaseModel):
    topic: str
    reference_url: str = ""
    avatar_mode: str = "cosyvoice"
    voice_provider: str = "deepseek"
    render_ratio: str = "9:16"

