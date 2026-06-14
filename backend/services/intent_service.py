import json
import re

from groq import Groq

from backend.config import settings
from backend.models.schemas import IntentResult


INTENT_PROMPT = """You are an ML/DS interview evaluator. Analyze the candidate's spoken answer.

Interview question:
{question}

Candidate answer (transcribed):
{answer}

Return ONLY valid JSON with this schema:
{{
  "extracted_intent": "one sentence summarizing what the candidate is trying to explain",
  "key_concepts": ["concept1", "concept2"],
  "addresses_question": true,
  "intent_score": 75,
  "feedback": "brief constructive feedback on whether they understood and addressed the question"
}}

Rules:
- intent_score is 0-100 based on how well the answer addresses the question intent
- key_concepts lists technical concepts the candidate mentioned (empty list if none)
- addresses_question is true only if the answer is on-topic
- Be fair to spoken/transcribed answers with minor grammar issues"""


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


class IntentService:
    def __init__(self) -> None:
        self._client: Groq | None = None

    def _get_client(self) -> Groq:
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is not configured")
        if self._client is None:
            self._client = Groq(api_key=settings.groq_api_key)
        return self._client

    def _extract_via_groq(self, question: str, answer: str) -> IntentResult:
        client = self._get_client()
        prompt = INTENT_PROMPT.format(question=question, answer=answer)

        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": "You return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)

        return IntentResult(
            extracted_intent=payload.get("extracted_intent", ""),
            key_concepts=payload.get("key_concepts", []),
            addresses_question=bool(payload.get("addresses_question", False)),
            score=float(payload.get("intent_score", 0)),
            feedback=payload.get("feedback", ""),
        )

    def _fallback_intent(self, question: str, answer: str) -> IntentResult:
        question_tokens = _tokenize(question)
        answer_tokens = _tokenize(answer)
        overlap = question_tokens & answer_tokens

        if not answer_tokens:
            score = 0.0
            addresses = False
            intent = "No substantive answer detected."
            feedback = "Provide a clearer explanation that addresses the question."
        else:
            overlap_ratio = len(overlap) / max(len(question_tokens), 1)
            length_bonus = min(len(answer_tokens) / 20, 1.0) * 20
            score = round(min(100.0, overlap_ratio * 60 + length_bonus + 10), 2)
            addresses = overlap_ratio >= 0.15 or len(answer_tokens) >= 8
            intent = f"Candidate discusses concepts related to: {', '.join(sorted(overlap)[:5]) or 'general topic'}"
            feedback = (
                "Intent analysis used a local fallback (Groq unavailable). "
                "Configure GROQ_API_KEY for richer feedback."
            )

        return IntentResult(
            extracted_intent=intent,
            key_concepts=sorted(overlap)[:6],
            addresses_question=addresses,
            score=score,
            feedback=feedback,
        )

    def extract_intent(self, question: str, answer: str) -> tuple[IntentResult, str]:
        try:
            return self._extract_via_groq(question, answer), "groq"
        except Exception:
            return self._fallback_intent(question, answer), "fallback"


intent_service = IntentService()
