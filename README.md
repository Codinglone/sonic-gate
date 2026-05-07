# Sonic Gate

> Stop paying humans to listen to corrupted audio files. Fix them automatically.

Sonic Gate is a CLI-first audio/video quality gate that uses deterministic audio analysis to catch corrupted, invalid, or low-quality audio files before they reach human reviewers or downstream pipelines.

**Optional AI Probe:** Includes an experimental Whisper-based speech quality probe (disabled by default) for users who want to detect language mismatches or speech quality issues.

## Features

- **Traditional Analysis (Fast & Deterministic):**
  - LUFS loudness measurement (FFmpeg ebur128)
  - Silence detection (pydub)
  - Duration validation
  - Format/corruption checking
- **Video Support:** Auto-extract audio from MP4, MOV, AVI, MKV, WebM
- **Fix Mode:** Auto-trim silence, normalize LUFS, non-destructive repairs
- **Multiple Formats:** Table, JSON, CSV, Markdown output
- **Optional AI Probe:** Whisper-based speech detection (off by default)

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
# Analyze a single file (deterministic only, fast)
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

### Default (Deterministic Only - Fast)

```yaml
rules:
  traditional:
    max_silence_seconds: 3.0
    lufs_range: [-24, -16]
  
  ai_probe:
    enabled: false  # Whisper is OFF by default

output:
  format: table
  show_passed: false
```

### With AI Probe Enabled (Experimental)

```yaml
rules:
  traditional:
    max_silence_seconds: 3.0
    lufs_range: [-24, -16]
  
  ai_probe:
    enabled: true           # Enable Whisper
    whisper_model: base     # tiny/base/small/medium/large
    min_confidence: -1.0    # Logprob threshold (negative values)
    expected_language: en   # Optional language check
    speaking_rate_range: [100, 180]

fix:
  enabled: false
  output_dir: ./fixed
  normalize_lufs: -16.0

output:
  format: table
  show_passed: false
```

**Note:** The AI probe uses Whisper logprob-based confidence scores which are always negative. Typical values range from -0.5 (good) to -5.0 (poor). Adjust `min_confidence` based on your audio quality and language.

## Performance

| Analyzer | Speed | Notes |
|----------|-------|-------|
| Traditional (LUFS, silence, format) | ~4ms/file | Deterministic, always accurate |
| AI Probe (Whisper tiny) | ~200ms/file | Optional, experimental |
| Video extraction | +100ms/file | One-time FFmpeg extract |

**Recommendation:** Use traditional analysis for batch processing. Enable AI probe only when you need speech-specific checks.

## Requirements

- Python 3.9+
- FFmpeg (for LUFS and video support)

## License

MIT
