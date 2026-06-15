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
            try:
                self._model = WhisperModel(
                    settings.whisper_model_size,
                    device=settings.whisper_device,
                    compute_type=settings.whisper_compute_type,
                )
            except Exception as exc:
                if settings.whisper_device == "cuda":
                    import logging
                    logging.warning(
                        f"CUDA Whisper model loading failed: {exc}. "
                        "Falling back to CPU device with int8 compute type."
                    )
                    self._model = WhisperModel(
                        settings.whisper_model_size,
                        device="cpu",
                        compute_type="int8",
                    )
                else:
                    raise exc
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
