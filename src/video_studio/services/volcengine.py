from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from ..config import settings
from .deepseek import DeepSeekResult


@dataclass
class VolcImageResult:
    url: str
    model: str
    raw: dict | None = None


@dataclass
class VolcSpeechResult:
    audio_path: Path
    task_id: str
    speaker: str
    resource_id: str
    raw: dict | None = None


@dataclass
class VolcVideoResult:
    task_id: str
    status: str
    video_url: str = ""
    last_frame_url: str = ""
    raw: dict | None = None


class VolcArkClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.volcengine_ark_api_key
        self.base_url = (base_url or settings.volcengine_ark_base_url).rstrip("/")
        self.model = model or settings.volcengine_ark_model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def build_video_brief(
        self,
        reference_title: str,
        reference_summary: str,
        topic: str,
        audience: str = "",
        tone: str = "sharp, energetic, practical",
        duration_sec: int = 60,
        platform: str = "short-video",
    ) -> DeepSeekResult:
        if not self.enabled:
            return self._fallback(reference_title, reference_summary, topic, duration_sec)

        system = (
            "You are a senior short-video strategist. "
            "Return strict JSON only with keys: title, hook, script, subtitle_lines, hashtags, shot_list, notes."
        )
        user = {
            "reference_title": reference_title,
            "reference_summary": reference_summary,
            "topic": topic,
            "audience": audience,
            "tone": tone,
            "duration_sec": duration_sec,
            "platform": platform,
            "requirements": [
                "Keep the same structural rhythm as the reference, but do not copy text.",
                "Create a different theme and different concrete examples.",
                "The first 3 seconds must have a strong hook.",
                "Subtitle lines should be punchy and easy to burn into video.",
                "Shot list should be a sequence of visual suggestions for FFmpeg rendering.",
            ],
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return self._normalize(parsed)

    async def generate_image(
        self,
        prompt: str,
        model: str = "doubao-seedream-5.0-lite",
        size: str = "1024x1024",
        style: str = "vivid",
        quality: str = "standard",
    ) -> VolcImageResult:
        if not self.enabled:
            raise RuntimeError("Volcengine Ark API key is not configured")
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "style": style,
            "quality": quality,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{self.base_url}/images/generations", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        url = ""
        if isinstance(data.get("data"), list) and data["data"]:
            item = data["data"][0]
            if isinstance(item, dict):
                url = str(item.get("url") or item.get("image_url") or "")
        if not url:
            raise RuntimeError(f"Volcengine image generation failed: {data}")
        return VolcImageResult(url=url, model=model, raw=data)

    async def test_chat(self, model: Optional[str] = None) -> DeepSeekResult:
        return await self.build_video_brief(
            reference_title="参考标题",
            reference_summary="参考摘要",
            topic="火山引擎联通测试",
            duration_sec=20,
            platform="short-video",
        )

    async def download_image(self, url: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            async with client.stream("GET", url) as resp:
                resp.raise_for_status()
                with output_path.open("wb") as f:
                    async for chunk in resp.aiter_bytes():
                        f.write(chunk)
        return output_path

    def _normalize(self, parsed: Dict[str, Any]) -> DeepSeekResult:
        subtitle_lines = parsed.get("subtitle_lines") or parsed.get("subtitles") or []
        if isinstance(subtitle_lines, str):
            subtitle_lines = [line.strip() for line in subtitle_lines.split("\n") if line.strip()]
        hashtags = parsed.get("hashtags") or []
        if isinstance(hashtags, str):
            hashtags = [tag.strip() for tag in hashtags.split() if tag.strip()]
        shot_list = parsed.get("shot_list") or []
        if isinstance(shot_list, str):
            shot_list = [{"text": line.strip()} for line in shot_list.split("\n") if line.strip()]
        return DeepSeekResult(
            title=parsed.get("title", "Untitled"),
            hook=parsed.get("hook", ""),
            script=parsed.get("script", ""),
            subtitle_lines=subtitle_lines,
            hashtags=hashtags,
            shot_list=shot_list,
            notes=parsed.get("notes", ""),
            raw=parsed,
        )

    def _fallback(self, reference_title: str, reference_summary: str, topic: str, duration_sec: int) -> DeepSeekResult:
        title = f"{topic}：把{reference_title[:12] or '参考视频'}的方法换个方向"
        hook = f"如果你喜欢{reference_title[:10] or '这个爆款'}的节奏，这条换成{topic}会更炸。"
        script = "\n".join(
            [
                hook,
                f"今天我们用一个更接地气的角度，讲清楚{topic}为什么值得做。",
                "第一步，先把最强钩子放在前3秒。",
                "第二步，用短句和高密度信息拉住注意力。",
                "第三步，把结尾收成一个可执行动作，让观众愿意收藏和转发。",
                "如果你想继续看，我会把完整模板放到下一条。",
            ]
        )
        subtitles = [line for line in script.splitlines() if line.strip()]
        hashtags = ["#短视频", f"#{topic.replace(' ', '')}", "#数字人", "#自动剪辑"]
        shot_list = [
            {"text": "开场钩子", "visual": "full-screen title card"},
            {"text": "核心观点", "visual": "animated bullets"},
            {"text": "案例拆解", "visual": "split-screen"},
            {"text": "总结收口", "visual": "bold closing card"},
        ]
        return DeepSeekResult(
            title=title,
            hook=hook,
            script=script,
            subtitle_lines=subtitles,
            hashtags=hashtags,
            shot_list=shot_list,
            notes=f"Fallback generated for {duration_sec}s",
            raw={"fallback": True},
        )


class VolcSpeechClient:
    def __init__(
        self,
        app_id: str,
        access_key: str,
        resource_id: str,
        speaker: str,
        base_url: str = "https://openspeech.bytedance.com",
        model: str = "seed-tts-2.0-standard",
        output_format: str = "mp3",
        sample_rate: int = 24000,
        uid: str = "viral-studio",
    ):
        self.app_id = app_id.strip()
        self.access_key = access_key.strip()
        self.resource_id = resource_id.strip()
        self.speaker = speaker.strip()
        self.base_url = base_url.rstrip("/")
        self.model = model.strip()
        self.output_format = output_format.strip() or "mp3"
        self.sample_rate = sample_rate
        self.uid = uid.strip() or "viral-studio"

    @property
    def enabled(self) -> bool:
        return bool(self.app_id and self.access_key and self.resource_id and self.speaker)

    def synthesize(self, text: str, output_path: Path, timeout_s: int = 120) -> VolcSpeechResult:
        if not self.enabled:
            raise RuntimeError("Volcengine speech config is incomplete")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        headers = {
            "X-Api-App-Id": self.app_id,
            "X-Api-Access-Key": self.access_key,
            "X-Api-Resource-Id": self.resource_id,
            "Content-Type": "application/json",
        }
        submit_payload = {
            "user": {"uid": self.uid},
            "unique_id": str(uuid.uuid4()),
            "namespace": "BidirectionalTTS",
            "req_params": {
                "text": text,
                "speaker": self.speaker,
                "model": self.model,
                "audio_params": {
                    "format": self.output_format,
                    "sample_rate": self.sample_rate,
                },
            },
        }
        submit_url = f"{self.base_url}/api/v3/tts/submit"
        query_url = f"{self.base_url}/api/v3/tts/query"

        with httpx.Client(timeout=30) as client:
            submit_resp = client.post(submit_url, headers=headers, json=submit_payload)
            submit_resp.raise_for_status()
            submit_data = submit_resp.json()
            task_id = str(
                (submit_data.get("data") or {}).get("task_id")
                or submit_data.get("task_id")
                or submit_payload["unique_id"]
            )

            deadline = time.time() + timeout_s
            last_data: dict | None = None
            while time.time() < deadline:
                query_resp = client.post(query_url, headers=headers, json={"task_id": task_id})
                query_resp.raise_for_status()
                query_data = query_resp.json()
                last_data = query_data
                data = query_data.get("data") or {}
                status = int(data.get("task_status") or query_data.get("task_status") or 0)
                audio_url = str(data.get("audio_url") or "")
                if status == 2 and audio_url:
                    self._download_audio(client, audio_url, output_path)
                    return VolcSpeechResult(
                        audio_path=output_path,
                        task_id=task_id,
                        speaker=self.speaker,
                        resource_id=self.resource_id,
                        raw=last_data,
                    )
                if status == 3:
                    raise RuntimeError(f"Volcengine speech synthesis failed: {query_data}")
                time.sleep(2.5)

        raise RuntimeError(f"Volcengine speech synthesis timeout: {last_data or submit_data}")

    def _download_audio(self, client: httpx.Client, audio_url: str, output_path: Path) -> None:
        with client.stream("GET", audio_url) as resp:
            resp.raise_for_status()
            with output_path.open("wb") as f:
                for chunk in resp.iter_bytes():
                    f.write(chunk)


class VolcVideoClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.volcengine_ark_api_key
        self.base_url = (base_url or settings.volcengine_ark_base_url).rstrip("/")
        self.model = model or settings.volcengine_video_model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def create_video_task(self, prompt: str, image_url: str = "", model: Optional[str] = None, aspect_ratio: str = "9:16") -> VolcVideoResult:
        if not self.enabled:
            raise RuntimeError("Volcengine Ark API key is not configured")
        payload: dict[str, Any] = {
            "model": model or self.model,
            "content": [{"type": "text", "text": prompt}],
        }
        if image_url:
            payload["content"].append({"type": "image_url", "image_url": {"url": image_url}})
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=120) as client:
            resp = client.post(f"{self.base_url}/contents/generations/tasks", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        task_id = str(data.get("id") or data.get("task_id") or "")
        if not task_id:
            raise RuntimeError(f"Volcengine video task creation failed: {data}")
        return VolcVideoResult(task_id=task_id, status=str(data.get("status") or "pending"), raw=data)

    def get_video_task(self, task_id: str) -> VolcVideoResult:
        if not self.enabled:
            raise RuntimeError("Volcengine Ark API key is not configured")
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=120) as client:
            resp = client.get(f"{self.base_url}/contents/generations/tasks/{task_id}", headers=headers)
            resp.raise_for_status()
            data = resp.json()
        payload = data.get("data") or data
        status = str(payload.get("status") or payload.get("task_status") or data.get("status") or "pending")
        video_url = str(
            payload.get("video_url")
            or payload.get("output_video_url")
            or payload.get("url")
            or ""
        )
        last_frame_url = str(payload.get("last_frame_url") or payload.get("thumbnail_url") or "")
        return VolcVideoResult(task_id=task_id, status=status, video_url=video_url, last_frame_url=last_frame_url, raw=data)

    def wait_for_video(self, task_id: str, timeout_s: int = 900, poll_interval_s: int = 10) -> VolcVideoResult:
        deadline = time.time() + timeout_s
        last: VolcVideoResult | None = None
        while time.time() < deadline:
            last = self.get_video_task(task_id)
            if last.status.lower() in {"completed", "failed", "success"} and (last.video_url or last.last_frame_url):
                return last
            time.sleep(poll_interval_s)
        return last or VolcVideoResult(task_id=task_id, status="timeout")

    def download_video(self, url: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with httpx.Client(timeout=120, follow_redirects=True) as client:
            with client.stream("GET", url) as resp:
                resp.raise_for_status()
                with output_path.open("wb") as f:
                    for chunk in resp.iter_bytes():
                        f.write(chunk)
        return output_path
