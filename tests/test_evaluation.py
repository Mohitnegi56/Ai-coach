from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app
from models.schemas import GrammarResult, IntentResult, TechnicalResult
from services.grammar_score_service import grammar_score_service
from services.intent_service import intent_service
from services.technical_score_service import technical_score_service

client = TestClient(app)

MOCK_INTENT = IntentResult(
    extracted_intent="Explains supervised vs unsupervised learning.",
    key_concepts=["supervised learning", "unsupervised learning", "labeled data"],
    addresses_question=True,
    score=88.0,
    feedback="Good conceptual coverage.",
)


def test_technical_score_similar_answers():
    ideal = "Supervised learning uses labeled data to predict outcomes."
    candidate = "Supervised learning trains on labeled examples to make predictions."
    result = technical_score_service.score(candidate, ideal)
    assert result.score > 60
    assert 0 <= result.cosine_similarity <= 1


def test_technical_score_dissimilar_answers():
    ideal = "Supervised learning uses labeled data to predict outcomes."
    candidate = "SQL joins combine rows from multiple tables."
    result = technical_score_service.score(candidate, ideal)
    assert result.score < 50


def test_grammar_score_clean_text():
    result = grammar_score_service.score("This is a clean and grammatically correct sentence.")
    assert result.score >= 80
    assert result.error_count >= 0


def test_intent_fallback_without_groq():
    with patch("services.intent_service.settings.groq_api_key", ""):
        result, source = intent_service.extract_intent(
            "What is supervised learning?",
            "Supervised learning uses labeled data to train predictive models.",
        )
    assert source == "fallback"
    assert result.score > 0
    assert result.addresses_question


@patch(
    "services.evaluation_service.intent_service.extract_intent",
    return_value=(MOCK_INTENT, "groq"),
)

def test_evaluate_endpoint(mock_intent):
    payload = {
        "question_id": "ml-001",
        "answer": (
            "Supervised learning uses labeled data to learn a mapping from inputs to outputs, "
            "while unsupervised learning finds structure in data without labels."
        ),
    }
    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["question_id"] == "ml-001"
    assert "overall_score" in data
    assert "technical" in data
    assert "grammar" in data
    assert "ideal_answer" in data
    assert data["intent"]["extracted_intent"]
    assert data["intent_source"] == "groq"
    mock_intent.assert_called_once()


def test_evaluate_unknown_question():
    response = client.post(
        "/api/evaluate",
        json={"question_id": "missing-id", "answer": "Some answer text here."},
    )
    assert response.status_code == 404
