from __future__ import annotations

import asyncio
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from .config import settings
from .crud import add_job_step, create_reference_video, get_integration, list_publish_targets, create_publish_job
from .db import session_scope
from .models import JobStep, Project, PublishJob, PublishTarget, ReferenceVideo, VideoJob
from .services.distributor import DistributionPackage
from .services.deepseek import DeepSeekClient
from .services.distributor import DistributorClient
from .services.ffmpeg import FFmpegRenderer
from .services.heygen import HeyGenClient
from .services.heygen_preview import HeyGenPreviewRenderer
from .services.monica import MonicaClient
from .services.volc_avatar import VolcAvatarClient
from .services.volc_avatar_preview import VolcAvatarPreviewRenderer
from .services.voice import VoiceSynthesizer
from .services.volcengine import VolcArkClient, VolcVideoClient
from .services.whisper import WhisperClient
from .utils import ensure_path, slugify


class VideoPipeline:
    def __init__(self) -> None:
        self.distributor = DistributorClient()

    def run(self, job_id: str) -> None:
        with session_scope() as db:
            job = db.get(VideoJob, job_id)
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            project = db.get(Project, job.project_id)
            if not project:
                raise ValueError(f"Project not found: {job.project_id}")
            project_settings = project.settings or {}
            mvp_mode = bool(project_settings.get("mvp_mode"))

            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            job.progress = 3
            db.flush()
            db.commit()

            reference = self._ensure_reference(db, job, project)
            db.commit()

            add_job_step(db, job.id, "reference-analysis", "running", {"reference_url": reference.reference_url})
            db.commit()
            analysis = asyncio.run(self._analyze_reference(db, job.owner_id, reference.reference_url, reference.source_title))
            reference.source_title = analysis["source_title"]
            reference.source_platform = analysis["source_platform"]
            reference.duration_sec = analysis["duration_sec"]
            reference.transcript_text = analysis["transcript_text"]
            reference.transcript_json = analysis.get("transcript_json", [])
            reference.hook_summary = analysis["hook_summary"]
            reference.style_notes = analysis["style_notes"]
            reference.analysis_payload = analysis
            reference.status = "analyzed"
            self._finish_step(db, job.id, "reference-analysis", analysis)
            job.progress = 20
            db.commit()

            add_job_step(db, job.id, "script-generation", "running", {"topic": job.topic})
            db.commit()
            llm_cfg = None if mvp_mode else (
                get_integration(db, job.owner_id, "volcengine")
                or get_integration(db, job.owner_id, "monica")
                or get_integration(db, job.owner_id, "deepseek")
            )
            if mvp_mode:
                deepseek = DeepSeekClient(api_key=None, base_url=None, model=None)
            elif llm_cfg and llm_cfg.provider == "volcengine":
                deepseek = VolcArkClient(
                    api_key=(llm_cfg.api_key_enc if llm_cfg else None) or None,
                    base_url=(llm_cfg.base_url if llm_cfg else None) or None,
                    model=(llm_cfg.model if llm_cfg else None) or None,
                )
            else:
                deepseek = DeepSeekClient(
                    api_key=(llm_cfg.api_key_enc if llm_cfg else None) or None,
                    base_url=(llm_cfg.base_url if llm_cfg else None) or None,
                    model=(llm_cfg.model if llm_cfg else None) or None,
                )
            brief = asyncio.run(
                deepseek.build_video_brief(
                    reference_title=reference.source_title,
                    reference_summary=reference.hook_summary or reference.transcript_text,
                    topic=job.topic,
                    duration_sec=reference.duration_sec or 60,
                    platform="short-video",
                )
            )
            title = "MVP 最小闭环" if mvp_mode else brief.title
            job.title = title
            job.script_text = brief.script
            job.script_json = {
                "title": title,
                "generated_title": brief.title,
                "hook": brief.hook,
                "script": brief.script,
                "subtitle_lines": brief.subtitle_lines,
                "hashtags": brief.hashtags,
                "shot_list": brief.shot_list,
                "notes": brief.notes,
                "raw": brief.raw,
            }
            self._finish_step(db, job.id, "script-generation", job.script_json)
            job.progress = 38
            db.commit()

            preview_hook = brief.hook
            preview_subtitle_lines = brief.subtitle_lines or job.script_text.splitlines()
            if mvp_mode:
                preview_hook = "先用最少资源跑通一个视频项目。"
                preview_subtitle_lines = [
                    "先把最强钩子放在前 3 秒。",
                    "第二步，用短句和高密度信息拉住注意力。",
                    "最后先跑通闭环，再谈更精致的效果。",
                ]
            render_hook = preview_hook if mvp_mode else brief.hook
            render_script_lines = preview_subtitle_lines if mvp_mode else (brief.subtitle_lines or job.script_text.splitlines())

            render_dir = ensure_path(settings.render_dir / job.id)
            cover_image_path: Optional[Path] = None
            cover_cfg = None if mvp_mode else (get_integration(db, job.owner_id, "volcengine") or get_integration(db, job.owner_id, "monica"))
            if cover_cfg and cover_cfg.api_key_enc:
                try:
                    cover_settings = cover_cfg.settings or {}
                    if cover_cfg.provider == "volcengine":
                        cover_client = VolcArkClient(
                            api_key=cover_cfg.api_key_enc,
                            base_url=cover_cfg.base_url or "https://ark.cn-beijing.volces.com/api/v3",
                            model=cover_cfg.model or "doubao-1-5-pro-32k-250115",
                        )
                        cover_model = str(cover_settings.get("image_model") or "doubao-seedream-5.0-lite").strip() or "doubao-seedream-5.0-lite"
                        cover_style = str(cover_settings.get("image_style") or "vivid").strip() or "vivid"
                        cover_quality = str(cover_settings.get("image_quality") or "standard").strip() or "standard"
                    else:
                        cover_client = MonicaClient(
                            api_key=cover_cfg.api_key_enc,
                            base_url=cover_cfg.base_url or "https://openapi.monica.im/v1",
                        )
                        cover_model = str((cover_settings.get("image_model") or "dall-e-3")).strip() or "dall-e-3"
                        cover_style = str(cover_settings.get("image_style") or "vivid").strip() or "vivid"
                        cover_quality = str(cover_settings.get("image_quality") or "standard").strip() or "standard"
                    cover_size = "1024x1792" if job.render_ratio == "9:16" else "1792x1024"
                    cover_prompt = self._build_cover_prompt(
                        project_name=project.name,
                        topic=job.topic,
                        title=job.title or brief.title,
                        hook=preview_hook or reference.hook_summary,
                        script=brief.script,
                    )
                    cover_result = asyncio.run(
                        cover_client.generate_image(
                            prompt=cover_prompt,
                            model=cover_model,
                            size=cover_size,
                            style=cover_style,
                            quality=cover_quality,
                        )
                    )
                    cover_image_path = render_dir / f"{slugify(job.title or brief.title)}-cover.png"
                    asyncio.run(cover_client.download_image(cover_result.url, cover_image_path))
                    job.pipeline_state = {
                        **(job.pipeline_state or {}),
                        "cover_image": str(cover_image_path),
                        "cover_model": cover_model,
                        "cover_url": cover_result.url,
                    }
                    db.commit()
                except Exception as exc:
                    job.pipeline_state = {**(job.pipeline_state or {}), "cover_image_error": str(exc)}
                    db.commit()
            elif mvp_mode:
                preview_renderer = VolcAvatarPreviewRenderer(render_dir)
                preview = preview_renderer.build_preview_card(
                    title=job.title or brief.title,
                    hook=preview_hook,
                    subtitle_lines=preview_subtitle_lines,
                    ratio=job.render_ratio,
                )
                cover_image_path = preview.preview_path
                job.pipeline_state = {
                    **(job.pipeline_state or {}),
                    "mvp_mode": True,
                    "cover_image": str(preview.preview_path),
                    "cover_model": "local-preview",
                }
                db.commit()

            add_job_step(db, job.id, "voice-generation", "running", {"provider": job.avatar_mode})
            db.commit()
            final_video_path: Path
            avatar_thumb = ""

            if job.avatar_mode == "volc_avatar":
                volc_cfg = get_integration(db, job.owner_id, "volcengine")
                volc_settings = volc_cfg.settings if volc_cfg else {}
                voice_mode = str(volc_settings.get("avatar_voice_mode") or "volc_tts").strip() or "volc_tts"
                voice_provider = "volc_clone" if voice_mode == "volc_clone" else "volc_tts"
                voice = VoiceSynthesizer(provider=voice_provider, config=volc_settings).synthesize(
                    job.script_text,
                    render_dir,
                    stem="avatar-voiceover",
                )
                preview_renderer = VolcAvatarPreviewRenderer(render_dir)
                preview = preview_renderer.build_preview_card(
                    title=job.title or brief.title,
                    hook=preview_hook,
                    subtitle_lines=preview_subtitle_lines,
                    ratio=job.render_ratio,
                )
                avatar_thumb = str(preview.preview_path)
                job.voice_provider = voice.provider
                job.pipeline_state = {
                    **(job.pipeline_state or {}),
                    "volc_avatar_mode": "simulated",
                    "volc_avatar_preview_image": str(preview.preview_path),
                    "volc_avatar_voice_mode": voice_mode,
                }
                avatar_client = VolcAvatarClient(
                    access_key_id=str(volc_settings.get("avatar_access_key_id") or settings.volcengine_avatar_access_key_id or "").strip(),
                    secret_access_key=str(volc_settings.get("avatar_secret_access_key") or settings.volcengine_avatar_secret_access_key or "").strip(),
                    app_id=str(
                        volc_settings.get("avatar_app_id")
                        or volc_settings.get("avatar_rtc_app_id")
                        or settings.volcengine_avatar_app_id
                        or settings.volcengine_avatar_rtc_app_id
                        or ""
                    ).strip(),
                    region=str(volc_settings.get("avatar_region") or settings.volcengine_avatar_region or "cn-north-1").strip() or "cn-north-1",
                    llm_endpoint_id=str(volc_settings.get("avatar_llm_endpoint_id") or settings.volcengine_avatar_llm_endpoint_id or "").strip(),
                    avatar_token=str(volc_settings.get("avatar_token") or settings.volcengine_avatar_token or "").strip(),
                    avatar_role=str(volc_settings.get("avatar_role") or settings.volcengine_avatar_role or "").strip(),
                    avatar_user_id=str(volc_settings.get("avatar_user_id") or settings.volcengine_avatar_user_id or "").strip(),
                    avatar_background_url=str(volc_settings.get("avatar_background_url") or settings.volcengine_avatar_background_url or "").strip(),
                    avatar_video_bitrate=int(volc_settings.get("avatar_video_bitrate") or settings.volcengine_avatar_video_bitrate or 2000),
                    avatar_config=(volc_settings.get("avatar_config") if isinstance(volc_settings.get("avatar_config"), dict) else {}) or {},
                    tts_app_id=str(volc_settings.get("tts_app_id") or settings.volcengine_tts_app_id or "").strip(),
                    tts_access_key=str(volc_settings.get("tts_access_key") or settings.volcengine_tts_access_key or "").strip(),
                    tts_resource_id=str(volc_settings.get("tts_resource_id") or settings.volcengine_tts_resource_id or "volc.service_type.10029").strip(),
                    tts_speaker=str(volc_settings.get("tts_speaker") or settings.volcengine_tts_speaker or "").strip(),
                    tts_model=str(volc_settings.get("tts_model") or "seed-tts-2.0-standard").strip() or "seed-tts-2.0-standard",
                    tts_output_format=str(volc_settings.get("tts_output_format") or "mp3").strip() or "mp3",
                    tts_sample_rate=int(volc_settings.get("tts_sample_rate") or 24000),
                    default_voice_mode=voice_mode,
                )
                try:
                    avatar_session = avatar_client.test_session(
                        title=job.title or brief.title,
                        hook=render_hook or reference.hook_summary,
                        script_text=job.script_text,
                        voice_mode=voice_mode,
                        stop_after=True,
                    )
                    job.pipeline_state = {
                        **(job.pipeline_state or {}),
                        "volc_avatar_mode": "hybrid",
                        "volc_avatar_room_id": avatar_session.room_id,
                        "volc_avatar_user_id": avatar_session.user_id,
                        "volc_avatar_bot_name": avatar_session.bot_name,
                        "volc_avatar_request_id": avatar_session.start_response.request_id if avatar_session.start_response else "",
                        "volc_avatar_stop_request_id": avatar_session.stop_response.request_id if avatar_session.stop_response else "",
                        "volc_avatar_start_result": avatar_session.start_response.result if avatar_session.start_response else "",
                        "volc_avatar_stop_result": avatar_session.stop_response.result if avatar_session.stop_response else "",
                        "volc_avatar_payload": avatar_session.payload,
                    }
                    self._finish_step(
                        db,
                        job.id,
                        "voice-generation",
                        {
                            "provider": "volc_avatar",
                            "mode": "hybrid",
                            "room_id": avatar_session.room_id,
                            "user_id": avatar_session.user_id,
                            "bot_name": avatar_session.bot_name,
                            "start_request_id": avatar_session.start_response.request_id if avatar_session.start_response else "",
                            "start_result": avatar_session.start_response.result if avatar_session.start_response else "",
                            "stop_request_id": avatar_session.stop_response.request_id if avatar_session.stop_response else "",
                            "stop_result": avatar_session.stop_response.result if avatar_session.stop_response else "",
                            "preview_path": str(preview.preview_path),
                        },
                    )
                except Exception as exc:
                    job.pipeline_state = {
                        **(job.pipeline_state or {}),
                        "volc_avatar_mode": "simulated",
                        "volc_avatar_error": str(exc),
                    }
                    self._finish_step(
                        db,
                        job.id,
                        "voice-generation",
                        {"provider": "volc_avatar", "mode": "simulated", "preview_path": str(preview.preview_path), "error": str(exc)},
                    )
                renderer = FFmpegRenderer(render_dir)
                render = renderer.render_short_video(
                    title=job.title or brief.title,
                    hook=render_hook,
                    script_lines=render_script_lines,
                    audio_path=voice.audio_path,
                    output_name=slugify(job.title or brief.title),
                    ratio=job.render_ratio,
                    cover_image_path=preview.preview_path,
                )
                final_video_path = render.video_path
                avatar_thumb = str(preview.preview_path)
                self._finish_step(
                    db,
                    job.id,
                    "render",
                    {
                        "video_path": str(render.video_path),
                        "thumbnail_path": str(render.thumbnail_path),
                        "subtitle_path": str(render.subtitle_path),
                        "poster_path": str(render.poster_path),
                    },
                )
                job.progress = 72
                db.commit()

            elif job.avatar_mode == "heygen":
                heygen_cfg = get_integration(db, job.owner_id, "heygen")
                heygen_payload = (heygen_cfg.settings if heygen_cfg else {}) or {}
                avatar_id = str(heygen_payload.get("avatar_id") or settings.heygen_avatar_id or "").strip()
                voice_id = str(heygen_payload.get("voice_id") or settings.heygen_voice_id or "").strip()
                heygen_api_key = str((heygen_cfg.api_key_enc if heygen_cfg else "") or settings.heygen_api_key or "").strip()
                if heygen_api_key and avatar_id and voice_id:
                    heygen = HeyGenClient(api_key=heygen_api_key, base_url=(heygen_cfg.base_url if heygen_cfg else None) or None)
                    video_req = asyncio.run(
                        heygen.create_avatar_video(
                            title=job.title or brief.title,
                            script=job.script_text,
                            avatar_id=avatar_id,
                            voice_id=voice_id,
                            aspect_ratio=self._ratio_to_heygen(job.render_ratio),
                            callback_url=str(heygen_payload.get("callback_url", "")).strip(),
                            caption=True,
                        )
                    )
                    video_status = asyncio.run(heygen.wait_for_video(video_req.video_id))
                    if video_status.status.lower() != "completed" or not video_status.video_url:
                        raise RuntimeError(f"HeyGen video failed: {json.dumps(video_status.raw or {}, ensure_ascii=False)}")
                    final_video_path = render_dir / f"{slugify(job.title or brief.title)}-heygen.mp4"
                    asyncio.run(heygen.download_video(video_status.video_url, final_video_path))
                    avatar_thumb = str(cover_image_path) if cover_image_path else video_status.thumbnail_url
                    voice_provider = "heygen"
                    job.pipeline_state = {**(job.pipeline_state or {}), "heygen_mode": "real"}
                    job.voice_provider = "heygen"
                    self._finish_step(
                        db,
                        job.id,
                        "voice-generation",
                        {"provider": "heygen", "mode": "real", "video_id": video_status.video_id, "video_url": video_status.video_url},
                    )
                else:
                    preview_renderer = HeyGenPreviewRenderer(render_dir)
                    preview = preview_renderer.build_preview_card(
                        title=job.title or brief.title,
                        hook=preview_hook,
                        subtitle_lines=preview_subtitle_lines,
                        ratio=job.render_ratio,
                    )
                    voice = VoiceSynthesizer(provider="heygen_preview").synthesize(job.script_text, render_dir, stem="heygen-preview-voice")
                    renderer = FFmpegRenderer(render_dir)
                    render = renderer.render_short_video(
                        title=job.title or brief.title,
                        hook=render_hook,
                        script_lines=render_script_lines,
                        audio_path=voice.audio_path,
                        output_name=f"{slugify(job.title or brief.title)}-heygen-preview",
                        ratio=job.render_ratio,
                        cover_image_path=preview.preview_path,
                    )
                    final_video_path = render.video_path
                    avatar_thumb = str(preview.preview_path)
                    voice_provider = "heygen_preview"
                    job.pipeline_state = {
                        **(job.pipeline_state or {}),
                        "heygen_mode": "simulated",
                        "heygen_preview_image": str(preview.preview_path),
                    }
                    job.voice_provider = "heygen_preview"
                    self._finish_step(
                        db,
                        job.id,
                        "voice-generation",
                        {"provider": "heygen_preview", "mode": "simulated", "preview_path": str(preview.preview_path)},
                    )
            elif job.avatar_mode in {"volc_tts", "volc_clone"}:
                voice_cfg = get_integration(db, job.owner_id, "volcengine")
                voice = VoiceSynthesizer(provider=job.avatar_mode, config=(voice_cfg.settings if voice_cfg else {})).synthesize(
                    job.script_text,
                    render_dir,
                    stem="voiceover",
                )
                self._finish_step(
                    db,
                    job.id,
                    "voice-generation",
                    {"audio_path": str(voice.audio_path), "provider": voice.provider, "note": voice.note},
                )
                job.pipeline_state = {**(job.pipeline_state or {}), "voiceover": str(voice.audio_path), "voice_provider": voice.provider}
                job.voice_provider = voice.provider

                voice_settings = voice_cfg.settings if voice_cfg else {}
                video_model = str(voice_settings.get("video_model") or settings.volcengine_video_model).strip() or settings.volcengine_video_model
                video_client = VolcVideoClient(
                    api_key=(voice_cfg.api_key_enc if voice_cfg else None) or None,
                    base_url=(voice_cfg.base_url if voice_cfg else None) or None,
                    model=video_model,
                )
                if video_client.enabled:
                    video_prompt = self._build_seedance_prompt(
                        project_name=project.name,
                        topic=job.topic,
                        title=job.title or brief.title,
                        hook=brief.hook or reference.hook_summary,
                        script=brief.script,
                        ratio=job.render_ratio,
                    )
                    video_task = video_client.create_video_task(prompt=video_prompt, model=video_model)
                    video_result = video_client.wait_for_video(video_task.task_id, timeout_s=900, poll_interval_s=12)
                    if not video_result.video_url:
                        raise RuntimeError(f"Seedance video generation failed: {json.dumps(video_result.raw or {}, ensure_ascii=False)}")
                    raw_video_path = render_dir / f"{slugify(job.title or brief.title)}-seedance-raw.mp4"
                    video_client.download_video(video_result.video_url, raw_video_path)
                    renderer = FFmpegRenderer(render_dir)
                    render = renderer.compose_generated_video(
                        source_video=raw_video_path,
                        audio_path=voice.audio_path,
                        script_lines=brief.subtitle_lines or job.script_text.splitlines(),
                        output_name=slugify(job.title or brief.title),
                        ratio=job.render_ratio,
                    )
                    final_video_path = render.video_path
                    avatar_thumb = str(render.thumbnail_path)
                    job.pipeline_state = {
                        **(job.pipeline_state or {}),
                        "seedance_mode": "enabled",
                        "seedance_task_id": video_task.task_id,
                        "seedance_video_url": video_result.video_url,
                        "seedance_model": video_model,
                    }
                    self._finish_step(
                        db,
                        job.id,
                        "video-generation",
                        {
                            "task_id": video_task.task_id,
                            "video_url": video_result.video_url,
                            "model": video_model,
                        },
                    )
                    self._finish_step(
                        db,
                        job.id,
                        "render",
                        {
                            "video_path": str(render.video_path),
                            "thumbnail_path": str(render.thumbnail_path),
                            "subtitle_path": str(render.subtitle_path),
                            "poster_path": str(render.poster_path),
                        },
                    )
                else:
                    renderer = FFmpegRenderer(render_dir)
                    render = renderer.render_short_video(
                        title=job.title or brief.title,
                        hook=render_hook,
                        script_lines=render_script_lines,
                        audio_path=voice.audio_path,
                        output_name=slugify(job.title or brief.title),
                        ratio=job.render_ratio,
                        cover_image_path=cover_image_path,
                    )
                    final_video_path = render.video_path
                    avatar_thumb = str(render.thumbnail_path)
                    self._finish_step(
                        db,
                        job.id,
                        "render",
                        {
                            "video_path": str(render.video_path),
                            "thumbnail_path": str(render.thumbnail_path),
                            "subtitle_path": str(render.subtitle_path),
                            "poster_path": str(render.poster_path),
                        },
                    )
                job.progress = 72
                db.commit()

            else:
                voice_cfg = get_integration(db, job.owner_id, "volcengine")
                voice = VoiceSynthesizer(provider=job.avatar_mode, config=(voice_cfg.settings if voice_cfg else {})).synthesize(
                    job.script_text,
                    render_dir,
                    stem="voiceover",
                )
                self._finish_step(
                    db,
                    job.id,
                    "voice-generation",
                    {"audio_path": str(voice.audio_path), "provider": voice.provider, "note": voice.note},
                )
                job.pipeline_state = {**(job.pipeline_state or {}), "voiceover": str(voice.audio_path), "voice_provider": voice.provider}
                job.voice_provider = voice.provider
                renderer = FFmpegRenderer(render_dir)
                render = renderer.render_short_video(
                    title=job.title or brief.title,
                    hook=render_hook,
                    script_lines=render_script_lines,
                    audio_path=voice.audio_path,
                    output_name=slugify(job.title or brief.title),
                    ratio=job.render_ratio,
                    cover_image_path=cover_image_path,
                )
                final_video_path = render.video_path
                avatar_thumb = str(render.thumbnail_path)
                self._finish_step(
                    db,
                    job.id,
                    "render",
                    {
                        "video_path": str(render.video_path),
                        "thumbnail_path": str(render.thumbnail_path),
                        "subtitle_path": str(render.subtitle_path),
                    "poster_path": str(render.poster_path),
                },
                )
                job.progress = 72
                db.commit()

            job.output_path = str(final_video_path)
            job.thumbnail_url = avatar_thumb
            job.status = "ready_to_publish"
            job.progress = 84
            db.commit()

            add_job_step(db, job.id, "distribution-bundle", "running", {"platforms": project.target_platforms})
            db.commit()
            bundle = self.distributor.build_package(
                title=job.title,
                script=job.script_text,
                hashtags=brief.hashtags,
                platforms=list(project.target_platforms or []),
                output_video_url=str(final_video_path),
                thumbnail_url=avatar_thumb,
            )
            job.publish_bundle = bundle.payload
            self._finish_step(db, job.id, "distribution-bundle", bundle.payload)
            db.commit()

            publish_results = self._publish_to_targets(db, job, project, bundle, final_video_path, brief.hashtags)
            job.pipeline_state = {**(job.pipeline_state or {}), "publish_results": publish_results}
            job.progress = 100
            job.status = "completed"
            job.finished_at = datetime.now(timezone.utc)
            db.commit()

    def retry_publish_job(self, db, publish_job: PublishJob) -> dict:
        job = db.get(VideoJob, publish_job.job_id)
        target = db.get(PublishTarget, publish_job.target_id)
        if not job or not target:
            raise ValueError("Publish job target or video job no longer exists")
        if not job.output_path:
            raise ValueError("Video output is not ready")
        package = DistributionPackage.from_payload(publish_job.payload or job.publish_bundle or {})
        publish_job.status = "running"
        publish_job.error = ""
        db.commit()
        result = self._publish_target(db, job, target, package, Path(job.output_path), list(package.platforms or []))
        publish_job.status = "published" if result.get("status") == "published" else result.get("status", "manual")
        publish_job.remote_id = str(result.get("remote_id", ""))
        publish_job.remote_url = str(result.get("remote_url", ""))
        publish_job.payload = {**(publish_job.payload or {}), "retry_result": result}
        publish_job.error = str(result.get("error", ""))
        db.commit()
        return result

    def _publish_to_targets(self, db, job: VideoJob, project: Project, bundle, video_path: Path, hashtags: list[str]) -> list[dict]:
        results: list[dict] = []
        targets = [t for t in list_publish_targets(db, job.owner_id, project.id) if t.is_enabled]
        for target in targets:
            publish_job = create_publish_job(db, job.id, target.id, status="queued", payload=bundle.payload)
            db.commit()
            try:
                result = self._publish_target(db, job, target, bundle, video_path, hashtags)
                publish_job.status = "published"
                publish_job.remote_id = str(result.get("remote_id", ""))
                publish_job.remote_url = str(result.get("remote_url", ""))
                publish_job.payload = result
                results.append(result)
            except Exception as exc:
                publish_job.status = "failed"
                publish_job.error = str(exc)
                results.append({"platform": target.platform, "status": "failed", "error": str(exc)})
            db.commit()
        return results

    def _publish_target(self, db, job: VideoJob, target, bundle, video_path: Path, hashtags: list[str]) -> dict:
        adapter = (target.settings or {}).get("adapter") or target.platform
        description = bundle.description
        account_name = target.handle or str((target.settings or {}).get("account_name", "")).strip()
        if adapter == "social-auto-upload" or adapter in {"douyin", "xiaohongshu", "kuaishou", "bilibili", "youtube", "tiktok"}:
            platform = adapter if adapter != "social-auto-upload" else target.platform
            extra_args = []
            if platform == "bilibili":
                extra_args.extend(["--tid", str((target.settings or {}).get("tid", 249))])
            return self.distributor.publish_social_auto_upload(
                platform=platform,
                video_path=video_path,
                title=job.title,
                description=description,
                account_name=account_name or platform,
                extra_args=extra_args,
            )

        if adapter == "multipost":
            return asyncio.run(self.distributor.publish_multipost(bundle))

        return {
            "status": "manual",
            "platform": target.platform,
            "message": f"Unknown adapter '{adapter}', package exported only.",
            "bundle": bundle.payload,
        }

    def _ensure_reference(self, db, job: VideoJob, project: Project) -> ReferenceVideo:
        if job.reference_id:
            ref = db.get(ReferenceVideo, job.reference_id)
            if ref:
                return ref
        reference_url = project.reference_url or ""
        ref = create_reference_video(
            db,
            owner_id=job.owner_id,
            project_id=project.id,
            reference_url=reference_url or "manual://reference",
            source_title=project.name,
            source_platform="manual",
            duration_sec=60,
            transcript_text=project.description or "Reference description not provided.",
            hook_summary=project.description or "Project reference summary",
            style_notes="Reference analyzed from project metadata.",
            analysis_payload={"project_reference": True},
        )
        job.reference_id = ref.id
        return ref

    async def _analyze_reference(self, db, owner_id: str, reference_url: str, source_title: str) -> dict:
        platform = "unknown"
        duration_sec = 60
        transcript_text = ""
        transcript_json = []
        title = source_title or "Reference Video"
        hook_summary = ""
        style_notes = "Fast hook, dense pacing, clear close."

        info = self._try_extract_metadata(reference_url)
        if info:
            title = info.get("title") or title
            platform = info.get("extractor") or info.get("ie_key") or platform
            duration_sec = int(info.get("duration") or duration_sec)
            uploader = info.get("uploader") or info.get("channel") or ""
            hook_summary = f"{title} | {uploader}".strip(" |")
            transcript_text = info.get("description") or info.get("title") or title
            style_notes = "Derived from platform metadata and reference description."

        downloaded = await self._download_reference_media(reference_url)
        if downloaded:
            whisper_cfg = get_integration(db, owner_id, "openai")
            whisper_api_key = str((whisper_cfg.api_key_enc if whisper_cfg else "") or settings.openai_api_key or "").strip()
            if whisper_api_key:
                whisper = WhisperClient(api_key=whisper_api_key, base_url=(whisper_cfg.base_url if whisper_cfg else None) or None, model=(whisper_cfg.model if whisper_cfg else None) or None)
                transcript = await whisper.transcribe_file(downloaded, prompt=title)
                transcript_text = transcript.text or transcript_text
                transcript_json = transcript.raw.get("segments", []) if isinstance(transcript.raw, dict) else []
                style_notes = "Transcribed from reference media via OpenAI Whisper."
            else:
                transcript_text = transcript_text or f"Reference link: {reference_url}"
        elif not transcript_text:
            transcript_text = f"Reference link: {reference_url}"
            hook_summary = f"Use the reference rhythm of {title} to generate a new angle."

        return {
            "source_title": title,
            "source_platform": platform,
            "duration_sec": duration_sec,
            "transcript_text": transcript_text,
            "transcript_json": transcript_json,
            "hook_summary": hook_summary,
            "style_notes": style_notes,
            "reference_url": reference_url,
        }

    def _try_extract_metadata(self, reference_url: str) -> Optional[dict]:
        if not reference_url or reference_url.startswith("manual://"):
            return None
        try:
            import yt_dlp

            ydl_opts = {"quiet": True, "skip_download": True, "nocheckcertificate": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(reference_url, download=False)
        except Exception:
            return None

    async def _download_reference_media(self, reference_url: str) -> Optional[Path]:
        if not reference_url or reference_url.startswith("manual://"):
            return None
        try:
            import yt_dlp

            tmpdir = Path(tempfile.mkdtemp(prefix="viral-studio-ref-"))
            outtmpl = str(tmpdir / "%(title).80s.%(ext)s")
            ydl_opts = {
                "quiet": True,
                "nocheckcertificate": True,
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "restrictfilenames": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(reference_url, download=True)
                filepath = ydl.prepare_filename(info)
            path = Path(filepath)
            if path.exists():
                return path
            candidates = list(tmpdir.glob("*"))
            return candidates[0] if candidates else None
        except Exception:
            return None

    def _ratio_to_heygen(self, ratio: str) -> str:
        return "16:9" if ratio == "16:9" else "9:16"

    def _build_cover_prompt(self, project_name: str, topic: str, title: str, hook: str, script: str) -> str:
        return "\n".join(
            [
                "Create a premium short-video cover image.",
                "Style: cinematic, modern, high contrast, social-media ready.",
                "Leave generous negative space for Chinese title text.",
                f"Project: {project_name}",
                f"Topic: {topic}",
                f"Title: {title}",
                f"Hook: {hook}",
                f"Script excerpt: {script[:400]}",
                "Do not render readable text in the image.",
            ]
        )

    def _build_seedance_prompt(self, project_name: str, topic: str, title: str, hook: str, script: str, ratio: str = "9:16") -> str:
        aspect = "vertical 9:16" if ratio != "16:9" else "horizontal 16:9"
        return "\n".join(
            [
                "Create a polished short-form video for social media.",
                f"Aspect ratio: {aspect}.",
                "Cinematic, modern, premium, high contrast.",
                "Human-centered framing, dynamic camera motion, clean composition.",
                "No readable text in the visual, leave safe negative space for subtitles.",
                "Make it feel like a finished creator video, not a slideshow.",
                f"Project: {project_name}",
                f"Topic: {topic}",
                f"Title: {title}",
                f"Hook: {hook}",
                f"Script excerpt: {script[:500]}",
            ]
        )

    def _finish_step(self, db, job_id: str, step_key: str, detail: dict) -> None:
        step = db.execute(
            select(JobStep).where(JobStep.job_id == job_id, JobStep.step_key == step_key).order_by(JobStep.created_at.desc())
        ).scalars().first()
        if step is None:
            step = add_job_step(db, job_id, step_key, "done", detail)
        step.status = "done"
        step.detail = detail
        step.finished_at = datetime.now(timezone.utc)
        db.commit()
