"""Silence detection analyzer."""

from pydub import AudioSegment
from pydub.silence import detect_nonsilent

from sonic_gate.analyzers.base import BaseAnalyzer
from sonic_gate.core.result import AnalysisResult


class SilenceAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, result: AnalysisResult) -> None:
        audio = self.load_audio(file_path)
        if audio is None:
            result.add_failure("silence", actual="load failed", expected="loaded")
            return

        duration_sec = len(audio) / 1000.0
        result.add_metric("duration_seconds", round(duration_sec, 2))

        # Detect non-silent ranges
        nonsilent = detect_nonsilent(
            audio,
            min_silence_len=100,  # 100ms
            silence_thresh=-50,   # -50 dBFS
        )

        # Calculate longest silence
        if len(nonsilent) == 0:
            longest_silence = duration_sec
        else:
            longest_silence = 0.0
            prev_end = 0
            for start, end in nonsilent:
                gap = (start - prev_end) / 1000.0
                longest_silence = max(longest_silence, gap)
                prev_end = end
            # Check trailing silence
            trailing = (len(audio) - prev_end) / 1000.0
            longest_silence = max(longest_silence, trailing)

        result.add_metric("silence_seconds", round(longest_silence, 2))

        max_silence = self.config.rules.traditional.max_silence_seconds
        if longest_silence > max_silence:
            result.add_failure(
                "max_silence",
                actual=f"{longest_silence:.1f}s",
                expected=f"<={max_silence}s",
            )
