from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import relationship

from .db import Base


def uuid_str() -> str:
    return str(uuid.uuid4())


JSONType = JSON


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class AppUser(Base, TimestampMixin):
    __tablename__ = "app_users"

    id = Column(String(36), primary_key=True, default=uuid_str)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(120), nullable=False, default="")
    avatar_url = Column(String(512), nullable=False, default="")
    role = Column(String(32), nullable=False, default="member")
    status = Column(String(32), nullable=False, default="active")
    plan = Column(String(32), nullable=False, default="starter")

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="owner", cascade="all, delete-orphan")


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=uuid_str)
    owner_id = Column(String(36), ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(140), nullable=False)
    description = Column(Text, nullable=False, default="")
    reference_url = Column(Text, nullable=False, default="")
    niche = Column(String(120), nullable=False, default="")
    status = Column(String(32), nullable=False, default="active")
    target_platforms = Column(JSONType, nullable=False, default=list)
    default_avatar_mode = Column(String(32), nullable=False, default="cosyvoice")
    default_voice_provider = Column(String(32), nullable=False, default="deepseek")
    settings = Column(JSONType, nullable=False, default=dict)

    owner = relationship("AppUser", back_populates="projects")
    references = relationship("ReferenceVideo", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("VideoJob", back_populates="project", cascade="all, delete-orphan")


class ReferenceVideo(Base, TimestampMixin):
    __tablename__ = "reference_videos"

    id = Column(String(36), primary_key=True, default=uuid_str)
    owner_id = Column(String(36), ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    reference_url = Column(Text, nullable=False)
    source_title = Column(String(255), nullable=False, default="")
    source_platform = Column(String(64), nullable=False, default="")
    duration_sec = Column(Integer, nullable=False, default=0)
    transcript_text = Column(Text, nullable=False, default="")
    transcript_json = Column(JSONType, nullable=False, default=list)
    hook_summary = Column(Text, nullable=False, default="")
    style_notes = Column(Text, nullable=False, default="")
    analysis_payload = Column(JSONType, nullable=False, default=dict)
    status = Column(String(32), nullable=False, default="draft")

    project = relationship("Project", back_populates="references")


class VideoJob(Base, TimestampMixin):
    __tablename__ = "video_jobs"

    id = Column(String(36), primary_key=True, default=uuid_str)
    owner_id = Column(String(36), ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    reference_id = Column(String(36), ForeignKey("reference_videos.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="queued")
    topic = Column(String(255), nullable=False, default="")
    title = Column(String(255), nullable=False, default="")
    script_text = Column(Text, nullable=False, default="")
    script_json = Column(JSONType, nullable=False, default=dict)
    avatar_mode = Column(String(32), nullable=False, default="cosyvoice")
    voice_provider = Column(String(32), nullable=False, default="deepseek")
    render_ratio = Column(String(16), nullable=False, default="9:16")
    output_path = Column(Text, nullable=False, default="")
    output_url = Column(Text, nullable=False, default="")
    thumbnail_url = Column(Text, nullable=False, default="")
    error = Column(Text, nullable=False, default="")
    progress = Column(Integer, nullable=False, default=0)
    pipeline_state = Column(JSONType, nullable=False, default=dict)
    publish_bundle = Column(JSONType, nullable=False, default=dict)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="jobs")
    steps = relationship("JobStep", back_populates="job", cascade="all, delete-orphan")


class JobStep(Base, TimestampMixin):
    __tablename__ = "job_steps"

    id = Column(String(36), primary_key=True, default=uuid_str)
    job_id = Column(String(36), ForeignKey("video_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_key = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="queued")
    detail = Column(JSONType, nullable=False, default=dict)
    error = Column(Text, nullable=False, default="")
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    job = relationship("VideoJob", back_populates="steps")


class Integration(Base, TimestampMixin):
    __tablename__ = "integrations"

    id = Column(String(36), primary_key=True, default=uuid_str)
    owner_id = Column(String(36), ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(64), nullable=False)
    api_key_enc = Column(Text, nullable=False, default="")
    base_url = Column(Text, nullable=False, default="")
    model = Column(String(128), nullable=False, default="")
    settings = Column(JSONType, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)

    owner = relationship("AppUser", back_populates="integrations")


class PublishTarget(Base, TimestampMixin):
    __tablename__ = "publish_targets"

    id = Column(String(36), primary_key=True, default=uuid_str)
    owner_id = Column(String(36), ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    platform = Column(String(64), nullable=False)
    handle = Column(String(128), nullable=False, default="")
    publish_mode = Column(String(32), nullable=False, default="manual")
    settings = Column(JSONType, nullable=False, default=dict)
    auth_payload = Column(JSONType, nullable=False, default=dict)
    is_enabled = Column(Boolean, nullable=False, default=True)


class PublishJob(Base, TimestampMixin):
    __tablename__ = "publish_jobs"

    id = Column(String(36), primary_key=True, default=uuid_str)
    job_id = Column(String(36), ForeignKey("video_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(String(36), ForeignKey("publish_targets.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="queued")
    remote_id = Column(String(255), nullable=False, default="")
    remote_url = Column(Text, nullable=False, default="")
    error = Column(Text, nullable=False, default="")
    payload = Column(JSONType, nullable=False, default=dict)
