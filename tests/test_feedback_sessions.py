from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app
from models.schemas import FeedbackResponse, ScoreRadar
from services.chart_service import chart_service
from services.feedback_service import feedback_service
from services.session_service import SessionService

client = TestClient(app)


def test_feedback_service_fallback():
    result = feedback_service._fallback_feedback(
        question="What is supervised learning?",
        technical=85,
        communication=70,
        presence=65,
        grammar=80,
        interview_score=76,
    )
    assert result.summary
    assert len(result.strengths) >= 1
    assert result.radar.technical == 85


def test_radar_chart_generates():
    radar = ScoreRadar(technical=80, communication=70, presence=65, grammar=75)
    encoded = chart_service.radar_chart_base64(radar)
    assert len(encoded) > 100


@patch("services.feedback_service.feedback_service.generate")
def test_feedback_endpoint(mock_generate):
    mock_generate.return_value = FeedbackResponse(
        summary="Good job.",
        strengths=["Clear structure"],
        improvements=["Add more detail"],
        action_items=["Review reference answer"],
        voice_script="Your score is 75.",
        radar=ScoreRadar(technical=80, communication=70, presence=65, grammar=75),
        interview_score=75,
        source="groq",
    )

    payload = {
        "question_id": "ml-001",
        "question": "What is supervised learning?",
        "answer": "Supervised learning uses labeled data.",
        "topic": "machine_learning",
        "difficulty": "easy",
        "technical": 80,
        "communication": 70,
        "presence": 65,
        "grammar": 75,
        "interview_score": 75,
        "include_tts": False,
        "save_session": False,
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["feedback"]["summary"]
    assert data["radar_chart_base64"]


def test_session_persistence(tmp_path):
    service = SessionService(db_path=tmp_path / "test.db")
    from models.schemas import SessionRecord


    feedback = feedback_service._fallback_feedback(
        "Q?", 80, 70, 65, 75, 74
    )
    record = service.save(
        SessionRecord(
            question_id="ml-001",
            question="What is supervised learning?",
            topic="machine_learning",
            difficulty="easy",
            answer="Supervised learning uses labels.",
            interview_score=74,
            technical_score=80,
            communication_score=70,
            presence_score=65,
            grammar_score=75,
            feedback=feedback,
        )
    )
    assert record.id is not None
    sessions = service.list_sessions()
    assert len(sessions) == 1
    assert sessions[0].interview_score == 74


def test_sessions_api():
    response = client.get("/api/sessions?limit=5")
    assert response.status_code == 200
    assert "sessions" in response.json()
