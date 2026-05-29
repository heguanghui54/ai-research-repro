from __future__ import annotations

import asyncio
import json
import threading
from pathlib import Path
from typing import Any

from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .db import (
    APP_DB_PATH,
    Artifact,
    Project,
    Run,
    RunEvent,
    SessionLocal,
    User,
    decrypt_text,
    encrypt_text,
    hash_password,
    init_db,
    serialize_model,
    utcnow,
    verify_password,
)
from .pipeline import RUN_CONTROLLERS, RunControl, run_full_loop, slugify


PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"

app = FastAPI(title="AI Scientist-v2 Workspace", version="0.1.0")
app.add_middleware(SessionMiddleware, secret_key="dev-session-secret-change-me", same_site="lax")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _current_user(request: Request, db=None) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    owns_session = db is None
    db = db or SessionLocal()
    try:
        return db.get(User, int(user_id))
    finally:
        if owns_session:
            db.close()


def require_user(request: Request, db=Depends(_db)) -> User:
    user = _current_user(request, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    return user


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def root(request: Request, db=Depends(_db)):
    user = _current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db=Depends(_db)):
    user = _current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db=Depends(_db)):
    user = _current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": serialize_model(user),
            "db_path": str(APP_DB_PATH),
        },
    )


@app.get("/api/me")
def api_me(request: Request, db=Depends(_db)):
    user = _current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not logged in")
    return {"user": serialize_model(user)}


@app.post("/api/auth/register")
def api_register(payload: dict[str, Any] = Body(...), db=Depends(_db)):
    username = (payload.get("username") or "").strip()
    password = (payload.get("password") or "").strip()
    email = (payload.get("email") or "").strip() or None
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    if db.scalar(select(User).where(User.username == username)) is not None:
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(username=username, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user": serialize_model(user)}


@app.post("/api/auth/login")
def api_login(request: Request, payload: dict[str, Any] = Body(...), db=Depends(_db)):
    username = (payload.get("username") or "").strip()
    password = (payload.get("password") or "").strip()
    user = db.scalar(select(User).where(User.username == username))
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["user_id"] = user.id
    return {"user": serialize_model(user)}


@app.post("/api/auth/logout")
def api_logout(request: Request):
    request.session.clear()
    return {"ok": True}


@app.get("/api/projects")
def api_projects(user: User = Depends(require_user), db=Depends(_db)):
    projects = db.scalars(select(Project).where(Project.user_id == user.id).order_by(Project.created_at.desc())).all()
    return {"projects": [serialize_model(p) for p in projects]}


@app.post("/api/projects")
def api_create_project(payload: dict[str, Any] = Body(...), user: User = Depends(require_user), db=Depends(_db)):
    name = (payload.get("name") or "").strip()
    topic = (payload.get("topic") or "").strip()
    if not name or not topic:
        raise HTTPException(status_code=400, detail="Project name and topic are required")
    project = Project(
        user_id=user.id,
        name=name,
        topic=topic,
        venue=(payload.get("venue") or "").strip() or None,
        description=(payload.get("description") or "").strip() or None,
        provider_name=(payload.get("provider_name") or "openai-compatible").strip() or "openai-compatible",
        api_base_url=(payload.get("api_base_url") or "https://api.openai.com/v1").strip(),
        model_name=(payload.get("model_name") or "gpt-4o-mini").strip(),
        api_key_enc=encrypt_text((payload.get("api_key") or "").strip() or None),
        experiment_template=(payload.get("experiment_template") or "sandbox").strip() or "sandbox",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"project": serialize_model(project)}


@app.get("/api/projects/{project_id}")
def api_project(project_id: int, user: User = Depends(require_user), db=Depends(_db)):
    project = db.get(Project, project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    runs = (
        db.scalars(
            select(Run)
            .where(Run.project_id == project.id)
            .order_by(Run.created_at.desc())
        ).all()
    )
    return {
        "project": serialize_model(project),
        "runs": [serialize_model(run) for run in runs],
    }


@app.get("/api/history")
def api_history(user: User = Depends(require_user), db=Depends(_db)):
    runs = (
        db.scalars(
            select(Run)
            .join(Project, Project.id == Run.project_id)
            .where(Project.user_id == user.id)
            .order_by(Run.created_at.desc())
        ).all()
    )
    return {
        "runs": [serialize_model(run) for run in runs],
    }


@app.get("/api/library")
def api_library(user: User = Depends(require_user), db=Depends(_db)):
    artifacts = (
        db.scalars(
            select(Artifact)
            .join(Run, Run.id == Artifact.run_id)
            .join(Project, Project.id == Run.project_id)
            .where(Project.user_id == user.id)
            .order_by(Artifact.created_at.desc())
        ).all()
    )
    return {"artifacts": [serialize_model(artifact) for artifact in artifacts]}


def _spawn_run(project_id: int, run_id: int, pause_points: list[str]) -> None:
    control = RunControl(pause_points=set(pause_points))
    RUN_CONTROLLERS.register(run_id, control)

    def _worker() -> None:
        try:
            run_full_loop(run_id=run_id, session_factory=SessionLocal, emit=_emit_event, control=control)
        finally:
            RUN_CONTROLLERS.unregister(run_id)

    thread = threading.Thread(target=_worker, name=f"run-{run_id}", daemon=True)
    thread.start()


def _emit_event(session, run, **kwargs):
    from .pipeline import _emit

    return _emit(session, run, **kwargs)


@app.post("/api/projects/{project_id}/runs")
def api_start_run(
    project_id: int,
    payload: dict[str, Any] = Body(default={}),
    user: User = Depends(require_user),
    db=Depends(_db),
):
    project = db.get(Project, project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    label = (payload.get("label") or "").strip() or f"{project.name} run"
    pause_points = payload.get("pause_points") or ["ideation", "benchmark", "planning", "execution", "writing"]
    if payload.get("auto_continue"):
        pause_points = []
    run = Run(
        project_id=project.id,
        parent_run_id=payload.get("parent_run_id"),
        label=label,
        status="queued",
        current_stage="queued",
        progress=0,
        pause_points=list(pause_points),
        user_notes=[],
        config_json={
            "label": label,
            "pause_points": list(pause_points),
            "auto_continue": bool(payload.get("auto_continue")),
        },
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    output_dir = Path("data") / "runs" / f"{run.id:05d}-{slugify(label)}"
    output_dir.mkdir(parents=True, exist_ok=True)
    run.output_dir = str(output_dir)
    db.commit()
    _spawn_run(project.id, run.id, list(pause_points))
    return {"run": serialize_model(run)}


@app.post("/api/runs/{run_id}/resume")
def api_resume_run(run_id: int, user: User = Depends(require_user), db=Depends(_db)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    project = db.get(Project, run.project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    control = RUN_CONTROLLERS.get(run.id)
    if control is None:
        raise HTTPException(status_code=409, detail="Run is not currently waiting")
    control.resume()
    run.status = "running"
    db.commit()
    return {"ok": True, "run": serialize_model(run)}


@app.post("/api/runs/{run_id}/notes")
def api_add_note(run_id: int, payload: dict[str, Any] = Body(...), user: User = Depends(require_user), db=Depends(_db)):
    note = (payload.get("note") or "").strip()
    if not note:
        raise HTTPException(status_code=400, detail="Note is required")
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    project = db.get(Project, run.project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    notes = list(run.user_notes or [])
    notes.append({"note": note, "stage": run.current_stage, "created_at": utcnow().isoformat()})
    run.user_notes = notes
    db.commit()
    return {"ok": True, "notes": notes}


@app.post("/api/runs/{run_id}/clone")
def api_clone_run(run_id: int, user: User = Depends(require_user), db=Depends(_db)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    project = db.get(Project, run.project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    clone = Run(
        project_id=project.id,
        parent_run_id=run.id,
        label=f"{run.label} (rewind)",
        status="queued",
        current_stage="queued",
        progress=0,
        pause_points=list(run.pause_points or []),
        user_notes=list(run.user_notes or []),
        config_json=run.config_json or {},
    )
    db.add(clone)
    db.commit()
    db.refresh(clone)
    output_dir = Path("data") / "runs" / f"{clone.id:05d}-{slugify(clone.label)}"
    output_dir.mkdir(parents=True, exist_ok=True)
    clone.output_dir = str(output_dir)
    db.commit()
    _spawn_run(project.id, clone.id, list(clone.pause_points or []))
    return {"run": serialize_model(clone)}


@app.get("/api/runs/{run_id}")
def api_run(run_id: int, user: User = Depends(require_user), db=Depends(_db)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    project = db.get(Project, run.project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    events = db.scalars(select(RunEvent).where(RunEvent.run_id == run.id).order_by(RunEvent.seq.asc())).all()
    artifacts = db.scalars(select(Artifact).where(Artifact.run_id == run.id).order_by(Artifact.created_at.asc())).all()
    return {
        "run": serialize_model(run),
        "project": serialize_model(project),
        "events": [serialize_model(event) for event in events],
        "artifacts": [serialize_model(artifact) for artifact in artifacts],
    }


@app.get("/api/runs/{run_id}/events")
def api_run_events(run_id: int, after: int = 0, user: User = Depends(require_user), db=Depends(_db)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    project = db.get(Project, run.project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    events = db.scalars(
        select(RunEvent)
        .where(RunEvent.run_id == run.id, RunEvent.id > after)
        .order_by(RunEvent.id.asc())
    ).all()
    return {"events": [serialize_model(event) for event in events]}


@app.get("/api/runs/{run_id}/stream")
async def api_run_stream(run_id: int, user: User = Depends(require_user), db=Depends(_db)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    project = db.get(Project, run.project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Run not found")

    async def event_generator():
        last_id = 0
        while True:
            session = SessionLocal()
            try:
                fresh_run = session.get(Run, run.id)
                new_events = session.scalars(
                    select(RunEvent).where(RunEvent.run_id == run.id, RunEvent.id > last_id).order_by(RunEvent.id.asc())
                ).all()
                for event in new_events:
                    last_id = event.id
                    payload = json.dumps(serialize_model(event), ensure_ascii=False)
                    yield f"id: {event.id}\nevent: run-event\ndata: {payload}\n\n"
                if fresh_run and fresh_run.status in {"completed", "failed"} and not new_events:
                    yield f"event: run-final\ndata: {json.dumps({'status': fresh_run.status, 'progress': fresh_run.progress})}\n\n"
                    break
            finally:
                session.close()
            await asyncio.sleep(1.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/runs/{run_id}/pdf")
def api_run_pdf(run_id: int, user: User = Depends(require_user), db=Depends(_db)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    project = db.get(Project, run.project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    if not run.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not available")
    return Response(Path(run.pdf_path).read_bytes(), media_type="application/pdf")


@app.get("/api/artifacts/{artifact_id}/download")
def api_download_artifact(artifact_id: int, user: User = Depends(require_user), db=Depends(_db)):
    artifact = db.get(Artifact, artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    run = db.get(Run, artifact.run_id)
    project = db.get(Project, run.project_id) if run else None
    if run is None or project is None or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Artifact not found")
    path = Path(artifact.path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact file missing")
    return Response(path.read_bytes(), media_type=artifact.mime_type, headers={"Content-Disposition": f'attachment; filename="{artifact.file_name}"'})


@app.get("/api/runs/{run_id}/paper-html", response_class=HTMLResponse)
def api_run_paper_html(run_id: int, user: User = Depends(require_user), db=Depends(_db)):
    run = db.get(Run, run_id)
    if run is None or not run.paper_html:
        raise HTTPException(status_code=404, detail="Paper not available")
    project = db.get(Project, run.project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Paper not available")
    return HTMLResponse(run.paper_html)


def main() -> None:
    import uvicorn

    uvicorn.run("ai_research_repro.webapp.app:app", host="127.0.0.1", port=8000, reload=False)
