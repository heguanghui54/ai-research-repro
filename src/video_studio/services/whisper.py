from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx

from ..config import settings


@dataclass
class TranscriptResult:
    text: str
    language: str = "zh"
    raw: dict | None = None


class WhisperClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.base_url = (base_url or settings.openai_base_url).rstrip("/")
        self.model = model or settings.openai_whisper_model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def transcribe_file(self, audio_path: Path, prompt: str = "") -> TranscriptResult:
        if not self.enabled:
            return TranscriptResult(
                text=f"参考视频转写占位文本。文件：{audio_path.name}。请接入 OpenAI Whisper 或本地 faster-whisper。",
                language="zh",
                raw={"fallback": True},
            )

        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"model": self.model, "response_format": "json"}
        if prompt:
            data["prompt"] = prompt
        async with httpx.AsyncClient(timeout=120) as client:
            with audio_path.open("rb") as audio_file:
                resp = await client.post(f"{self.base_url}/audio/transcriptions", headers=headers, data=data, files={"file": audio_file})
                resp.raise_for_status()
                payload = resp.json()
        return TranscriptResult(text=payload.get("text", ""), language=payload.get("language", "zh"), raw=payload)

    async def transcribe_url(self, audio_url: str, prompt: str = "") -> TranscriptResult:
        if not self.enabled:
            return TranscriptResult(
                text=f"参考音频占位文本。URL：{audio_url}。请接入 OpenAI Whisper 或本地 faster-whisper。",
                language="zh",
                raw={"fallback": True},
            )
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            audio_resp = await client.get(audio_url)
            audio_resp.raise_for_status()
            suffix = ".mp4"
            content_type = audio_resp.headers.get("content-type", "")
            if "mpeg" in content_type or "mp3" in content_type:
                suffix = ".mp3"
            elif "wav" in content_type:
                suffix = ".wav"
            elif "webm" in content_type:
                suffix = ".webm"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(audio_resp.content)
                tmp_path = Path(tmp_file.name)
        try:
            return await self.transcribe_file(tmp_path, prompt=prompt)
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
