"""Configuration models and loader."""

from pathlib import Path
from typing import Optional, List

import yaml
from pydantic import BaseModel, Field, field_validator


class TraditionalRules(BaseModel):
    max_silence_seconds: float = 3.0
    lufs_range: List[float] = Field(default_factory=lambda: [-24.0, -16.0])
    min_duration_seconds: float = 1.0
    max_duration_seconds: float = 3600.0

    @field_validator("lufs_range")
    @classmethod
    def validate_lufs_range(cls, v: List[float]) -> List[float]:
        if len(v) != 2:
            raise ValueError("lufs_range must have exactly 2 values [min, max]")
        if v[0] >= v[1]:
            raise ValueError("lufs_range[0] must be less than lufs_range[1]")
        return v


class AiProbeRules(BaseModel):
    enabled: bool = False
    whisper_model: str = "base"
    min_confidence: float = Field(-1.0, le=1.0)
    expected_language: Optional[str] = None
    detect_crosstalk: bool = False
    speaking_rate_range: List[float] = Field(default_factory=lambda: [100.0, 180.0])

    @field_validator("whisper_model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        allowed = {"tiny", "base", "small", "medium", "large"}
        if v not in allowed:
            raise ValueError(f"whisper_model must be one of {allowed}")
        return v

    @field_validator("speaking_rate_range")
    @classmethod
    def validate_speaking_rate_range(cls, v: List[float]) -> List[float]:
        if len(v) != 2:
            raise ValueError("speaking_rate_range must have exactly 2 values [min, max]")
        if v[0] >= v[1]:
            raise ValueError("speaking_rate_range[0] must be less than speaking_rate_range[1]")
        if v[0] < 0:
            raise ValueError("speaking_rate_range values must be non-negative")
        return v


class VideoConfig(BaseModel):
    extract_audio: bool = True
    audio_stream: int = 0


class FixConfig(BaseModel):
    enabled: bool = False
    output_dir: str = "./fixed"
    trim_silence: bool = True
    silence_threshold: float = -50.0
    normalize_lufs: Optional[float] = -16.0
    remove_dc_offset: bool = True
    soft_limit: bool = True
    dry_run: bool = False


class OutputConfig(BaseModel):
    format: str = "table"
    show_passed: bool = False
    verbose: bool = False

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        allowed = {"table", "json", "csv", "markdown"}
        if v not in allowed:
            raise ValueError(f"format must be one of {allowed}")
        return v


class RulesConfig(BaseModel):
    traditional: TraditionalRules = Field(default_factory=TraditionalRules)
    ai_probe: AiProbeRules = Field(default_factory=AiProbeRules)


class Config(BaseModel):
    rules: RulesConfig = Field(default_factory=RulesConfig)
    video: VideoConfig = Field(default_factory=VideoConfig)
    fix: FixConfig = Field(default_factory=FixConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)


def load_config(path: str) -> Config:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(config_path, "r") as f:
        data = yaml.safe_load(f)

    return Config.model_validate(data)
