from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.models.schemas import SpeechAnalyticsResponse
from backend.services.speech_analytics_service import speech_analytics_service

router = APIRouter(prefix="/analyze-speech", tags=["speech-analytics"])

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".webm", ".ogg", ".flac"}


@router.post("", response_model=SpeechAnalyticsResponse)
async def analyze_speech(
    file: UploadFile = File(...),
    transcript: str = Form(...),
    duration_seconds: float | None = Form(default=None),
) -> SpeechAnalyticsResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if not transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript is required")

    try:
        return speech_analytics_service.analyze(
            audio_bytes=audio_bytes,
            transcript=transcript.strip(),
            suffix=suffix,
            duration_seconds=duration_seconds,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
