from fastapi import APIRouter, HTTPException, Query

from backend.models.schemas import PublicQuestion, QuestionBankMetadata, QuestionListResponse
from backend.services.question_service import question_service

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/metadata", response_model=QuestionBankMetadata)
def get_metadata() -> QuestionBankMetadata:
    return question_service.get_metadata()


@router.get("", response_model=QuestionListResponse)
def list_questions(
    topic: str | None = Query(default=None),
    difficulty: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=500),
) -> QuestionListResponse:
    questions = question_service.list_questions(
        topic=topic,
        difficulty=difficulty,
        limit=limit,
    )
    public = [question_service.to_public(q) for q in questions]
    return QuestionListResponse(total=len(public), questions=public)


@router.get("/random", response_model=PublicQuestion)
def get_random_question(
    topic: str | None = Query(default=None),
    difficulty: str | None = Query(default=None),
) -> PublicQuestion:
    question = question_service.get_random_question(topic=topic, difficulty=difficulty)
    if question is None:
        raise HTTPException(status_code=404, detail="No questions match the given filters")
    return question_service.to_public(question)


@router.get("/{question_id}", response_model=PublicQuestion)
def get_question(question_id: str) -> PublicQuestion:
    question = question_service.get_question(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return question_service.to_public(question)
