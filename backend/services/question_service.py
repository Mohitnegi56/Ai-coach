import json
import random
from pathlib import Path

from backend.config import settings
from backend.models.schemas import PublicQuestion, Question, QuestionBank, QuestionBankMetadata


class QuestionService:
    def __init__(self, questions_path: Path | None = None) -> None:
        self.questions_path = questions_path or settings.questions_path
        self._bank: QuestionBank | None = None

    def load(self) -> QuestionBank:
        if self._bank is None:
            with self.questions_path.open(encoding="utf-8") as handle:
                payload = json.load(handle)
            self._bank = QuestionBank.model_validate(payload)
        return self._bank

    def get_metadata(self) -> QuestionBankMetadata:
        return self.load().metadata

    def list_questions(
        self,
        topic: str | None = None,
        difficulty: str | None = None,
        limit: int | None = None,
    ) -> list[Question]:
        questions = self.load().questions

        if topic:
            questions = [q for q in questions if q.topic == topic]
        if difficulty:
            questions = [q for q in questions if q.difficulty == difficulty]
        if limit is not None:
            questions = questions[:limit]

        return questions

    def get_question(self, question_id: str) -> Question | None:
        for question in self.load().questions:
            if question.id == question_id:
                return question
        return None

    def get_random_question(
        self,
        topic: str | None = None,
        difficulty: str | None = None,
    ) -> Question | None:
        pool = self.list_questions(topic=topic, difficulty=difficulty)
        if not pool:
            return None
        return random.choice(pool)

    @staticmethod
    def to_public(question: Question) -> PublicQuestion:
        return PublicQuestion(
            id=question.id,
            question=question.question,
            topic=question.topic,
            difficulty=question.difficulty,
            tags=question.tags,
        )


question_service = QuestionService()
