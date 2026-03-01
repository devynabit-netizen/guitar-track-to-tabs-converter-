"""Project domain service orchestrating transcription pipeline."""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, TabVersion
from app.schemas.transcription import MappedNote
from app.services.fretboard_mapper import FretboardMapper
from app.services.tab_formatter import TabFormatter
from app.ml.transcriber import TranscriptionService


class ProjectService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.transcriber = TranscriptionService()

    def create_project(self, name: str, audio_path: str, tuning: list[str] | None = None) -> Project:
        project = Project(name=name, audio_path=audio_path, tuning=tuning or ["E2", "A2", "D3", "G3", "B3", "E4"])
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def process_project(self, project_id: int) -> TabVersion:
        project = self.db.get(Project, project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        raw_notes = self.transcriber.transcribe(project.audio_path)
        mapper = FretboardMapper(project.tuning)
        mapped: list[MappedNote] = mapper.map_notes(raw_notes)
        formatter = TabFormatter(project.tempo_bpm)
        mapped_quantized = formatter.quantize(mapped)
        ascii_tab = formatter.to_ascii(mapped_quantized)

        next_version = len(project.versions) + 1
        version = TabVersion(
            project_id=project.id,
            version=next_version,
            notes_raw=[n.model_dump() for n in raw_notes],
            notes_mapped=[n.model_dump() for n in mapped_quantized],
            tab_ascii=ascii_tab,
            metadata={"tempo_bpm": project.tempo_bpm},
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def latest_tab(self, project_id: int) -> tuple[Project, TabVersion | None]:
        project = self.db.get(Project, project_id)
        if not project:
            raise ValueError("Project not found")
        version = self.db.execute(
            select(TabVersion).where(TabVersion.project_id == project_id).order_by(TabVersion.version.desc())
        ).scalars().first()
        return project, version
