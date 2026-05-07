import pytest
from pathlib import Path
from sonic_gate.config import Config, load_config


def test_default_config():
    config = Config()
    assert config.rules.traditional.max_silence_seconds == 3.0
    assert config.rules.ai_probe.min_confidence == 0.8
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


def test_config_validation():
    with pytest.raises(ValueError):
        Config(rules={"traditional": {"lufs_range": [-30]}})  # Need 2 values


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
