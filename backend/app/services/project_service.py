"""Project domain service orchestrating transcription pipeline."""
from __future__ import annotations

from pathlib import Path

import librosa
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import PHASE_NAMES, TOTAL_PHASES, ProjectErrorCode, ProjectStatus
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
        project = Project(
            name=name,
            audio_path=audio_path,
            tuning=tuning or ["E2", "A2", "D3", "G3", "B3", "E4"],
            status=ProjectStatus.QUEUED.value,
            progress=1 / TOTAL_PHASES,
            current_phase=1,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def _set_phase(self, project: Project, phase: int, status: ProjectStatus = ProjectStatus.PROCESSING) -> None:
        project.current_phase = phase
        project.progress = phase / TOTAL_PHASES
        project.status = status.value
        if status != ProjectStatus.FAILED:
            project.error_message = None
            project.error_code = None
        self.db.add(project)
        self.db.commit()

    def _mark_failure(self, project: Project, error_message: str, error_code: ProjectErrorCode) -> None:
        project.status = ProjectStatus.FAILED.value
        project.error_message = error_message
        project.error_code = error_code.value
        self.db.add(project)
        self.db.commit()

    def process_project(self, project_id: int) -> TabVersion:
        project = self.db.get(Project, project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        try:
            self._set_phase(project, phase=2)
            self._run_preprocessing(project)

            self._set_phase(project, phase=3)
            raw_notes = self._run_transcription(project)

            self._set_phase(project, phase=4)
            mapped_quantized, ascii_tab = self._run_tab_generation(project, raw_notes)

            self._set_phase(project, phase=5)
            version = self._persist_version(project, raw_notes, mapped_quantized, ascii_tab)

            project.status = ProjectStatus.COMPLETE.value
            project.progress = 1.0
            project.current_phase = TOTAL_PHASES
            self.db.add(project)
            self.db.commit()
            self.db.refresh(version)
            return version
        except Exception as exc:  # noqa: BLE001
            if not project.error_code:
                self._mark_failure(project, str(exc), ProjectErrorCode.UNKNOWN)
            raise

    def _run_preprocessing(self, project: Project) -> None:
        try:
            tempo, _ = librosa.beat.beat_track(path=Path(project.audio_path), units="time")
            if tempo and tempo > 0:
                project.tempo_bpm = float(tempo)
            self.db.add(project)
            self.db.commit()
        except Exception as exc:  # noqa: BLE001
            self._mark_failure(project, f"Preprocessing failed: {exc}", ProjectErrorCode.PREPROCESSING_FAILED)
            raise

    def _run_transcription(self, project: Project):
        try:
            return self.transcriber.transcribe(project.audio_path)
        except Exception as exc:  # noqa: BLE001
            self._mark_failure(project, f"Transcription failed: {exc}", ProjectErrorCode.TRANSCRIPTION_FAILED)
            raise

    def _run_tab_generation(self, project: Project, raw_notes):
        try:
            mapper = FretboardMapper(project.tuning)
            mapped: list[MappedNote] = mapper.map_notes(raw_notes)
            formatter = TabFormatter(project.tempo_bpm)
            mapped_quantized = formatter.quantize(mapped)
            ascii_tab = formatter.to_ascii(mapped_quantized)
            return mapped_quantized, ascii_tab
        except Exception as exc:  # noqa: BLE001
            self._mark_failure(project, f"Tab generation failed: {exc}", ProjectErrorCode.TAB_GENERATION_FAILED)
            raise

    def _persist_version(self, project: Project, raw_notes, mapped_quantized, ascii_tab: str) -> TabVersion:
        try:
            next_version = len(project.versions) + 1
            version = TabVersion(
                project_id=project.id,
                version=next_version,
                notes_raw=[n.model_dump() for n in raw_notes],
                notes_mapped=[n.model_dump() for n in mapped_quantized],
                tab_ascii=ascii_tab,
                metadata_json={"tempo_bpm": project.tempo_bpm, "phase_name": PHASE_NAMES[5]},
            )
            self.db.add(version)
            self.db.commit()
            return version
        except Exception as exc:  # noqa: BLE001
            self._mark_failure(project, f"Finalization failed: {exc}", ProjectErrorCode.VERSION_PERSIST_FAILED)
            raise

    def latest_tab(self, project_id: int) -> tuple[Project, TabVersion | None]:
        project = self.db.get(Project, project_id)
        if not project:
            raise ValueError("Project not found")
        version = self.db.execute(
            select(TabVersion).where(TabVersion.project_id == project_id).order_by(TabVersion.version.desc())
        ).scalars().first()
        return project, version
