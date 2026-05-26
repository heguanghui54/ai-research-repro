from __future__ import annotations

from typing import Any, Dict, List


STATUS_LABELS: dict[str, str] = {
    "all": "全部",
    "queued": "排队中",
    "running": "进行中",
    "ready_to_publish": "待发布",
    "published": "已发布",
    "completed": "已完成",
    "failed": "失败",
    "manual": "待手动处理",
    "active": "启用",
    "archived": "归档",
}

PLATFORM_LABELS: dict[str, str] = {
    "douyin": "抖音",
    "xiaohongshu": "小红书",
    "kuaishou": "快手",
    "bilibili": "B站",
    "youtube": "YouTube",
    "tiktok": "TikTok",
    "multipost": "MultiPost",
}

AVATAR_MODE_LABELS: dict[str, str] = {
    "cosyvoice": "CosyVoice",
    "volc_avatar": "火山数字人",
    "heygen": "HeyGen 数字人（旧）",
    "volc_tts": "火山语音（公版音色）",
    "volc_clone": "火山声音复刻",
}

VOICE_PROVIDER_LABELS: dict[str, str] = {
    "deepseek": "DeepSeek",
    "openai": "OpenAI Whisper",
    "monica": "Monica API",
    "heygen_preview": "HeyGen 预览",
    "volc_tts": "火山语音（公版音色）",
    "volc_clone": "火山声音复刻",
}

PUBLISH_ADAPTER_LABELS: dict[str, str] = {
    "social-auto-upload": "social-auto-upload",
    "multipost": "MultiPost",
}

ROLE_LABELS: dict[str, str] = {
    "admin": "管理员",
    "member": "成员",
}

API_CONFIG_SECTIONS: list[dict[str, Any]] = [
    {
        "provider": "monica",
        "label": "Monica API（推荐默认）",
        "description": "OpenAI 兼容的大模型与图像模型，适合作为默认 AI 后台。",
        "api_key_placeholder": "粘贴 Monica API Key",
        "base_url": "https://openapi.monica.im/v1",
        "model": "gpt-4o",
        "extra_defaults": {
            "image_model": "dall-e-3",
            "image_style": "vivid",
            "image_quality": "standard",
            "notes": "Monica Open API: chat + image",
        },
    },
    {
        "provider": "deepseek",
        "label": "DeepSeek（兼容）",
        "description": "保留兼容模式，便于从旧配置平滑迁移。",
        "api_key_placeholder": "粘贴 DeepSeek API Key",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "extra_defaults": {},
    },
    {
        "provider": "volcengine",
        "label": "火山方舟 / 豆包语音 / 火山数字人",
        "description": "默认优先用低成本但可用的 Ark 文本模型、Seedream 封面图、豆包语音和火山数字人。公版 TTS 用最便宜的音色；复刻音色和数字人会用到 RTC / 语音服务的 App ID、Access Key、Secret Key、Avatar AppId 等信息。",
        "api_key_placeholder": "粘贴 Ark API Key",
        "api_key_default": "ark-b028c713-b2c6-4b71-a5dd-cd6231598a93-2017c",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-1-5-pro-32k-250115",
        "extra_defaults": {
            "image_model": "doubao-seedream-5.0-lite",
            "image_size": "1024x1024",
            "image_style": "vivid",
            "image_quality": "standard",
            "video_model": "doubao-seedance-1-5-pro-251215",
            "avatar_access_key_id": "",
            "avatar_secret_access_key": "",
            "avatar_rtc_app_id": "",
            "avatar_app_id": "",
            "avatar_token": "",
            "avatar_role": "",
            "avatar_user_id": "",
            "avatar_region": "cn-north-1",
            "avatar_llm_endpoint_id": "",
            "avatar_background_url": "",
            "avatar_video_bitrate": 2000,
            "avatar_voice_mode": "volc_tts",
            "tts_app_id": "",
            "tts_access_key": "",
            "tts_resource_id": "volc.service_type.10029",
            "tts_speaker": "zh_female_qingxin_moon_bigtts",
            "tts_model": "seed-tts-2.0-standard",
            "tts_output_format": "mp3",
            "tts_sample_rate": 24000,
            "clone_resource_id": "seed-icl-2.0",
            "notes": "Ark text/image + Doubao TTS / voice clone + Volc avatar",
        },
    },
    {
        "provider": "openai",
        "label": "OpenAI Whisper",
        "description": "用于参考视频音频转写。",
        "api_key_placeholder": "粘贴 OpenAI API Key",
        "base_url": "https://api.openai.com/v1",
        "model": "whisper-1",
        "extra_defaults": {},
    },
    {
        "provider": "multipost",
        "label": "MultiPost 分发",
        "description": "用于多平台分发的 HTTP 接口。",
        "api_key_placeholder": "粘贴 MultiPost API Key",
        "base_url": "",
        "model": "",
        "extra_defaults": {
            "publish_path": "/publish",
        },
    },
]


def label_or_default(mapping: dict[str, str], value: str) -> str:
    if not value:
        return "未设置"
    return mapping.get(value, value)


def label_status(value: str) -> str:
    return label_or_default(STATUS_LABELS, value)


def label_platform(value: str) -> str:
    return label_or_default(PLATFORM_LABELS, value)


def label_avatar_mode(value: str) -> str:
    return label_or_default(AVATAR_MODE_LABELS, value)


def label_voice_provider(value: str) -> str:
    return label_or_default(VOICE_PROVIDER_LABELS, value)


def label_publish_adapter(value: str) -> str:
    return label_or_default(PUBLISH_ADAPTER_LABELS, value)


def label_role(value: str) -> str:
    return label_or_default(ROLE_LABELS, value)
