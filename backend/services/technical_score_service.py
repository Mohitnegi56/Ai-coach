import numpy as np
from sentence_transformers import SentenceTransformer

from config import settings
from models.schemas import TechnicalResult


class TechnicalScoreService:
    def __init__(self) -> None:
        self._model: SentenceTransformer | None = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(settings.embedding_model)
        return self._model

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    def score(self, candidate_answer: str, ideal_answer: str) -> TechnicalResult:
        model = self._get_model()
        embeddings = model.encode([candidate_answer, ideal_answer], normalize_embeddings=True)
        similarity = self._cosine_similarity(embeddings[0], embeddings[1])
        similarity = max(0.0, min(1.0, similarity))
        return TechnicalResult(
            score=round(similarity * 100, 2),
            cosine_similarity=round(similarity, 4),
        )


technical_score_service = TechnicalScoreService()
