"""Quiz schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    """Quiz question schema (without correct answer)."""

    question_id: str = Field(..., description="Unique question identifier")
    type: str = Field(..., description="Question type (multiple_choice, true_false)")
    question: str = Field(..., description="Question text")
    options: List[str] = Field(..., description="Answer options")
    difficulty: str = Field(..., description="Question difficulty")

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "q1",
                "type": "multiple_choice",
                "question": "What does RAG stand for?",
                "options": ["Retrieve and Generate", "Random Answer Generator", "Ranked Answer Generator"],
                "difficulty": "moderate",
            }
        }


class Quiz(BaseModel):
    """Quiz schema."""

    quiz_id: str = Field(..., description="Unique quiz identifier")
    chapter_id: str = Field(..., description="Associated chapter ID")
    title: str = Field(..., description="Quiz title")
    total_questions: int = Field(..., description="Total number of questions")
    passing_score: int = Field(..., description="Minimum score to pass (percentage)")
    questions: List[QuizQuestion] = Field(..., description="List of questions")

    class Config:
        json_schema_extra = {
            "example": {
                "quiz_id": "quiz-01",
                "chapter_id": "01",
                "title": "Chapter 1 Quiz",
                "total_questions": 3,
                "passing_score": 70,
                "questions": [
                    {
                        "question_id": "q1",
                        "type": "multiple_choice",
                        "question": "What does RAG stand for?",
                        "options": ["Retrieve and Generate", "Random Answer Generator", "Ranked Answer Generator"],
                        "difficulty": "moderate",
                    }
                ],
            }
        }


class QuizAnswer(BaseModel):
    """User's answer to a quiz question."""

    question_id: str = Field(..., description="Question identifier")
    selected_index: int = Field(..., description="Index of selected answer")


class QuizSubmission(BaseModel):
    """Quiz submission schema."""

    user_id: str = Field(..., description="User identifier")
    answers: List[QuizAnswer] = Field(..., description="List of answers")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "answers": [
                    {"question_id": "q1", "selected_index": 0},
                    {"question_id": "q2", "selected_index": 1},
                ],
            }
        }


class QuestionResult(BaseModel):
    """Result for a single question."""

    question_id: str = Field(..., description="Question identifier")
    correct: bool = Field(..., description="Whether answer was correct")
    selected_index: int = Field(..., description="Index of selected answer")
    correct_index: int = Field(..., description="Index of correct answer")
    explanation: str = Field(..., description="Explanation of correct answer")


class QuizResult(BaseModel):
    """Quiz result schema."""

    quiz_id: str = Field(..., description="Quiz identifier")
    score: float = Field(..., description="Score as percentage")
    passed: bool = Field(..., description="Whether user passed the quiz")
    total_questions: int = Field(..., description="Total number of questions")
    correct_answers: int = Field(..., description="Number of correct answers")
    results: List[QuestionResult] = Field(..., description="Detailed results per question")
    feedback: str = Field(..., description="Feedback message")

    class Config:
        json_schema_extra = {
            "example": {
                "quiz_id": "quiz-01",
                "score": 85.0,
                "passed": True,
                "total_questions": 10,
                "correct_answers": 8,
                "results": [],
                "feedback": "Great job! You have a strong understanding.",
            }
        }


class AttemptSummary(BaseModel):
    """Summary of a single quiz attempt."""

    score: float = Field(..., description="Score percentage")
    passed: bool = Field(..., description="Whether attempt passed")
    attempted_at: str = Field(..., description="Attempt timestamp")


class QuizHistory(BaseModel):
    """Quiz attempt history response."""

    chapter_id: str = Field(..., description="Chapter identifier")
    total_attempts: int = Field(..., description="Total attempts by user")
    best_score: float = Field(..., description="Best score")
    latest_score: Optional[float] = Field(None, description="Latest score")
    passed: bool = Field(..., description="Whether latest attempt passed")
    attempts: List[AttemptSummary] = Field(..., description="List of attempt summaries")

    class Config:
        json_schema_extra = {
            "example": {
                "chapter_id": "01",
                "total_attempts": 3,
                "best_score": 92.0,
                "latest_score": 85.0,
                "passed": True,
                "attempts": [
                    {"score": 70.0, "passed": False, "attempted_at": "2026-01-25T10:20:30Z"},
                    {"score": 92.0, "passed": True, "attempted_at": "2026-01-28T09:15:00Z"},
                ],
            }
        }