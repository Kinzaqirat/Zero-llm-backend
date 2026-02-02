"""API dependencies."""

from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db


def get_database() -> Generator[Session, None, None]:
    """Get database session dependency.

    Yields:
        Database session
    """
    return get_db()


async def verify_user_id(user_id: str) -> str:
    """Verify user ID format.

    Args:
        user_id: User ID to verify

    Returns:
        Validated user ID

    Raises:
        HTTPException: If user ID is invalid
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User ID is required"
        )
    return user_id


async def verify_chapter_id(chapter_id: str) -> str:
    """Verify chapter ID format.

    Args:
        chapter_id: Chapter ID to verify

    Returns:
        Validated chapter ID

    Raises:
        HTTPException: If chapter ID is invalid
    """
    if not chapter_id or not chapter_id.isdigit() or int(chapter_id) < 1 or int(chapter_id) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chapter ID. Must be between 01 and 10",
        )
    return chapter_id
