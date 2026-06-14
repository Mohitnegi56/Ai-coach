from typing import Literal

from pydantic import BaseModel, Field


Difficulty = Literal["easy", "medium", "hard"]


class Question(BaseModel):
    id: str
    question: str
    topic: str
    difficulty: Difficulty
    tags: list[str] = Field(default_factory=list)
    ideal_answer: str = ""


class PublicQuestion(BaseModel):
    id: str
    question: str
    topic: str
    difficulty: Difficulty
    tags: list[str] = Field(default_factory=list)


class EvaluationRequest(BaseModel):
    question_id: str
    answer: str = Field(min_length=1)


class GrammarIssue(BaseModel):
    message: str
    context: str
    offset: int
    length: int


class IntentResult(BaseModel):
    extracted_intent: str
    key_concepts: list[str]
    addresses_question: bool
    score: float = Field(ge=0, le=100)
    feedback: str


class TechnicalResult(BaseModel):
    score: float = Field(ge=0, le=100)
    cosine_similarity: float = Field(ge=0, le=1)


class GrammarResult(BaseModel):
    score: float = Field(ge=0, le=100)
    error_count: int
    issues: list[GrammarIssue]


class EvaluationResponse(BaseModel):
    question_id: str
    question: str
    answer: str
    ideal_answer: str
    intent: IntentResult
    technical: TechnicalResult
    grammar: GrammarResult
    overall_score: float = Field(ge=0, le=100)
    intent_source: Literal["groq", "fallback"] = "groq"


class QuestionBankMetadata(BaseModel):
    version: str
    total_questions: int
    topics: list[str]
    difficulties: list[str]


class QuestionBank(BaseModel):
    metadata: QuestionBankMetadata
    questions: list[Question]


class QuestionListResponse(BaseModel):
    total: int
    questions: list[PublicQuestion]


class TranscriptionResponse(BaseModel):
    text: str
    language: str | None = None
    duration_seconds: float | None = None


class EvaluationHealth(BaseModel):
    groq_configured: bool
    embedding_model: str
    grammar_tool: str
    speech_analytics: str
    presence_analytics: str


class HealthResponse(BaseModel):
    status: str
    app: str
    whisper_model: str
    evaluation: EvaluationHealth


class FillerWordResult(BaseModel):
    total_count: int
    per_minute: float
    breakdown: dict[str, int]


class VoiceConfidenceResult(BaseModel):
    score: float = Field(ge=0, le=100)
    speaking_rate_wpm: float
    pitch_variance: float
    pause_ratio: float
    duration_seconds: float


class CommunicationResult(BaseModel):
    score: float = Field(ge=0, le=100)
    speaking_rate_score: float
    filler_score: float
    structure_score: float
    voice_confidence: float | None = None
    speaking_rate_wpm: float
    pitch_variance: float | None = None
    pause_ratio: float | None = None
    filler_words: FillerWordResult


class SpeechAnalyticsResponse(BaseModel):
    communication: CommunicationResult
    voice_source: Literal["librosa", "unavailable"] = "librosa"


class EyeContactStats(BaseModel):
    percentage: float = Field(ge=0, le=100)
    samples: int
    looking_at_camera: int


class EmotionSnapshot(BaseModel):
    timestamp_seconds: float = 0.0
    dominant_emotion: str = "neutral"
    confidence: float = 0.0
    scores: dict[str, float] = Field(default_factory=lambda: {"neutral": 100.0})


class PresenceAnalyticsResponse(BaseModel):
    score: float = Field(ge=0, le=100)
    eye_contact: EyeContactStats
    eye_contact_score: float = Field(ge=0, le=100)
    emotion_score: float = Field(ge=0, le=100)
    dominant_emotion: str
    emotions: list[EmotionSnapshot]
    frames_analyzed: int


class ScoreRadar(BaseModel):
    technical: float = Field(ge=0, le=100)
    communication: float = Field(ge=0, le=100)
    presence: float = Field(ge=0, le=100)
    grammar: float = Field(ge=0, le=100)


class FeedbackResponse(BaseModel):
    summary: str
    strengths: list[str]
    improvements: list[str]
    action_items: list[str]
    voice_script: str
    radar: ScoreRadar
    interview_score: float = Field(ge=0, le=100)
    source: Literal["groq", "fallback"] = "groq"


class FeedbackRequest(BaseModel):
    question_id: str = ""
    question: str
    answer: str = Field(min_length=1)
    topic: str = ""
    difficulty: str = ""
    technical: float = Field(ge=0, le=100)
    communication: float = Field(ge=0, le=100)
    presence: float = Field(ge=0, le=100)
    grammar: float = Field(ge=0, le=100)
    interview_score: float = Field(ge=0, le=100)
    include_tts: bool = True
    save_session: bool = False


class FeedbackPackageResponse(BaseModel):
    feedback: FeedbackResponse
    radar_chart_base64: str
    radar_chart_svg: str
    audio_base64: str | None = None
    audio_mime: str | None = None
    session_id: int | None = None


class SessionRecord(BaseModel):
    id: int | None = None
    created_at: str | None = None
    question_id: str
    question: str
    topic: str
    difficulty: str
    answer: str
    interview_score: float
    technical_score: float
    communication_score: float
    presence_score: float
    grammar_score: float
    feedback: FeedbackResponse


class SessionSummary(BaseModel):
    id: int
    created_at: str
    question_id: str
    question: str
    topic: str
    difficulty: str
    interview_score: float
    technical_score: float
    communication_score: float
    presence_score: float
    grammar_score: float
    feedback_summary: str


class SessionListResponse(BaseModel):
    total: int
    sessions: list[SessionSummary]
