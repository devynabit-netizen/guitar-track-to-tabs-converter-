"""Persistent models for projects and note versions."""
from datetime import datetime
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    audio_path: Mapped[str] = mapped_column(String(512), nullable=False)
    tuning: Mapped[list[str]] = mapped_column(JSON, default=["E2", "A2", "D3", "G3", "B3", "E4"])
    tempo_bpm: Mapped[float] = mapped_column(default=120.0)
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False)
    progress: Mapped[float] = mapped_column(default=0.2, nullable=False)
    current_phase: Mapped[int] = mapped_column(default=1, nullable=False)
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions: Mapped[list["TabVersion"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class TabVersion(Base):
    __tablename__ = "tab_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    notes_raw: Mapped[list[dict]] = mapped_column(JSON, default=list)
    notes_mapped: Mapped[list[dict]] = mapped_column(JSON, default=list)
    tab_ascii: Mapped[str] = mapped_column(String, default="")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped[Project] = relationship(back_populates="versions")
