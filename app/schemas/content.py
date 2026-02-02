"""Course content schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class CourseMetadata(BaseModel):
    """Course metadata schema."""

    course_id: str = Field(..., description="Unique course identifier")
    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Course description")
    total_chapters: int = Field(..., description="Total number of chapters")
    total_quizzes: int = Field(..., description="Total number of quizzes")
    difficulty: str = Field(..., description="Difficulty level")
    estimated_hours: int = Field(..., description="Estimated completion time in hours")
    version: str = Field(..., description="Course version")
    last_updated: str = Field(..., description="Last update date")
    language: str = Field(default="en", description="Course language")

    class Config:
        json_schema_extra = {
            "example": {
                "course_id": "genai-fundamentals-2026",
                "title": "Generative AI Fundamentals",
                "description": "Comprehensive course on Generative AI",
                "total_chapters": 10,
                "total_quizzes": 10,
                "difficulty": "beginner to advanced",
                "estimated_hours": 30,
                "version": "1.0.0",
                "last_updated": "2026-01-30",
                "language": "en",
            }
        }


class ChapterMetadata(BaseModel):
    """Chapter metadata schema."""

    chapter_id: str = Field(..., description="Unique chapter identifier")
    title: str = Field(..., description="Chapter title")
    level: str = Field(..., description="Difficulty level")
    order: int = Field(..., description="Chapter order in course")
    estimated_minutes: int = Field(..., description="Estimated completion time")
    has_quiz: bool = Field(..., description="Whether chapter has a quiz")
    is_free: bool = Field(..., description="Whether chapter is free to access")


class ChapterContent(BaseModel):
    """Chapter content schema."""

    chapter_id: str = Field(..., description="Unique chapter identifier")
    title: str = Field(..., description="Chapter title")
    level: str = Field(..., description="Difficulty level")
    content: str = Field(..., description="Chapter content in markdown")
    next_chapter: Optional[str] = Field(None, description="Next chapter ID")
    previous_chapter: Optional[str] = Field(None, description="Previous chapter ID")
    estimated_minutes: int = Field(..., description="Estimated completion time")
    has_quiz: bool = Field(default=True, description="Whether chapter has a quiz")
    is_free: bool = Field(default=False, description="Whether chapter is free")

    class Config:
        json_schema_extra = {
            "example": {
                "chapter_id": "01",
                "title": "Introduction to Generative AI",
                "level": "beginner",
                "content": "# Chapter 1: Introduction to Generative AI\n\nWelcome to the world of Generative AI!",
                "next_chapter": "02",
                "previous_chapter": None,
                "estimated_minutes": 180,
                "has_quiz": True,
                "is_free": True,
            }
        }


class ChaptersList(BaseModel):
    """Response schema for listing chapters."""

    chapters: List[ChapterMetadata] = Field(..., description="List of chapter metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "chapters": [
                    {
                        "chapter_id": "01",
                        "title": "Introduction to Generative AI",
                        "level": "beginner",
                        "order": 1,
                        "estimated_minutes": 180,
                        "has_quiz": True,
                        "is_free": True,
                    },
                    {
                        "chapter_id": "02",
                        "title": "Transformers and Attention",
                        "level": "beginner",
                        "order": 2,
                        "estimated_minutes": 240,
                        "has_quiz": True,
                        "is_free": True,
                    },
                ]
            }
        }

class ChapterNavigation(BaseModel):
    """Chapter navigation schema."""

    chapter_id: str = Field(..., description="Chapter identifier")
    title: str = Field(..., description="Chapter title")
    url: str = Field(..., description="Chapter URL")
