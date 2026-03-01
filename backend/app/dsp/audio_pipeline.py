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


class AudioPipeline:
    """Prepares audio for model inference."""

    def normalize(self, y: np.ndarray) -> np.ndarray:
        peak = np.max(np.abs(y))
        if peak == 0:
            return y
        return y / peak

    def load_and_process(self, path: str | Path, target_sr: int = 22050) -> ProcessedAudio:
        samples, sr = librosa.load(path, sr=target_sr, mono=True)
        samples = self.normalize(samples)
        return ProcessedAudio(samples=samples, sample_rate=sr, duration=len(samples) / sr)
