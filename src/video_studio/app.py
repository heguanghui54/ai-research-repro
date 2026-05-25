from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from fastapi import BackgroundTasks, Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, select
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
from .utils import format_dt


app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax")
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
templates = Jinja2Templates(directory=str(settings.template_dir))
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
    context.update(
        {
            "request": request,
            "user": user,
            "settings": settings,
            "format_dt": format_dt,
            "json_dumps": json.dumps,
        }
    )
    return templates.TemplateResponse(template_name, context)


def _auth_redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=303)


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if user:
        return _auth_redirect("/dashboard")
    return render(
        request,
        "index.html",
        stats={
            "paid_apis": ["HeyGen", "OpenAI Whisper", "DeepSeek"],
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
    user = create_user(db, email=email, password=password, display_name=display_name)
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


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    integrations = {item.provider: item for item in list_integrations(db, user.id)}
    return render(
        request,
        "settings.html",
        user=user,
        integrations=integrations,
    )


@app.post("/settings/integrations")
def settings_integrations(
    request: Request,
    provider: str = Form(...),
    api_key: str = Form(""),
    base_url: str = Form(""),
    model: str = Form(""),
    extra_json: str = Form("{}"),
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    try:
        extra_settings = json.loads(extra_json or "{}")
    except json.JSONDecodeError:
        extra_settings = {}
    upsert_integration(
        db,
        owner_id=user.id,
        provider=provider,
        api_key_enc=api_key,
        base_url=base_url,
        model=model,
        settings=extra_settings,
        is_active=True,
    )
    db.commit()
    return _auth_redirect("/settings")


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if user.role != "admin":
        return _auth_redirect("/dashboard")
    users = db.execute(select(AppUser).order_by(desc(AppUser.created_at))).scalars().all()
    return render(request, "dashboard.html", user=user, projects=[], jobs=[], integrations=[], admin_users=users)


@app.get("/healthz")
def healthz():
    return {"ok": True, "name": settings.app_name}
