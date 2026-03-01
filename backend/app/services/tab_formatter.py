"""Tab formatting and quantization utilities."""
from __future__ import annotations

from app.schemas.transcription import MappedNote
from app.utils.music import quantize_time


class TabFormatter:
    def __init__(self, tempo_bpm: float = 120.0, bars_per_line: int = 4) -> None:
        self.tempo = tempo_bpm
        self.bars_per_line = bars_per_line

    def quantize(self, notes: list[MappedNote], division: int = 16) -> list[MappedNote]:
        quantized = []
        for note in notes:
            quantized.append(
                note.model_copy(
                    update={
                        "start_time": quantize_time(note.start_time, self.tempo, division),
                        "duration": max(0.05, quantize_time(note.duration, self.tempo, division)),
                    }
                )
            )
        return sorted(quantized, key=lambda n: n.start_time)

    def to_ascii(self, notes: list[MappedNote], length_beats: int = 16) -> str:
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
