import re
from pathlib import Path

import librosa
import numpy as np

from backend.models.schemas import VoiceConfidenceResult


class VoiceConfidenceService:
    def analyze(self, audio_path: Path, duration_seconds: float | None = None) -> VoiceConfidenceResult:
        y, sr = librosa.load(str(audio_path), sr=22050, mono=True)
        duration = duration_seconds or float(librosa.get_duration(y=y, sr=sr))

        speaking_rate_wpm = self._speaking_rate_wpm(y, sr, duration)
        pitch_variance = self._pitch_variance(y, sr)
        pause_ratio = self._pause_ratio(y, sr)
        score = self._confidence_score(speaking_rate_wpm, pitch_variance, pause_ratio)

        return VoiceConfidenceResult(
            score=round(score, 2),
            speaking_rate_wpm=round(speaking_rate_wpm, 1),
            pitch_variance=round(pitch_variance, 4),
            pause_ratio=round(pause_ratio, 4),
            duration_seconds=round(duration, 2),
        )

    @staticmethod
    def _speaking_rate_wpm(y: np.ndarray, sr: int, duration: float) -> float:
        intervals = librosa.effects.split(y, top_db=28)
        speech_seconds = sum((end - start) / sr for start, end in intervals)
        speech_seconds = max(speech_seconds, duration * 0.3, 1.0)
        # Proxy syllable rate from energy peaks, scaled to approximate WPM
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        peaks = librosa.util.peak_pick(onset_env, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.1, wait=10)
        syllables_per_sec = len(peaks) / speech_seconds if speech_seconds else 0
        return syllables_per_sec * 15  # rough syllables-to-words conversion

    @staticmethod
    def _pitch_variance(y: np.ndarray, sr: int) -> float:
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=75, fmax=400)
        voiced = pitches[magnitudes > np.median(magnitudes)]
        voiced = voiced[voiced > 0]
        if len(voiced) < 5:
            return 0.0
        return float(np.std(voiced) / max(np.mean(voiced), 1.0))

    @staticmethod
    def _pause_ratio(y: np.ndarray, sr: int) -> float:
        intervals = librosa.effects.split(y, top_db=28)
        if not len(intervals):
            return 1.0
        speech_samples = sum(end - start for start, end in intervals)
        return 1.0 - (speech_samples / max(len(y), 1))

    @staticmethod
    def _confidence_score(speaking_rate_wpm: float, pitch_variance: float, pause_ratio: float) -> float:
        # Speaking rate: best around 110-170 wpm
        if 110 <= speaking_rate_wpm <= 170:
            rate_score = 100.0
        elif speaking_rate_wpm < 110:
            rate_score = max(40.0, 100.0 - (110 - speaking_rate_wpm) * 1.2)
        else:
            rate_score = max(40.0, 100.0 - (speaking_rate_wpm - 170) * 1.5)

        # Moderate pitch variation signals confidence; too flat or too erratic is penalized
        if 0.08 <= pitch_variance <= 0.35:
            pitch_score = 100.0
        elif pitch_variance < 0.08:
            pitch_score = max(50.0, 100.0 - (0.08 - pitch_variance) * 400)
        else:
            pitch_score = max(50.0, 100.0 - (pitch_variance - 0.35) * 120)

        # Some pauses are natural; too many long pauses reduce confidence
        if pause_ratio <= 0.35:
            pause_score = 100.0 - pause_ratio * 80
        else:
            pause_score = max(30.0, 100.0 - pause_ratio * 140)

        return rate_score * 0.35 + pitch_score * 0.35 + pause_score * 0.30


voice_confidence_service = VoiceConfidenceService()
