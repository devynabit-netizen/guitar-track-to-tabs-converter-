from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.constants import ProjectStatus
from app.db.base import Base
from app.models import Project
from app.schemas.transcription import NoteEvent
from app.services.project_service import ProjectService


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return SessionLocal()


def test_process_project_marks_failed_with_error_code(monkeypatch) -> None:
    session = _make_session()
    try:
        project = Project(name="fail", audio_path="/tmp/missing.wav")
        session.add(project)
        session.commit()

        service = ProjectService(session)

        def _raise(*args, **kwargs):
            raise RuntimeError("boom")

        monkeypatch.setattr(service, "_run_preprocessing", _raise)

        try:
            service.process_project(project.id)
            raise AssertionError("expected exception")
        except RuntimeError:
            pass

        session.refresh(project)
        assert project.status == ProjectStatus.FAILED.value
        assert project.error_code == "unknown"
        assert project.error_message == "boom"
    finally:
        session.close()


def test_process_project_completes_and_sets_progress(monkeypatch) -> None:
    session = _make_session()
    try:
        project = Project(name="ok", audio_path="/tmp/ok.wav")
        session.add(project)
        session.commit()

        service = ProjectService(session)

        monkeypatch.setattr(service, "_run_preprocessing", lambda _project: None)
        monkeypatch.setattr(
            service,
            "_run_transcription",
            lambda _project: [
                NoteEvent(pitch_midi=64, start_time=0.0, duration=0.5, confidence=0.9, velocity=90)
            ],
        )
        monkeypatch.setattr(service, "_run_tab_generation", lambda _project, notes: ([], "e|--|"))

        version = service.process_project(project.id)
        session.refresh(project)

        assert version.version == 1
        assert project.status == ProjectStatus.COMPLETE.value
        assert project.progress == 1.0
        assert project.current_phase == 5
    finally:
        session.close()
