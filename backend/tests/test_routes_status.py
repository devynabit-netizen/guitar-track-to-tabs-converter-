from __future__ import annotations

import io

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.constants import ProjectStatus
from app.models import Project, TabVersion


def test_create_project_rejects_invalid_extension(client: TestClient) -> None:
    response = client.post(
        "/api/v1/projects",
        data={"name": "Bad Audio"},
        files={"audio": ("track.txt", io.BytesIO(b"abc"), "text/plain")},
    )
    assert response.status_code == 422


def test_project_status_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/projects/999/status")
    assert response.status_code == 404


def test_project_status_includes_phase_and_error_fields(client: TestClient, db_session: Session) -> None:
    project = Project(
        name="Demo",
        audio_path="/tmp/demo.wav",
        status=ProjectStatus.FAILED.value,
        progress=0.6,
        current_phase=3,
        error_message="Transcription failed",
        error_code="transcription_failed",
    )
    db_session.add(project)
    db_session.commit()

    response = client.get(f"/api/v1/projects/{project.id}/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == ProjectStatus.FAILED.value
    assert payload["current_phase"] == 3
    assert payload["total_phases"] == 5
    assert payload["phase_name"] == "transcribing"
    assert payload["error_message"] == "Transcription failed"
    assert payload["error_code"] == "transcription_failed"


def test_tab_and_export_return_not_ready_without_versions(client: TestClient, db_session: Session) -> None:
    project = Project(name="No Tab", audio_path="/tmp/no-tab.wav")
    db_session.add(project)
    db_session.commit()

    tab_response = client.get(f"/api/v1/projects/{project.id}/tab")
    export_response = client.post(f"/api/v1/projects/{project.id}/export/midi")

    assert tab_response.status_code == 404
    assert export_response.status_code == 404


def test_tab_route_returns_latest_tab(client: TestClient, db_session: Session) -> None:
    project = Project(name="Ready", audio_path="/tmp/ready.wav", tuning=["E2", "A2", "D3", "G3", "B3", "E4"])
    db_session.add(project)
    db_session.flush()
    version = TabVersion(
        project_id=project.id,
        version=1,
        notes_raw=[],
        notes_mapped=[
            {
                "pitch_midi": 64,
                "start_time": 0.0,
                "duration": 0.5,
                "confidence": 0.8,
                "velocity": 95,
                "string": 1,
                "fret": 0,
            }
        ],
        tab_ascii="e|--0--|",
        metadata_json={"tempo_bpm": 120},
    )
    db_session.add(version)
    db_session.commit()

    response = client.get(f"/api/v1/projects/{project.id}/tab")
    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project.id
    assert payload["notes"][0]["fret"] == 0
