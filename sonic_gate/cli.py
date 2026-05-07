"""CLI interface using Typer."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from sonic_gate import __version__
from sonic_gate.config import Config, load_config
from sonic_gate.core.reporter import Reporter
from sonic_gate.core.runner import Runner
from sonic_gate.core.result import AnalysisResult
from sonic_gate.analyzers.lufs import LUFSAnalyzer
from sonic_gate.analyzers.silence import SilenceAnalyzer
from sonic_gate.analyzers.duration import DurationAnalyzer
from sonic_gate.analyzers.format import FormatAnalyzer
from sonic_gate.analyzers.video import VideoAnalyzer
from sonic_gate.fix.engine import FixEngine

app = typer.Typer(
    name="sonic-gate",
    help="Audio/video quality gate with AI probing",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    if value:
        typer.echo(f"sonic-gate version {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show version"
    ),
):
    pass


def get_analyzers(config: Config):
    analyzers = [
        FormatAnalyzer(config),
        DurationAnalyzer(config),
        SilenceAnalyzer(config),
        LUFSAnalyzer(config),
        VideoAnalyzer(config),
    ]
    if config.rules.ai_probe.enabled:
        from sonic_gate.analyzers.whisper_probe import WhisperProbe
        analyzers.append(WhisperProbe(config))
    return analyzers


@app.command()
def analyze(
    paths: List[str] = typer.Argument(..., help="Files or directories to analyze"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table/json/csv/markdown)"),
    show_passed: bool = typer.Option(False, "--show-passed", help="Show passed files in output"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Include detailed metrics"),
    fix: bool = typer.Option(False, "--fix", help="Auto-repair failed files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview fixes without writing"),
):
    """Analyze audio/video files for quality issues."""
    cfg = load_config(config) if config else Config()

    if fix:
        cfg.fix.enabled = True
        cfg.fix.dry_run = dry_run

    cfg.output.format = format
    cfg.output.show_passed = show_passed
    cfg.output.verbose = verbose

    analyzers = get_analyzers(cfg)
    runner = Runner(cfg, analyzers)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing files...", total=None)
        results = runner.run(paths)
        progress.update(task, completed=True)

    reporter = Reporter(
        format=cfg.output.format,
        show_passed=cfg.output.show_passed,
        verbose=cfg.output.verbose,
    )
    output = reporter.render(results)
    console.print(output)

    if cfg.fix.enabled:
        fix_engine = FixEngine(cfg)
        failed = [r for r in results if not r.passed]
        if failed:
            console.print(f"\n[bold]Fixing {len(failed)} failed file(s)...[/bold]")
            for result in failed:
                fixed = fix_engine.fix(result.file_path)
                console.print(f"  [green]Fixed: {fixed}[/green]")

    # Exit with error code if any failed
    failed_count = sum(1 for r in results if not r.passed)
    if failed_count > 0:
        raise typer.Exit(code=1)


@app.command()
def demo():
    """Run demo with sample files."""
    console.print("[bold]Sonic Gate Demo[/bold]")
    console.print("Demo mode requires sample files in ./demo/ directory")
    # TODO: Generate or use demo files


@app.command()
def benchmark(
    paths: List[str] = typer.Argument(..., help="Files to benchmark"),
    iterations: int = typer.Option(5, "--iterations", "-n", help="Number of iterations"),
):
    """Benchmark analysis performance."""
    console.print(f"[bold]Benchmarking {len(paths)} file(s) x {iterations} iterations[/bold]")
    # TODO: Implement benchmark


def main():
    app()


if __name__ == "__main__":
    main()
