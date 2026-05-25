from __future__ import annotations

import asyncio
import json
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx

from ..config import settings


@dataclass
class DistributionPackage:
    title: str
    description: str
    platforms: list[str]
    payload: dict

    @classmethod
    def from_payload(cls, payload: dict) -> "DistributionPackage":
        media = payload.get("media") or {}
        platforms = payload.get("platforms") or []
        hashtags = payload.get("hashtags") or []
        title = payload.get("title") or ""
        description = " | ".join(filter(None, [title, " ".join(hashtags[:6])]))
        return cls(
            title=title,
            description=description,
            platforms=list(platforms),
            payload={**payload, "media": media, "platforms": list(platforms), "hashtags": list(hashtags)},
        )


class DistributorClient:
    def __init__(self) -> None:
        self.base_url = settings.multipost_api_base.rstrip("/")
        self.api_key = settings.multipost_api_key

    @property
    def enabled(self) -> bool:
        return bool(self.base_url and self.api_key)

    async def publish_multipost(self, package: DistributionPackage) -> dict:
        if not self.enabled:
            return {"status": "manual", "message": "MultiPost API is not configured.", "package": package.payload}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(f"{self.base_url}/publish", json=package.payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    def publish_social_auto_upload(
        self,
        platform: str,
        video_path: Path,
        title: str,
        description: str,
        account_name: str,
        extra_args: Optional[list[str]] = None,
    ) -> dict:
        sau = shutil.which("sau")
        if not sau:
            return {
                "status": "manual",
                "message": "social-auto-upload CLI (sau) is not installed.",
                "platform": platform,
                "video_path": str(video_path),
            }

        cmd = [sau, platform, "upload-video", "--account", account_name, "--file", str(video_path), "--title", title, "--desc", description]
        if extra_args:
            cmd.extend(extra_args)
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"sau publish failed for {platform}")
        return {
            "status": "published",
            "platform": platform,
            "account": account_name,
            "stdout": proc.stdout.strip(),
            "command": shlex.join(cmd),
        }

    def build_package(
        self,
        title: str,
        script: str,
        hashtags: list[str],
        platforms: list[str],
        output_video_url: str,
        thumbnail_url: str = "",
    ) -> DistributionPackage:
        payload = {
            "title": title,
            "script": script,
            "hashtags": hashtags,
            "platforms": platforms,
            "media": {"video_url": output_video_url, "thumbnail_url": thumbnail_url},
            "content_types": ["video"],
        }
        description = " | ".join(filter(None, [title, " ".join(hashtags[:6])]))
        return DistributionPackage(title=title, description=description, platforms=platforms, payload=payload)
