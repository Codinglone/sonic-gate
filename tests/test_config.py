import pytest
from pathlib import Path
from sonic_gate.config import Config, load_config


def test_default_config():
    config = Config()
    assert config.rules.traditional.max_silence_seconds == 3.0
    assert config.rules.ai_probe.min_confidence == -1.0
    assert config.rules.ai_probe.enabled == False
    assert config.output.format == "table"


def test_config_from_dict():
    data = {
        "rules": {
            "traditional": {"max_silence_seconds": 5.0},
            "ai_probe": {"min_confidence": 0.9},
        },
        "output": {"format": "json"},
    }
    config = Config.model_validate(data)
    assert config.rules.traditional.max_silence_seconds == 5.0
    assert config.rules.ai_probe.min_confidence == 0.9
    assert config.output.format == "json"


def test_config_validation_lufs_range_length():
    with pytest.raises(ValueError):
        Config(rules={"traditional": {"lufs_range": [-30]}})  # Need 2 values


def test_config_validation_lufs_range_min_ge_max():
    with pytest.raises(ValueError):
        Config(rules={"traditional": {"lufs_range": [-16.0, -24.0]}})  # min >= max


def test_config_validation_invalid_whisper_model():
    with pytest.raises(ValueError):
        Config(rules={"ai_probe": {"whisper_model": "invalid_model"}})


def test_config_validation_invalid_output_format():
    with pytest.raises(ValueError):
        Config(output={"format": "xml"})


def test_config_validation_speaking_rate_range_length():
    with pytest.raises(ValueError):
        Config(rules={"ai_probe": {"speaking_rate_range": [100.0]}})  # Need 2 values


def test_config_validation_speaking_rate_range_min_ge_max():
    with pytest.raises(ValueError):
        Config(rules={"ai_probe": {"speaking_rate_range": [200.0, 100.0]}})  # min >= max


def test_config_validation_speaking_rate_range_negative():
    with pytest.raises(ValueError):
        Config(rules={"ai_probe": {"speaking_rate_range": [-10.0, 100.0]}})  # negative value


def test_load_config_from_file(tmp_path: Path):
    config_file = tmp_path / "test.yaml"
    config_file.write_text("""
rules:
  traditional:
    max_silence_seconds: 2.0
output:
  format: csv
""")
    config = load_config(str(config_file))
    assert config.rules.traditional.max_silence_seconds == 2.0
    assert config.output.format == "csv"
