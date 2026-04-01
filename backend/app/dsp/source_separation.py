"""Source separation using Demucs when available."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class SourceSeparator:
    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def separate_if_needed(self, audio_path: str | Path, mode: str = "auto") -> dict[str, str]:
        source = Path(audio_path)
        if mode in {"guitar", "lead_guitar", "rhythm_guitar"}:
            return {"guitar": str(source)}

        if shutil.which("demucs"):
            run = subprocess.run(
                [
                    "demucs",
                    "--two-stems",
                    "other",
                    "-o",
                    str(self.output_dir),
                    str(source),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if run.returncode == 0:
                stem_root = self.output_dir / "htdemucs" / source.stem
                other = stem_root / "other.wav"
                vocals = stem_root / "vocals.wav"
                drums = stem_root / "drums.wav"
                bass = stem_root / "bass.wav"
                return {
                    "lead_guitar": str(other if other.exists() else source),
                    "rhythm_guitar": str(other if other.exists() else source),
                    "bass": str(bass if bass.exists() else source),
                    "drums": str(drums) if drums.exists() else "",
                    "vocals": str(vocals) if vocals.exists() else "",
                }

        # Graceful fallback when demucs is not available.
        return {"full_mix": str(source), "lead_guitar": str(source), "rhythm_guitar": str(source)}
