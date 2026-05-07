"""Result types for audio analysis."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Failure:
    rule: str
    actual: Any
    expected: Any
    message: Optional[str] = None


@dataclass
class AnalysisResult:
    file_path: str
    passed: bool
    failures: List[Failure] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    backend_used: str = ""

    def add_failure(
        self, rule: str, actual: Any, expected: Any, message: Optional[str] = None
    ) -> None:
        self.failures.append(Failure(rule=rule, actual=actual, expected=expected, message=message))
        self.passed = False

    def add_metric(self, key: str, value: Any) -> None:
        self.metrics[key] = value
