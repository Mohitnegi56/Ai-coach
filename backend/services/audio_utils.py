import tempfile
from pathlib import Path


def write_audio_bytes(audio_bytes: bytes, suffix: str = ".webm") -> Path:
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(audio_bytes)
    temp_file.close()
    return Path(temp_file.name)
