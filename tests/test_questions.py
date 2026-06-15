import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app
from services.question_service import QuestionService

client = TestClient(app)
QUESTIONS_PATH = Path(__file__).resolve().parent.parent / "backend" / "data" / "questions.json"


def test_question_bank_has_100_plus_questions():
    with QUESTIONS_PATH.open(encoding="utf-8") as handle:
        bank = json.load(handle)

    assert bank["metadata"]["total_questions"] >= 100
    assert len(bank["questions"]) >= 100


def test_question_bank_schema():
    with QUESTIONS_PATH.open(encoding="utf-8") as handle:
        bank = json.load(handle)

    for question in bank["questions"]:
        assert question["id"]
        assert question["question"]
        assert question["topic"] in bank["metadata"]["topics"]
        assert question["difficulty"] in bank["metadata"]["difficulties"]
        assert isinstance(question["tags"], list)
        assert question.get("ideal_answer")


def test_questions_metadata_endpoint():
    response = client.get("/api/questions/metadata")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_questions"] >= 100


def test_random_question_endpoint():
    response = client.get("/api/questions/random?difficulty=easy")
    assert response.status_code == 200
    payload = response.json()
    assert payload["difficulty"] == "easy"
    assert "ideal_answer" not in payload


def test_question_service_filters():
    service = QuestionService(QUESTIONS_PATH)
    ml_questions = service.list_questions(topic="machine_learning")
    assert len(ml_questions) > 0
    assert all(q.topic == "machine_learning" for q in ml_questions)
