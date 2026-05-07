# Changelog

## [0.1.4] - 2026-05-07

### Fixed
- Skip `test_whisper_probe` when `flite` or `openai-whisper` is not installed (fixes CI)
- Fixed `test_cli_version` assertion for v0.1.3

### Removed
- Blank demo SVG from README (will be replaced with proper recording later)

## [0.1.3] - 2026-05-07

### Fixed
- Made `openai-whisper` imports lazy so CI/tests pass without the optional `[ai]` dependency
- Fixed `test_cli_version` assertion for v0.1.2

## [0.1.2] - 2026-05-07

### Fixed
- Fixed author email in `pyproject.toml` (`codinglone@example.com` → `codinglone@gmail.com`)
- Added missing Pydantic validator for `speaking_rate_range` (length, ordering, non-negative)
- Fixed test assertions to match updated default config values

### Added
- GitHub Actions CI workflow running pytest across Python 3.9–3.12
- CI badge in README
- Terminal demo recording (`demo/demo.svg`) for README
- Issue templates and contributing guidelines

### Changed
- NEXT_STEPS.md narrative flipped: deterministic-first, Whisper as optional footnote

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
