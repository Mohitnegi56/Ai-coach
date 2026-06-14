from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "AI Interview Coach"
    api_prefix: str = "/api"
    cors_origins: list[str] = ["*"]

    whisper_model_size: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"

    embedding_model: str = "all-MiniLM-L6-v2"

    score_weight_technical: float = 0.45
    score_weight_intent: float = 0.30
    score_weight_grammar: float = 0.25

    score_weight_interview_content: float = 0.50
    score_weight_interview_communication: float = 0.25
    score_weight_interview_presence: float = 0.25

    BASE_DIR = Path(__file__).resolve().parent

    database_path: Path = BASE_DIR / "data" / "sessions.db"

    questions_path: Path = BASE_DIR / "data" / "questions.json"
    tts_engine = "gtts"

    filler_words: list[str] = [
        "um",
        "uh",
        "like",
        "actually",
        "basically",
        "you know",
        "sort of",
        "kind of",
        "i mean",
        "so",
    ]

    questions_path: Path = Path(__file__).resolve().parent.parent / "data" / "questions.json"


settings = Settings()
