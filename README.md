# Sonic Gate

> Stop paying humans to listen to corrupted audio files. Fix them automatically.

Sonic Gate is a CLI-first audio/video quality gate that combines traditional audio metrics with AI probing to catch corrupted, invalid, or low-quality audio files before they reach human reviewers or downstream pipelines.

**The Hook:** We use OpenAI Whisper -- not to transcribe, but as a free quality engineer. Nobody in FOSS uses Whisper this way.

## Features

- **Traditional Analysis:** LUFS, silence detection, duration validation, format checking
- **AI Probe:** Speech detection, language validation, confidence scoring, speaking rate analysis
- **Video Support:** Auto-extract audio from MP4, MOV, AVI, MKV, WebM
- **Fix Mode:** Auto-trim silence, normalize LUFS, non-destructive repairs
- **Multiple Formats:** Table, JSON, CSV, Markdown output
- **Fast:** Cython-accelerated processing where available

## Installation

```bash
pip install sonic-gate
```

Or install from source:

```bash
git clone https://github.com/yourusername/sonic-gate.git
cd sonic-gate
pip install -e .
```

## Quick Start

```bash
# Analyze a single file
sonic-gate interview.wav

# Analyze a directory
sonic-gate ./recordings/

# With custom config
sonic-gate --config gate.yaml ./podcasts/

# Fix failed files automatically
sonic-gate --fix ./recordings/

# JSON output for CI
sonic-gate --format json ./files/ > report.json

# Demo mode
sonic-gate --demo
```

## Configuration

Create `sonic-gate.yaml`:

```yaml
rules:
  traditional:
    max_silence_seconds: 3.0
    lufs_range: [-24, -16]
  
  ai_probe:
    whisper_model: base
    min_confidence: 0.8
    expected_language: en

fix:
  enabled: false
  output_dir: ./fixed
  normalize_lufs: -16.0

output:
  format: table
  show_passed: false
```

## Performance

| Metric | Value |
|--------|-------|
| Traditional analysis | ~4ms per file (Cython) |
| AI probe (Whisper tiny) | ~200ms per file (CPU) |
| Combined | ~200ms per file |

## Requirements

- Python 3.9+
- FFmpeg (for LUFS and video support)

## License

MIT
