from __future__ import annotations

import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..config import settings


@dataclass
class VoiceResult:
    audio_path: Path
    provider: str
    note: str = ""


class VoiceSynthesizer:
    def __init__(self, provider: str = "cosyvoice", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or settings.heygen_api_key

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
