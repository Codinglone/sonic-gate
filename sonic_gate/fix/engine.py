"""Fix engine that coordinates audio repairs."""

import shutil
from pathlib import Path

from sonic_gate.config import Config
from sonic_gate.fix.trimmer import SilenceTrimmer
from sonic_gate.fix.normalizer import LUFSNormalizer


class FixEngine:
    def __init__(self, config: Config):
        self.config = config
        self.trimmer = SilenceTrimmer(
            threshold_db=config.fix.silence_threshold,
            min_silence_ms=100,
        )
        self.normalizer = LUFSNormalizer(
            target_lufs=config.fix.normalize_lufs,
        )

    def fix(self, file_path: str) -> str:
        if self.config.fix.dry_run:
            return self._dry_run(file_path)

        output_dir = Path(self.config.fix.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        current = file_path

        if self.config.fix.trim_silence:
            current = self.trimmer.trim(current)

        if self.config.fix.normalize_lufs is not None:
            current = self.normalizer.normalize(current)

        # Copy to output directory
        dest = output_dir / Path(file_path).name
        shutil.copy2(current, dest)

        return str(dest)

    def _dry_run(self, file_path: str) -> str:
        print(f"[DRY RUN] Would fix: {file_path}")
        if self.config.fix.trim_silence:
            print("  - Trim silence")
        if self.config.fix.normalize_lufs:
            print(f"  - Normalize to {self.config.fix.normalize_lufs} LUFS")
        return file_path
