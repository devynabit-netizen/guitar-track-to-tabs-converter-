"""Tab formatting and quantization utilities."""
from __future__ import annotations

from collections import defaultdict

from app.schemas.transcription import MappedNote
from app.utils.music import quantize_time


class TabFormatter:
    def __init__(self, tempo_bpm: float = 120.0, bars_per_line: int = 4) -> None:
        self.tempo = tempo_bpm
        self.bars_per_line = bars_per_line

    def quantize(self, notes: list[MappedNote], division: int = 16, triplets: bool = True) -> list[MappedNote]:
        quantized = []
        triplet_division = 12
        for note in notes:
            start_16 = quantize_time(note.start_time, self.tempo, division)
            start_12 = quantize_time(note.start_time, self.tempo, triplet_division)
            start = start_12 if triplets and abs(start_12 - note.start_time) < abs(start_16 - note.start_time) else start_16
            quantized.append(
                note.model_copy(
                    update={
                        "start_time": start,
                        "duration": max(0.05, quantize_time(note.duration, self.tempo, division)),
                    }
                )
            )
        return sorted(quantized, key=lambda n: n.start_time)

    def detect_chords(self, notes: list[MappedNote]) -> list[dict[str, float | str]]:
        grouped: defaultdict[float, list[MappedNote]] = defaultdict(list)
        for n in notes:
            grouped[round(n.start_time, 3)].append(n)
        chords: list[dict[str, float | str]] = []
        for t, ns in sorted(grouped.items()):
            if len(ns) < 2:
                continue
            pcs = sorted({n.pitch_midi % 12 for n in ns})
            label = f"Chord({','.join(map(str, pcs))})"
            chords.append({"time": t, "label": label})
            for n in ns:
                n.chord = label
        return chords

    def to_ascii(self, notes: list[MappedNote], length_beats: int = 32) -> str:
        grid = [["-" for _ in range(length_beats * 4)] for _ in range(6)]
        for note in notes:
            beat_idx = int((note.start_time / (60 / self.tempo)) * 4)
            if 0 <= beat_idx < len(grid[0]):
                fret = str(note.fret)
                row = 6 - note.string
                for i, ch in enumerate(fret):
                    if beat_idx + i < len(grid[row]):
                        grid[row][beat_idx + i] = ch
        names = ["e", "B", "G", "D", "A", "E"]
        lines = [f"{n}|{''.join(row)}|" for n, row in zip(names, grid, strict=True)]
        return "\n".join(lines)
