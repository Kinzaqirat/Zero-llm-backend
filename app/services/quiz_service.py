"""Quiz service for loading and grading quizzes."""

import json
import logging
from typing import List

from ..schemas.quizzes import (
    Quiz,
    QuizResult,
    QuizSubmission,
    QuestionResult,
)
from .storage_service import storage_service
from .cache_service import cache_service

logger = logging.getLogger(__name__)


class QuizService:
    """Service for managing quizzes and grading."""

    COURSE_PREFIX = "genai-fundamentals"

    async def get_quiz(self, chapter_id: str) -> Quiz:
        """Get quiz for a chapter.

        Args:
            chapter_id: Chapter identifier

        Returns:
            Quiz object without correct answers

        Raises:
            ValueError: If quiz not found
        """
        # Try cache first (key: quiz:{chapter_id})
        cache_key = f"quiz:{chapter_id}"

        try:
            cached = await cache_service.get(cache_key)
            if cached:
                quiz_data = json.loads(cached)
            else:
                # Fetch from storage
                key = f"{self.COURSE_PREFIX}/quizzes/quiz-{chapter_id}.json"
                content = await storage_service.get_object(key)

                if not content:
                    raise ValueError(f"Quiz not found for chapter {chapter_id}")

                quiz_data = json.loads(content)

                # Cache full quiz (including answers) for future use
                try:
                    await cache_service.set(cache_key, json.dumps(quiz_data), ttl=3600)
                except Exception:
                    logger.warning(f"Failed to cache quiz {chapter_id}")

            # Prepare public version (remove correct answers and explanations)
            public_quiz = json.loads(json.dumps(quiz_data))  # deep copy
            for question in public_quiz.get("questions", []):
                question.pop("correct_answer_index", None)
                question.pop("correct_answer", None)
                question.pop("explanation", None)

            return Quiz(**public_quiz)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching quiz for chapter {chapter_id}: {str(e)}")
            raise

    async def submit_quiz(self, chapter_id: str, submission: QuizSubmission) -> QuizResult:
        """Grade quiz submission.

        Args:
            chapter_id: Chapter identifier
            submission: User's quiz submission

        Returns:
            Quiz result with score and feedback

        Raises:
            ValueError: If quiz not found
        """
        try:
            # Get full quiz with answers
            key = f"{self.COURSE_PREFIX}/quizzes/quiz-{chapter_id}.json"
            content = await storage_service.get_object(key)

            if not content:
                raise ValueError(f"Quiz not found for chapter {chapter_id}")

            quiz_data = json.loads(content)

            # Grade answers
            correct_count = 0
            results: List[QuestionResult] = []

            for answer in submission.answers:
                # Find question
                question = next(
                    (q for q in quiz_data["questions"] if q["question_id"] == answer.question_id),
                    None,
                )

                if not question:
                    logger.warning(f"Question {answer.question_id} not found in quiz")
                    continue

                # Check if correct
                correct_index = question.get("correct_answer_index")
                if correct_index is None:
                    # True/False question - check correct_answer field
                    correct_answer = question.get("correct_answer")
                    is_correct = answer.selected_index == (1 if correct_answer else 0)
                    correct_index = 1 if correct_answer else 0
                else:
                    is_correct = answer.selected_index == correct_index

                if is_correct:
                    correct_count += 1

                results.append(
                    QuestionResult(
                        question_id=answer.question_id,
                        correct=is_correct,
                        selected_index=answer.selected_index,
                        correct_index=correct_index,
                        explanation=question.get("explanation", ""),
                    )
                )

            # Calculate score
            total_questions = len(submission.answers)
            score = (correct_count / total_questions * 100) if total_questions > 0 else 0
            passing_score = quiz_data.get("passing_score", 70)
            passed = score >= passing_score

            # Generate feedback
            feedback = self._generate_feedback(score, passed)

            logger.info(
                f"Quiz graded for user {submission.user_id}: {correct_count}/{total_questions} correct ({score:.1f}%)"
            )

            return QuizResult(
                quiz_id=quiz_data["quiz_id"],
                score=score,
                passed=passed,
                total_questions=total_questions,
                correct_answers=correct_count,
                results=results,
                feedback=feedback,
            )
        except Exception as e:
            logger.error(f"Error grading quiz for chapter {chapter_id}: {str(e)}")
            raise

    def _generate_feedback(self, score: float, passed: bool) -> str:
        """Generate feedback message based on score.

        Args:
            score: Score percentage
            passed: Whether user passed

        Returns:
            Feedback message
        """
        if score >= 90:
            return "Excellent work! You've mastered this chapter! 🌟"
        elif score >= 80:
            return "Great job! You have a strong understanding. 👏"
        elif passed:
            return "Good work! You passed the quiz. Keep learning! 📚"
        else:
            return "Keep learning! Review the chapter and try again. You've got this! 💪"


# Singleton instance
quiz_service = QuizService()
