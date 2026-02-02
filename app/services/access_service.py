"""Access control service for managing user permissions."""

import logging
from typing import Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.user import User

logger = logging.getLogger(__name__)


class AccessService:
    """Service for checking user access to content."""

    FREE_CHAPTERS = ["01", "02", "03"]  # First 3 chapters are free

    async def check_chapter_access(
        self, db: Session, user_id: UUID, chapter_id: str
    ) -> Tuple[bool, str]:
        """Check if user has access to a chapter.

        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter ID

        Returns:
            Tuple of (has_access, reason)
        """
        # Get user from database
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            logger.warning(f"User not found: {user_id}")
            return False, "User not found"

        # Check if chapter is free
        if chapter_id in self.FREE_CHAPTERS:
            logger.info(f"User {user_id} accessing free chapter {chapter_id}")
            return True, "Free content"

        # Check if user is premium
        if user.is_premium:
            logger.info(f"Premium user {user_id} accessing chapter {chapter_id}")
            return True, "Premium access"

        logger.info(f"User {user_id} denied access to chapter {chapter_id}")
        return False, "Premium content - upgrade required"

    async def check_quiz_access(
        self, db: Session, user_id: UUID, chapter_id: str
    ) -> Tuple[bool, str]:
        """Check if user has access to a quiz.

        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter ID for the quiz

        Returns:
            Tuple of (has_access, reason)
        """
        # Quiz access follows same rules as chapter access
        return await self.check_chapter_access(db, user_id, chapter_id)

    async def get_user_or_create(self, db: Session, user_id: UUID, email: str = None) -> User:
        """Get user by ID or create if doesn't exist.

        Args:
            db: Database session
            user_id: User ID
            email: Optional email address

        Returns:
            User object
        """
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            user = User(user_id=user_id, email=email, is_premium=False)
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {user_id}")

        return user


# Singleton instance
access_service = AccessService()
