from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
LIBRARY_DIR = DATA_DIR / "library"
APP_DB_PATH = DATA_DIR / "ai_scientist_web.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{APP_DB_PATH}",
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _derive_fernet_key() -> bytes:
    secret = os.getenv("APP_SECRET_KEY", "dev-secret-change-me").encode("utf-8")
    digest = hashlib.sha256(secret).digest()
    return base64.urlsafe_b64encode(digest)


_FERNET = Fernet(_derive_fernet_key())


def encrypt_text(value: str | None) -> str | None:
    if not value:
        return None
    return _FERNET.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_text(value: str | None) -> str | None:
    if not value:
        return None
    return _FERNET.decrypt(value.encode("utf-8")).decode("utf-8")


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"{base64.b64encode(salt).decode('utf-8')}${base64.b64encode(key).decode('utf-8')}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_b64, key_b64 = stored.split("$", 1)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(key_b64)
    except Exception:
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return secrets.compare_digest(actual, expected)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    projects: Mapped[List["Project"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    topic: Mapped[str] = mapped_column(Text)
    venue: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider_name: Mapped[str] = mapped_column(String(80), default="openai-compatible")
    api_base_url: Mapped[str] = mapped_column(String(255), default="https://api.openai.com/v1")
    model_name: Mapped[str] = mapped_column(String(120), default="gpt-4o-mini")
    api_key_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experiment_template: Mapped[str] = mapped_column(String(80), default="sandbox")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="projects")
    runs: Mapped[List["Run"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    parent_run_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    label: Mapped[str] = mapped_column(String(220))
    status: Mapped[str] = mapped_column(String(40), default="queued")
    current_stage: Mapped[str] = mapped_column(String(80), default="queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    pause_points: Mapped[List[str]] = mapped_column(JSON, default=list)
    user_notes: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    summary_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    config_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    paper_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    paper_markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_dir: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    project: Mapped[Project] = relationship(back_populates="runs")
    events: Mapped[list["RunEvent"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    artifacts: Mapped[List["Artifact"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class RunEvent(Base):
    __tablename__ = "run_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), index=True)
    seq: Mapped[int] = mapped_column(Integer, index=True)
    kind: Mapped[str] = mapped_column(String(120))
    stage: Mapped[str] = mapped_column(String(120), default="")
    title: Mapped[str] = mapped_column(String(240), default="")
    message: Mapped[str] = mapped_column(Text, default="")
    payload_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    run: Mapped[Run] = relationship(back_populates="events")


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), index=True)
    kind: Mapped[str] = mapped_column(String(80))
    label: Mapped[str] = mapped_column(String(220))
    file_name: Mapped[str] = mapped_column(String(240))
    mime_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    path: Mapped[str] = mapped_column(Text)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    run: Mapped[Run] = relationship(back_populates="artifacts")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def serialize_model(instance) -> Dict[str, Any]:
    if isinstance(instance, User):
        return {
            "id": instance.id,
            "username": instance.username,
            "email": instance.email,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
        }
    if isinstance(instance, Project):
        return {
            "id": instance.id,
            "name": instance.name,
            "topic": instance.topic,
            "venue": instance.venue,
            "description": instance.description,
            "provider_name": instance.provider_name,
            "api_base_url": instance.api_base_url,
            "model_name": instance.model_name,
            "experiment_template": instance.experiment_template,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
            "updated_at": instance.updated_at.isoformat() if instance.updated_at else None,
        }
    if isinstance(instance, Run):
        return {
            "id": instance.id,
            "project_id": instance.project_id,
            "parent_run_id": instance.parent_run_id,
            "label": instance.label,
            "status": instance.status,
            "current_stage": instance.current_stage,
            "progress": instance.progress,
            "pause_points": instance.pause_points or [],
            "user_notes": instance.user_notes or [],
            "summary_json": instance.summary_json or {},
            "config_json": instance.config_json or {},
            "paper_html": instance.paper_html,
            "paper_markdown": instance.paper_markdown,
            "pdf_path": instance.pdf_path,
            "output_dir": instance.output_dir,
            "error_text": instance.error_text,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
            "updated_at": instance.updated_at.isoformat() if instance.updated_at else None,
        }
    if isinstance(instance, RunEvent):
        return {
            "id": instance.id,
            "run_id": instance.run_id,
            "seq": instance.seq,
            "kind": instance.kind,
            "stage": instance.stage,
            "title": instance.title,
            "message": instance.message,
            "payload": instance.payload_json or {},
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
        }
    if isinstance(instance, Artifact):
        return {
            "id": instance.id,
            "run_id": instance.run_id,
            "kind": instance.kind,
            "label": instance.label,
            "file_name": instance.file_name,
            "mime_type": instance.mime_type,
            "path": instance.path,
            "size_bytes": instance.size_bytes,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
        }
    raise TypeError(f"Unsupported model type: {type(instance)!r}")
