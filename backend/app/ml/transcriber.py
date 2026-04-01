"""ML transcription service using Basic Pitch with DSP fallback strategy."""
from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np

from app.schemas.transcription import NoteEvent
from app.utils.music import confidence_from_velocity


class TranscriptionService:
    """Runs polyphonic transcription and returns normalized note events."""

    def transcribe(self, audio_path: str | Path) -> list[NoteEvent]:
        notes = self._transcribe_basic_pitch(audio_path)
        if notes:
            return self._post_process(notes)
        return self._post_process(self._transcribe_dsp_fallback(audio_path))

    def _transcribe_basic_pitch(self, audio_path: str | Path) -> list[NoteEvent]:
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

    def _transcribe_dsp_fallback(self, audio_path: str | Path) -> list[NoteEvent]:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units="frames")
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        if len(onset_times) == 0:
            return []

        notes: list[NoteEvent] = []
        for idx, onset in enumerate(onset_times):
            end = onset_times[idx + 1] if idx + 1 < len(onset_times) else min(onset + 0.5, len(y) / sr)
            seg = y[int(onset * sr): int(end * sr)]
            if len(seg) < 128:
                continue
            pitch, _, _ = librosa.pyin(seg, fmin=librosa.note_to_hz("E2"), fmax=librosa.note_to_hz("E6"), sr=sr)
            valid = pitch[~np.isnan(pitch)]
            if len(valid) == 0:
                continue
            midi = int(round(librosa.hz_to_midi(float(np.median(valid)))))
            notes.append(
                NoteEvent(
                    pitch_midi=midi,
                    start_time=float(onset),
                    duration=max(0.05, float(end - onset)),
                    confidence=0.55,
                    velocity=85,
                )
            )
        return notes

    def _post_process(self, notes: list[NoteEvent]) -> list[NoteEvent]:
        ordered = sorted(notes, key=lambda n: n.start_time)
        for i in range(1, len(ordered)):
            prev, cur = ordered[i - 1], ordered[i]
            pitch_delta = cur.pitch_midi - prev.pitch_midi
            if abs(pitch_delta) in {1, 2} and cur.start_time - prev.start_time < 0.25:
                cur.articulation = "hammer-on" if pitch_delta > 0 else "pull-off"
            elif abs(pitch_delta) >= 3 and cur.start_time - prev.start_time < 0.3:
                cur.articulation = "slide"
        return ordered

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
