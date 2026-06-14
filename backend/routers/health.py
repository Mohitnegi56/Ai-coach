from fastapi import APIRouter

from config import settings
from models.schemas import EvaluationHealth, HealthResponse
from services.grammar_score_service import grammar_score_service

router = APIRouter(tags=["health"])


def _check_grammar_tool() -> str:
    try:
        grammar_score_service._get_tool()
        return "ready"
    except Exception as exc:
        return f"unavailable: {exc}"


def _check_speech_analytics() -> str:
    try:
        import librosa  # noqa: F401

        return "ready"
    except Exception as exc:
        return f"unavailable: {exc}"


def _check_presence_analytics() -> str:
    try:
        import deepface  # noqa: F401
        import PIL  # noqa: F401

        return "ready"
    except Exception as exc:
        return f"unavailable: {exc}"


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        whisper_model=settings.whisper_model_size,
        evaluation=EvaluationHealth(
            groq_configured=bool(settings.groq_api_key),
            embedding_model=settings.embedding_model,
            grammar_tool=_check_grammar_tool(),
            speech_analytics=_check_speech_analytics(),
            presence_analytics=_check_presence_analytics(),
        ),
    )
