import tempfile
from pathlib import Path

from faster_whisper import WhisperModel

from config import settings
from models.schemas import TranscriptionResponse


class STTService:
    def __init__(self) -> None:
        self._model: WhisperModel | None = None

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(
                settings.whisper_model_size,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type,
            )
        return self._model

    def transcribe_file(self, audio_path: Path) -> TranscriptionResponse:
        model = self._get_model()
        segments, info = model.transcribe(str(audio_path), beam_size=5)
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return TranscriptionResponse(
            text=text,
            language=info.language,
            duration_seconds=info.duration,
        )

    def transcribe_bytes(self, audio_bytes: bytes, suffix: str = ".wav") -> TranscriptionResponse:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = Path(temp_file.name)

        try:
            return self.transcribe_file(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)


stt_service = STTService()
