"""Format validation analyzer."""

from pydub import AudioSegment

from sonic_gate.analyzers.base import BaseAnalyzer
from sonic_gate.core.result import AnalysisResult


class FormatAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, result: AnalysisResult) -> None:
        try:
            audio = AudioSegment.from_file(file_path)
            result.add_metric("channels", audio.channels)
            result.add_metric("sample_rate", audio.frame_rate)
            result.add_metric("sample_width", audio.sample_width)
        except Exception as e:
            result.add_failure(
                "format",
                actual=str(e),
                expected="valid audio file",
                message=f"Failed to decode audio: {e}",
            )
