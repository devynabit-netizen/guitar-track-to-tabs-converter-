"""Dynamic programming-based fretboard mapping."""
from __future__ import annotations

from dataclasses import dataclass

from app.schemas.transcription import MappedNote, NoteEvent
from app.utils.music import note_name_to_midi


@dataclass(slots=True)
class Position:
    string: int
    fret: int


class FretboardMapper:
    def __init__(self, tuning: list[str] | None = None, max_fret: int = 24) -> None:
        tuning = tuning or ["E2", "A2", "D3", "G3", "B3", "E4"]
        self.open_midi = [note_name_to_midi(n) for n in tuning]
        self.max_fret = max_fret

    def generate_positions(self, midi_pitch: int) -> list[Position]:
        positions = []
        for idx, open_note in enumerate(self.open_midi):
            fret = midi_pitch - open_note
            if 0 <= fret <= self.max_fret:
                positions.append(Position(string=idx + 1, fret=fret))
        return positions

    def _transition_cost(self, a: Position, b: Position) -> float:
        fret_shift = abs(a.fret - b.fret)
        string_jump = abs(a.string - b.string) * 0.6
        stretch_penalty = 5.0 if fret_shift > 5 else 0.0
        return fret_shift + string_jump + stretch_penalty

    def map_notes(self, notes: list[NoteEvent]) -> list[MappedNote]:
        if not notes:
            return []
        candidates = [self.generate_positions(n.pitch_midi) for n in notes]
        costs: list[list[float]] = [[float("inf")] * len(c) for c in candidates]
        back: list[list[int]] = [[-1] * len(c) for c in candidates]

        for j in range(len(candidates[0])):
            costs[0][j] = candidates[0][j].fret

        for i in range(1, len(notes)):
            for j, cur in enumerate(candidates[i]):
                for k, prev in enumerate(candidates[i - 1]):
                    score = costs[i - 1][k] + self._transition_cost(prev, cur)
                    if score < costs[i][j]:
                        costs[i][j] = score
                        back[i][j] = k

        last_idx = min(range(len(candidates[-1])), key=lambda idx: costs[-1][idx])
        sequence = [last_idx]
        for i in range(len(notes) - 1, 0, -1):
            sequence.append(back[i][sequence[-1]])
        sequence.reverse()

        mapped: list[MappedNote] = []
        for note, cand_list, idx in zip(notes, candidates, sequence, strict=True):
            pos = cand_list[idx]
            mapped.append(MappedNote(**note.model_dump(), string=pos.string, fret=pos.fret))
        return mapped
