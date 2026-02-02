"""Progress tracking API endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_database
from ...schemas.progress import (
    ProgressUpdateRequest,
    ProgressUpdateResponse,
    UserProgressSchema,
)
from ...services.access_service import access_service
from ...services.progress_service import progress_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/progress/{user_id}", response_model=UserProgressSchema)
async def get_user_progress(user_id: str, db: Session = Depends(get_database)):
    """Get user's progress for the course.

    Args:
        user_id: User identifier
        db: Database session

    Returns:
        User progress data

    Raises:
        HTTPException: If user_id is invalid
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format"
        )

    # Ensure user exists
    await access_service.get_user_or_create(db, user_uuid)

    # Get progress
    progress = await progress_service.get_user_progress(db, user_uuid)

    return progress


@router.put("/progress/{user_id}/chapters/{chapter_id}", response_model=ProgressUpdateResponse)
async def update_chapter_progress(
    user_id: str,
    chapter_id: str,
    update: ProgressUpdateRequest,
    db: Session = Depends(get_database),
):
    """Update user's progress for a chapter.

    Args:
        user_id: User identifier
        chapter_id: Chapter identifier
        update: Progress update data
        db: Database session

    Returns:
        Updated progress information

    Raises:
        HTTPException: If user_id is invalid or update fails
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format"
        )

    # Validate status
    valid_statuses = ["not_started", "in_progress", "completed"]
    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )

    # Ensure user exists
    await access_service.get_user_or_create(db, user_uuid)

    # Update progress
    success = await progress_service.update_chapter_progress(
        db, user_uuid, chapter_id, update.status, update.time_spent_minutes
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update progress"
        )

    # Get updated overall progress
    progress = await progress_service.get_user_progress(db, user_uuid)

    return ProgressUpdateResponse(
        success=True,
        chapter_id=chapter_id,
        status=update.status,
        overall_progress=progress.overall_progress,
        message=f"Progress updated successfully for chapter {chapter_id}",
    )
