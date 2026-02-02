# """Main FastAPI application."""

# import logging

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from .api.v1 import api_router
# from .config import settings
# from .logging_config import setup_logging

# # Set up logging
# setup_logging(settings.LOG_LEVEL)
# logger = logging.getLogger(__name__)

# # Create FastAPI application
# app = FastAPI(
#     title=settings.APP_NAME,
#     version=settings.APP_VERSION,
#     description="Backend API for Course Companion FTE - Generative AI Fundamentals",
#     docs_url="/docs",
#     redoc_url="/redoc",
#     openapi_url="/openapi.json",
# )

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.on_event("startup")
# async def startup_event():
#     """Run on application startup."""
#     # Initialize local DB *first* to ensure it's available even if Redis or other
#     # services are unreachable during startup.
#     try:
#         from .database import init_db

#         init_db()
#         logger.info("Database initialized (local fallback)")
#     except Exception as e:
#         logger.error(f"Database initialization failed: {e}")

#     logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
#     logger.info(f"Environment: {settings.ENVIRONMENT}")
#     logger.info(f"Debug mode: {settings.DEBUG}")


# @app.on_event("shutdown")
# async def shutdown_event():
#     """Run on application shutdown."""
#     logger.info(f"Shutting down {settings.APP_NAME}")


# @app.get("/")
# async def root():
#     """Root endpoint.

#     Returns:
#         Application information
#     """
#     return {
#         "name": settings.APP_NAME,
#         "version": settings.APP_VERSION,
#         "status": "operational",
#         "docs": "/docs",
#     }


# @app.get("/health")
# async def health_check():
#     """Health check endpoint.

#     Returns:
#         Health status
#     """
#     return {"status": "healthy", "version": settings.APP_VERSION}


# # Include API router
# app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=settings.DEBUG,
#         log_level=settings.LOG_LEVEL.lower(),
#     )
# #

"""Main FastAPI application."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import api_router
from .config import settings
from .logging_config import setup_logging

# Set up logging
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Course Companion FTE - Generative AI Fundamentals",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS - ChatGPT Apps ke liye important!
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chatgpt.com",
        "https://chat.openai.com",
        "https://cdn.jsdelivr.net",  # ChatGPT plugins
        *settings.CORS_ORIGINS,  # Your existing CORS origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    # Initialize local DB *first* to ensure it's available even if Redis or other
    # services are unreachable during startup.
    try:
        from .database import init_db

        init_db()
        logger.info("Database initialized (local fallback)")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint.

    Returns:
        Application information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "chatgpt_app_ready": True,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy", "version": settings.APP_VERSION}


# ============================================
# ChatGPT Apps Support
# ============================================

@app.get("/.well-known/ai-plugin.json")
async def ai_plugin_manifest():
    """
    ChatGPT Plugin manifest (for ChatGPT Apps).
    This tells ChatGPT about your API capabilities.
    
    NOTE: OAuth NOT required - using 'none' authentication for simplicity.
    """
    return {
        "schema_version": "v1",
        "name_for_human": "Course Companion",
        "name_for_model": "course_companion",
        "description_for_human": "Learn Generative AI fundamentals with interactive lessons, quizzes, and progress tracking.",
        "description_for_model": "Course Companion is an AI-powered tutor that helps students learn Generative AI fundamentals. It provides chapter content, quizzes, progress tracking, and personalized learning paths. Use the available tools to retrieve chapters, give quizzes, and track student progress.",
        "auth": {
            "type": "none"  # No authentication required - simple & easy!
        },
        "api": {
            "type": "openapi",
            "url": f"{settings.BASE_URL}/openapi.json",
            "is_user_authenticated": False
        },
        "logo_url": f"{settings.BASE_URL}/static/logo.png",  # Optional: add your logo
        "contact_email": "support@coursecompanion.com",  # Optional: your email
        "legal_info_url": f"{settings.BASE_URL}/legal"  # Optional: legal info
    }


@app.get("/.well-known/mcp.json")
async def mcp_manifest():
    """
    MCP (Model Context Protocol) manifest.
    Alternative to ai-plugin.json - newer standard.
    
    This defines the tools (functions) ChatGPT can call.
    """
    return {
        "name": "Course Companion",
        "version": settings.APP_VERSION,
        "description": "AI-powered tutor for Generative AI fundamentals",
        "capabilities": {
            "tools": True,
            "prompts": True,
            "resources": True
        },
        "tools": [
            {
                "name": "list_chapters",
                "description": "Get a list of all available course chapters with their metadata",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_chapter",
                "description": "Retrieve the full content of a specific chapter by its ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chapter_id": {
                            "type": "string",
                            "description": "The unique identifier of the chapter (e.g., 'intro-to-llms')"
                        }
                    },
                    "required": ["chapter_id"]
                }
            },
            {
                "name": "search_content",
                "description": "Search across all chapters for specific keywords or topics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query or keywords"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_quiz",
                "description": "Get quiz questions for a specific chapter to test student understanding",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chapter_id": {
                            "type": "string",
                            "description": "The chapter ID to get quiz for"
                        }
                    },
                    "required": ["chapter_id"]
                }
            },
            {
                "name": "submit_quiz",
                "description": "Submit student's quiz answers for grading and get immediate feedback",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "quiz_id": {
                            "type": "string",
                            "description": "The quiz identifier"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Student identifier"
                        },
                        "answers": {
                            "type": "object",
                            "description": "Quiz answers as key-value pairs (question_id: answer)",
                            "additionalProperties": True
                        }
                    },
                    "required": ["quiz_id", "user_id", "answers"]
                }
            },
            {
                "name": "get_progress",
                "description": "Get student's learning progress including completed chapters, streaks, and quiz scores",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Student identifier"
                        }
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "complete_chapter",
                "description": "Mark a chapter as completed and update student progress",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Student identifier"
                        },
                        "chapter_id": {
                            "type": "string",
                            "description": "Chapter to mark as complete"
                        },
                        "time_spent_minutes": {
                            "type": "integer",
                            "description": "Time spent on the chapter in minutes"
                        }
                    },
                    "required": ["user_id", "chapter_id", "time_spent_minutes"]
                }
            }
        ]
    }


@app.get("/legal")
async def legal_info():
    """Legal information endpoint (optional)."""
    return {
        "terms_of_service": "https://coursecompanion.com/terms",
        "privacy_policy": "https://coursecompanion.com/privacy"
    }


# ============================================
# Include API Router
# ============================================

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )