"""Unit tests for content service."""

import pytest

from backend.app.services.content_service import ContentService


@pytest.mark.asyncio
async def test_parse_chapter_markdown():
    """Test markdown parsing."""
    service = ContentService()

    markdown = """---
title: "Introduction to AI"
level: "beginner"
estimated_minutes: 180
---

# Introduction

This is the chapter content.

## Section 1

More content here.
"""

    result = service._parse_chapter_markdown(markdown, "01")

    assert result["chapter_id"] == "01"
    assert result["title"] == "Introduction to AI"
    assert result["level"] == "beginner"
    assert result["estimated_minutes"] == 180
    assert "Introduction" in result["content"]
    assert result["is_free"] is True
    assert result["next_chapter"] == "02"
    assert result["previous_chapter"] is None


@pytest.mark.asyncio
async def test_parse_chapter_markdown_no_frontmatter():
    """Test markdown parsing without frontmatter."""
    service = ContentService()

    markdown = """# Chapter Title

Content without frontmatter.
"""

    result = service._parse_chapter_markdown(markdown, "05")

    assert result["chapter_id"] == "05"
    assert result["title"] == "Chapter 05"  # Default title
    assert result["level"] == "beginner"  # Default level
    assert "Chapter Title" in result["content"]
    assert result["is_free"] is False  # Chapter 5 is not free
    assert result["next_chapter"] == "06"
    assert result["previous_chapter"] == "04"
