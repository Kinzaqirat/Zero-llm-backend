"""Progress tracking service."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.progress import ChapterProgress, DailyActivity
from ..models.quiz import QuizAttempt
from ..schemas.progress import ChapterProgressSchema, UserProgressSchema

logger = logging.getLogger(__name__)


class ProgressService:
    """Service for tracking user progress."""

    TOTAL_CHAPTERS = 10
    COURSE_ID = "genai-fundamentals-2026"

    async def get_user_progress(self, db: Session, user_id: UUID) -> UserProgressSchema:
        """Get user's progress for the course.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User progress data
        """
        # Get all chapter progress
        chapter_progress_list = (
            db.query(ChapterProgress).filter(ChapterProgress.user_id == user_id).all()
        )

        # Build chapter progress schemas
        chapters: List[ChapterProgressSchema] = []
        chapters_completed = 0

        for i in range(1, self.TOTAL_CHAPTERS + 1):
            chapter_id = f"{i:02d}"
            progress = next(
                (cp for cp in chapter_progress_list if cp.chapter_id == chapter_id), None
            )

            if progress:
                # Get quiz info
                quiz_attempt = (
                    db.query(QuizAttempt)
                    .filter(
                        QuizAttempt.user_id == user_id, QuizAttempt.chapter_id == chapter_id
                    )
                    .order_by(QuizAttempt.attempted_at.desc())
                    .first()
                )

                quiz_passed = quiz_attempt.passed if quiz_attempt else None
                quiz_score = quiz_attempt.score if quiz_attempt else None

                chapters.append(
                    ChapterProgressSchema(
                        chapter_id=chapter_id,
                        status=progress.status,
                        quiz_passed=quiz_passed,
                        quiz_score=quiz_score,
                        time_spent_minutes=progress.time_spent_minutes,
                        completed_at=progress.completed_at,
                    )
                )

                if progress.status == "completed":
                    chapters_completed += 1
            else:
                # No progress yet
                chapters.append(
                    ChapterProgressSchema(
                        chapter_id=chapter_id,
                        status="not_started",
                        quiz_passed=None,
                        quiz_score=None,
                        time_spent_minutes=0,
                        completed_at=None,
                    )
                )

        # Calculate overall progress
        overall_progress = int((chapters_completed / self.TOTAL_CHAPTERS) * 100)

        # Determine current chapter
        current_chapter = "01"
        for chapter in chapters:
            if chapter.status != "completed":
                current_chapter = chapter.chapter_id
                break

        # Calculate streak
        streak_days = await self._calculate_streak(db, user_id)

        # Get quiz statistics
        quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
        total_quiz_attempts = len(quiz_attempts)
        average_quiz_score = (
            sum(attempt.score for attempt in quiz_attempts) / total_quiz_attempts
            if total_quiz_attempts > 0
            else None
        )

        # Get last activity
        last_activity = (
            db.query(func.max(ChapterProgress.updated_at))
            .filter(ChapterProgress.user_id == user_id)
            .scalar()
        ) or datetime.utcnow()

        return UserProgressSchema(
            user_id=str(user_id),
            course_id=self.COURSE_ID,
            overall_progress=overall_progress,
            chapters_completed=chapters_completed,
            total_chapters=self.TOTAL_CHAPTERS,
            current_chapter=current_chapter,
            streak_days=streak_days,
            total_quiz_attempts=total_quiz_attempts,
            average_quiz_score=average_quiz_score,
            last_activity=last_activity,
            chapters=chapters,
        )

    async def update_chapter_progress(
        self, db: Session, user_id: UUID, chapter_id: str, status: str, time_spent: int = 0
    ) -> bool:
        """Update user's progress for a chapter.

        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter ID
            status: New status (not_started, in_progress, completed)
            time_spent: Additional time spent in minutes

        Returns:
            True if successful
        """
        try:
            # Get or create progress record
            progress = (
                db.query(ChapterProgress)
                .filter(
                    ChapterProgress.user_id == user_id, ChapterProgress.chapter_id == chapter_id
                )
                .first()
            )

            if not progress:
                progress = ChapterProgress(
                    user_id=user_id, chapter_id=chapter_id, status=status, time_spent_minutes=0
                )
                db.add(progress)

            # Update progress
            progress.status = status
            progress.time_spent_minutes += time_spent
            progress.updated_at = datetime.utcnow()

            if status == "completed" and not progress.completed_at:
                progress.completed_at = datetime.utcnow()

            # Record daily activity
            await self._record_daily_activity(db, user_id)

            db.commit()
            logger.info(f"Updated progress for user {user_id}, chapter {chapter_id}: {status}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating progress: {str(e)}")
            return False

    async def _calculate_streak(self, db: Session, user_id: UUID) -> int:
        """Calculate user's activity streak in days.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Number of consecutive days with activity
        """
        activities = (
            db.query(DailyActivity)
            .filter(DailyActivity.user_id == user_id)
            .order_by(DailyActivity.activity_date.desc())
            .all()
        )

        if not activities:
            return 0

        streak = 0
        current_date = datetime.utcnow().date()

        for activity in activities:
            activity_date = activity.activity_date.date()

            # Check if activity is from current date or consecutive previous date
            if activity_date == current_date - timedelta(days=streak):
                streak += 1
            else:
                break

        return streak

    async def _record_daily_activity(self, db: Session, user_id: UUID) -> None:
        """Record daily activity for streak tracking.

        Args:
            db: Database session
            user_id: User ID
        """
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        activity = (
            db.query(DailyActivity)
            .filter(DailyActivity.user_id == user_id, DailyActivity.activity_date == today)
            .first()
        )

        if not activity:
            activity = DailyActivity(user_id=user_id, activity_date=today, actions_count=1)
            db.add(activity)
        else:
            activity.actions_count += 1

        db.commit()


# Singleton instance
progress_service = ProgressService()
