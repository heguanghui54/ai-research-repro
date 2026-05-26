from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from .fonts import load_cjk_font, wrap_cjk_text_limited
from ..utils import ensure_path


@dataclass
class HeyGenPreviewResult:
    preview_path: Path
    note: str = "simulated"


class HeyGenPreviewRenderer:
    def __init__(self, workdir: Path):
        self.workdir = ensure_path(workdir)

    def build_preview_card(
        self,
        title: str,
        hook: str,
        subtitle_lines: list[str],
        ratio: str = "9:16",
    ) -> HeyGenPreviewResult:
        width, height = (1080, 1920) if ratio == "9:16" else (1920, 1080)
        output = self.workdir / "heygen-preview.png"
        self.workdir.mkdir(parents=True, exist_ok=True)

        img = Image.new("RGB", (width, height), (10, 16, 30))
        draw = ImageDraw.Draw(img)

        # Gradient background
        top = (14, 20, 36)
        bottom = (32, 74, 118)
        for y in range(height):
            t = y / max(1, height - 1)
            color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
            draw.line((0, y, width, y), fill=color)

        # Light glow
        draw.ellipse((-120, 120, width * 0.55, height * 0.62), fill=(58, 132, 212))
        draw.ellipse((width * 0.48, height * 0.10, width * 1.15, height * 0.68), fill=(214, 107, 92))

        title_font = load_cjk_font(50)
        body_font = load_cjk_font(30)
        small_font = load_cjk_font(26)

        margin = 86
        draw.rounded_rectangle((margin, 84, width - margin, height - 84), radius=46, outline=(255, 255, 255), width=3)
        draw.rounded_rectangle((margin + 24, 112, margin + 300, 164), radius=20, fill=(24, 41, 66))
        draw.text((margin + 40, 121), "HEYGEN 预览模式", fill=(124, 224, 255), font=small_font)

        y = 284
        for chunk in wrap_cjk_text_limited(title, title_font, width - margin * 2, max_lines=2):
            draw.text((margin, y), chunk, fill=(255, 255, 255), font=title_font)
            y += 54

        y += 28
        draw.text((margin, y), "Hook", fill=(124, 224, 255), font=small_font)
        y += 32
        for chunk in wrap_cjk_text_limited(hook, body_font, width - margin * 2, max_lines=2):
            draw.text((margin, y), chunk, fill=(235, 245, 255), font=body_font)
            y += 40

        # Avatar stage
        stage_top = int(height * 0.45)
        stage_bottom = int(height * 0.77)
        draw.rounded_rectangle((margin, stage_top, width - margin, stage_bottom), radius=38, fill=(12, 18, 34), outline=(255, 255, 255, 60), width=2)
        stage_cx = width // 2
        stage_cy = stage_top + 180
        # Avatar silhouette
        draw.ellipse((stage_cx - 120, stage_cy - 170, stage_cx + 120, stage_cy + 70), fill=(239, 199, 167))
        draw.rounded_rectangle((stage_cx - 170, stage_cy + 20, stage_cx + 170, stage_cy + 330), radius=88, fill=(54, 83, 120))
        draw.rounded_rectangle((stage_cx - 210, stage_cy + 40, stage_cx - 140, stage_cy + 180), radius=28, fill=(54, 83, 120))
        draw.rounded_rectangle((stage_cx + 140, stage_cy + 40, stage_cx + 210, stage_cy + 180), radius=28, fill=(54, 83, 120))
        # Hair and face details
        draw.pieslice((stage_cx - 132, stage_cy - 190, stage_cx + 132, stage_cy + 50), start=180, end=360, fill=(45, 40, 54))
        draw.ellipse((stage_cx - 38, stage_cy - 40, stage_cx - 18, stage_cy - 20), fill=(48, 50, 58))
        draw.ellipse((stage_cx + 18, stage_cy - 40, stage_cx + 38, stage_cy - 20), fill=(48, 50, 58))
        draw.arc((stage_cx - 38, stage_cy - 12, stage_cx + 38, stage_cy + 48), start=10, end=170, fill=(180, 100, 88), width=4)
        draw.line((stage_cx - 190, stage_cy + 70, stage_cx - 260, stage_cy + 30), fill=(124, 224, 255), width=4)
        draw.line((stage_cx + 190, stage_cy + 70, stage_cx + 260, stage_cy + 30), fill=(124, 224, 255), width=4)

        draw.rounded_rectangle((margin + 28, stage_bottom + 26, width - margin - 28, stage_bottom + 156), radius=28, fill=(20, 30, 52))
        draw.text((margin + 48, stage_bottom + 52), "字幕预览", fill=(124, 224, 255), font=small_font)
        y = stage_bottom + 92
        for idx, line in enumerate((subtitle_lines or [hook])[:2], start=1):
            for sub_line in wrap_cjk_text_limited(f"{idx}. {line}", body_font, width - margin * 2 - 48, max_lines=2):
                draw.text((margin + 48, y), sub_line, fill=(245, 248, 252), font=body_font)
                y += 34

        footer = "这是一版模拟效果，接入 HeyGen API 后会变成真实数字人视频"
        draw.text((margin, height - 132), footer, fill=(220, 226, 235), font=small_font)
        img.save(output)
        return HeyGenPreviewResult(preview_path=output)
