from fastapi import APIRouter, HTTPException

from backend.models.schemas import SessionListResponse, SessionRecord
from backend.services.session_service import session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=SessionListResponse)
def list_sessions(limit: int = 50) -> SessionListResponse:
    sessions = session_service.list_sessions(limit=limit)
    return SessionListResponse(total=len(sessions), sessions=sessions)


@router.get("/{session_id}", response_model=SessionRecord)
def get_session(session_id: int) -> SessionRecord:
    record = session_service.get_session(session_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return record
