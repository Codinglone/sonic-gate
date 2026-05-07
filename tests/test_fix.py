import wave
import numpy as np
from pathlib import Path

from sonic_gate.config import Config
from sonic_gate.fix.engine import FixEngine
from sonic_gate.fix.trimmer import SilenceTrimmer
from sonic_gate.fix.normalizer import LUFSNormalizer


def create_test_wav(path: str, duration_sec: float = 2.0, freq: float = 440, amp: float = 0.3):
    sample_rate = 48000
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec))
    audio = np.sin(2 * np.pi * freq * t) * amp
    audio_int = (audio * 32767).astype(np.int16)

    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(audio_int.tobytes())


def test_silence_trimmer(tmp_path: Path):
    wav = str(tmp_path / "test.wav")
    create_test_wav(wav, duration_sec=2.0)

    trimmer = SilenceTrimmer(threshold_db=-50, min_silence_ms=100)
    result = trimmer.trim(wav)

    assert Path(result).exists()


def test_lufs_normalizer(tmp_path: Path):
    wav = str(tmp_path / "test.wav")
    create_test_wav(wav, duration_sec=2.0, amp=0.1)  # Quiet

    normalizer = LUFSNormalizer(target_lufs=-16.0)
    result = normalizer.normalize(wav)

    assert Path(result).exists()


def test_fix_engine(tmp_path: Path):
    wav = str(tmp_path / "test.wav")
    create_test_wav(wav, duration_sec=2.0)

    config = Config()
    config.fix.enabled = True
    config.fix.output_dir = str(tmp_path / "fixed")
    config.fix.dry_run = False

    engine = FixEngine(config)
    fixed = engine.fix(wav)

    assert fixed is not None
    assert Path(fixed).exists()
