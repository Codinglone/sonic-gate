"""LUFS (loudness) analyzer using FFmpeg."""

import re
import subprocess

from sonic_gate.analyzers.base import BaseAnalyzer
from sonic_gate.core.result import AnalysisResult


class LUFSAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, result: AnalysisResult) -> None:
        lufs = self._calculate_lufs(file_path)
        result.add_metric("lufs", lufs)

        if lufs is None:
            result.add_failure("lufs", actual="failed", expected="valid value")
            return

        min_lufs, max_lufs = self.config.rules.traditional.lufs_range
        if not (min_lufs <= lufs <= max_lufs):
            result.add_failure(
                "lufs",
                actual=f"{lufs:.1f} LUFS",
                expected=f"[{min_lufs}, {max_lufs}]",
            )

    def _calculate_lufs(self, file_path: str) -> float:
        try:
            cmd = [
                "ffmpeg",
                "-i",
                file_path,
                "-af",
                "ebur128=framelog=verbose",
                "-f",
                "null",
                "-",
            ]
            process = subprocess.run(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                timeout=30,
            )
            match = re.search(r"I:\s*(-?\d+\.\d+)\s*LUFS", process.stderr)
            if match:
                return float(match.group(1))
        except Exception:
            pass
        return None
