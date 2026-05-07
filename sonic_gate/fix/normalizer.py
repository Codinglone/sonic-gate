"""LUFS normalization using FFmpeg."""

import re
import subprocess
import tempfile
from pathlib import Path

from pydub import AudioSegment


class LUFSNormalizer:
    def __init__(self, target_lufs: float = -16.0):
        self.target_lufs = target_lufs

    def normalize(self, file_path: str) -> str:
        # Measure current LUFS
        current_lufs = self._measure_lufs(file_path)
        if current_lufs is None:
            return file_path

        # Calculate gain adjustment
        gain_db = self.target_lufs - current_lufs

        # Apply gain with soft limiting
        audio = AudioSegment.from_file(file_path)
        normalized = audio + gain_db

        # Apply soft limiter if needed
        peak_db = normalized.max_dBFS
        if peak_db > -1.0:
            normalized = normalized.normalize(headroom=1.0)

        output = self._temp_output(file_path)
        normalized.export(output, format="wav", bitrate="192k")
        return output

    def _measure_lufs(self, file_path: str) -> float:
        try:
            cmd = [
                "ffmpeg", "-i", file_path,
                "-af", "ebur128=framelog=verbose",
                "-f", "null", "-",
            ]
            result = subprocess.run(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                timeout=30,
            )
            match = re.search(r'I:\s*(-?\d+\.\d+)\s*LUFS', result.stderr)
            if match:
                return float(match.group(1))
        except Exception:
            pass
        return None

    def _temp_output(self, file_path: str) -> str:
        base = Path(file_path).stem
        return str(Path(tempfile.gettempdir()) / f"{base}_normalized.wav")
