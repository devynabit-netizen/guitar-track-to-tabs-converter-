# Guitar Track to Tabs Converter

Production-oriented full-stack application to upload guitar stems, transcribe audio into notes, map notes to fretboard positions, render/edit tablature, and export MIDI/GP5-compatible artifacts.

## Architecture

- **Backend (`backend/`)**: FastAPI + PostgreSQL + Redis/RQ job queue.
  - `app/dsp`: audio preprocessing.
  - `app/ml`: model inference layer (Basic Pitch integration).
  - `app/services/fretboard_mapper.py`: dynamic-programming fingering optimization.
  - `app/services/tab_formatter.py`: quantization + 6-line ASCII tab renderer.
  - `app/services/exporters.py`: MIDI and GP5-compatible export payload generation.
- **Frontend (`frontend/`)**: React + TypeScript + Tailwind.
  - Upload workflow, polling transcription progress, tab viewer/editor shell, playback controls.
  - WebAudio oscillator playback with cursor sync and tempo adjustment.
- **Persistence**:
  - `projects`: original audio and project metadata (tuning/tempo + lifecycle status).
  - `tab_versions`: versioned raw notes, mapped notes, ascii tab, metadata.

## Features Delivered

- WAV/MP3 upload endpoint and async queue enqueue.
- Transcription JSON output (`pitch_midi`, `start_time`, `duration`, `confidence`, `velocity`).
- Guitar string/fret optimization via shortest-path dynamic programming.
- Quantization to 1/16 grid and bar-oriented tab rendering.
- Browser playback controls (play/stop/tempo), scroll/progress cursor.
- Export API for MIDI and GP5-compatible JSON package.
- Version-ready schema for iterative user edits.
- Five-phase status lifecycle + explicit failure metadata.

## Processing Phases

Projects report a five-phase lifecycle through `GET /api/v1/projects/{id}/status`:

1. `uploaded`
2. `preprocessing`
3. `transcribing`
4. `tab_generation`
5. `finalizing`

Status payload fields include `current_phase`, `total_phases`, `phase_name`, `progress`, `error_message`, and `error_code`.

## Setup

### Prerequisites
- Python 3.11
- Node 20+
- Docker (for PostgreSQL + Redis)

### Infrastructure only
```bash
docker compose up -d postgres redis
```

### Full stack via docker compose
```bash
docker compose --profile app up --build
```

### Backend local
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

Run worker in another shell:
```bash
cd backend
source .venv/bin/activate
rq worker transcription
```

### Frontend local
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Database Migrations (Alembic)

```bash
cd backend
alembic upgrade head
```

Generate a new migration:
```bash
alembic revision -m "describe_change"
```

## API Overview

- `POST /api/v1/projects` (multipart: `name`, `audio`)
- `GET /api/v1/projects/{id}/status`
- `GET /api/v1/projects/{id}/tab`
- `POST /api/v1/projects/{id}/export/midi`
- `POST /api/v1/projects/{id}/export/gp5`

## Ops Notes / Runbook

- Health endpoint: `GET /health`
- Requests include `X-Request-ID` in responses.
- Common failure checks:
  - Basic Pitch first-run model download delay.
  - Redis/worker availability (`rq worker transcription`).
  - DB connectivity and migration state (`alembic upgrade head`).

## Limitations & Known Edge Cases

- Basic Pitch integration may require model download at first run.
- GP5 export is a compatibility JSON package, not binary `.gp5` encoding.
- Current frontend editor is a structured shell (tempo changes, playback, export), with note drag/hit-test hooks intended for SVG canvas extension.
- Polyphonic passages with dense articulations (bends/slides/legato) are represented as base note events only.
- Playback currently uses synthesized oscillator voices; replace with multisample guitar engine for production timbre realism.

## Roadmap Extensions

- Add bends/slides/hammer-on detection heuristics and per-note articulations.
- Implement SVG tab canvas with per-note drag/edit interactions.
- Add PDF export pipeline (LilyPond/VexFlow rendering service).
- Integrate CREPE/onsets-and-frames ensemble mode toggles.
