"""ML transcription service using Basic Pitch with fallback strategy."""
from __future__ import annotations

from pathlib import Path

from app.schemas.transcription import NoteEvent
from app.utils.music import confidence_from_velocity


class TranscriptionService:
    """Runs polyphonic transcription and returns normalized note events."""

    def transcribe(self, audio_path: str | Path) -> list[NoteEvent]:
        try:
            from basic_pitch.inference import predict

            _, midi_data, note_events = predict(str(audio_path))
            parsed = []
            for event in note_events:
                velocity = int(event.get("amplitude", 90))
                parsed.append(
                    NoteEvent(
                        pitch_midi=int(event["pitch"]),
                        start_time=float(event["start_time_s"]),
                        duration=max(0.05, float(event["end_time_s"]) - float(event["start_time_s"])),
                        confidence=float(event.get("confidence", confidence_from_velocity(velocity))),
                        velocity=velocity,
                    )
                )
            if parsed:
                return parsed
            if midi_data:
                return self._from_midi(midi_data)
        except Exception:
            return []
        return []

    def _from_midi(self, midi_data: object) -> list[NoteEvent]:
        notes: list[NoteEvent] = []
        for track in getattr(midi_data, "tracks", []):
            elapsed = 0.0
            active: dict[int, float] = {}
            for msg in track:
                elapsed += getattr(msg, "time", 0.0)
                if msg.type == "note_on" and msg.velocity > 0:
                    active[msg.note] = elapsed
                elif msg.type in {"note_off", "note_on"} and msg.note in active:
                    start = active.pop(msg.note)
                    notes.append(
                        NoteEvent(
                            pitch_midi=msg.note,
                            start_time=start,
                            duration=max(0.05, elapsed - start),
                            confidence=confidence_from_velocity(getattr(msg, "velocity", 100)),
                            velocity=getattr(msg, "velocity", 100),
                        )
                    )
        return notes
