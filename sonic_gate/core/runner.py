"""Analysis runner that coordinates all analyzers."""

import os
from pathlib import Path
from typing import List, Optional

from sonic_gate.config import Config
from sonic_gate.core.result import AnalysisResult
from sonic_gate.analyzers.base import BaseAnalyzer


class Runner:
    def __init__(self, config: Config, analyzers: List[BaseAnalyzer]):
        self.config = config
        self.analyzers = analyzers

    def run(self, paths: List[str]) -> List[AnalysisResult]:
        files = self._collect_files(paths)
        results = []

        for file_path in files:
            result = self._analyze_file(file_path)
            results.append(result)

        return results

    def _collect_files(self, paths: List[str]) -> List[str]:
        files = []
        for path in paths:
            p = Path(path)
            if p.is_file():
                files.append(str(p))
            elif p.is_dir():
                files.extend(str(f) for f in p.rglob("*") if f.is_file())
        return files

    def _analyze_file(self, file_path: str) -> AnalysisResult:
        result = AnalysisResult(file_path=file_path, passed=True)

        for analyzer in self.analyzers:
            analyzer.timed_analyze(file_path, result)

        return result
