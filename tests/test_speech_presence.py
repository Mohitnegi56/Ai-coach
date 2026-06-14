from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.main import app
from backend.models.schemas import EmotionSnapshot, EyeContactStats
from backend.services.communication_score_service import communication_score_service
from backend.services.filler_word_service import filler_word_service
from backend.services.presence_service import presence_service

client = TestClient(app)


def test_filler_word_detection():
    transcript = "Um, supervised learning is like, actually a core ML concept, you know."
    result = filler_word_service.detect(transcript, duration_seconds=60)
    assert result.total_count >= 4
    assert result.per_minute > 0
    assert "um" in result.breakdown or "like" in result.breakdown


def test_communication_score_structure():
    filler = filler_word_service.detect(
        "Supervised learning uses labeled data. Unsupervised learning finds patterns without labels.",
        duration_seconds=30,
    )
    result = communication_score_service.score(
        "Supervised learning uses labeled data. Unsupervised learning finds patterns without labels.",
        filler,
        duration_seconds=30,
    )
    assert result.score >= 50
    assert result.structure_score >= 50
    assert result.filler_score >= 80


@patch("backend.services.speech_analytics_service.voice_confidence_service.analyze")
def test_analyze_speech_endpoint(mock_voice):
    from backend.models.schemas import VoiceConfidenceResult

    mock_voice.return_value = VoiceConfidenceResult(
        score=82.0,
        speaking_rate_wpm=135.0,
        pitch_variance=0.15,
        pause_ratio=0.2,
        duration_seconds=20.0,
    )

    payload = {
        "transcript": "Supervised learning uses labeled data to train predictive models.",
        "duration_seconds": "20",
    }
    files = {"file": ("recording.webm", b"fake-audio-bytes", "audio/webm")}
    response = client.post("/api/analyze-speech", data=payload, files=files)
    assert response.status_code == 200
    data = response.json()
    assert "communication" in data
    assert data["communication"]["score"] >= 0


@patch("backend.services.presence_service.PresenceService._analyze_emotions")
def test_analyze_presence_endpoint(mock_emotions):
    mock_emotions.return_value = [
        EmotionSnapshot(
            timestamp_seconds=0.0,
            dominant_emotion="neutral",
            confidence=88.0,
            scores={"neutral": 88.0, "happy": 8.0},
        )
    ]

    image = Image.new("RGB", (64, 64), color=(120, 120, 120))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)

    payload = {
        "eye_contact_percentage": "72.5",
        "eye_contact_samples": "40",
        "eye_contact_looking": "29",
    }
    files = [("frames", ("frame-0.jpg", buffer.getvalue(), "image/jpeg"))]
    response = client.post("/api/analyze-presence", data=payload, files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["eye_contact"]["percentage"] == 72.5
    assert data["dominant_emotion"] == "neutral"


def test_presence_fallback_without_deepface():
    result = presence_service.analyze(
        frame_bytes_list=[b"fake"],
        eye_contact=EyeContactStats(percentage=70, samples=10, looking_at_camera=7),
    )
    assert result.score >= 0
    assert result.emotions[0].timestamp_seconds == 0.0


def test_presence_emotion_score():
    emotions = [
        EmotionSnapshot(
            timestamp_seconds=0.0,
            dominant_emotion="happy",
            confidence=90.0,
            scores={"happy": 70.0, "neutral": 20.0, "fear": 5.0},
        ),
        EmotionSnapshot(
            timestamp_seconds=2.0,
            dominant_emotion="neutral",
            confidence=80.0,
            scores={"neutral": 75.0, "happy": 15.0, "fear": 3.0},
        ),
    ]
    score = presence_service._emotion_score(emotions)
    assert score >= 60
