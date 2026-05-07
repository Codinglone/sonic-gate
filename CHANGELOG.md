# Changelog

## [0.1.1] - 2026-05-07

### Changed
- Moved `openai-whisper` from required to optional dependency (`pip install "sonic-gate[ai]"`)
- Default install is now deterministic-only (fast, no AI overhead)
- Updated PyPI keywords and classifiers for better discoverability
- Added project URLs (Homepage, Repository, Issues, Changelog)

## [0.1.0] - 2026-05-07

### Added
- Initial release
- Traditional analyzers: LUFS, silence detection, duration validation, format checking
- Video support with auto audio extraction (MP4, MOV, AVI, MKV, WebM)
- Fix mode: auto-trim silence, normalize LUFS, non-destructive repairs
- Multiple output formats: table, JSON, CSV, markdown
- Optional AI probe via OpenAI Whisper (speech detection, language validation, confidence scoring)
- YAML-based configuration with Pydantic validation
- Typer-based CLI with analyze, demo, and benchmark commands
- Integration test suite (25 tests)

### Notes
- AI probe disabled by default after real-world testing showed Whisper is unreliable for low-resource languages (e.g., Kinyarwanda)
- Whisper confidence uses logprob values (negative), not probabilities
