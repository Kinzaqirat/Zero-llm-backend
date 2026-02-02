"""Quiz API endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_database
from ...models.quiz import QuizAttempt
from ...schemas.quizzes import Quiz, QuizResult, QuizSubmission, QuizHistory
from ...services.quiz_service import quiz_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/quizzes/{chapter_id}", response_model=Quiz)
async def get_quiz(chapter_id: str):
    """Get quiz for a chapter.

    Args:
        chapter_id: Chapter identifier

    Returns:
        Quiz with questions (without correct answers)

    Raises:
        HTTPException: If quiz not found
    """
    try:
        quiz = await quiz_service.get_quiz(chapter_id)
        return quiz
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching quiz"
        )


@router.post("/quizzes/{chapter_id}/submit", response_model=QuizResult)
async def submit_quiz(
    chapter_id: str, submission: QuizSubmission, db: Session = Depends(get_database)
):
    """Submit quiz answers and get results.

    Args:
        chapter_id: Chapter identifier
        submission: User's quiz submission
        db: Database session

    Returns:
        Quiz result with score and feedback

    Raises:
        HTTPException: If quiz not found or submission invalid
    """
    try:
        # Grade the quiz
        result = await quiz_service.submit_quiz(chapter_id, submission)

        # Store attempt in database
        try:
            user_uuid = UUID(submission.user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format"
            )

        attempt = QuizAttempt(
            user_id=user_uuid,
            quiz_id=result.quiz_id,
            chapter_id=chapter_id,
            score=result.score,
            passed=result.passed,
            answers=[answer.model_dump() for answer in submission.answers],
        )

        db.add(attempt)
        db.commit()

        logger.info(
            f"Quiz submitted for user {submission.user_id}, chapter {chapter_id}: {result.score}%"
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error submitting quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error submitting quiz"
        )


@router.get("/quizzes/{chapter_id}/history", response_model=QuizHistory)
async def get_quiz_history(chapter_id: str, user_id: str, db: Session = Depends(get_database)):
    """Get quiz attempt history for a user.

    Args:
        chapter_id: Chapter identifier
        user_id: User identifier
        db: Database session

    Returns:
        Quiz attempt history

    Raises:
        HTTPException: If user_id is invalid
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format"
        )

    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_uuid, QuizAttempt.chapter_id == chapter_id)
        .order_by(QuizAttempt.attempted_at.desc())
        .all()
    )

    return {
        "chapter_id": chapter_id,
        "total_attempts": len(attempts),
        "best_score": max([a.score for a in attempts]) if attempts else 0,
        "latest_score": attempts[0].score if attempts else None,
        "passed": attempts[0].passed if attempts else False,
        "attempts": [
            {"score": a.score, "passed": a.passed, "attempted_at": a.attempted_at}
            for a in attempts
        ],
    }
