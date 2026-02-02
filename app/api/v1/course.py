"""Course and chapter API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status

from ...schemas.content import ChapterContent, ChapterNavigation, CourseMetadata, ChaptersList
from ...services.content_service import content_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/course", response_model=CourseMetadata)
async def get_course_info():
    """Get course metadata.

    Returns:
        Course metadata including title, description, and statistics
    """
    metadata = await content_service.get_course_metadata()

    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course metadata not found"
        )

    return metadata


@router.get("/chapters", response_model=ChaptersList)
async def get_all_chapters():
    """Get list of all chapters.

    Returns:
        List of chapter metadata
    """
    chapters = await content_service.get_all_chapters()
    return {"chapters": chapters}

@router.get("/chapters/{chapter_id}", response_model=ChapterContent)
async def get_chapter_content(chapter_id: str):
    """Get specific chapter content.

    Args:
        chapter_id: Chapter identifier (01-10)

    Returns:
        Chapter content including markdown text

    Raises:
        HTTPException: If chapter not found
    """
    chapter = await content_service.get_chapter(chapter_id)

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Chapter {chapter_id} not found"
        )

    return chapter


@router.get("/chapters/{chapter_id}/next", response_model=ChapterNavigation)
async def get_next_chapter(chapter_id: str):
    """Get next chapter information.

    Args:
        chapter_id: Current chapter identifier

    Returns:
        Next chapter navigation info

    Raises:
        HTTPException: If no next chapter exists
    """
    chapter = await content_service.get_chapter(chapter_id)

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Chapter {chapter_id} not found"
        )

    if not chapter.next_chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No next chapter available"
        )

    next_chapter = await content_service.get_chapter(chapter.next_chapter)

    if not next_chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Next chapter not found")

    return ChapterNavigation(
        chapter_id=next_chapter.chapter_id,
        title=next_chapter.title,
        url=f"/api/v1/chapters/{next_chapter.chapter_id}",
    )


@router.get("/chapters/{chapter_id}/previous", response_model=ChapterNavigation)
async def get_previous_chapter(chapter_id: str):
    """Get previous chapter information.

    Args:
        chapter_id: Current chapter identifier

    Returns:
        Previous chapter navigation info

    Raises:
        HTTPException: If no previous chapter exists
    """
    chapter = await content_service.get_chapter(chapter_id)

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Chapter {chapter_id} not found"
        )

    if not chapter.previous_chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No previous chapter available"
        )

    prev_chapter = await content_service.get_chapter(chapter.previous_chapter)

    if not prev_chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Previous chapter not found"
        )

    return ChapterNavigation(
        chapter_id=prev_chapter.chapter_id,
        title=prev_chapter.title,
        url=f"/api/v1/chapters/{prev_chapter.chapter_id}",
    )
