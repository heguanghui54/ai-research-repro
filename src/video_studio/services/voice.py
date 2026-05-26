from __future__ import annotations

import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..config import settings
from .volcengine import VolcSpeechClient


@dataclass
class VoiceResult:
    audio_path: Path
    provider: str
    note: str = ""


class VoiceSynthesizer:
    def __init__(self, provider: str = "cosyvoice", api_key: Optional[str] = None, config: Optional[dict] = None):
        self.provider = provider
        self.api_key = api_key or settings.heygen_api_key
        self.config = config or {}

    def synthesize(self, text: str, output_dir: Path, stem: str = "voiceover") -> VoiceResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        wav_path = output_dir / f"{stem}.wav"

        if self.provider in {"heygen", "heygen_preview"} and self.api_key:
            # Placeholder adapter. Keep the interface stable so the real API can be
            # wired in without changing pipeline code.
            self._write_silence(wav_path, seconds=max(6, min(30, len(text) // 10 + 6)))
            note = "HeyGen adapter placeholder" if self.provider == "heygen" else "HeyGen preview placeholder"
            return VoiceResult(audio_path=wav_path, provider=self.provider, note=note)

        if self.provider == "cosyvoice":
            self._write_silence(wav_path, seconds=max(6, min(30, len(text) // 10 + 6)))
            return VoiceResult(audio_path=wav_path, provider="cosyvoice", note="Local CosyVoice placeholder")

        if self.provider in {"volcengine", "volc_tts", "volc_clone"}:
            volc_app_id = str(self.config.get("tts_app_id") or settings.volcengine_tts_app_id or "").strip()
            volc_access_key = str(self.config.get("tts_access_key") or settings.volcengine_tts_access_key or "").strip()
            volc_resource_id = str(
                self.config.get("tts_resource_id")
                or settings.volcengine_tts_resource_id
                or ("seed-icl-2.0" if self.provider == "volc_clone" else "volc.service_type.10029")
            ).strip()
            volc_speaker = str(
                self.config.get("tts_speaker")
                or settings.volcengine_tts_speaker
                or ("seed-icl-2.0" if self.provider == "volc_clone" else "zh_female_qingxin_moon_bigtts")
            ).strip()
            volc_model = str(self.config.get("tts_model") or ("seed-icl-2.0" if self.provider == "volc_clone" else "seed-tts-2.0-standard")).strip()
            volc_format = str(self.config.get("tts_output_format") or "mp3").strip() or "mp3"
            volc_sample_rate = int(self.config.get("tts_sample_rate") or 24000)
            if volc_app_id and volc_access_key and volc_resource_id and volc_speaker:
                output_path = output_dir / f"{stem}.{volc_format}"
                client = VolcSpeechClient(
                    app_id=volc_app_id,
                    access_key=volc_access_key,
                    resource_id=volc_resource_id,
                    speaker=volc_speaker,
                    model=volc_model,
                    output_format=volc_format,
                    sample_rate=volc_sample_rate,
                )
                result = client.synthesize(text, output_path)
                note = "Volcengine voice clone" if self.provider == "volc_clone" else "Volcengine TTS"
                return VoiceResult(audio_path=result.audio_path, provider=self.provider, note=note)
            self._write_silence(wav_path, seconds=max(6, min(30, len(text) // 10 + 6)))
            note = "Volcengine TTS placeholder" if self.provider == "volc_tts" else "Volcengine voice clone placeholder"
            return VoiceResult(audio_path=wav_path, provider=self.provider, note=note)

        self._write_silence(wav_path, seconds=max(6, min(20, len(text) // 12 + 4)))
        return VoiceResult(audio_path=wav_path, provider="fallback", note="Silence fallback")

    def _write_silence(self, path: Path, seconds: int = 10, sample_rate: int = 16000) -> None:
        frames = seconds * sample_rate
        with wave.open(str(path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for _ in range(frames):
                wav.writeframes(struct.pack("<h", 0))
