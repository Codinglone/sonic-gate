import pytest
from sonic_gate.analyzers.base import BaseAnalyzer
from sonic_gate.core.result import AnalysisResult
from sonic_gate.config import Config


class DummyAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, result: AnalysisResult) -> None:
        result.add_metric("dummy", 42)
        if file_path == "fail.wav":
            result.add_failure("dummy_rule", actual="bad", expected="good")


def test_base_analyzer_name():
    analyzer = DummyAnalyzer(Config())
    assert analyzer.name == "dummy"


def test_analyzer_pass():
    analyzer = DummyAnalyzer(Config())
    result = AnalysisResult(file_path="pass.wav", passed=True)
    analyzer.analyze("pass.wav", result)
    assert result.passed is True
    assert result.metrics["dummy"] == 42


def test_analyzer_fail():
    analyzer = DummyAnalyzer(Config())
    result = AnalysisResult(file_path="fail.wav", passed=True)
    analyzer.analyze("fail.wav", result)
    assert result.passed is False
    assert len(result.failures) == 1


import wave
import numpy as np
from pathlib import Path

from sonic_gate.analyzers.lufs import LUFSAnalyzer
from sonic_gate.analyzers.silence import SilenceAnalyzer
from sonic_gate.analyzers.duration import DurationAnalyzer
from sonic_gate.analyzers.format import FormatAnalyzer


def create_test_wav(path: str, duration_sec: float = 1.0, sample_rate: int = 48000):
    """Create a simple test WAV file."""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec))
    audio = np.sin(2 * np.pi * 440 * t) * 0.3
    audio_int = (audio * 32767).astype(np.int16)

    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(audio_int.tobytes())


def test_lufs_analyzer(tmp_path: Path):
    wav = str(tmp_path / "test.wav")
    create_test_wav(wav)

    config = Config()
    analyzer = LUFSAnalyzer(config)
    result = AnalysisResult(file_path=wav, passed=True)
    analyzer.analyze(wav, result)

    assert "lufs" in result.metrics
    assert isinstance(result.metrics["lufs"], float)


def test_silence_analyzer(tmp_path: Path):
    wav = str(tmp_path / "test.wav")
    create_test_wav(wav, duration_sec=2.0)

    config = Config()
    analyzer = SilenceAnalyzer(config)
    result = AnalysisResult(file_path=wav, passed=True)
    analyzer.analyze(wav, result)

    assert "silence_seconds" in result.metrics
    assert "duration_seconds" in result.metrics
    assert result.metrics["duration_seconds"] == pytest.approx(2.0, abs=0.1)


def test_duration_analyzer(tmp_path: Path):
    wav = str(tmp_path / "test.wav")
    create_test_wav(wav, duration_sec=0.5)

    config = Config()
    config.rules.traditional.min_duration_seconds = 1.0
    analyzer = DurationAnalyzer(config)
    result = AnalysisResult(file_path=wav, passed=True)
    analyzer.analyze(wav, result)

    assert result.passed is False
    assert any(f.rule == "min_duration" for f in result.failures)


def test_format_analyzer(tmp_path: Path):
    bad_file = str(tmp_path / "bad.wav")
    with open(bad_file, "w") as f:
        f.write("not audio data")

    config = Config()
    analyzer = FormatAnalyzer(config)
    result = AnalysisResult(file_path=bad_file, passed=True)
    analyzer.analyze(bad_file, result)

    assert result.passed is False
    assert any(f.rule == "format" for f in result.failures)
