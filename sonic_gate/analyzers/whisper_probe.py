"""AI probe using OpenAI Whisper for quality analysis."""

from typing import Optional

from sonic_gate.analyzers.base import BaseAnalyzer
from sonic_gate.core.result import AnalysisResult


class WhisperProbe(BaseAnalyzer):
    _model_cache = {}

    def __init__(self, config):
        super().__init__(config)
        self.model = None

    def _load_model(self):
        import warnings
        import whisper

        warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

        if self.model is not None:
            return

        model_name = self.config.rules.ai_probe.whisper_model
        if model_name in self._model_cache:
            self.model = self._model_cache[model_name]
            return

        self.model = whisper.load_model(model_name)
        self._model_cache[model_name] = self.model

    def analyze(self, file_path: str, result: AnalysisResult) -> None:
        import whisper

        # Skip if AI probe not configured
        if not self.config.rules.ai_probe:
            return

        self._load_model()

        try:
            audio = whisper.load_audio(file_path)
            audio = whisper.pad_or_trim(audio)

            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            result.add_metric("whisper_language", detected_lang)
            result.add_metric("whisper_language_prob", round(probs[detected_lang], 4))

            # Transcribe
            decode_options = {"language": detected_lang, "fp16": False}
            transcription = self.model.transcribe(file_path, **decode_options)

            segments = transcription.get("segments", [])
            if not segments:
                result.add_failure(
                    "speech_detection",
                    actual="no speech detected",
                    expected="speech",
                )
                return

            # Calculate average confidence
            confidences = [seg.get("avg_logprob", -1.0) for seg in segments]
            avg_confidence = sum(confidences) / len(confidences)
            result.add_metric("whisper_confidence", round(avg_confidence, 4))

            min_conf = self.config.rules.ai_probe.min_confidence
            if avg_confidence < min_conf:
                result.add_failure(
                    "min_confidence",
                    actual=round(avg_confidence, 4),
                    expected=f">={min_conf}",
                )

            # Language check
            expected_lang = self.config.rules.ai_probe.expected_language
            if expected_lang and detected_lang != expected_lang:
                result.add_failure(
                    "language",
                    actual=detected_lang,
                    expected=expected_lang,
                )

            # Speaking rate
            total_words = sum(len(seg.get("text", "").split()) for seg in segments)
            duration = transcription.get("duration")
            if duration is None and segments:
                duration = segments[-1].get("end", 0)
            duration_min = (duration or 0) / 60.0
            if duration_min > 0:
                wpm = total_words / duration_min
                result.add_metric("speaking_rate_wpm", round(wpm, 1))

                min_wpm, max_wpm = self.config.rules.ai_probe.speaking_rate_range
                if wpm < min_wpm or wpm > max_wpm:
                    result.add_failure(
                        "speaking_rate",
                        actual=f"{wpm:.0f} wpm",
                        expected=f"[{min_wpm}, {max_wpm}]",
                    )

            # Crosstalk (simple heuristic: many short segments)
            if self.config.rules.ai_probe.detect_crosstalk:
                short_segments = sum(1 for seg in segments if seg.get("end", 0) - seg.get("start", 0) < 1.0)
                if len(segments) > 0 and short_segments / len(segments) > 0.5:
                    result.add_failure(
                        "crosstalk",
                        actual=f"{short_segments}/{len(segments)} short segments",
                        expected="<50% short segments",
                    )

        except Exception as e:
            result.add_failure(
                "whisper_error",
                actual=str(e),
                expected="successful analysis",
                message=f"Whisper analysis failed: {e}",
            )
