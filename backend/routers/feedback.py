from fastapi import APIRouter, HTTPException

from backend.models.schemas import FeedbackPackageResponse, FeedbackRequest
from backend.services.chart_service import chart_service
from backend.services.feedback_service import feedback_service
from backend.services.session_service import session_service
from backend.services.tts_service import tts_service

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackPackageResponse)
def generate_feedback(payload: FeedbackRequest) -> FeedbackPackageResponse:
    try:
        feedback = feedback_service.generate(
            question=payload.question,
            answer=payload.answer,
            technical=payload.technical,
            communication=payload.communication,
            presence=payload.presence,
            grammar=payload.grammar,
            interview_score=payload.interview_score,
        )
        radar_chart = chart_service.radar_chart_base64(feedback.radar)
        radar_svg = chart_service.radar_chart_svg(feedback.radar)

        audio_base64 = None
        audio_mime = None
        if payload.include_tts and feedback.voice_script:
            try:
                audio_bytes, audio_mime = tts_service.synthesize(feedback.voice_script)
                audio_base64 = tts_service.to_base64(audio_bytes)
            except Exception:
                audio_base64 = None
                audio_mime = None

        session_id = None
        if payload.save_session and payload.question_id:
            from backend.models.schemas import SessionRecord

            record = session_service.save(
                SessionRecord(
                    question_id=payload.question_id,
                    question=payload.question,
                    topic=payload.topic,
                    difficulty=payload.difficulty,
                    answer=payload.answer,
                    interview_score=payload.interview_score,
                    technical_score=payload.technical,
                    communication_score=payload.communication,
                    presence_score=payload.presence,
                    grammar_score=payload.grammar,
                    feedback=feedback,
                )
            )
            session_id = record.id

        return FeedbackPackageResponse(
            feedback=feedback,
            radar_chart_base64=radar_chart,
            radar_chart_svg=radar_svg,
            audio_base64=audio_base64,
            audio_mime=audio_mime,
            session_id=session_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Feedback generation failed: {exc}") from exc
