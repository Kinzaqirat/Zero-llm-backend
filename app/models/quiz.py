"""Quiz attempt model."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import Base


class QuizAttempt(Base):
    """Quiz attempt model for storing quiz submissions and results."""

    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    quiz_id = Column(String(20), nullable=False, index=True)
    chapter_id = Column(String(10), nullable=False, index=True)
    score = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)
    answers = Column(JSONB, nullable=False)
    attempted_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<QuizAttempt(user_id={self.user_id}, quiz_id={self.quiz_id}, score={self.score}, passed={self.passed})>"
