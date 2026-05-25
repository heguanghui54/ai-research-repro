from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from ..config import settings


@dataclass
class DeepSeekResult:
    title: str
    hook: str
    script: str
    subtitle_lines: list[str]
    hashtags: list[str]
    shot_list: list[dict]
    notes: str
    raw: dict


class DeepSeekClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.deepseek_api_key
        self.base_url = (base_url or settings.deepseek_base_url).rstrip("/")
        self.model = model or settings.deepseek_model

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

