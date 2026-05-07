# Sonic Gate - Design Specification

**Date:** 2026-05-07  
**Status:** Draft - Pending Review  
**Author:** Codinglone 

---

## 1. Product Concept

Sonic Gate is a CLI-first audio/video quality gate that combines traditional audio metrics with AI probing to catch corrupted, invalid, or low-quality audio files before they reach human reviewers or downstream pipelines. Includes an auto-repair mode that fixes common audio problems.

**The Hook:** We use OpenAI Whisper—not to transcribe, but as a free quality engineer. Nobody in FOSS uses Whisper this way. We analyze its confidence scores, language detection, and metadata to catch problems that silence/LUFS metrics completely miss.

**Tagline:** *Stop paying humans to listen to corrupted audio files. Fix them automatically.*

---

## 2. Problem Statement

ML teams, podcast networks, research labs, and data collection platforms waste hours of human review on audio that is:
- Corrupted (static, encoding errors)
- In the wrong language
- Empty or nearly silent
- Unintelligible (bad mic, muffled, far from speaker)
- Wrong content type (music instead of speech)
- Sped up or slowed down
- Video files with corrupted or missing audio tracks

**Current solutions:**
- Manual listening: slow, expensive, doesn't scale
- FFmpeg analysis: catches silence/LUFS, misses everything else
- Enterprise QA platforms: $500+/month, overkill for most teams

**Sonic Gate:** Free, open-source, runs locally, catches 90% of bad audio in milliseconds.

---

## 3. Target Users

1. **ML/Data Engineers** — validating training datasets before labeling
2. **Podcast Producers** — batch-checking recordings before editing
3. **Research Labs** — ensuring interview/field recording quality
4. **QA Automation Teams** — gating audio in CI/CD pipelines
5. **Content Moderation Teams** — pre-filtering user-uploaded audio/video
6. **Video Creators** — validating audio tracks in video files before publishing

---

## 4. Core Features

### 4.1 Traditional Analysis (Existing Cython Engine)
- **LUFS calculation** — integrated loudness (EBU R 128 compliant via FFmpeg, fast via Cython)
- **Silence detection** — longest continuous silence segment
- **Duration validation** — file length checks
- **Format validation** — corrupt file detection

### 4.2 AI Probe (Whisper Integration)
- **Speech detection** — does the file contain speech? (vs music, noise, silence)
- **Language validation** — is it the expected language?
- **Confidence scoring** — low confidence = bad audio quality (muffled, noisy, corrupted)
- **Speaking rate analysis** — too fast/slow = possible manipulation or bad recording
- **Crosstalk detection** — multiple overlapping speakers

### 4.3 Video Support
- **Auto-extract audio** — accepts `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`; extracts audio track via FFmpeg for analysis
- **Video metadata** — reports resolution, duration, codec as additional context
- **Unified reporting** — video files analyzed alongside audio files in the same run
- **Audio stream selection** — supports multi-track video (e.g., choose stream 0:1 vs 0:2)

### 4.4 Fix Mode (Auto-Repair)
- **Trim silence** — remove leading/trailing silence and optionally internal silent gaps longer than threshold
- **Normalize LUFS** — adjust gain to target integrated loudness (e.g., -16 LUFS for podcasts, -23 for broadcast)
- **Remove DC offset** — fix DC bias in recordings
- **Soft limiting** — prevent clipping when normalizing
- **Non-destructive** — outputs repaired files to `./fixed/` directory with original filenames preserved
- **Preview mode** — `sonic-gate --fix --dry-run` shows what would change without writing files

### 4.5 CLI Interface
```bash
# Check single file
sonic-gate interview.wav

# Check directory
sonic-gate ./recordings/

# With config
sonic-gate --config gate.yaml ./podcasts/

# Output formats
sonic-gate --format json ./files/ > report.json
sonic-gate --format csv ./files/ > report.csv
sonic-gate --format markdown ./files/ > report.md

# Demo mode (ships with sample files)
sonic-gate --demo

# Video files (auto-extract audio)
sonic-gate interview.mp4

# Fix mode — auto-repair failed files
sonic-gate --fix ./recordings/

# Fix with preview (dry run)
sonic-gate --fix --dry-run ./recordings/

# Performance benchmark
sonic-gate --benchmark ./test-files/
```

### 4.6 Configuration (YAML)
```yaml
# sonic-gate.yaml
rules:
  traditional:
    max_silence_seconds: 3.0
    lufs_range: [-24, -16]
    min_duration_seconds: 1.0
    max_duration_seconds: 3600
  
  ai_probe:
    whisper_model: base      # tiny/base/small/medium
    min_confidence: 0.8      # speech intelligibility (0-1)
    expected_language: en    # null to skip language check
    detect_crosstalk: true   # flag multiple speakers
    speaking_rate_range: [100, 180]  # words per minute
    
video:
  extract_audio: true      # auto-extract from video files
  audio_stream: 0          # which audio stream to use
  
fix:
  enabled: false           # auto-repair failed files
  output_dir: ./fixed/     # where to write fixed files
  trim_silence: true       # remove leading/trailing silence
  silence_threshold: -50   # dBFS for silence detection
  normalize_lufs: -16.0    # target LUFS (null to skip)
  remove_dc_offset: true   # fix DC bias
  soft_limit: true         # prevent clipping
  dry_run: false           # preview without writing
  
output:
  format: table            # table/json/csv/markdown
  show_passed: false       # only show failures
  verbose: false           # include raw metrics
```

### 4.7 Output Examples

**Table (default):**
```
File                          Status    Failures
interview_001.wav             PASS      —
interview_002.wav             FAIL      confidence: 0.32 (min: 0.8)
interview_003.wav             FAIL      language: fr (expected: en)
interview_004.wav             FAIL      silence: 5.2s (max: 3.0s)
interview_005.wav             FAIL      no_speech_detected
```

**JSON (for CI/pipelines):**
```json
{
  "summary": {"total": 5, "passed": 1, "failed": 4},
  "results": [
    {
      "file": "interview_002.wav",
      "passed": false,
      "failures": [
        {"rule": "min_confidence", "actual": 0.32, "expected": 0.8}
      ],
      "metrics": {
        "lufs": -18.5,
        "silence_seconds": 0.5,
        "duration_seconds": 245.3,
        "whisper_confidence": 0.32,
        "detected_language": "en",
        "speaking_rate_wpm": 142
      }
    }
  ]
}
```

---

## 5. Architecture

```
┌─────────────────────────────────────┐
│         sonic-gate CLI              │
│  • Argument parsing                 │
│  • File discovery                   │
│  • Config loading                   │
│  • Report generation                │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌──────────────┐    ┌──────────────┐
│  Traditional │    │  AI Probe    │
│  Analysis    │    │  (Whisper)   │
│  (Cython)    │    │              │
│  • LUFS      │    │  • Language  │
│  • Silence   │    │  • Confidence│
│  • Duration  │    │  • Crosstalk │
│  • Format    │    │  • Speaking  │
│  • Video     │    │    rate      │
│    extract   │    └──────────────┘
└──────────────┘
               │
               ▼
         ┌──────────────┐
         │  Result      │
         │  Aggregator  │
         └──────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
┌──────────────┐ ┌──────────────┐
│   Reporter   │ │  Fix Engine  │
│(Table/JSON/  │ │  • Trim      │
│ CSV/MD)      │ │  • Normalize │
└──────────────┘ │  • DC offset │
                 └──────────────┘
```

**Key Design Decisions:**
- **No backend, no database, no message queue** — runs entirely locally
- **Modular analyzers** — each check is a plugin, easy to add new ones
- **Lazy Whisper loading** — only initialize AI if AI rules are configured
- **Parallel processing** — analyze multiple files concurrently

---

## 6. Technology Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| Language | Python 3.9+ | Wide adoption, easy to contribute |
| CLI Framework | Typer | Modern, typed, auto-generates help text |
| Audio Processing | Cython + NumPy | Reuse existing fast engine |
| Audio I/O | pydub + FFmpeg | Reliable format support |
| AI Probe | openai-whisper | Runs on CPU, no API key needed |
| Config | PyYAML | Standard, human-readable |
| Output | rich (tables) | Beautiful terminal output |
| Testing | pytest | Standard Python testing |
| Packaging | setuptools | pip installable |

---

## 7. Project Structure

```
sonic-gate/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── Makefile
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── DESIGN.md
│   ├── USAGE.md
│   └── BENCHMARKS.md
├── demo/
│   ├── good_interview.wav
│   ├── wrong_language.wav
│   ├── corrupted_noise.wav
│   ├── muffled_mic.wav
│   ├── empty_file.wav
│   └── video_bad_audio.mp4
├── sonic_gate/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   │   ├── result.py
│   │   └── reporter.py
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── lufs.py
│   │   ├── silence.py
│   │   ├── duration.py
│   │   ├── format.py
│   │   ├── video.py
│   │   └── whisper_probe.py
│   └── fix/
│       ├── __init__.py
│       ├── trimmer.py
│       ├── normalizer.py
│       └── dc_offset.py
│   └── cython_modules/
│       ├── __init__.py
│       ├── fast_lufs.pyx
│       ├── fast_rms.pyx
│       └── fast_silence.pyx
├── tests/
│   ├── __init__.py
│   ├── test_analyzers.py
│   ├── test_cli.py
│   └── test_config.py
└── scripts/
    ├── build_cython.sh
    └── benchmark.py
```

---

## 8. Performance Strategy

**The 58x Story:**
- FFmpeg path: ~218ms per file (accurate but slow)
- Cython path: ~3.8ms per file (fast, good accuracy)
- Whisper probe: ~150-400ms per file (CPU, base model)

**Combined:** Traditional analysis (Cython) + AI probe = ~200ms per file on CPU.

**Parallelization:** Process N files concurrently where N = CPU cores.

**Benchmark output ships with the tool** so users can verify claims on their own hardware.

---

## 9. Distribution Strategy

| Channel | Priority | Effort |
|---------|----------|--------|
| `pip install sonic-gate` | P0 | Low |
| `docker run sonic-gate` | P0 | Low |
| GitHub Action | P1 | Medium |
| pre-commit hook | P1 | Low |
| Homebrew | P2 | Medium |
| conda | P2 | Medium |

---

## 10. FOSS Adoption Strategy

### What Gets Stars
1. **Demo mode** — `sonic-gate --demo` shows instant value
2. **Clear README** — problem, solution, one-liner install, screenshot
3. **Benchmarks** — verifiable performance claims
4. **Real use cases** — examples for podcasts, ML datasets, research
5. **Easy contribution** — single language, modular analyzers

### Launch Plan
1. **Hacker News post:** "We use Whisper as a $0 quality engineer"
2. **r/MachineLearning:** "Validate your audio datasets before labeling"
3. **r/podcasting:** "Batch-check your recordings before editing"
4. **GitHub trending:** via README quality + demo + benchmarks

---

## 11. Milestones

### v0.1 — MVP (Week 1-2)
- [ ] CLI skeleton (Typer)
- [ ] Traditional analyzers (LUFS, silence, duration, format)
- [ ] Video support (auto-extract audio)
- [ ] Basic table output
- [ ] YAML config support
- [ ] `--demo` mode with 5 sample files

### v0.2 — AI Probe (Week 3)
- [ ] Whisper integration
- [ ] Confidence scoring
- [ ] Language detection
- [ ] Speaking rate analysis
- [ ] JSON/CSV/Markdown output

### v0.3 — Fix Mode (Week 4)
- [ ] Auto-trim silence
- [ ] LUFS normalization
- [ ] DC offset removal
- [ ] Soft limiting
- [ ] Dry-run preview
- [ ] Output to `./fixed/` directory

### v0.4 — Polish (Week 5)
- [ ] Parallel processing
- [ ] Rich terminal tables
- [ ] Benchmark command
- [ ] Full test coverage
- [ ] Progress bar for batch ops

### v0.5 — Distribution (Week 6)
- [ ] PyPI release
- [ ] Docker image
- [ ] GitHub Action
- [ ] README with screenshots

### v1.0 — Launch (Week 7)
- [ ] Hacker News / Reddit launch
- [ ] Homebrew formula
- [ ] First community contributions

---

## 12. What We're NOT Building

- ❌ Web UI
- ❌ User authentication
- ❌ Cloud hosting
- ❌ Multi-tenant platform
- ❌ Real-time processing
- ❌ GPU acceleration (Whisper runs fine on CPU)
- ❌ Custom model training
- ✅ Video support (audio extraction via FFmpeg)
- ✅ Fix mode (auto-repair failed files)

**Scope guard:** If a feature requires a database, a server, a user account, or cloud infrastructure, it's out of scope. Video support and fix mode are in scope because they run entirely locally using FFmpeg.

---

## 13. Open Questions

1. Should we support remote files (S3 URLs) or local only?
2. Should fix mode support batch processing with different targets per file type?
3. Should we add a progress bar for long-running batch operations?

---

**Next Step:** Review this design, then create implementation plan.
