from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .models import (
    AppUser,
    Integration,
    JobStep,
    Project,
    PublishJob,
    PublishTarget,
    ReferenceVideo,
    VideoJob,
)
from .security import hash_password, verify_password


def normalize_email(email: str) -> str:
    return email.strip().lower()


def create_user(db: Session, email: str, password: str, display_name: str = "") -> AppUser:
    user = AppUser(
        email=normalize_email(email),
        password_hash=hash_password(password),
        display_name=display_name.strip() or normalize_email(email).split("@", 1)[0],
    )
    db.add(user)
    db.flush()
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[AppUser]:
    user = get_user_by_email(db, email)
    if user and verify_password(password, user.password_hash):
        return user
    return None


def get_user_by_email(db: Session, email: str) -> Optional[AppUser]:
    return db.execute(select(AppUser).where(AppUser.email == normalize_email(email))).scalar_one_or_none()


def get_user(db: Session, user_id: str) -> Optional[AppUser]:
    return db.get(AppUser, user_id)


def list_projects(db: Session, owner_id: str) -> List[Project]:
    stmt = select(Project).where(Project.owner_id == owner_id).order_by(desc(Project.created_at))
    return list(db.execute(stmt).scalars().all())


def create_project(
    db: Session,
    owner_id: str,
    name: str,
    description: str,
    reference_url: str = "",
    niche: str = "",
    target_platforms: Optional[list] = None,
) -> Project:
    project = Project(
        owner_id=owner_id,
        name=name.strip(),
        description=description.strip(),
        reference_url=reference_url.strip(),
        niche=niche.strip(),
        target_platforms=target_platforms or ["douyin", "xiaohongshu", "bilibili", "youtube", "tiktok"],
    )
    db.add(project)
    db.flush()
    return project


def get_project(db: Session, owner_id: str, project_id: str) -> Optional[Project]:
    stmt = select(Project).where(Project.id == project_id, Project.owner_id == owner_id)
    return db.execute(stmt).scalar_one_or_none()


def create_reference_video(
    db: Session,
    owner_id: str,
    project_id: str,
    reference_url: str,
    source_title: str = "",
    source_platform: str = "",
    duration_sec: int = 0,
    transcript_text: str = "",
    transcript_json: Optional[list] = None,
    hook_summary: str = "",
    style_notes: str = "",
    analysis_payload: Optional[dict] = None,
) -> ReferenceVideo:
    ref = ReferenceVideo(
        owner_id=owner_id,
        project_id=project_id,
        reference_url=reference_url.strip(),
        source_title=source_title.strip(),
        source_platform=source_platform.strip(),
        duration_sec=duration_sec,
        transcript_text=transcript_text,
        transcript_json=transcript_json or [],
        hook_summary=hook_summary,
        style_notes=style_notes,
        analysis_payload=analysis_payload or {},
    )
    db.add(ref)
    db.flush()
    return ref


def create_job(
    db: Session,
    owner_id: str,
    project_id: str,
    reference_id: Optional[str],
    topic: str,
    title: str = "",
    avatar_mode: str = "cosyvoice",
    voice_provider: str = "deepseek",
    render_ratio: str = "9:16",
) -> VideoJob:
    job = VideoJob(
        owner_id=owner_id,
        project_id=project_id,
        reference_id=reference_id,
        topic=topic.strip(),
        title=title.strip(),
        avatar_mode=avatar_mode,
        voice_provider=voice_provider,
        render_ratio=render_ratio,
    )
    db.add(job)
    db.flush()
    return job


def get_job(db: Session, owner_id: str, job_id: str) -> Optional[VideoJob]:
    stmt = select(VideoJob).where(VideoJob.id == job_id, VideoJob.owner_id == owner_id)
    return db.execute(stmt).scalar_one_or_none()


def list_jobs(db: Session, owner_id: str, project_id: Optional[str] = None) -> List[VideoJob]:
    stmt = select(VideoJob).where(VideoJob.owner_id == owner_id)
    if project_id:
        stmt = stmt.where(VideoJob.project_id == project_id)
    stmt = stmt.order_by(desc(VideoJob.created_at))
    return list(db.execute(stmt).scalars().all())


def add_job_step(db: Session, job_id: str, step_key: str, status: str = "queued", detail: Optional[dict] = None) -> JobStep:
    step = JobStep(job_id=job_id, step_key=step_key, status=status, detail=detail or {})
    db.add(step)
    db.flush()
    return step


def get_job_steps(db: Session, job_id: str) -> List[JobStep]:
    stmt = select(JobStep).where(JobStep.job_id == job_id).order_by(JobStep.created_at.asc())
    return list(db.execute(stmt).scalars().all())


def create_integration(
    db: Session,
    owner_id: str,
    provider: str,
    api_key_enc: str = "",
    base_url: str = "",
    model: str = "",
    settings: Optional[dict] = None,
    is_active: bool = True,
) -> Integration:
    integration = Integration(
        owner_id=owner_id,
        provider=provider,
        api_key_enc=api_key_enc,
        base_url=base_url,
        model=model,
        settings=settings or {},
        is_active=is_active,
    )
    db.add(integration)
    db.flush()
    return integration


def upsert_integration(
    db: Session,
    owner_id: str,
    provider: str,
    api_key_enc: str = "",
    base_url: str = "",
    model: str = "",
    settings: Optional[dict] = None,
    is_active: bool = True,
) -> Integration:
    integration = get_integration(db, owner_id, provider)
    if integration is None:
        return create_integration(
            db,
            owner_id=owner_id,
            provider=provider,
            api_key_enc=api_key_enc,
            base_url=base_url,
            model=model,
            settings=settings,
            is_active=is_active,
        )
    integration.api_key_enc = api_key_enc
    integration.base_url = base_url
    integration.model = model
    integration.settings = settings or {}
    integration.is_active = is_active
    db.flush()
    return integration


def list_integrations(db: Session, owner_id: str) -> List[Integration]:
    stmt = select(Integration).where(Integration.owner_id == owner_id).order_by(desc(Integration.created_at))
    return list(db.execute(stmt).scalars().all())


def get_integration(db: Session, owner_id: str, provider: str) -> Optional[Integration]:
    stmt = select(Integration).where(Integration.owner_id == owner_id, Integration.provider == provider).order_by(desc(Integration.created_at))
    return db.execute(stmt).scalar_one_or_none()


def list_publish_targets(db: Session, owner_id: str, project_id: Optional[str] = None) -> List[PublishTarget]:
    stmt = select(PublishTarget).where(PublishTarget.owner_id == owner_id)
    if project_id:
        stmt = stmt.where(PublishTarget.project_id == project_id)
    stmt = stmt.order_by(desc(PublishTarget.created_at))
    return list(db.execute(stmt).scalars().all())


def list_publish_jobs(
    db: Session,
    owner_id: str,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[PublishJob]:
    stmt = (
        select(PublishJob)
        .join(VideoJob, PublishJob.job_id == VideoJob.id)
        .where(VideoJob.owner_id == owner_id)
        .order_by(desc(PublishJob.created_at))
        .limit(limit)
    )
    if status and status != "all":
        stmt = stmt.where(PublishJob.status == status)
    return list(db.execute(stmt).scalars().all())


def get_publish_job(db: Session, owner_id: str, publish_job_id: str) -> Optional[PublishJob]:
    stmt = (
        select(PublishJob)
        .join(VideoJob, PublishJob.job_id == VideoJob.id)
        .where(PublishJob.id == publish_job_id, VideoJob.owner_id == owner_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def upsert_publish_target(
    db: Session,
    owner_id: str,
    platform: str,
    handle: str = "",
    project_id: Optional[str] = None,
    publish_mode: str = "manual",
    settings: Optional[dict] = None,
    auth_payload: Optional[dict] = None,
    is_enabled: bool = True,
) -> PublishTarget:
    stmt = select(PublishTarget).where(
        PublishTarget.owner_id == owner_id,
        PublishTarget.platform == platform,
        PublishTarget.handle == handle,
        PublishTarget.project_id == project_id,
    )
    target = db.execute(stmt).scalar_one_or_none()
    if target is None:
        target = PublishTarget(
            owner_id=owner_id,
            project_id=project_id,
            platform=platform,
            handle=handle,
            publish_mode=publish_mode,
            settings=settings or {},
            auth_payload=auth_payload or {},
            is_enabled=is_enabled,
        )
        db.add(target)
    else:
        target.publish_mode = publish_mode
        target.settings = settings or {}
        target.auth_payload = auth_payload or {}
        target.is_enabled = is_enabled
    db.flush()
    return target


def create_publish_job(db: Session, job_id: str, target_id: str, status: str = "queued", payload: Optional[dict] = None) -> PublishJob:
    pj = PublishJob(job_id=job_id, target_id=target_id, status=status, payload=payload or {})
    db.add(pj)
    db.flush()
    return pj
