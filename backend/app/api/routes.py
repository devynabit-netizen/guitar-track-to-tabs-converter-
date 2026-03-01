"""API routes."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.transcription import ProjectCreateResponse, ProjectStatusResponse, TabResponse, MappedNote
from app.services.exporters import ExportService
from app.services.project_service import ProjectService
from app.workers.queue import queue, run_transcription_job

router = APIRouter()
settings = get_settings()


@router.post("/projects", response_model=ProjectCreateResponse)
async def create_project(
    name: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ProjectCreateResponse:
    ext = Path(audio.filename or "track.wav").suffix.lower()
    if ext not in {".wav", ".mp3"}:
        raise HTTPException(status_code=400, detail="Only WAV/MP3 supported")

    upload_dir = Path(settings.uploads_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / f"{uuid4().hex}{ext}"
    destination.write_bytes(await audio.read())

    project = ProjectService(db).create_project(name=name, audio_path=str(destination))
    queue.enqueue(run_transcription_job, project.id)
    return ProjectCreateResponse(project_id=project.id, status="queued")


@router.get("/projects/{project_id}/status", response_model=ProjectStatusResponse)
def project_status(project_id: int, db: Session = Depends(get_db)) -> ProjectStatusResponse:
    _, latest = ProjectService(db).latest_tab(project_id)
    return ProjectStatusResponse(project_id=project_id, status="complete" if latest else "processing", progress=1.0 if latest else 0.5)


@router.get("/projects/{project_id}/tab", response_model=TabResponse)
def get_tab(project_id: int, db: Session = Depends(get_db)) -> TabResponse:
    project, latest = ProjectService(db).latest_tab(project_id)
    if not latest:
        raise HTTPException(status_code=404, detail="Tab not ready")

    notes = [MappedNote.model_validate(item) for item in latest.notes_mapped]
    return TabResponse(
        project_id=project.id,
        tempo_bpm=project.tempo_bpm,
        tuning=project.tuning,
        notes=notes,
        tab_ascii=latest.tab_ascii,
    )


@router.post("/projects/{project_id}/export/{fmt}")
def export(project_id: int, fmt: str, db: Session = Depends(get_db)) -> dict[str, str]:
    project, latest = ProjectService(db).latest_tab(project_id)
    if not latest:
        raise HTTPException(status_code=404, detail="Tab not ready")
    notes = [MappedNote.model_validate(item) for item in latest.notes_mapped]

    artifacts = Path(settings.artifacts_dir)
    artifacts.mkdir(parents=True, exist_ok=True)
    exporter = ExportService()

    if fmt == "midi":
        out = artifacts / f"project_{project.id}.mid"
        exporter.export_midi(notes, str(out))
    elif fmt == "gp5":
        out = artifacts / f"project_{project.id}.gp5.json"
        exporter.export_gp5_compatible(notes, str(out))
    else:
        raise HTTPException(status_code=400, detail="Supported export formats: midi, gp5")

    return {"path": str(out)}
