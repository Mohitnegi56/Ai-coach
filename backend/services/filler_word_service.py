import re

from config import settings
from models.schemas import FillerWordResult


class FillerWordService:
    def detect(self, transcript: str, duration_seconds: float) -> FillerWordResult:
        text = transcript.lower()
        counts: dict[str, int] = {}
        total = 0

        for phrase in settings.filler_words:
            pattern = rf"\b{re.escape(phrase)}\b"
            matches = re.findall(pattern, text)
            if matches:
                counts[phrase] = len(matches)
                total += len(matches)

        minutes = max(duration_seconds / 60.0, 0.01)
        per_minute = round(total / minutes, 2)

        return FillerWordResult(
            total_count=total,
            per_minute=per_minute,
            breakdown=counts,
        )


filler_word_service = FillerWordService()
