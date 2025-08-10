"""
API v1 router
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import auth

# Create main API router
api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# WebSocket router moved to root level in main.py


# Health check endpoint
@api_router.get("/health")
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "1.0.0",
            "message": "API is running"
        }
    )

# Test endpoint


@api_router.get("/test")
async def test_endpoint():
    return JSONResponse(
        content={
            "message": "Backend is working!",
            "timestamp": "2025-08-09T10:00:00Z"
        }
    )

# TODO: Add more routers here
# api_router.include_router(
#     conversations.router, prefix="/conversations", tags=["conversations"]
# )
# api_router.include_router(
#     messages.router, prefix="/messages", tags=["messages"]
# )
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
