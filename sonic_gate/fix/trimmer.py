"""Silence trimming utilities."""

import tempfile
from pathlib import Path

from pydub import AudioSegment
from pydub.silence import detect_nonsilent


class SilenceTrimmer:
    def __init__(self, threshold_db: float = -50, min_silence_ms: int = 100):
        self.threshold_db = threshold_db
        self.min_silence_ms = min_silence_ms

    def trim(self, file_path: str) -> str:
        audio = AudioSegment.from_file(file_path)

        nonsilent = detect_nonsilent(
            audio,
            min_silence_len=self.min_silence_ms,
            silence_thresh=self.threshold_db,
        )

        if not nonsilent:
            return file_path

        # Keep only non-silent parts
        segments = [audio[start:end] for start, end in nonsilent]
        trimmed = segments[0]
        for seg in segments[1:]:
            trimmed += seg

        output = self._temp_output(file_path)
        trimmed.export(output, format="wav")
        return output

    def _temp_output(self, file_path: str) -> str:
        base = Path(file_path).stem
        return str(Path(tempfile.gettempdir()) / f"{base}_trimmed.wav")
