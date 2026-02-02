"""API v1 package."""

from fastapi import APIRouter

from . import course, progress, quizzes, search

api_router = APIRouter()

# Include all routers
api_router.include_router(course.router, tags=["course"])
api_router.include_router(quizzes.router, tags=["quizzes"])
api_router.include_router(progress.router, tags=["progress"])
api_router.include_router(search.router, tags=["search"])

# Admin routes (dev only)
from fastapi import APIRouter, HTTPException

admin_router = APIRouter()


@admin_router.post("/admin/seed-cache")
async def seed_cache_endpoint():
    """Seed cache (course, chapters, quizzes) into cache storage."""
    try:
        # Import and run the seeder
        from scripts.seed_cache import main as seed_main

        await seed_main()
        return {"status": "ok", "message": "Cache seeded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

api_router.include_router(admin_router, tags=["admin"])
