from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ..utils import ensure_path


@dataclass
class RenderResult:
    video_path: Path
    thumbnail_path: Path
    subtitle_path: Path
    poster_path: Path
    note: str = ""


class FFmpegRenderer:
    def __init__(self, workdir: Path):
        self.workdir = ensure_path(workdir)

    def render_short_video(
        self,
        title: str,
        hook: str,
        script_lines: list[str],
        audio_path: Path,
        output_name: str,
        ratio: str = "9:16",
        cover_image_path: Path | None = None,
    ) -> RenderResult:
        self.workdir.mkdir(parents=True, exist_ok=True)
        width, height = (1080, 1920) if ratio == "9:16" else (1920, 1080)
        poster = self.workdir / f"{output_name}.png"
        thumbnail = self.workdir / f"{output_name}_thumb.png"
        subtitles = self.workdir / f"{output_name}.srt"
        video = self.workdir / f"{output_name}.mp4"

        self._draw_poster(poster, width, height, title, hook, script_lines, cover_image_path=cover_image_path)
        self._write_srt(subtitles, script_lines)
        self._render_mp4(video, poster, audio_path, subtitles, width, height)
        thumbnail.write_bytes(poster.read_bytes())
        return RenderResult(video_path=video, thumbnail_path=thumbnail, subtitle_path=subtitles, poster_path=poster, note="rendered")

    def compose_generated_video(
        self,
        source_video: Path,
        audio_path: Path,
        script_lines: list[str],
        output_name: str,
        ratio: str = "9:16",
    ) -> RenderResult:
        self.workdir.mkdir(parents=True, exist_ok=True)
        subtitles = self.workdir / f"{output_name}.srt"
        video = self.workdir / f"{output_name}.mp4"
        thumbnail = self.workdir / f"{output_name}_thumb.png"
        poster = self.workdir / f"{output_name}.png"
        self._write_srt(subtitles, script_lines)
        self._extract_thumbnail(source_video, thumbnail)
        if not thumbnail.exists():
            self._draw_placeholder_thumbnail(thumbnail, source_video.stem)
        self._mux_video_audio(video, source_video, audio_path, subtitles)
        poster.write_bytes(thumbnail.read_bytes() if thumbnail.exists() else b"")
        return RenderResult(video_path=video, thumbnail_path=thumbnail, subtitle_path=subtitles, poster_path=poster, note="composed")

    def _draw_poster(
        self,
        path: Path,
        width: int,
        height: int,
        title: str,
        hook: str,
        lines: list[str],
        cover_image_path: Path | None = None,
    ) -> None:
        bg1 = (14, 20, 38)
        bg2 = (34, 78, 115)
        if cover_image_path and cover_image_path.exists():
            try:
                base = Image.open(cover_image_path).convert("RGB")
                img = ImageOps.fit(base, (width, height), method=Image.Resampling.LANCZOS)
            except Exception:
                img = Image.new("RGB", (width, height), bg1)
        else:
            img = Image.new("RGB", (width, height), bg1)
        draw = ImageDraw.Draw(img)

        if not cover_image_path or not cover_image_path.exists():
            # soft gradient bands
            for i in range(height):
                ratio = i / max(1, height - 1)
                color = tuple(int(bg1[c] * (1 - ratio) + bg2[c] * ratio) for c in range(3))
                draw.line((0, i, width, i), fill=color)
        else:
            overlay = Image.new("RGB", (width, height), (8, 14, 26))
            img = Image.blend(img, overlay, 0.34)
            draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 76)
            body_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 42)
            small_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 34)
        except Exception:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        margin = 88
        y = 140
        draw.rounded_rectangle((margin - 24, 84, width - margin + 24, height - 84), radius=48, outline=(255, 255, 255), width=4)
        draw.text((margin, y), "VIRAL STUDIO", fill=(255, 214, 102), font=small_font)
        y += 90
        for chunk in wrap(title, width=18):
            draw.text((margin, y), chunk, fill=(255, 255, 255), font=title_font)
            y += 88

        y += 36
        draw.text((margin, y), "Hook", fill=(128, 216, 255), font=small_font)
        y += 44
        for chunk in wrap(hook, width=24):
            draw.text((margin, y), chunk, fill=(235, 245, 255), font=body_font)
            y += 58

        y += 32
        draw.line((margin, y, width - margin, y), fill=(255, 255, 255, 80), width=3)
        y += 30
        for idx, line in enumerate(lines[:4], start=1):
            draw.ellipse((margin, y + 10, margin + 16, y + 26), fill=(255, 214, 102))
            draw.text((margin + 28, y), line[:48], fill=(245, 248, 252), font=body_font)
            y += 76

        footer = "Auto-cut · AI script · Digital human ready"
        draw.text((margin, height - 140), footer, fill=(220, 226, 235), font=small_font)
        img.save(path)

    def _write_srt(self, path: Path, lines: list[str]) -> None:
        blocks = []
        seconds = 0
        for idx, line in enumerate(lines, start=1):
            start = seconds
            end = seconds + 4
            blocks.append(
                "\n".join(
                    [
                        str(idx),
                        f"{self._ts(start)} --> {self._ts(end)}",
                        line,
                        "",
                    ]
                )
            )
            seconds = end
        path.write_text("\n".join(blocks), encoding="utf-8")

    def _ts(self, seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d},000"

    def _render_mp4(self, output: Path, poster: Path, audio: Path, subtitles: Path, width: int, height: int) -> None:
        subtitle_path = str(subtitles).replace(":", "\\:")
        ffmpeg_bin = self._ffmpeg_binary()
        cmd = [
            ffmpeg_bin,
            "-y",
            "-loop",
            "1",
            "-i",
            str(poster),
            "-i",
            str(audio),
            "-vf",
            f"subtitles={subtitle_path}:force_style='FontSize=24,PrimaryColour=&H00FFFFFF&'",
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-pix_fmt",
            "yuv420p",
            "-shortest",
            str(output),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except FileNotFoundError:
            raise RuntimeError("ffmpeg not found on PATH")
        except subprocess.CalledProcessError as exc:
            fallback_cmd = [
                ffmpeg_bin,
                "-y",
                "-loop",
                "1",
                "-i",
                str(poster),
                "-i",
                str(audio),
                "-c:v",
                "libx264",
                "-tune",
                "stillimage",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-pix_fmt",
                "yuv420p",
                "-shortest",
                str(output),
            ]
            try:
                subprocess.run(fallback_cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                raise RuntimeError(f"ffmpeg render failed: {exc.stderr.decode('utf-8', errors='ignore')[:500]}")

    def _extract_thumbnail(self, source_video: Path, thumbnail: Path) -> None:
        ffmpeg_bin = self._ffmpeg_binary()
        try:
            subprocess.run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-i",
                    str(source_video),
                    "-frames:v",
                    "1",
                    "-q:v",
                    "2",
                    str(thumbnail),
                ],
                check=True,
                capture_output=True,
            )
        except Exception:
            return

    def _draw_placeholder_thumbnail(self, path: Path, title: str) -> None:
        img = Image.new("RGB", (1080, 1920), (12, 18, 34))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((72, 120, 1008, 1800), radius=42, outline=(255, 255, 255), width=4)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 64)
        except Exception:
            font = ImageFont.load_default()
        draw.text((108, 220), "Seedance 预览", fill=(130, 220, 255), font=font)
        draw.text((108, 340), title[:24], fill=(255, 255, 255), font=font)
        img.save(path)

    def _mux_video_audio(self, output: Path, source_video: Path, audio: Path, subtitles: Path) -> None:
        ffmpeg_bin = self._ffmpeg_binary()
        subtitle_path = str(subtitles).replace(":", "\\:")
        cmd = [
            ffmpeg_bin,
            "-y",
            "-i",
            str(source_video),
            "-i",
            str(audio),
            "-vf",
            f"subtitles={subtitle_path}:force_style='FontSize=24,PrimaryColour=&H00FFFFFF&'",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-pix_fmt",
            "yuv420p",
            "-shortest",
            str(output),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"ffmpeg mux failed: {exc.stderr.decode('utf-8', errors='ignore')[:500]}")

    def _ffmpeg_binary(self) -> str:
        try:
            import imageio_ffmpeg

            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            return shutil.which("ffmpeg") or "ffmpeg"
