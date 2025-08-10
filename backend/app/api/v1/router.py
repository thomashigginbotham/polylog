"""
API v1 router
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import auth
from app.api.v1.endpoints.auth import get_current_user

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

# AI Test endpoint
@api_router.post("/test-ai")
async def test_ai_endpoint():
    """Test endpoint to verify AI integration is working"""
    try:
        from app.services.ai_service import ai_service
        
        # Test basic AI response
        response = await ai_service.generate_response(
            "Hello, can you introduce yourself?",
            "TestUser", 
            "test-conversation"
        )
        
        return JSONResponse(
            content={
                "status": "success",
                "ai_available": ai_service.is_available,
                "model": ai_service.model_name,
                "project_id": ai_service.project_id,
                "ai_response": response
            }
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "ai_available": False
            },
            status_code=500
        )

# Reset AI conversation context
@api_router.post("/reset-ai/{conversation_id}")
async def reset_ai_conversation(conversation_id: str):
    """Reset AI conversation context for better behavior"""
    try:
        from app.services.ai_service import ai_service
        
        ai_service.reset_conversation_behavior(conversation_id)
        
        return JSONResponse(
            content={
                "status": "success",
                "message": f"AI conversation context reset for {conversation_id}",
                "conversation_id": conversation_id
            }
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e)
            },
            status_code=500
        )

# Debug endpoint to test JWT token validation
@api_router.get("/debug-token")
async def debug_token_endpoint(current_user: dict = Depends(get_current_user)):
    """Debug endpoint to test JWT token validation"""
    try:
        from app.api.v1.endpoints.auth import get_current_user
        
        return JSONResponse(
            content={
                "status": "success", 
                "message": "Token is valid and user is authenticated",
                "user": {
                    "name": current_user["name"],
                    "email": current_user["email"],
                    "id": str(current_user["_id"])
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e)
            },
            status_code=401
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
