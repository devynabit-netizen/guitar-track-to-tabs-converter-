"""Pydantic schemas for transcription workflow."""
from pydantic import BaseModel, Field


class NoteEvent(BaseModel):
    pitch_midi: int
    start_time: float
    duration: float
    confidence: float = Field(ge=0.0, le=1.0)
    velocity: int | None = None


class MappedNote(NoteEvent):
    string: int
    fret: int


class ProjectCreateResponse(BaseModel):
    project_id: int
    status: str


class ProjectStatusResponse(BaseModel):
    project_id: int
    status: str
    progress: float = 0.0
    current_phase: int = 1
    total_phases: int = 5
    phase_name: str = "queued"
    error_message: str | None = None
    error_code: str | None = None


class TabResponse(BaseModel):
    project_id: int
    tempo_bpm: float
    tuning: list[str]
    notes: list[MappedNote]
    tab_ascii: str
