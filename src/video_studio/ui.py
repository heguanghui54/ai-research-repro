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
    "heygen": "HeyGen 数字人",
}

VOICE_PROVIDER_LABELS: dict[str, str] = {
    "deepseek": "DeepSeek",
    "openai": "OpenAI Whisper",
    "monica": "Monica API",
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
        "provider": "openai",
        "label": "OpenAI Whisper",
        "description": "用于参考视频音频转写。",
        "api_key_placeholder": "粘贴 OpenAI API Key",
        "base_url": "https://api.openai.com/v1",
        "model": "whisper-1",
        "extra_defaults": {},
    },
    {
        "provider": "heygen",
        "label": "HeyGen 数字人",
        "description": "用于头像播报和数字人口播。",
        "api_key_placeholder": "粘贴 HeyGen API Key",
        "base_url": "https://api.heygen.com",
        "model": "",
        "extra_defaults": {
            "avatar_id": "",
            "voice_id": "",
            "callback_url": "",
        },
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

