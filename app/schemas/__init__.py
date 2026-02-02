"""Pydantic schemas package."""

from .content import (
    ChapterContent,
    ChapterMetadata,
    ChapterNavigation,
    CourseMetadata,
)
from .progress import (
    ChapterProgressSchema,
    ProgressUpdateRequest,
    ProgressUpdateResponse,
    UserProgressSchema,
)
from .quizzes import (
    Quiz,
    QuizAnswer,
    QuizQuestion,
    QuizResult,
    QuizSubmission,
    QuestionResult,
)
from .search import AccessCheckResponse, SearchResponse, SearchResult

__all__ = [
    "CourseMetadata",
    "ChapterMetadata",
    "ChapterContent",
    "ChapterNavigation",
    "Quiz",
    "QuizQuestion",
    "QuizAnswer",
    "QuizSubmission",
    "QuizResult",
    "QuestionResult",
    "ChapterProgressSchema",
    "UserProgressSchema",
    "ProgressUpdateRequest",
    "ProgressUpdateResponse",
    "SearchResult",
    "SearchResponse",
    "AccessCheckResponse",
]
