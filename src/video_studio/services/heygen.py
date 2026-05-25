from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx

from ..config import settings


@dataclass
class HeyGenVideoResult:
    video_id: str
    status: str
    video_url: str = ""
    thumbnail_url: str = ""
    subtitle_url: str = ""
    raw: dict | None = None


class HeyGenClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.heygen_api_key
        self.base_url = (base_url or "https://api.heygen.com").rstrip("/")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def create_avatar_video(
        self,
        title: str,
        script: str,
        avatar_id: str,
        voice_id: str,
        aspect_ratio: str = "9:16",
        callback_url: str = "",
        caption: bool = True,
    ) -> HeyGenVideoResult:
        if not self.enabled:
            raise RuntimeError("HEYGEN_API_KEY is not configured")

        payload = {
            "type": "avatar",
            "avatar_id": avatar_id,
            "title": title,
            "aspect_ratio": aspect_ratio,
            "script": script,
            "voice_id": voice_id,
            "caption": {"file_format": "srt"} if caption else None,
            "callback_url": callback_url or None,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(f"{self.base_url}/v3/videos", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json().get("data", {})
        return HeyGenVideoResult(video_id=data.get("video_id", ""), status=data.get("status", "pending"), raw=data)

    async def get_video(self, video_id: str) -> HeyGenVideoResult:
        if not self.enabled:
            raise RuntimeError("HEYGEN_API_KEY is not configured")
        headers = {"x-api-key": self.api_key}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(f"{self.base_url}/v3/videos/{video_id}", headers=headers)
            resp.raise_for_status()
            data = resp.json().get("data", {})
        return HeyGenVideoResult(
            video_id=data.get("id", video_id),
            status=data.get("status", "pending"),
            video_url=data.get("video_url", ""),
            thumbnail_url=data.get("thumbnail_url", ""),
            subtitle_url=data.get("subtitle_url", ""),
            raw=data,
        )

    async def wait_for_video(self, video_id: str, timeout_s: int = 900, poll_interval_s: int = 8) -> HeyGenVideoResult:
        deadline = asyncio.get_event_loop().time() + timeout_s
        last = None
        while asyncio.get_event_loop().time() < deadline:
            last = await self.get_video(video_id)
            if last.status.lower() in {"completed", "failed"}:
                return last
            await asyncio.sleep(poll_interval_s)
        return last or HeyGenVideoResult(video_id=video_id, status="timeout")

    async def download_video(self, url: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            async with client.stream("GET", url) as resp:
                resp.raise_for_status()
                with output_path.open("wb") as f:
                    async for chunk in resp.aiter_bytes():
                        f.write(chunk)
        return output_path

