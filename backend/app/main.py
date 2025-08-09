"""
Polylog Backend Application
Main FastAPI application entry point
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Manage application lifecycle events
    """
    # Startup
    logger.info("Starting Polylog backend application")
    
    # Try to initialize MongoDB and Redis, but don't fail if they're not available
    try:
        from app.db.mongodb import init_mongodb, close_mongodb
        await init_mongodb()
        logger.info("MongoDB connection initialized")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.warning("Running without MongoDB")
    
    try:
        from app.db.redis import init_redis, close_redis
        await init_redis()
        logger.info("Redis connection initialized")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        logger.warning("Running without Redis")
    
    # Initialize WebSocket manager
    try:
        from app.websocket.connection_manager import ConnectionManager
        ws_manager = ConnectionManager()
        await ws_manager.initialize()
        app.state.ws_manager = ws_manager
        logger.info("WebSocket manager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize WebSocket manager: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Polylog backend application")
    
    # Close connections if they exist
    try:
        if hasattr(app.state, 'ws_manager'):
            await app.state.ws_manager.disconnect_all()
    except:
        pass
    
    try:
        await close_mongodb()
    except:
        pass
        
    try:
        await close_redis()
    except:
        pass
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Polylog - Multi-user collaborative AI chat platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
try:
    from app.core.middleware import RequestLoggingMiddleware
    app.add_middleware(RequestLoggingMiddleware)
except Exception as e:
    logger.error(f"Failed to add RequestLoggingMiddleware: {e}")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return JSONResponse(
        content={
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "healthy",
            "message": "Many voices, one conversation",
        }
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    # Check MongoDB
    try:
        from app.db.mongodb import check_mongodb_health
        mongodb_healthy = await check_mongodb_health()
        health_status["services"]["mongodb"] = "connected" if mongodb_healthy else "disconnected"
    except:
        health_status["services"]["mongodb"] = "unavailable"
    
    # Check Redis
    try:
        from app.db.redis import check_redis_health
        redis_healthy = await check_redis_health()
        health_status["services"]["redis"] = "connected" if redis_healthy else "disconnected"
    except:
        health_status["services"]["redis"] = "unavailable"
    
    # Check WebSocket
    health_status["services"]["websocket"] = "active" if hasattr(app.state, 'ws_manager') else "unavailable"
    
    return JSONResponse(content=health_status)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )
