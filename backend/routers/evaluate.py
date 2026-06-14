from fastapi import APIRouter, HTTPException

from models.schemas import EvaluationRequest, EvaluationResponse
from services.evaluation_service import evaluation_service

router = APIRouter(prefix="/evaluate", tags=["evaluate"])


@router.post("", response_model=EvaluationResponse)
def evaluate_answer(payload: EvaluationRequest) -> EvaluationResponse:
    try:
        return evaluation_service.evaluate(payload.question_id, payload.answer.strip())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {exc}") from exc
