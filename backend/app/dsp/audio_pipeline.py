"""Audio preprocessing and metadata extraction."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np


@dataclass(slots=True)
class ProcessedAudio:
    samples: np.ndarray
    sample_rate: int
    duration: float
    tempo_bpm: float
    time_signature: str
    key_signature: str
    chunks: list[tuple[int, int]]


class AudioPipeline:
    """Prepares audio for model inference with guitar-friendly preprocessing."""

    def __init__(self, target_lufs: float = -14.0) -> None:
        self.target_lufs = target_lufs

    def normalize(self, y: np.ndarray) -> np.ndarray:
        peak = np.max(np.abs(y))
        if peak == 0:
            return y
        return y / peak

    def normalize_loudness(self, y: np.ndarray) -> np.ndarray:
        rms = float(np.sqrt(np.mean(np.square(y)) + 1e-12))
        current_lufs_like = 20 * np.log10(max(rms, 1e-8))
        gain_db = self.target_lufs - current_lufs_like
        gained = y * (10 ** (gain_db / 20.0))
        return np.clip(gained, -1.0, 1.0)

    def reduce_noise(self, y: np.ndarray) -> np.ndarray:
        # Light denoising gate: suppress very low-level segments.
        threshold = max(0.005, float(np.std(y) * 0.4))
        gated = np.where(np.abs(y) < threshold, 0.0, y)
        return gated.astype(np.float32)

    def detect_time_signature(self, y: np.ndarray, sr: int) -> str:
        _, beats = librosa.beat.beat_track(y=y, sr=sr)
        if len(beats) < 8:
            return "4/4"
        intervals = np.diff(beats)
        pulse = int(np.clip(np.round(np.median(intervals)), 1, None))
        return "3/4" if pulse % 3 == 0 else "4/4"

    def detect_key_signature(self, y: np.ndarray, sr: int) -> str:
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        profile = np.mean(chroma, axis=1)
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        return names[int(np.argmax(profile))]

    def segment_chunks(self, y: np.ndarray, sr: int, chunk_seconds: float = 15.0) -> list[tuple[int, int]]:
        hop = int(chunk_seconds * sr)
        return [(i, min(i + hop, len(y))) for i in range(0, len(y), hop)]

    def load_and_process(self, path: str | Path, target_sr: int = 22050) -> ProcessedAudio:
        samples, sr = librosa.load(path, sr=target_sr, mono=True)
        samples = self.normalize(samples)
        samples = self.normalize_loudness(samples)
        samples = self.reduce_noise(samples)
        tempo, _ = librosa.beat.beat_track(y=samples, sr=sr)
        return ProcessedAudio(
            samples=samples,
            sample_rate=sr,
            duration=len(samples) / sr,
            tempo_bpm=float(tempo) if tempo else 120.0,
            time_signature=self.detect_time_signature(samples, sr),
            key_signature=self.detect_key_signature(samples, sr),
            chunks=self.segment_chunks(samples, sr),
        )
