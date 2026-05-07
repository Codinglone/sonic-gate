"""Base analyzer interface."""

import time
from abc import ABC, abstractmethod
from typing import Optional

from pydub import AudioSegment

from sonic_gate.config import Config
from sonic_gate.core.result import AnalysisResult


class BaseAnalyzer(ABC):
    def __init__(self, config: Config):
        self.config = config

    @property
    def name(self) -> str:
        return self.__class__.__name__.lower().replace("analyzer", "")

    @abstractmethod
    def analyze(self, file_path: str, result: AnalysisResult) -> None:
        """Analyze the file and update the result."""
        pass

    def load_audio(self, file_path: str) -> Optional[AudioSegment]:
        """Load audio file using pydub."""
        try:
            return AudioSegment.from_file(file_path)
        except Exception as e:
            return None

    def timed_analyze(self, file_path: str, result: AnalysisResult) -> None:
        """Run analyze with timing."""
        start = time.perf_counter()
        try:
            self.analyze(file_path, result)
        except Exception as e:
            result.add_failure(
                rule=f"{self.name}_error",
                actual=str(e),
                expected="no error",
                message=f"Analyzer '{self.name}' failed: {e}",
            )
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            result.add_metric(f"{self.name}_time_ms", round(elapsed, 2))
