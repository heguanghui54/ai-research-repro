from __future__ import annotations

import asyncio
import json
import tempfile
import wave
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urlencode

from fastapi import BackgroundTasks, Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from .auth import current_user, require_user, sign_in, sign_out
from .config import settings
from .crud import (
    authenticate_user,
    create_job,
    create_project,
    create_reference_video,
    create_user,
    get_user_by_email,
    get_integration,
    get_job,
    get_job_steps,
    get_project,
    get_publish_job,
    list_integrations,
    list_jobs,
    list_projects,
    list_publish_jobs,
    list_publish_targets,
    upsert_integration,
    upsert_publish_target,
)
from .db import Base, SessionLocal, engine
from .models import AppUser, Integration, Project, PublishJob, PublishTarget, VideoJob
from .pipeline import VideoPipeline
from .services.monica import MonicaClient
from .services.volcengine import VolcArkClient, VolcSpeechClient
from .ui import (
    API_CONFIG_SECTIONS,
    label_avatar_mode,
    label_platform,
    label_publish_adapter,
    label_role,
    label_status,
    label_voice_provider,
)
from .utils import format_dt


app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax")
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
templates = Jinja2Templates(directory=str(settings.template_dir))
templates.env.globals.update(
    {
        "label_status": label_status,
        "label_platform": label_platform,
        "label_avatar_mode": label_avatar_mode,
        "label_voice_provider": label_voice_provider,
        "label_publish_adapter": label_publish_adapter,
        "label_role": label_role,
    }
)
executor = ThreadPoolExecutor(max_workers=2)
pipeline = VideoPipeline()
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


def render(request: Request, template_name: str, **context):
    user = context.pop("user", None)
    if user is None:
        with SessionLocal() as db:
            user = current_user(request, db)
    can_access_admin = False
    if user:
        with SessionLocal() as db:
            admin_count = db.execute(select(func.count()).select_from(AppUser).where(AppUser.role == "admin")).scalar_one()
            can_access_admin = user.role == "admin" or admin_count == 0
    context.update(
        {
            "request": request,
            "user": user,
            "settings": settings,
            "format_dt": format_dt,
            "json_dumps": json.dumps,
            "page_notice": request.query_params.get("notice", ""),
            "page_notice_type": request.query_params.get("notice_type", "success"),
            "page_focus": request.query_params.get("focus", ""),
            "can_access_admin": can_access_admin,
            "label_status": label_status,
            "label_platform": label_platform,
            "label_avatar_mode": label_avatar_mode,
            "label_voice_provider": label_voice_provider,
            "label_publish_adapter": label_publish_adapter,
            "label_role": label_role,
        }
    )
    return templates.TemplateResponse(template_name, context)


def _auth_redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=303)


def _notice_redirect(path: str, notice: str, notice_type: str = "success", focus: str = "") -> RedirectResponse:
    query = urlencode({"notice": notice, "notice_type": notice_type, "focus": focus})
    return _auth_redirect(f"{path}?{query}")


def _silent_wav(path: Path, seconds: float = 0.4, sample_rate: int = 16000) -> None:
    frames = max(1, int(seconds * sample_rate))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frames)


def _normalize_extra_json(raw: str) -> dict:
    try:
        return json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if user:
        return _auth_redirect("/dashboard")
    return render(
        request,
        "index.html",
        stats={
            "paid_apis": ["Monica API", "HeyGen", "OpenAI Whisper"],
            "open_source": ["CosyVoice", "FFmpeg", "MultiPost"],
        },
    )


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return render(request, "register.html")


@app.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    display_name: str = Form(""),
    db: Session = Depends(get_db),
):
    if get_user_by_email(db, email):
        return render(request, "register.html", error="Email already exists.")
    admin_exists = db.execute(select(func.count()).select_from(AppUser).where(AppUser.role == "admin")).scalar_one() > 0
    user = create_user(db, email=email, password=password, display_name=display_name, role="member" if admin_exists else "admin")
    db.commit()
    sign_in(request, user.id)
    return _auth_redirect("/dashboard")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render(request, "login.html")


@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, email=email, password=password)
    if not user:
        return render(request, "login.html", error="Invalid email or password.")
    sign_in(request, user.id)
    return _auth_redirect("/dashboard")


@app.post("/logout")
def logout(request: Request):
    sign_out(request)
    return _auth_redirect("/")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    projects = list_projects(db, user.id)
    jobs = list_jobs(db, user.id)[:8]
    integrations = list_integrations(db, user.id)
    return render(
        request,
        "dashboard.html",
        user=user,
        projects=projects,
        jobs=jobs,
        integrations=integrations,
    )


@app.get("/publish-jobs", response_class=HTMLResponse)
def publish_jobs_page(request: Request, status: str = "all", db: Session = Depends(get_db)):
    user = require_user(request, db)
    publish_jobs = list_publish_jobs(db, user.id, status=status, limit=100)
    items = []
    for publish_job in publish_jobs:
        job = db.get(VideoJob, publish_job.job_id)
        target = db.get(PublishTarget, publish_job.target_id)
        items.append({"publish_job": publish_job, "job": job, "target": target})
    failed_count = len(list_publish_jobs(db, user.id, status="failed", limit=1000))
    return render(
        request,
        "publish_jobs.html",
        user=user,
        items=items,
        status=status,
        failed_count=failed_count,
    )


@app.get("/projects/new", response_class=HTMLResponse)
def project_new_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    return render(request, "project_form.html", user=user, project=None)


@app.post("/projects/new")
def project_new(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    reference_url: str = Form(""),
    niche: str = Form(""),
    target_platforms: str = Form("douyin,xiaohongshu,bilibili,youtube,tiktok"),
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    platforms = [p.strip() for p in target_platforms.split(",") if p.strip()]
    project = create_project(
        db,
        owner_id=user.id,
        name=name,
        description=description,
        reference_url=reference_url,
        niche=niche,
        target_platforms=platforms,
    )
    db.commit()
    return _auth_redirect(f"/projects/{project.id}")


@app.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(request: Request, project_id: str, db: Session = Depends(get_db)):
    user = require_user(request, db)
    project = get_project(db, user.id, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    jobs = list_jobs(db, user.id, project.id)
    targets = list_publish_targets(db, user.id, project.id)
    return render(
        request,
        "project_detail.html",
        user=user,
        project=project,
        jobs=jobs,
        targets=targets,
    )


@app.post("/projects/{project_id}/targets")
def project_create_target(
    request: Request,
    project_id: str,
    platform: str = Form(...),
    handle: str = Form(""),
    adapter: str = Form("social-auto-upload"),
    settings_json: str = Form("{}"),
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    project = get_project(db, user.id, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        extra_settings = json.loads(settings_json or "{}")
    except json.JSONDecodeError:
        extra_settings = {}
    extra_settings["adapter"] = adapter
    upsert_publish_target(
        db,
        owner_id=user.id,
        project_id=project.id,
        platform=platform,
        handle=handle,
        publish_mode="auto",
        settings=extra_settings,
        auth_payload={},
        is_enabled=True,
    )
    db.commit()
    return _auth_redirect(f"/projects/{project.id}")


@app.post("/projects/{project_id}/jobs")
def project_create_job(
    request: Request,
    project_id: str,
    topic: str = Form(...),
    reference_url: str = Form(""),
    avatar_mode: str = Form("cosyvoice"),
    voice_provider: str = Form("deepseek"),
    render_ratio: str = Form("9:16"),
    auto_start: str = Form("1"),
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    project = get_project(db, user.id, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    reference = None
    if reference_url.strip() or project.reference_url.strip():
        reference = create_reference_video(
            db,
            owner_id=user.id,
            project_id=project.id,
            reference_url=reference_url.strip() or project.reference_url.strip(),
            source_title=project.name,
            source_platform="manual",
            duration_sec=60,
            transcript_text=project.description or topic,
            hook_summary=project.description or topic,
            style_notes="Manual reference captured from project or form.",
            analysis_payload={"manual": True},
        )

    job = create_job(
        db,
        owner_id=user.id,
        project_id=project.id,
        reference_id=reference.id if reference else None,
        topic=topic,
        title="",
        avatar_mode=avatar_mode,
        voice_provider=voice_provider,
        render_ratio=render_ratio,
    )
    db.commit()

    if auto_start == "1":
        executor.submit(pipeline.run, job.id)
    return _auth_redirect(f"/jobs/{job.id}")


@app.get("/jobs/{job_id}", response_class=HTMLResponse)
def job_detail(request: Request, job_id: str, db: Session = Depends(get_db)):
    user = require_user(request, db)
    job = get_job(db, user.id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    steps = get_job_steps(db, job.id)
    project = get_project(db, user.id, job.project_id)
    return render(
        request,
        "job_detail.html",
        user=user,
        job=job,
        steps=steps,
        project=project,
        publish_bundle_json=json.dumps(job.publish_bundle or {}, ensure_ascii=False, indent=2),
    )


@app.post("/jobs/{job_id}/run")
def job_run(request: Request, job_id: str, db: Session = Depends(get_db)):
    user = require_user(request, db)
    job = get_job(db, user.id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    executor.submit(pipeline.run, job.id)
    return _auth_redirect(f"/jobs/{job.id}")


@app.get("/jobs/{job_id}/download")
def job_download(request: Request, job_id: str, db: Session = Depends(get_db)):
    user = require_user(request, db)
    job = get_job(db, user.id, job_id)
    if not job or not job.output_path:
        raise HTTPException(status_code=404, detail="Video not ready")
    return FileResponse(job.output_path, filename=Path(job.output_path).name)


@app.get("/jobs/{job_id}/preview-image")
def job_preview_image(request: Request, job_id: str, db: Session = Depends(get_db)):
    user = require_user(request, db)
    job = get_job(db, user.id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    candidate = job.thumbnail_url or str((job.pipeline_state or {}).get("heygen_preview_image", ""))
    if candidate and Path(candidate).exists():
        return FileResponse(candidate, filename=Path(candidate).name)
    if job.output_path and Path(job.output_path).exists():
        return FileResponse(job.output_path, filename=Path(job.output_path).name)
    raise HTTPException(status_code=404, detail="Preview not ready")


@app.get("/api/jobs/{job_id}/status")
def job_status(request: Request, job_id: str, db: Session = Depends(get_db)):
    user = require_user(request, db)
    job = get_job(db, user.id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "status": job.status,
        "progress": job.progress,
        "title": job.title,
        "output_path": job.output_path,
        "thumbnail_url": job.thumbnail_url,
        "updated_at": format_dt(job.updated_at),
    }


@app.post("/publish-jobs/{publish_job_id}/retry")
def publish_job_retry(request: Request, publish_job_id: str, db: Session = Depends(get_db)):
    user = require_user(request, db)
    publish_job = get_publish_job(db, user.id, publish_job_id)
    if not publish_job:
        raise HTTPException(status_code=404, detail="Publish job not found")
    publish_job.status = "queued"
    publish_job.error = ""
    db.commit()

    def _retry() -> None:
        with SessionLocal() as retry_db:
            retry_pj = get_publish_job(retry_db, user.id, publish_job_id)
            if not retry_pj:
                return
            pipeline.retry_publish_job(retry_db, retry_pj)

    executor.submit(_retry)
    return _auth_redirect("/publish-jobs?status=failed")


def _admin_access_allowed(db: Session, user: AppUser) -> bool:
    admin_count = db.execute(select(func.count()).select_from(AppUser).where(AppUser.role == "admin")).scalar_one()
    return user.role == "admin" or admin_count == 0


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not _admin_access_allowed(db, user):
        return _auth_redirect("/dashboard")
    return _auth_redirect("/admin/api-config")


@app.get("/admin/api-config", response_class=HTMLResponse)
def admin_api_config_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not _admin_access_allowed(db, user):
        return _auth_redirect("/dashboard")
    integrations = {item.provider: item for item in list_integrations(db, user.id)}
    sections = []
    for item in API_CONFIG_SECTIONS:
        current = integrations.get(item["provider"])
        sections.append(
            {
                **item,
                "current": current,
                "extra_json": json.dumps((current.settings if current else item["extra_defaults"]) or {}, ensure_ascii=False, indent=2),
            }
        )
    return render(
        request,
        "settings.html",
        user=user,
        integrations=integrations,
        api_sections=sections,
    )


def _resolve_api_section(db: Session, user: AppUser, provider: str, api_key: str, base_url: str, model: str, extra_json: str) -> dict:
    current = get_integration(db, user.id, provider)
    current_settings = current.settings if current else {}
    extra_settings = _normalize_extra_json(extra_json) if extra_json.strip() else current_settings
    return {
        "provider": provider,
        "api_key": api_key.strip() or (current.api_key_enc if current else ""),
        "base_url": base_url.strip() or (current.base_url if current else ""),
        "model": model.strip() or (current.model if current else ""),
        "extra_settings": extra_settings or current_settings or {},
    }


@app.post("/admin/api-config")
def admin_api_config_save(
    request: Request,
    provider: str = Form(...),
    api_key: str = Form(""),
    base_url: str = Form(""),
    model: str = Form(""),
    extra_json: str = Form("{}"),
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    if not _admin_access_allowed(db, user):
        return _auth_redirect("/dashboard")
    section = _resolve_api_section(db, user, provider, api_key, base_url, model, extra_json)
    upsert_integration(
        db,
        owner_id=user.id,
        provider=provider,
        api_key_enc=section["api_key"],
        base_url=section["base_url"],
        model=section["model"],
        settings=section["extra_settings"],
        is_active=True,
    )
    db.commit()
    return _notice_redirect("/admin/api-config", f"已保存 {provider} 配置", "success", provider)


@app.post("/admin/api-config/test")
def admin_api_config_test(
    request: Request,
    provider: str = Form(...),
    api_key: str = Form(""),
    base_url: str = Form(""),
    model: str = Form(""),
    extra_json: str = Form("{}"),
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    if not _admin_access_allowed(db, user):
        return _auth_redirect("/dashboard")
    section = _resolve_api_section(db, user, provider, api_key, base_url, model, extra_json)
    if not section["api_key"]:
        return _notice_redirect("/admin/api-config", f"{provider} 还没有 API key，先保存后再测试。", "error", provider)

    try:
        result = asyncio.run(_test_api_section(section))
    except Exception as exc:
        return _notice_redirect("/admin/api-config", f"{provider} 测试失败：{exc}", "error", provider)
    return _notice_redirect("/admin/api-config", result, "success", provider)


async def _test_api_section(section: dict) -> str:
    provider = section["provider"]
    api_key = section["api_key"]
    base_url = section["base_url"] or ""
    model = section["model"] or ""
    extra_settings = section["extra_settings"] or {}

    if provider == "monica":
        client = MonicaClient(api_key=api_key, base_url=base_url or "https://openapi.monica.im/v1")
        text_result = await client.test_chat(model=model or "gpt-4o")
        image_model = str(extra_settings.get("image_model") or "dall-e-3").strip() or "dall-e-3"
        image_size = "1024x1792"
        image_result = await client.generate_image(
            prompt="生成一张适合短视频封面的科技风背景图，画面要有强烈对比和留白，中文内容留出空间。",
            model=image_model,
            size=image_size,
        )
        return f"Monica 连通成功，聊天返回：{text_result.text[:30]}；图像模型返回正常。"

    if provider == "deepseek":
        client = MonicaClient(api_key=api_key, base_url=base_url or "https://api.deepseek.com")
        text_result = await client.chat_completion("Reply with a single word: ok", model=model or "deepseek-chat")
        return f"DeepSeek 连通成功：{text_result.text[:30]}"

    if provider == "volcengine":
        volc_chat = VolcArkClient(api_key=api_key, base_url=base_url or "https://ark.cn-beijing.volces.com/api/v3", model=model or "doubao-seed-2.0-lite")
        chat_result = await volc_chat.test_chat(model=model or "doubao-seed-2.0-lite")
        extra_image_model = str(extra_settings.get("image_model") or "doubao-seedream-5.0-lite").strip() or "doubao-seedream-5.0-lite"
        image_result_text = "未测试图像"
        try:
            image_result = await volc_chat.generate_image(
                prompt="生成一张适合短视频封面的科技风背景图，画面要有强烈对比和留白，中文内容留出空间。",
                model=extra_image_model,
                size=str(extra_settings.get("image_size") or "1024x1024").strip() or "1024x1024",
                style=str(extra_settings.get("image_style") or "vivid").strip() or "vivid",
                quality=str(extra_settings.get("image_quality") or "standard").strip() or "standard",
            )
            image_result_text = f"图像模型返回正常：{image_result.model}"
        except Exception as exc:
            image_result_text = f"图像模型测试跳过：{exc}"
        speech_info = ""
        tts_app_id = str(extra_settings.get("tts_app_id") or "").strip()
        tts_access_key = str(extra_settings.get("tts_access_key") or "").strip()
        tts_resource_id = str(extra_settings.get("tts_resource_id") or "volc.service_type.10029").strip()
        tts_speaker = str(extra_settings.get("tts_speaker") or "").strip()
        if tts_app_id and tts_access_key and tts_speaker:
            speech = VolcSpeechClient(
                app_id=tts_app_id,
                access_key=tts_access_key,
                resource_id=tts_resource_id,
                speaker=tts_speaker,
                model=str(extra_settings.get("tts_model") or "seed-tts-2.0-standard").strip() or "seed-tts-2.0-standard",
                output_format=str(extra_settings.get("tts_output_format") or "mp3").strip() or "mp3",
                sample_rate=int(extra_settings.get("tts_sample_rate") or 24000),
            )
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_path = Path(tmp_file.name)
            try:
                result = speech.synthesize("火山引擎联通测试，正在生成一段语音。", tmp_path)
                speech_info = f"；语音合成返回正常：{result.task_id}"
            finally:
                try:
                    tmp_path.unlink(missing_ok=True)
                except Exception:
                    pass
        else:
            speech_info = "；语音合成未配置 App ID / Access Key / Speaker，已跳过"
        return f"火山方舟连通成功，聊天返回：{chat_result.title[:20]}；{image_result_text}{speech_info}"

    if provider == "openai":
        from .services.whisper import WhisperClient

        client = WhisperClient(api_key=api_key, base_url=base_url or None, model=model or None)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_path = Path(tmp_file.name)
        try:
            _silent_wav(tmp_path)
            transcript = await client.transcribe_file(tmp_path, prompt="连接测试")
            return f"OpenAI Whisper 连通成功：{transcript.text[:30] or '已返回结果'}"
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

    if provider == "heygen":
        from .services.heygen import HeyGenClient

        client = HeyGenClient(api_key=api_key, base_url=base_url or None)
        voices = await client.list_voices()
        return "HeyGen 连通测试已通过。"

    if provider == "multipost":
        import httpx

        if not base_url:
            raise RuntimeError("请先填写 MultiPost 基础地址")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(base_url, headers=headers)
            if resp.status_code >= 500:
                resp.raise_for_status()
        return f"MultiPost 基础地址可达，当前返回状态码 {resp.status_code}。"

    raise RuntimeError(f"不支持的 provider: {provider}")


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not _admin_access_allowed(db, user):
        return _auth_redirect("/dashboard")
    return _auth_redirect("/admin/api-config")


@app.get("/healthz")
def healthz():
    return {"ok": True, "name": settings.app_name}
