"""Content service for managing course and chapter content."""

import json
import logging
from typing import List, Optional

from app.schemas.content import ChapterContent, ChapterMetadata, CourseMetadata
from app.services.cache_service import cache_service
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)


class ContentService:
    """Service for retrieving and managing course content."""

    COURSE_PREFIX = "genai-fundamentals"

    async def get_course_metadata(self) -> Optional[CourseMetadata]:
        """Get course metadata.

        Returns:
            Course metadata or None if not found
        """
        cache_key = "course:metadata"

        # Try cache first
        cached = await cache_service.get(cache_key)
        if cached:
            return CourseMetadata(**json.loads(cached))

        # Fetch from storage
        try:
            key = f"{self.COURSE_PREFIX}/metadata.json"
            content = await storage_service.get_object(key)

            if not content:
                logger.error("Course metadata not found in storage")
                return None

            metadata = CourseMetadata(**json.loads(content))

            # Cache for 1 hour
            await cache_service.set(cache_key, content, ttl=3600)

            return metadata
        except Exception as e:
            logger.error(f"Error fetching course metadata: {str(e)}")
            return None

    async def get_chapter(self, chapter_id: str) -> Optional[ChapterContent]:
        """Get chapter content.

        Args:
            chapter_id: Chapter identifier (e.g., "01", "02" or "1")

        Returns:
            Chapter content or None if not found
        """
        orig_id = chapter_id
        # Normalize numeric chapter ids to two-digit format (01, 02, ...)
        norm_id = chapter_id.zfill(2) if chapter_id.isdigit() else chapter_id

        # Try cache keys in both forms for backward compatibility
        cache_keys = [f"chapter:{orig_id}"]
        if orig_id != norm_id:
            cache_keys.append(f"chapter:{norm_id}")

        for cache_key in cache_keys:
            cached = await cache_service.get(cache_key)
            if cached:
                try:
                    return ChapterContent(**json.loads(cached))
                except Exception:
                    # ignore malformed cache and continue
                    logger.warning(f"Malformed cache for {cache_key}, ignoring")

        # Fetch from storage using normalized id
        try:
            key = f"{self.COURSE_PREFIX}/chapters/chapter-{norm_id}.md"
            content = await storage_service.get_object(key)

            if not content:
                logger.warning(f"Chapter {orig_id} not found in storage (tried {key})")
                return None

            # Parse markdown and create ChapterContent
            chapter_data = self._parse_chapter_markdown(content, norm_id)
            chapter = ChapterContent(**chapter_data)

            # Cache for 1 hour under normalized key
            await cache_service.set(f"chapter:{norm_id}", chapter.model_dump_json(), ttl=3600)

            return chapter
        except Exception as e:
            logger.error(f"Error fetching chapter {orig_id}: {str(e)}")
            return None

    def _parse_chapter_markdown(self, content: str, chapter_id: str) -> dict:
        """Parse markdown file and extract metadata.

        Args:
            content: Markdown content
            chapter_id: Chapter identifier

        Returns:
            Dictionary with chapter data
        """
        lines = content.split("\n")
        metadata = {}
        body_start = 0

        # Parse frontmatter (YAML between --- markers)
        if lines and lines[0].strip() == "---":
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    body_start = i + 1
                    break
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip().strip('"')

        # Get content without frontmatter
        content_body = "\n".join(lines[body_start:])

        # Determine next/previous chapters
        try:
            ch_num = int(chapter_id)
            next_chapter = f"{ch_num + 1:02d}" if ch_num < 10 else None
            prev_chapter = f"{ch_num - 1:02d}" if ch_num > 1 else None
        except ValueError:
            next_chapter = None
            prev_chapter = None

        # Determine if chapter is free (first 3 chapters)
        is_free = int(chapter_id) <= 3 if chapter_id.isdigit() else False

        return {
            "chapter_id": chapter_id,
            "title": metadata.get("title", f"Chapter {chapter_id}"),
            "level": metadata.get("level", "beginner"),
            "content": content_body,
            "next_chapter": next_chapter,
            "previous_chapter": prev_chapter,
            "estimated_minutes": int(metadata.get("estimated_minutes", 180)),
            "has_quiz": True,
            "is_free": is_free,
        }

    async def get_all_chapters(self) -> List[ChapterMetadata]:
        """Get metadata for all chapters.

        Returns:
            List of chapter metadata
        """
        chapters = []

        for i in range(1, 11):  # 10 chapters
            chapter_id = f"{i:02d}"
            chapter = await self.get_chapter(chapter_id)

            if chapter:
                chapters.append(
                    ChapterMetadata(
                        chapter_id=chapter.chapter_id,
                        title=chapter.title,
                        level=chapter.level,
                        order=i,
                        estimated_minutes=chapter.estimated_minutes,
                        has_quiz=chapter.has_quiz,
                        is_free=chapter.is_free,
                    )
                )

        return chapters


# Singleton instance
content_service = ContentService()
