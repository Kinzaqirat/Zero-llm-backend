import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse

from .api.v1 import api_router
from .config import settings
from .logging_config import setup_logging

setup_logging(settings.LOG_LEVEL)
from .logging_config import setup_logging

setup_logging(settings.LOG_LEVEL)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# CORS updated for ChatGPT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chatgpt.com", "https://chat.openai.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MCP SSE Implementation (Fix for your error) ---

@app.get("/sse")
async def sse_endpoint(request: Request):
    """
    Ye endpoint ChatGPT ko 'text/event-stream' bhejay ga jo usay chahiye.
    """
    async def event_generator():
        # Shuru mein connection establish karne ke liye ek 'endpoint' event bhejna zaroori hai
        yield {
            "event": "endpoint",
            "data": f"{settings.BASE_URL}/mcp" # Aapka MCP post endpoint
        }
        
        while True:
            if await request.is_disconnected():
                break
            await asyncio.sleep(10) # Connection zinda rakhne ke liye
            yield {"data": "heartbeat"}

    return EventSourceResponse(event_generator())

# --- Manifests ---

@app.get("/.well-known/mcp.json")
async def mcp_manifest():
    return {
        "mcp_version": "1.0",
        "name": "Course Companion",
        "version": settings.APP_VERSION,
        "capabilities": {"tools": True},
        "tools": [
            {
                "name": "list_chapters",
                "description": "Get all course chapters",
                "inputSchema": {"type": "object", "properties": {}}
            }
            # Baqi tools jo aapne likhay thay wo yahan add kar lein...
        ]
    }

# Baqi ka purana code (startup, health, routers) yahan nichey rahega...
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)