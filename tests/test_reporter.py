import json
from sonic_gate.core.result import AnalysisResult, Failure
from sonic_gate.core.reporter import Reporter


def test_analysis_result_passed():
    result = AnalysisResult(file_path="test.wav", passed=True)
    assert result.passed is True
    assert result.failures == []


def test_analysis_result_failed():
    failures = [Failure(rule="max_silence", actual=5.0, expected=3.0)]
    result = AnalysisResult(file_path="test.wav", passed=False, failures=failures)
    assert result.passed is False
    assert len(result.failures) == 1


def test_reporter_table():
    results = [
        AnalysisResult(file_path="a.wav", passed=True),
        AnalysisResult(file_path="b.wav", passed=False, failures=[
            Failure(rule="lufs", actual=-30.0, expected="[-24, -16]")
        ]),
    ]
    reporter = Reporter(format="table", show_passed=True)
    output = reporter.render(results)
    assert "a.wav" in output
    assert "b.wav" in output
    assert "lufs" in output


def test_reporter_json():
    results = [
        AnalysisResult(file_path="test.wav", passed=True, metrics={"lufs": -18.0}),
    ]
    reporter = Reporter(format="json")
    output = reporter.render(results)
    data = json.loads(output)
    assert data["summary"]["total"] == 1
    assert data["results"][0]["metrics"]["lufs"] == -18.0
