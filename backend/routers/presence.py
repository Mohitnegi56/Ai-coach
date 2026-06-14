from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.models.schemas import EyeContactStats, PresenceAnalyticsResponse
from backend.services.presence_service import presence_service

router = APIRouter(prefix="/analyze-presence", tags=["presence-analytics"])

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@router.post("", response_model=PresenceAnalyticsResponse)
async def analyze_presence(
    frames: list[UploadFile] = File(default=[]),
    eye_contact_percentage: float = Form(...),
    eye_contact_samples: int = Form(...),
    eye_contact_looking: int = Form(...),
) -> PresenceAnalyticsResponse:
    frame_bytes_list: list[bytes] = []

    for frame in frames:
        if not frame.filename:
            continue
        suffix = frame.filename.lower().rsplit(".", 1)[-1]
        if f".{suffix}" not in ALLOWED_IMAGE_EXTENSIONS:
            continue
        data = await frame.read()
        if data:
            frame_bytes_list.append(data)

    eye_contact = EyeContactStats(
        percentage=max(0.0, min(100.0, eye_contact_percentage)),
        samples=max(eye_contact_samples, 0),
        looking_at_camera=max(eye_contact_looking, 0),
    )

    try:
        return presence_service.analyze(frame_bytes_list, eye_contact)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
