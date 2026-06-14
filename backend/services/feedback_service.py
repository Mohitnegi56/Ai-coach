import json

from groq import Groq

from config import settings
from models.schemas import FeedbackResponse, ScoreRadar


FEEDBACK_PROMPT = """You are an expert ML/DS interview coach. Generate structured feedback from the candidate's scores.

Question: {question}
Answer: {answer}

Scores (0-100):
- Technical: {technical}
- Communication: {communication}
- Presence: {presence}
- Grammar: {grammar}
- Interview overall: {interview_score}

Return ONLY valid JSON:
{{
  "summary": "2-3 sentence overall assessment",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"],
  "action_items": ["specific next step 1", "specific next step 2"],
  "voice_script": "A concise 3-4 sentence spoken coaching message for the candidate"
}}

Be constructive, specific, and reference the actual scores."""


class FeedbackService:
    def __init__(self) -> None:
        self._client: Groq | None = None

    def _get_client(self) -> Groq:
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is not configured")
        if self._client is None:
            self._client = Groq(api_key=settings.groq_api_key)
        return self._client

    @staticmethod
    def build_radar(
        technical: float,
        communication: float,
        presence: float,
        grammar: float,
    ) -> ScoreRadar:
        return ScoreRadar(
            technical=round(technical, 2),
            communication=round(communication, 2),
            presence=round(presence, 2),
            grammar=round(grammar, 2),
        )

    def _fallback_feedback(
        self,
        question: str,
        technical: float,
        communication: float,
        presence: float,
        grammar: float,
        interview_score: float,
    ) -> FeedbackResponse:
        strengths: list[str] = []
        improvements: list[str] = []

        for label, score in [
            ("technical accuracy", technical),
            ("communication", communication),
            ("presence", presence),
            ("grammar", grammar),
        ]:
            if score >= 75:
                strengths.append(f"Strong {label} ({score:.0f}/100)")
            elif score < 60:
                improvements.append(f"Improve {label} ({score:.0f}/100)")

        if not strengths:
            strengths.append("You completed a full interview round with measurable feedback.")
        if not improvements:
            improvements.append("Keep practicing to maintain consistency across topics.")

        return FeedbackResponse(
            summary=(
                f"Overall interview score: {interview_score:.1f}/100. "
                f"Technical {technical:.0f}, Communication {communication:.0f}, "
                f"Presence {presence:.0f}, Grammar {grammar:.0f}."
            ),
            strengths=strengths,
            improvements=improvements,
            action_items=[
                "Review the reference answer and note missing concepts.",
                "Practice answering out loud with fewer filler words.",
                "Maintain eye contact with the camera during responses.",
            ],
            voice_script=(
                f"Your interview score is {interview_score:.0f} out of 100. "
                f"Focus on strengthening your weakest area next time. "
                "Review the reference answer and practice speaking clearly."
            ),
            radar=self.build_radar(technical, communication, presence, grammar),
            interview_score=round(interview_score, 2),
            source="fallback",
        )

    def generate(
        self,
        question: str,
        answer: str,
        technical: float,
        communication: float,
        presence: float,
        grammar: float,
        interview_score: float,
    ) -> FeedbackResponse:
        radar = self.build_radar(technical, communication, presence, grammar)

        try:
            client = self._get_client()
            prompt = FEEDBACK_PROMPT.format(
                question=question,
                answer=answer,
                technical=technical,
                communication=communication,
                presence=presence,
                grammar=grammar,
                interview_score=interview_score,
            )
            response = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": "You return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            payload = json.loads(response.choices[0].message.content or "{}")
            return FeedbackResponse(
                summary=payload.get("summary", ""),
                strengths=payload.get("strengths", []),
                improvements=payload.get("improvements", []),
                action_items=payload.get("action_items", []),
                voice_script=payload.get("voice_script", ""),
                radar=radar,
                interview_score=round(interview_score, 2),
                source="groq",
            )
        except Exception:
            return self._fallback_feedback(
                question, technical, communication, presence, grammar, interview_score
            )


feedback_service = FeedbackService()
