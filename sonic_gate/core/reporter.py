"""Report generation in multiple formats."""

import csv
import io
import json
from typing import List

from rich.console import Console
from rich.table import Table

from sonic_gate.core.result import AnalysisResult


class Reporter:
    def __init__(self, format: str = "table", show_passed: bool = False, verbose: bool = False):
        self.format = format
        self.show_passed = show_passed
        self.verbose = verbose

    def render(self, results: List[AnalysisResult]) -> str:
        if self.format == "table":
            return self._render_table(results)
        elif self.format == "json":
            return self._render_json(results)
        elif self.format == "csv":
            return self._render_csv(results)
        elif self.format == "markdown":
            return self._render_markdown(results)
        else:
            raise ValueError(f"Unknown format: {self.format}")

    def _render_table(self, results: List[AnalysisResult]) -> str:
        table = Table(title="Sonic Gate Analysis Results")
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Status", style="bold")
        table.add_column("Failures", style="red")

        if self.verbose:
            table.add_column("Metrics", style="dim")

        for result in results:
            if not self.show_passed and result.passed:
                continue

            status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
            failures = ", ".join(
                f"{f.rule}: {f.actual} (expected: {f.expected})"
                for f in result.failures
            ) or "—"

            if self.verbose:
                metrics = ", ".join(f"{k}={v}" for k, v in result.metrics.items())
                table.add_row(result.file_path, status, failures, metrics)
            else:
                table.add_row(result.file_path, status, failures)

        console = Console(force_terminal=True)
        with console.capture() as capture:
            console.print(table)
        return capture.get()

    def _render_json(self, results: List[AnalysisResult]) -> str:
        data = {
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r.passed),
                "failed": sum(1 for r in results if not r.passed),
            },
            "results": [
                {
                    "file": r.file_path,
                    "passed": r.passed,
                    "failures": [
                        {"rule": f.rule, "actual": f.actual, "expected": f.expected, "message": f.message}
                        for f in r.failures
                    ],
                    "metrics": r.metrics,
                    "processing_time_ms": r.processing_time_ms,
                    "backend_used": r.backend_used,
                }
                for r in results
            ],
        }
        return json.dumps(data, indent=2)

    def _render_csv(self, results: List[AnalysisResult]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["file", "passed", "failures", "processing_time_ms"])

        for result in results:
            if not self.show_passed and result.passed:
                continue
            failures = "; ".join(f"{f.rule}={f.actual}" for f in result.failures)
            writer.writerow([result.file_path, result.passed, failures, result.processing_time_ms])

        return output.getvalue()

    def _render_markdown(self, results: List[AnalysisResult]) -> str:
        lines = ["# Sonic Gate Analysis Report\n", "| File | Status | Failures |", "|------|--------|----------|"]

        for result in results:
            if not self.show_passed and result.passed:
                continue
            status = "PASS" if result.passed else "FAIL"
            failures = ", ".join(f.rule for f in result.failures) or "—"
            lines.append(f"| {result.file_path} | {status} | {failures} |")

        return "\n".join(lines) + "\n"
