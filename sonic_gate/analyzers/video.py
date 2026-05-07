"""Video analyzer - extracts metadata and audio for analysis."""

import json
import subprocess
import tempfile
from pathlib import Path

from sonic_gate.analyzers.base import BaseAnalyzer
from sonic_gate.core.result import AnalysisResult


class VideoAnalyzer(BaseAnalyzer):
    VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv"}

    def analyze(self, file_path: str, result: AnalysisResult) -> None:
        ext = Path(file_path).suffix.lower()
        if ext not in self.VIDEO_EXTENSIONS:
            return

        metadata = self._get_video_metadata(file_path)
        if metadata:
            result.add_metric("video_duration", metadata.get("duration"))
            result.add_metric("video_resolution", metadata.get("resolution"))
            result.add_metric("video_codec", metadata.get("video_codec"))
            result.add_metric("audio_codec", metadata.get("audio_codec"))

        if self.config.video.extract_audio:
            audio_path = self._extract_audio(file_path)
            if audio_path:
                result.add_metric("extracted_audio", audio_path)

    def _get_video_metadata(self, file_path: str) -> dict:
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-show_entries", "stream=codec_name,width,height",
                "-of", "json",
                file_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            data = json.loads(result.stdout)

            metadata = {"duration": float(data.get("format", {}).get("duration", 0))}

            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    w = stream.get("width", 0)
                    h = stream.get("height", 0)
                    metadata["resolution"] = f"{w}x{h}"
                    metadata["video_codec"] = stream.get("codec_name")
                elif stream.get("codec_type") == "audio":
                    metadata["audio_codec"] = stream.get("codec_name")

            return metadata
        except Exception:
            return {}

    def _extract_audio(self, file_path: str) -> str:
        try:
            temp_dir = tempfile.gettempdir()
            base = Path(file_path).stem
            output = Path(temp_dir) / f"{base}_extracted.wav"

            stream = self.config.video.audio_stream
            cmd = [
                "ffmpeg", "-i", file_path,
                "-map", f"0:a:{stream}",
                "-acodec", "pcm_s16le",
                "-ar", "48000",
                "-ac", "1",
                "-y", str(output),
            ]
            subprocess.run(cmd, capture_output=True, check=True, timeout=30)
            return str(output)
        except Exception:
            return ""
