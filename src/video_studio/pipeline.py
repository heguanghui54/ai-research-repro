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
from .services.monica import MonicaClient
from .services.voice import VoiceSynthesizer
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
            llm_cfg = get_integration(db, job.owner_id, "monica") or get_integration(db, job.owner_id, "deepseek")
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
            job.title = brief.title
            job.script_text = brief.script
            job.script_json = {
                "title": brief.title,
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

            render_dir = ensure_path(settings.render_dir / job.id)
            cover_image_path: Optional[Path] = None
            cover_cfg = get_integration(db, job.owner_id, "monica")
            if cover_cfg and cover_cfg.api_key_enc:
                try:
                    cover_client = MonicaClient(
                        api_key=cover_cfg.api_key_enc,
                        base_url=cover_cfg.base_url or "https://openapi.monica.im/v1",
                    )
                    cover_model = str((cover_cfg.settings or {}).get("image_model") or "dall-e-3").strip() or "dall-e-3"
                    cover_size = "1024x1792" if job.render_ratio == "9:16" else "1792x1024"
                    cover_prompt = self._build_cover_prompt(
                        project_name=project.name,
                        topic=job.topic,
                        title=job.title or brief.title,
                        hook=brief.hook or reference.hook_summary,
                        script=brief.script,
                    )
                    cover_result = asyncio.run(
                        cover_client.generate_image(
                            prompt=cover_prompt,
                            model=cover_model,
                            size=cover_size,
                            style=str((cover_cfg.settings or {}).get("image_style") or "vivid"),
                            quality=str((cover_cfg.settings or {}).get("image_quality") or "standard"),
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

            add_job_step(db, job.id, "voice-generation", "running", {"provider": job.avatar_mode})
            db.commit()
            final_video_path: Path
            avatar_thumb = ""

            if job.avatar_mode == "heygen":
                heygen_cfg = get_integration(db, job.owner_id, "heygen")
                heygen_payload = (heygen_cfg.settings if heygen_cfg else {}) or {}
                avatar_id = str(heygen_payload.get("avatar_id") or settings.heygen_avatar_id or "").strip()
                voice_id = str(heygen_payload.get("voice_id") or settings.heygen_voice_id or "").strip()
                heygen_api_key = str((heygen_cfg.api_key_enc if heygen_cfg else "") or settings.heygen_api_key or "").strip()
                if not (heygen_api_key and avatar_id and voice_id):
                    raise RuntimeError("HeyGen is selected but api_key/avatar_id/voice_id are not configured")
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
                self._finish_step(
                    db,
                    job.id,
                    "voice-generation",
                    {"provider": "heygen", "video_id": video_status.video_id, "video_url": video_status.video_url},
                )
            else:
                voice_provider_cfg = get_integration(db, job.owner_id, "openai")
                if voice_provider_cfg and voice_provider_cfg.api_key_enc and job.script_text:
                    # Whisper is used upstream for transcription; local voice remains the default narrator path.
                    pass
                voice = VoiceSynthesizer(provider=job.avatar_mode).synthesize(job.script_text, render_dir, stem="voiceover")
                self._finish_step(
                    db,
                    job.id,
                    "voice-generation",
                    {"audio_path": str(voice.audio_path), "provider": voice.provider, "note": voice.note},
                )
                job.pipeline_state = {**(job.pipeline_state or {}), "voiceover": str(voice.audio_path), "voice_provider": voice.provider}
                renderer = FFmpegRenderer(render_dir)
                render = renderer.render_short_video(
                    title=job.title or brief.title,
                    hook=brief.hook,
                    script_lines=brief.subtitle_lines or job.script_text.splitlines(),
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

    def _finish_step(self, db, job_id: str, step_key: str, detail: dict) -> None:
        step = db.execute(
            select(JobStep).where(JobStep.job_id == job_id, JobStep.step_key == step_key).order_by(JobStep.created_at.desc())
        ).scalar_one_or_none()
        if step is None:
            step = add_job_step(db, job_id, step_key, "done", detail)
        step.status = "done"
        step.detail = detail
        step.finished_at = datetime.now(timezone.utc)
        db.commit()
