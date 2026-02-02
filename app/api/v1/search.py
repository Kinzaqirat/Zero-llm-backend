"""Search and access control API endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..deps import get_database
from ...schemas.search import AccessCheckResponse, SearchResponse
from ...services.access_service import access_service
from ...services.search_service import search_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_content(
    q: str = Query(..., description="Search query"),
    chapter: str = Query(None, description="Optional chapter filter"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
):
    """Search course content.

    Args:
        q: Search query
        chapter: Optional chapter ID to filter results
        limit: Maximum number of results (1-50)

    Returns:
        Search results with snippets

    Raises:
        HTTPException: If query is invalid
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters",
        )

    results = await search_service.search_content(q, chapter, limit)

    return SearchResponse(query=q, results=results, total_results=len(results))


@router.get("/access/check", response_model=AccessCheckResponse)
async def check_access(
    user_id: str = Query(..., description="User identifier"),
    chapter_id: str = Query(..., description="Chapter identifier"),
    db: Session = Depends(get_database),
):
    """Check if user has access to a chapter.

    Args:
        user_id: User identifier
        chapter_id: Chapter identifier
        db: Database session

    Returns:
        Access check result

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
    user = await access_service.get_user_or_create(db, user_uuid)

    # Check access
    has_access, reason = await access_service.check_chapter_access(db, user_uuid, chapter_id)

    return AccessCheckResponse(
        has_access=has_access,
        is_premium=user.is_premium,
        chapter_id=chapter_id,
        reason=reason,
    )
