from config import settings
from models.schemas import EvaluationResponse
from services.grammar_score_service import grammar_score_service
from services.intent_service import intent_service
from services.question_service import question_service
from services.technical_score_service import technical_score_service


class EvaluationService:
    def evaluate(self, question_id: str, answer: str) -> EvaluationResponse:
        question = question_service.get_question(question_id)
        if question is None:
            raise ValueError(f"Question not found: {question_id}")

        if not question.ideal_answer:
            raise ValueError(f"No ideal answer available for question: {question_id}")

        intent, intent_source = intent_service.extract_intent(question.question, answer)
        technical = technical_score_service.score(answer, question.ideal_answer)
        grammar = grammar_score_service.score(answer)

        if intent_source == "groq":
            overall = (
                technical.score * settings.score_weight_technical
                + intent.score * settings.score_weight_intent
                + grammar.score * settings.score_weight_grammar
            )
        else:
            overall = technical.score * 0.643 + grammar.score * 0.357

        return EvaluationResponse(
            question_id=question.id,
            question=question.question,
            answer=answer,
            ideal_answer=question.ideal_answer,
            intent=intent,
            technical=technical,
            grammar=grammar,
            overall_score=round(overall, 2),
            intent_source=intent_source,
        )


evaluation_service = EvaluationService()
