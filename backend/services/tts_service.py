import base64
import io
import tempfile
from pathlib import Path

from config import settings


class TTSService:
    def synthesize(self, text: str) -> tuple[bytes, str]:
        if not text.strip():
            raise ValueError("TTS text is empty")

        if settings.tts_engine == "pyttsx3":
            try:
                return self._synthesize_pyttsx3(text), "audio/wav"
            except Exception:
                pass

        return self._synthesize_gtts(text), "audio/mpeg"

    @staticmethod
    def _synthesize_pyttsx3(text: str) -> bytes:
        import pyttsx3

        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_path = Path(temp_file.name)

        try:
            engine.save_to_file(text, str(temp_path))
            engine.runAndWait()
            return temp_path.read_bytes()
        finally:
            temp_path.unlink(missing_ok=True)

    @staticmethod
    def _synthesize_gtts(text: str) -> bytes:
        from gtts import gTTS

        buffer = io.BytesIO()
        gTTS(text=text, lang="en").write_to_fp(buffer)
        return buffer.getvalue()

    @staticmethod
    def to_base64(audio_bytes: bytes) -> str:
        return base64.b64encode(audio_bytes).decode("ascii")


tts_service = TTSService()
