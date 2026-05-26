from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx


@dataclass
class MonicaImageResult:
    url: str
    model: str
    raw: dict | None = None


@dataclass
class MonicaChatResult:
    text: str
    raw: dict | None = None


class MonicaClient:
    def __init__(self, api_key: str, base_url: str = "https://openapi.monica.im/v1"):
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def chat_completion(self, prompt: str, model: str = "gpt-4o") -> MonicaChatResult:
        if not self.enabled:
            raise RuntimeError("Monica API key is not configured")
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        text = data["choices"][0]["message"]["content"]
        return MonicaChatResult(text=text, raw=data)

    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        style: str = "vivid",
        quality: str = "standard",
    ) -> MonicaImageResult:
        if not self.enabled:
            raise RuntimeError("Monica API key is not configured")
        payload = {
            "prompt": prompt,
            "model": model,
            "n": 1,
            "quality": quality,
            "size": size,
            "style": style,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{self.base_url}/image/gen/dalle", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        url = ""
        if isinstance(data.get("data"), list) and data["data"]:
            url = str(data["data"][0].get("url", ""))
        if not url:
            raise RuntimeError(f"Monica image generation failed: {data}")
        return MonicaImageResult(url=url, model=model, raw=data)

    async def download_image(self, url: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            async with client.stream("GET", url) as resp:
                resp.raise_for_status()
                with output_path.open("wb") as f:
                    async for chunk in resp.aiter_bytes():
                        f.write(chunk)
        return output_path

    async def test_chat(self, model: str = "gpt-4o") -> MonicaChatResult:
        return await self.chat_completion("Reply with a single Chinese word: 通过", model=model)

