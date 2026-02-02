"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "CourseCompanionFTE"
    assert data["status"] == "operational"


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_all_chapters_structure(client: TestClient):
    """Test get all chapters endpoint structure."""
    response = client.get("/api/v1/chapters")
    assert response.status_code == 200
    data = response.json()
    assert "chapters" in data
    assert isinstance(data["chapters"], list)


def test_search_endpoint_validation(client: TestClient):
    """Test search endpoint validation."""
    # Test without query
    response = client.get("/api/v1/search")
    assert response.status_code == 422  # Validation error

    # Test with short query
    response = client.get("/api/v1/search?q=a")
    assert response.status_code == 400

    # Test with valid query
    response = client.get("/api/v1/search?q=transformer")
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert "total_results" in data


def test_access_check_validation(client: TestClient):
    """Test access check endpoint validation."""
    # Test without parameters
    response = client.get("/api/v1/access/check")
    assert response.status_code == 422  # Validation error

    # Test with invalid user_id
    response = client.get("/api/v1/access/check?user_id=invalid&chapter_id=01")
    assert response.status_code == 400

    # Test with valid parameters
    response = client.get(
        "/api/v1/access/check?user_id=123e4567-e89b-12d3-a456-426614174000&chapter_id=01"
    )
    assert response.status_code == 200
    data = response.json()
    assert "has_access" in data
    assert "is_premium" in data
    assert "chapter_id" in data
    assert "reason" in data
