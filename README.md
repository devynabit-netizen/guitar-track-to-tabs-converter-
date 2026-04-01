# Guitar Track to Tabs Converter

Production-oriented full-stack web app for uploading guitar/full-mix audio (WAV/MP3/FLAC), running source separation + transcription, and generating synchronized guitar tablature with export and playback controls.

## Highlights

- FastAPI backend with async job queue (RQ/Redis).
- Audio preprocessing pipeline: mono conversion, LUFS-style normalization, noise gating, tempo/time-signature/key detection, chunk metadata.
- Source separation via Demucs CLI (auto-fallback when unavailable).
- Hybrid transcription engine:
  - Basic Pitch neural inference (primary)
  - librosa onset+pyin DSP fallback (secondary)
  - articulation heuristics (slide/hammer-on/pull-off)
- Guitar-specific note mapping:
  - alternate tunings supported
  - dynamic programming fingering optimization
  - confidence-aware scale snapping for low-confidence notes
- Tab generation:
  - structured JSON notes with string/fret/duration/articulation/chord
  - timing quantization including triplet-aware snapping
  - ASCII tab rendering
  - chord grouping metadata
- React frontend with Songsterr-style workflow:
  - upload + status phases
  - synchronized playback cursor
  - speed control (0.5x-1.5x)
  - loop region toggle
  - MIDI / GP5-compatible export triggers

## Run locally

### Infra
```bash
docker compose up -d postgres redis
```

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

Worker:
```bash
cd backend
source .venv/bin/activate
rq worker transcription
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Optional Demucs setup
If you want full source separation, install Demucs CLI in backend environment:
```bash
pip install demucs
```

## API
- `POST /api/v1/projects` form-data: `name`, `tuning`, `audio` (.wav/.mp3/.flac)
- `GET /api/v1/projects/{id}/status`
- `GET /api/v1/projects/{id}/tab`
- `POST /api/v1/projects/{id}/export/midi`
- `POST /api/v1/projects/{id}/export/gp5`
