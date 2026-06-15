"""Run mock interview rounds to validate scoring weights."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from fastapi.testclient import TestClient

from main import app
from models.schemas import IntentResult
from services.question_service import question_service

client = TestClient(app)

MOCK_ANSWERS = [
    (
        "ml-001",
        "Supervised learning uses labeled data to train models, while unsupervised learning finds patterns without labels.",
        "good",
    ),
    (
        "ml-002",
        "Bias is error from overly simple models and variance is error from overly complex models. The tradeoff balances both.",
        "good",
    ),
    (
        "ml-003",
        "Um, like, I think overfitting means the model memorizes training data and performs poorly on new data.",
        "medium",
    ),
    (
        "ml-004",
        "Cross-validation splits data into folds to estimate generalization performance more reliably.",
        "good",
    ),
    (
        "dl-001",
        "A neural network has layers of neurons with weights and activation functions that learn hierarchical features.",
        "good",
    ),
    (
        "dl-002",
        "Backpropagation computes gradients with the chain rule and updates weights using gradient descent.",
        "good",
    ),
    (
        "stat-001",
        "P-value measures evidence against the null hypothesis; lower p-values suggest stronger evidence.",
        "good",
    ),
    (
        "stat-002",
        "Actually, um, standard deviation shows spread around the mean, you know.",
        "weak",
    ),
    (
        "py-001",
        "Pandas DataFrames store tabular data with labeled rows and columns for efficient analysis.",
        "good",
    ),
    (
        "py-002",
        "NumPy provides fast n-dimensional arrays and vectorized operations for numerical computing.",
        "good",
    ),
    (
        "nlp-001",
        "Tokenization splits text into words or subwords as the first step in most NLP pipelines.",
        "good",
    ),
    (
        "sql-001",
        "SQL joins combine rows from multiple tables based on related keys between them.",
        "good",
    ),
]

MOCK_INTENT = IntentResult(
    extracted_intent="Candidate explains the concept.",
    key_concepts=["machine learning"],
    addresses_question=True,
    score=82.0,
    feedback="Solid explanation.",
)


def run_rounds() -> list[dict]:
    results: list[dict] = []

    with patch("services.evaluation_service.intent_service.extract_intent") as mock_intent:
        mock_intent.return_value = (MOCK_INTENT, "groq")

        for question_id, answer, label in MOCK_ANSWERS:
            question = question_service.get_question(question_id)
            if question is None:
                continue

            evaluation = client.post(
                "/api/evaluate",
                json={"question_id": question_id, "answer": answer},
            ).json()

            communication = 78.0 if label == "good" else 62.0 if label == "medium" else 48.0
            presence = 72.0 if label == "good" else 58.0 if label == "medium" else 45.0
            interview_score = (
                evaluation["overall_score"] * 0.5
                + communication * 0.25
                + presence * 0.25
            )

            feedback = client.post(
                "/api/feedback",
                json={
                    "question_id": question_id,
                    "question": question.question,
                    "answer": answer,
                    "topic": question.topic,
                    "difficulty": question.difficulty,
                    "technical": evaluation["technical"]["score"],
                    "communication": communication,
                    "presence": presence,
                    "grammar": evaluation["grammar"]["score"],
                    "interview_score": interview_score,
                    "include_tts": False,
                    "save_session": True,
                },
            ).json()

            results.append(
                {
                    "question_id": question_id,
                    "label": label,
                    "content": evaluation["overall_score"],
                    "technical": evaluation["technical"]["score"],
                    "grammar": evaluation["grammar"]["score"],
                    "communication": communication,
                    "presence": presence,
                    "interview_score": interview_score,
                    "session_id": feedback.get("session_id"),
                }
            )

    return results


def main() -> None:
    results = run_rounds()
    print(f"Completed {len(results)} mock interview rounds\n")

    for item in results:
        print(
            f"{item['question_id']} [{item['label']}]: "
            f"interview={item['interview_score']:.1f} "
            f"content={item['content']:.1f} tech={item['technical']:.1f} "
            f"grammar={item['grammar']:.1f}"
        )

    averages = {
        "good": [r["interview_score"] for r in results if r["label"] == "good"],
        "medium": [r["interview_score"] for r in results if r["label"] == "medium"],
        "weak": [r["interview_score"] for r in results if r["label"] == "weak"],
    }
    print("\nAverage interview scores by quality band:")
    for band, scores in averages.items():
        if scores:
            print(f"  {band}: {sum(scores) / len(scores):.1f} ({len(scores)} rounds)")

    output_path = "backend/data/mock_interview_results.json"
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    print(f"\nSaved results to {output_path}")


if __name__ == "__main__":
    main()
