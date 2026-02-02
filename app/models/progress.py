"""Progress tracking models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class ChapterProgress(Base):
    """Chapter progress model for tracking user progress through chapters."""

    __tablename__ = "chapter_progress"
    __table_args__ = (UniqueConstraint("user_id", "chapter_id", name="uq_user_chapter"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    chapter_id = Column(String(10), nullable=False, index=True)
    status = Column(
        String(20), default="not_started", nullable=False
    )  # not_started, in_progress, completed
    time_spent_minutes = Column(Integer, default=0, nullable=False)
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<ChapterProgress(user_id={self.user_id}, chapter_id={self.chapter_id}, status={self.status})>"


class DailyActivity(Base):
    """Daily activity model for tracking user engagement streaks."""

    __tablename__ = "daily_activities"
    __table_args__ = (UniqueConstraint("user_id", "activity_date", name="uq_user_date"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    activity_date = Column(DateTime(timezone=True), nullable=False, index=True)
    actions_count = Column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:
        return f"<DailyActivity(user_id={self.user_id}, date={self.activity_date}, actions={self.actions_count})>"
