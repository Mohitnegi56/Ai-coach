import re

from models.schemas import CommunicationResult, FillerWordResult, VoiceConfidenceResult


class CommunicationScoreService:
    def score(
        self,
        transcript: str,
        filler: FillerWordResult,
        voice: VoiceConfidenceResult | None = None,
        duration_seconds: float | None = None,
    ) -> CommunicationResult:
        structure_score = self._sentence_structure_score(transcript)
        filler_score = self._filler_score(filler.per_minute)

        if voice:
            speaking_rate_wpm = voice.speaking_rate_wpm
            rate_score = self._speaking_rate_score(speaking_rate_wpm)
            overall = rate_score * 0.35 + filler_score * 0.35 + structure_score * 0.30
            voice_confidence = voice.score
            pitch_variance = voice.pitch_variance
            pause_ratio = voice.pause_ratio
        else:
            duration = duration_seconds or max(len(transcript.split()) / 2.5, 1.0)
            speaking_rate_wpm = self._estimate_wpm(transcript, duration)
            rate_score = self._speaking_rate_score(speaking_rate_wpm)
            overall = rate_score * 0.45 + filler_score * 0.35 + structure_score * 0.20
            voice_confidence = None
            pitch_variance = None
            pause_ratio = None

        return CommunicationResult(
            score=round(max(0.0, min(100.0, overall)), 2),
            speaking_rate_score=round(rate_score, 2),
            filler_score=round(filler_score, 2),
            structure_score=round(structure_score, 2),
            voice_confidence=voice_confidence,
            speaking_rate_wpm=speaking_rate_wpm,
            pitch_variance=pitch_variance,
            pause_ratio=pause_ratio,
            filler_words=filler,
        )

    @staticmethod
    def _estimate_wpm(transcript: str, duration_seconds: float) -> float:
        words = len(re.findall(r"\b\w+\b", transcript))
        return round(words / max(duration_seconds / 60.0, 0.01), 1)

    @staticmethod
    def _speaking_rate_score(wpm: float) -> float:
        if 120 <= wpm <= 160:
            return 100.0
        if wpm < 120:
            return max(45.0, 100.0 - (120 - wpm) * 1.5)
        return max(45.0, 100.0 - (wpm - 160) * 1.8)

    @staticmethod
    def _filler_score(per_minute: float) -> float:
        if per_minute <= 2:
            return 100.0
        if per_minute <= 6:
            return max(50.0, 100.0 - (per_minute - 2) * 10)
        return max(20.0, 100.0 - (per_minute - 6) * 8)

    @staticmethod
    def _sentence_structure_score(transcript: str) -> float:
        sentences = [s.strip() for s in re.split(r"[.!?]+", transcript) if s.strip()]
        if not sentences:
            return 30.0

        words = re.findall(r"\b\w+\b", transcript)
        avg_len = len(words) / len(sentences)
        complete = sum(1 for s in sentences if len(re.findall(r"\b\w+\b", s)) >= 4)

        length_score = 100.0 if 8 <= avg_len <= 28 else max(50.0, 100.0 - abs(avg_len - 16) * 3)
        completeness = (complete / len(sentences)) * 100
        return length_score * 0.55 + completeness * 0.45


communication_score_service = CommunicationScoreService()
