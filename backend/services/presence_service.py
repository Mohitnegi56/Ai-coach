import io
from collections import Counter

import numpy as np
from PIL import Image

from backend.models.schemas import EmotionSnapshot, EyeContactStats, PresenceAnalyticsResponse


class PresenceService:
    @staticmethod
    def _neutral_snapshot(timestamp_seconds: float = 0.0) -> EmotionSnapshot:
        return EmotionSnapshot(
            timestamp_seconds=timestamp_seconds,
            dominant_emotion="neutral",
            confidence=0.0,
            scores={"neutral": 100.0},
        )

    def analyze(
        self,
        frame_bytes_list: list[bytes],
        eye_contact: EyeContactStats,
    ) -> PresenceAnalyticsResponse:
        emotions = self._analyze_emotions(frame_bytes_list)
        emotion_score = self._emotion_score(emotions)
        eye_contact_score = eye_contact.percentage
        overall = eye_contact_score * 0.55 + emotion_score * 0.45

        dominant = Counter(snapshot.dominant_emotion for snapshot in emotions).most_common(1)
        dominant_emotion = dominant[0][0] if dominant else "neutral"

        return PresenceAnalyticsResponse(
            score=round(overall, 2),
            eye_contact=eye_contact,
            eye_contact_score=round(eye_contact_score, 2),
            emotion_score=round(emotion_score, 2),
            dominant_emotion=dominant_emotion,
            emotions=emotions,
            frames_analyzed=len(frame_bytes_list),
        )

    def _analyze_emotions(self, frame_bytes_list: list[bytes]) -> list[EmotionSnapshot]:
        if not frame_bytes_list:
            return []

        try:
            from deepface import DeepFace
        except ImportError:
            return [self._neutral_snapshot(0.0)]

        snapshots: list[EmotionSnapshot] = []
        for index, frame_bytes in enumerate(frame_bytes_list):
            timestamp = round(index * 2.0, 1)
            try:
                image = np.array(Image.open(io.BytesIO(frame_bytes)).convert("RGB"))
                result = DeepFace.analyze(
                    image,
                    actions=["emotion"],
                    enforce_detection=False,
                    silent=True,
                )
                payload = result[0] if isinstance(result, list) else result
                scores = {k: float(v) for k, v in payload.get("emotion", {}).items()}
                if not scores:
                    snapshots.append(self._neutral_snapshot(timestamp))
                    continue
                dominant = max(scores, key=scores.get)
                snapshots.append(
                    EmotionSnapshot(
                        timestamp_seconds=timestamp,
                        dominant_emotion=dominant,
                        confidence=round(scores.get(dominant, 0.0), 2),
                        scores=scores,
                    )
                )
            except Exception:
                snapshots.append(self._neutral_snapshot(timestamp))

        return snapshots or [self._neutral_snapshot(0.0)]

    @staticmethod
    def _emotion_score(emotions: list[EmotionSnapshot]) -> float:
        if not emotions:
            return 50.0

        positive = {"happy", "neutral", "surprise"}
        negative = {"fear", "sad", "angry", "disgust"}

        total = 0.0
        for snapshot in emotions:
            scores = snapshot.scores
            pos = sum(scores.get(label, 0.0) for label in positive)
            neg = sum(scores.get(label, 0.0) for label in negative)
            total += pos - neg * 0.5

        average = total / len(emotions)
        return max(0.0, min(100.0, average))


presence_service = PresenceService()
