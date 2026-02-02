"""Search schemas."""

from typing import List

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Search result schema."""

    chapter_id: str = Field(..., description="Chapter identifier")
    section_id: str = Field(..., description="Section identifier")
    title: str = Field(..., description="Section title")
    snippet: str = Field(..., description="Content snippet")
    relevance_score: float = Field(..., description="Relevance score")


class SearchResponse(BaseModel):
    """Search response schema."""

    query: str = Field(..., description="Search query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "transformer",
                "results": [
                    {
                        "chapter_id": "05",
                        "section_id": "5.2",
                        "title": "Transformer Architecture",
                        "snippet": "The transformer architecture revolutionized...",
                        "relevance_score": 0.95,
                    }
                ],
                "total_results": 1,
            }
        }


class AccessCheckResponse(BaseModel):
    """Access check response schema."""

    has_access: bool = Field(..., description="Whether user has access")
    is_premium: bool = Field(..., description="Whether user is premium")
    chapter_id: str = Field(..., description="Chapter identifier")
    reason: str = Field(..., description="Reason for access decision")

    class Config:
        json_schema_extra = {
            "example": {
                "has_access": True,
                "is_premium": False,
                "chapter_id": "01",
                "reason": "Free content",
            }
        }
