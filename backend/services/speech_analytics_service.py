from pathlib import Path

from models.schemas import SpeechAnalyticsResponse
from services.audio_utils import write_audio_bytes
from services.communication_score_service import communication_score_service
from services.filler_word_service import filler_word_service
from services.voice_confidence_service import voice_confidence_service


class SpeechAnalyticsService:
    def analyze(
        self,
        audio_bytes: bytes,
        transcript: str,
        suffix: str = ".webm",
        duration_seconds: float | None = None,
    ) -> SpeechAnalyticsResponse:
        duration = duration_seconds or max(len(transcript.split()) / 2.5, 1.0)
        filler = filler_word_service.detect(transcript, duration)

        voice = None
        voice_source = "unavailable"
        temp_path = write_audio_bytes(audio_bytes, suffix=suffix)
        try:
            voice = voice_confidence_service.analyze(temp_path, duration_seconds=duration)
            voice_source = "librosa"
        except Exception:
            voice = None
        finally:
            temp_path.unlink(missing_ok=True)

        communication = communication_score_service.score(
            transcript, filler, voice, duration_seconds=duration
        )

        return SpeechAnalyticsResponse(
            communication=communication,
            voice_source=voice_source,
        )


speech_analytics_service = SpeechAnalyticsService()
