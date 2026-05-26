from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

import httpx

from ..config import settings


@dataclass
class VolcAvatarResponse:
    action: str
    version: str
    request_id: str
    region: str
    service: str
    result: str
    raw: dict[str, Any]


@dataclass
class VolcAvatarSessionResult:
    room_id: str
    user_id: str
    bot_name: str
    started: bool
    stopped: bool
    start_response: VolcAvatarResponse | None
    stop_response: VolcAvatarResponse | None
    payload: dict[str, Any]
    stop_payload: dict[str, Any]


class VolcAvatarClient:
    def __init__(
        self,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        app_id: Optional[str] = None,
        region: Optional[str] = None,
        host: str = "rtc.volcengineapi.com",
        base_url: str = "https://rtc.volcengineapi.com",
        start_version: str = "2024-06-01",
        stop_version: str = "2024-12-01",
        llm_endpoint_id: Optional[str] = None,
        avatar_token: Optional[str] = None,
        avatar_role: Optional[str] = None,
        avatar_user_id: Optional[str] = None,
        avatar_background_url: Optional[str] = None,
        avatar_video_bitrate: Optional[int] = None,
        avatar_config: Optional[dict[str, Any]] = None,
        tts_app_id: Optional[str] = None,
        tts_access_key: Optional[str] = None,
        tts_resource_id: Optional[str] = None,
        tts_speaker: Optional[str] = None,
        tts_model: Optional[str] = None,
        tts_output_format: Optional[str] = None,
        tts_sample_rate: Optional[int] = None,
        default_voice_mode: str = "volc_tts",
    ):
        self.access_key_id = (access_key_id or settings.volcengine_avatar_access_key_id or "").strip()
        self.secret_access_key = (secret_access_key or settings.volcengine_avatar_secret_access_key or "").strip()
        self.app_id = (app_id or settings.volcengine_avatar_app_id or settings.volcengine_avatar_rtc_app_id or "").strip()
        self.region = (region or settings.volcengine_avatar_region or "cn-north-1").strip() or "cn-north-1"
        self.host = host.strip()
        self.base_url = base_url.rstrip("/")
        self.start_version = start_version
        self.stop_version = stop_version
        self.llm_endpoint_id = (llm_endpoint_id or settings.volcengine_avatar_llm_endpoint_id or "").strip()
        self.avatar_token = (avatar_token or settings.volcengine_avatar_token or "").strip()
        self.avatar_role = (avatar_role or settings.volcengine_avatar_role or "").strip()
        self.avatar_user_id = (avatar_user_id or settings.volcengine_avatar_user_id or "").strip()
        self.avatar_background_url = (avatar_background_url or settings.volcengine_avatar_background_url or "").strip()
        self.avatar_video_bitrate = avatar_video_bitrate or settings.volcengine_avatar_video_bitrate
        self.avatar_config = avatar_config or {}
        self.tts_app_id = (tts_app_id or settings.volcengine_tts_app_id or "").strip()
        self.tts_access_key = (tts_access_key or settings.volcengine_tts_access_key or "").strip()
        self.tts_resource_id = (tts_resource_id or settings.volcengine_tts_resource_id or "volc.service_type.10029").strip()
        self.tts_speaker = (tts_speaker or settings.volcengine_tts_speaker or "").strip()
        self.tts_model = (tts_model or "seed-tts-2.0-standard").strip() or "seed-tts-2.0-standard"
        self.tts_output_format = (tts_output_format or "mp3").strip() or "mp3"
        self.tts_sample_rate = tts_sample_rate or 24000
        self.default_voice_mode = default_voice_mode

    @property
    def enabled(self) -> bool:
        return bool(self.access_key_id and self.secret_access_key and self.app_id)

    def build_default_config(
        self,
        *,
        title: str,
        hook: str,
        script_text: str,
        voice_mode: Optional[str] = None,
        room_id: Optional[str] = None,
        user_id: Optional[str] = None,
        bot_name: Optional[str] = None,
    ) -> dict[str, Any]:
        voice_mode = (voice_mode or self.default_voice_mode or "volc_tts").strip() or "volc_tts"
        config: dict[str, Any] = {
            "BotName": bot_name or f"viral_studio_{uuid.uuid4().hex[:10]}",
        }

        avatar_config: dict[str, Any] = {}
        if isinstance(self.avatar_config, dict):
            avatar_config.update(self.avatar_config)
        if self.avatar_token:
            avatar_config.setdefault("AvatarToken", self.avatar_token)
        if self.avatar_role:
            avatar_config.setdefault("AvatarRole", self.avatar_role)
        if user_id or self.avatar_user_id:
            avatar_config.setdefault("AvatarUserId", user_id or self.avatar_user_id)
        if self.avatar_background_url:
            avatar_config.setdefault("BackgroundUrl", self.avatar_background_url)
        if self.avatar_video_bitrate:
            avatar_config.setdefault("VideoBitrate", self.avatar_video_bitrate)
        if self.app_id:
            avatar_config.setdefault("AvatarAppId", self.app_id)
        if avatar_config:
            config["AvatarConfig"] = avatar_config

        if self.llm_endpoint_id:
            config["LLMConfig"] = {
                "Mode": "ArkV3",
                "EndPointId": self.llm_endpoint_id,
                "MaxTokens": 1024,
                "Temperature": 0.2,
                "TopP": 0.3,
                "SystemMessages": [
                    "你是一个专业的数字人播报员。",
                    "表达自然、简洁、信息密度高。",
                    "内容围绕用户提供的脚本进行播报，不要擅自扩展无关信息。",
                ],
                "UserMessages": [
                    f'user:"{title}"',
                    f'assistant:"{hook}"',
                    f'user:"{script_text[:120]}"',
                ],
                "HistoryLength": 3,
                "WelcomeSpeech": hook[:64] or title[:64] or "大家好",
            }

        if self.tts_app_id and self.tts_access_key and self.tts_speaker:
            config["TTSConfig"] = {
                "Provider": "volcano_bidirection",
                "ProviderParams": {
                    "app": {
                        "appid": self.tts_app_id,
                        "token": self.tts_access_key,
                    },
                    "audio": {
                        "voice_type": self.tts_speaker,
                        "speech_rate": 0,
                        "pitch_rate": 0,
                    },
                    "ResourceId": self.tts_resource_id if voice_mode != "volc_clone" else "seed-icl-2.0",
                },
            }

        if voice_mode == "volc_clone":
            config["VoiceMode"] = "volc_clone"
            config["TTSConfig"] = {
                "Provider": "volcano_bidirection",
                "ProviderParams": {
                    "app": {
                        "appid": self.tts_app_id,
                        "token": self.tts_access_key,
                    },
                    "audio": {
                        "voice_type": self.tts_speaker,
                        "speech_rate": 0,
                        "pitch_rate": 0,
                    },
                    "ResourceId": "seed-icl-2.0",
                },
            }
        elif voice_mode == "volc_tts":
            config["VoiceMode"] = "volc_tts"

        # Allow any extra caller-provided settings to override defaults.
        if room_id:
            config["RoomId"] = room_id
        if user_id:
            config["UserId"] = user_id
        return config

    def start_voice_chat(
        self,
        *,
        room_id: str,
        user_id: str,
        config: dict[str, Any],
        version: Optional[str] = None,
        timeout_s: int = 60,
    ) -> VolcAvatarResponse:
        payload = {
            "AppId": self.app_id,
            "RoomId": room_id,
            "UserId": user_id,
            "Config": config,
        }
        data = self._request("StartVoiceChat", version or self.start_version, payload, timeout_s=timeout_s)
        return self._parse_response("StartVoiceChat", version or self.start_version, data)

    def stop_voice_chat(
        self,
        *,
        room_id: str,
        user_id: str,
        version: Optional[str] = None,
        timeout_s: int = 30,
    ) -> VolcAvatarResponse:
        payload = {
            "AppId": self.app_id,
            "RoomId": room_id,
            "UserId": user_id,
        }
        data = self._request("StopVoiceChat", version or self.stop_version, payload, timeout_s=timeout_s)
        return self._parse_response("StopVoiceChat", version or self.stop_version, data)

    def test_session(
        self,
        *,
        title: str,
        hook: str,
        script_text: str,
        voice_mode: Optional[str] = None,
        room_id: Optional[str] = None,
        user_id: Optional[str] = None,
        bot_name: Optional[str] = None,
        stop_after: bool = True,
        timeout_s: int = 60,
    ) -> VolcAvatarSessionResult:
        if not self.enabled:
            raise RuntimeError("Volcengine avatar access key / secret key / app id is not configured")

        room_id = room_id or f"viral-studio-{uuid.uuid4().hex[:10]}"
        user_id = user_id or self.avatar_user_id or f"studio-user-{uuid.uuid4().hex[:8]}"
        bot_name = bot_name or f"viral-studio-bot-{uuid.uuid4().hex[:8]}"
        config = self.build_default_config(
            title=title,
            hook=hook,
            script_text=script_text,
            voice_mode=voice_mode,
            room_id=room_id,
            user_id=user_id,
            bot_name=bot_name,
        )
        start_response = self.start_voice_chat(room_id=room_id, user_id=user_id, config=config, timeout_s=timeout_s)
        stop_response: VolcAvatarResponse | None = None
        stopped = False
        if stop_after:
            try:
                stop_response = self.stop_voice_chat(room_id=room_id, user_id=user_id)
                stopped = True
            except Exception:
                stop_response = None
        return VolcAvatarSessionResult(
            room_id=room_id,
            user_id=user_id,
            bot_name=bot_name,
            started=True,
            stopped=stopped,
            start_response=start_response,
            stop_response=stop_response,
            payload=config,
            stop_payload={
                "AppId": self.app_id,
                "RoomId": room_id,
                "UserId": user_id,
            },
        )

    def _request(
        self,
        action: str,
        version: str,
        payload: dict[str, Any],
        timeout_s: int = 60,
    ) -> dict[str, Any]:
        query = {"Action": action, "Version": version}
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        headers = self._sign_headers(
            method="POST",
            host=self.host,
            path="/",
            query=query,
            body=body,
        )
        url = f"{self.base_url}?Action={quote(action)}&Version={quote(version)}"
        with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
            resp = client.post(url, content=body, headers=headers)
            resp.raise_for_status()
            return resp.json()

    def _sign_headers(
        self,
        *,
        method: str,
        host: str,
        path: str,
        query: dict[str, str],
        body: bytes,
    ) -> dict[str, str]:
        now = datetime.now(timezone.utc)
        x_date = now.strftime("%Y%m%dT%H%M%SZ")
        date = x_date[:8]
        content_type = "application/json"
        headers_to_sign = {
            "content-type": content_type,
            "host": host,
            "x-date": x_date,
        }
        canonical_headers = "".join(f"{key}:{headers_to_sign[key].strip()}\n" for key in sorted(headers_to_sign))
        signed_headers = ";".join(sorted(headers_to_sign))
        canonical_query = "&".join(f"{quote(str(k), safe='-_.~')}={quote(str(v), safe='-_.~')}" for k, v in sorted(query.items()))
        payload_hash = hashlib.sha256(body).hexdigest()
        canonical_request = "\n".join(
            [
                method.upper(),
                path or "/",
                canonical_query,
                canonical_headers,
                signed_headers,
                payload_hash,
            ]
        )
        credential_scope = f"{date}/{self.region}/rtc/request"
        string_to_sign = "\n".join(
            [
                "HMAC-SHA256",
                x_date,
                credential_scope,
                hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
            ]
        )
        k_secret = self.secret_access_key.encode("utf-8")
        k_date = hmac.new(k_secret, date.encode("utf-8"), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode("utf-8"), hashlib.sha256).digest()
        k_service = hmac.new(k_region, b"rtc", hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
        signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        authorization = (
            "HMAC-SHA256 "
            f"Credential={self.access_key_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        return {
            "Authorization": authorization,
            "Content-Type": content_type,
            "Host": host,
            "X-Date": x_date,
        }

    def _parse_response(self, action: str, version: str, data: dict[str, Any]) -> VolcAvatarResponse:
        metadata = data.get("ResponseMetadata") or {}
        return VolcAvatarResponse(
            action=str(metadata.get("Action") or action),
            version=str(metadata.get("Version") or version),
            request_id=str(metadata.get("RequestId") or ""),
            region=str(metadata.get("Region") or self.region),
            service=str(metadata.get("Service") or "rtc"),
            result=str(data.get("Result") or ""),
            raw=data,
        )
