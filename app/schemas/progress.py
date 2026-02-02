"""Progress tracking schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChapterProgressSchema(BaseModel):
    """Chapter progress schema."""

    chapter_id: str = Field(..., description="Chapter identifier")
    status: str = Field(..., description="Progress status")
    quiz_passed: Optional[bool] = Field(None, description="Whether quiz was passed")
    quiz_score: Optional[float] = Field(None, description="Quiz score")
    time_spent_minutes: int = Field(default=0, description="Time spent on chapter")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


class UserProgressSchema(BaseModel):
    """User progress schema."""

    user_id: str = Field(..., description="User identifier")
    course_id: str = Field(..., description="Course identifier")
    overall_progress: int = Field(..., description="Overall progress percentage")
    chapters_completed: int = Field(..., description="Number of chapters completed")
    total_chapters: int = Field(..., description="Total number of chapters")
    current_chapter: str = Field(..., description="Current chapter ID")
    streak_days: int = Field(default=0, description="Consecutive days of activity")
    total_quiz_attempts: int = Field(default=0, description="Total quiz attempts")
    average_quiz_score: Optional[float] = Field(None, description="Average quiz score")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    chapters: List[ChapterProgressSchema] = Field(..., description="Progress per chapter")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "course_id": "genai-fundamentals-2026",
                "overall_progress": 30,
                "chapters_completed": 3,
                "total_chapters": 10,
                "current_chapter": "04",
                "streak_days": 5,
                "total_quiz_attempts": 3,
                "average_quiz_score": 85.5,
                "last_activity": "2026-01-30T10:00:00Z",
                "chapters": [],
            }
        }


class ProgressUpdateRequest(BaseModel):
    """Progress update request schema."""

    status: str = Field(..., description="New status (not_started, in_progress, completed)")
    time_spent_minutes: int = Field(default=0, description="Time spent on chapter")

    class Config:
        json_schema_extra = {
            "example": {"status": "completed", "time_spent_minutes": 45}
        }


class ProgressUpdateResponse(BaseModel):
    """Progress update response schema."""

    success: bool = Field(..., description="Whether update was successful")
    chapter_id: str = Field(..., description="Chapter identifier")
    status: str = Field(..., description="New status")
    overall_progress: int = Field(..., description="Updated overall progress")
    message: str = Field(..., description="Response message")
