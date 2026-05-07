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
