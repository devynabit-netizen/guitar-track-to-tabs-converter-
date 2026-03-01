"""Export tab to MIDI and pseudo GP5 (intermediate JSON package)."""
from __future__ import annotations

import json
from pathlib import Path

import mido

from app.schemas.transcription import MappedNote


class ExportService:
    def export_midi(self, notes: list[MappedNote], path: str) -> str:
        midi = mido.MidiFile()
        track = mido.MidiTrack()
        midi.tracks.append(track)
        ticks_per_beat = midi.ticks_per_beat
        current_tick = 0
        for note in sorted(notes, key=lambda n: n.start_time):
            start_tick = int(note.start_time * ticks_per_beat * 2)
            delta = max(0, start_tick - current_tick)
            track.append(mido.Message("note_on", note=note.pitch_midi, velocity=note.velocity or 96, time=delta))
            off_delta = max(1, int(note.duration * ticks_per_beat * 2))
            track.append(mido.Message("note_off", note=note.pitch_midi, velocity=0, time=off_delta))
            current_tick = start_tick + off_delta
        midi.save(path)
        return path

    def export_gp5_compatible(self, notes: list[MappedNote], path: str) -> str:
        payload = {"format": "gp5-compatible-json", "notes": [n.model_dump() for n in notes]}
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
