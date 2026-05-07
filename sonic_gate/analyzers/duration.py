"""Duration validation analyzer."""

from pydub import AudioSegment

from sonic_gate.analyzers.base import BaseAnalyzer
from sonic_gate.core.result import AnalysisResult


class DurationAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, result: AnalysisResult) -> None:
        audio = self.load_audio(file_path)
        if audio is None:
            return

        duration_sec = len(audio) / 1000.0
        result.add_metric("duration_seconds", round(duration_sec, 2))

        min_dur = self.config.rules.traditional.min_duration_seconds
        max_dur = self.config.rules.traditional.max_duration_seconds

        if duration_sec < min_dur:
            result.add_failure(
                "min_duration",
                actual=f"{duration_sec:.1f}s",
                expected=f">={min_dur}s",
            )
        elif duration_sec > max_dur:
            result.add_failure(
                "max_duration",
                actual=f"{duration_sec:.1f}s",
                expected=f"<={max_dur}s",
            )
