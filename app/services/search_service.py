"""Search service for content search."""

import logging
import re
from typing import List

from ..schemas.search import SearchResult
from .content_service import content_service

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching course content."""

    async def search_content(
        self, query: str, chapter_filter: str = None, limit: int = 10
    ) -> List[SearchResult]:
        """Search course content.

        Args:
            query: Search query
            chapter_filter: Optional chapter ID to filter results
            limit: Maximum number of results

        Returns:
            List of search results
        """
        results: List[SearchResult] = []
        query_lower = query.lower()

        # Determine which chapters to search
        if chapter_filter:
            chapter_ids = [chapter_filter]
        else:
            chapter_ids = [f"{i:02d}" for i in range(1, 11)]

        # Search through chapters
        for chapter_id in chapter_ids:
            chapter = await content_service.get_chapter(chapter_id)

            if not chapter:
                continue

            # Search in chapter content
            content_lower = chapter.content.lower()

            # Find all occurrences
            for match in re.finditer(re.escape(query_lower), content_lower):
                # Extract snippet around match
                start = max(0, match.start() - 100)
                end = min(len(chapter.content), match.end() + 100)
                snippet = chapter.content[start:end].strip()

                # Add ellipsis if truncated
                if start > 0:
                    snippet = "..." + snippet
                if end < len(chapter.content):
                    snippet = snippet + "..."

                # Calculate relevance score (simple: based on position and title match)
                relevance = 1.0
                if query_lower in chapter.title.lower():
                    relevance += 0.5

                results.append(
                    SearchResult(
                        chapter_id=chapter_id,
                        section_id=chapter_id,  # Simplified - could parse sections
                        title=chapter.title,
                        snippet=snippet,
                        relevance_score=relevance,
                    )
                )

                # Limit results per chapter
                if len([r for r in results if r.chapter_id == chapter_id]) >= 3:
                    break

            if len(results) >= limit:
                break

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:limit]


# Singleton instance
search_service = SearchService()
