import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from backend.config import settings
from backend.models.schemas import SessionRecord, SessionSummary


class SessionService:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or settings.database_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    interview_score REAL NOT NULL,
                    technical_score REAL NOT NULL,
                    communication_score REAL NOT NULL,
                    presence_score REAL NOT NULL,
                    grammar_score REAL NOT NULL,
                    feedback_summary TEXT NOT NULL,
                    feedback_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save(self, record: SessionRecord) -> SessionRecord:
        created_at = record.created_at or datetime.now(timezone.utc).isoformat()
        feedback_json = json.dumps(record.feedback.model_dump())

        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO sessions (
                    created_at, question_id, question, topic, difficulty, answer,
                    interview_score, technical_score, communication_score,
                    presence_score, grammar_score, feedback_summary, feedback_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    record.question_id,
                    record.question,
                    record.topic,
                    record.difficulty,
                    record.answer,
                    record.interview_score,
                    record.technical_score,
                    record.communication_score,
                    record.presence_score,
                    record.grammar_score,
                    record.feedback.summary,
                    feedback_json,
                ),
            )
            conn.commit()
            record.id = cursor.lastrowid
            record.created_at = created_at
        return record

    def list_sessions(self, limit: int = 50) -> list[SessionSummary]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, question_id, question, topic, difficulty,
                       interview_score, technical_score, communication_score,
                       presence_score, grammar_score, feedback_summary
                FROM sessions
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [SessionSummary.model_validate(dict(row)) for row in rows]

    def get_session(self, session_id: int) -> SessionRecord | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            return None

        from backend.models.schemas import FeedbackResponse

        payload = dict(row)
        feedback = FeedbackResponse.model_validate(json.loads(payload.pop("feedback_json")))
        return SessionRecord(
            id=payload["id"],
            created_at=payload["created_at"],
            question_id=payload["question_id"],
            question=payload["question"],
            topic=payload["topic"],
            difficulty=payload["difficulty"],
            answer=payload["answer"],
            interview_score=payload["interview_score"],
            technical_score=payload["technical_score"],
            communication_score=payload["communication_score"],
            presence_score=payload["presence_score"],
            grammar_score=payload["grammar_score"],
            feedback=feedback,
        )


session_service = SessionService()
