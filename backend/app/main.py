"""
Polylog Backend Application
Main FastAPI application entry point
"""

from app.api.v1.endpoints.websocket import router as websocket_router
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
    format=(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Manage application lifecycle events
    """
    # Startup
    logger.info("Starting Polylog backend application")
    # Try to initialize MongoDB/Redis, but don't fail if they're not available
    try:
        from app.db.mongodb import init_mongodb, close_mongodb
        await init_mongodb()
        logger.info("MongoDB connection initialized")
    except Exception:
        logger.exception("Failed to connect to MongoDB")
        logger.warning("Running without MongoDB")
    try:
        from app.db.redis import init_redis, close_redis
        await init_redis()
        logger.info("Redis connection initialized")
    except Exception:
        logger.exception("Failed to connect to Redis")
        logger.warning("Running without Redis")
    # Initialize WebSocket manager - using simple manager for now
    logger.info("WebSocket manager ready")
    yield
    # Shutdown
    logger.info("Shutting down Polylog backend application")
    # Close database connections
    try:
        await close_mongodb()
    except Exception:
        pass
    try:
        await close_redis()
    except Exception:
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
except Exception:
    logger.exception("Failed to add RequestLoggingMiddleware")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include WebSocket router at root level (not under API versioning)
app.include_router(websocket_router, tags=["websocket"])


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
        health_status["services"]["mongodb"] = (
            "connected" if mongodb_healthy else "disconnected"
        )
    except Exception:
        health_status["services"]["mongodb"] = "unavailable"
    # Check Redis
    try:
        from app.db.redis import check_redis_health
        redis_healthy = await check_redis_health()
        health_status["services"]["redis"] = (
            "connected" if redis_healthy else "disconnected"
        )
    except Exception:
        health_status["services"]["redis"] = "unavailable"
        logger.exception("Failed to check Redis health")
    # Check WebSocket
    health_status["services"]["websocket"] = "active"
    return JSONResponse(content=health_status)


@app.get("/ws-debug")
async def websocket_debug():
    """Debug endpoint to check WebSocket configuration"""
    from app.ws_manager import manager

    return JSONResponse(
        content={
            "websocket_status": "available",
            "active_conversations": manager.get_all_conversations(),
            "total_connections": sum(
                manager.get_connection_count(conv_id)
                for conv_id in manager.get_all_conversations()
            ),
            "cors_origins": settings.BACKEND_CORS_ORIGINS,
            "debug_mode": settings.DEBUG,
            "websocket_endpoint": "/ws/{conversation_id}"
        }
    )


@app.get("/ws-test")
async def websocket_test_page():
    """Simple WebSocket test page"""
    from fastapi.responses import HTMLResponse

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test - Polylog</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #messages { height: 300px; border: 1px solid #ccc; padding: 10px; overflow-y: scroll; margin: 10px 0; }
            input, button { margin: 5px; padding: 8px; }
            input { width: 300px; }
        </style>
    </head>
    <body>
        <h1>WebSocket Test - Polylog</h1>
        <button onclick="connect()" id="connectBtn">Connect</button>
        <button onclick="disconnect()" id="disconnectBtn" disabled>Disconnect</button>
        <br>
        <input type="text" id="messageInput" placeholder="Type a message..." disabled>
        <button onclick="sendMessage()" id="sendBtn" disabled>Send</button>
        <div id="messages"></div>
        
        <script>
            let ws = null;
            const messages = document.getElementById('messages');
            const messageInput = document.getElementById('messageInput');
            const connectBtn = document.getElementById('connectBtn');
            const disconnectBtn = document.getElementById('disconnectBtn');
            const sendBtn = document.getElementById('sendBtn');
            
            function connect() {
                try {
                    ws = new WebSocket('ws://localhost:8000/ws/test');
                    
                    ws.onopen = function(event) {
                        addMessage('✅ Connected to WebSocket', 'success');
                        connectBtn.disabled = true;
                        disconnectBtn.disabled = false;
                        messageInput.disabled = false;
                        sendBtn.disabled = false;
                    };
                    
                    ws.onmessage = function(event) {
                        addMessage('📨 Received: ' + event.data, 'received');
                    };
                    
                    ws.onclose = function(event) {
                        addMessage('❌ WebSocket closed (Code: ' + event.code + ')', 'error');
                        resetUI();
                    };
                    
                    ws.onerror = function(error) {
                        addMessage('⚠️ WebSocket error: ' + error, 'error');
                    };
                } catch (error) {
                    addMessage('💥 Connection failed: ' + error, 'error');
                }
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                }
            }
            
            function sendMessage() {
                const message = messageInput.value.trim();
                if (message && ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(message);
                    addMessage('📤 Sent: ' + message, 'sent');
                    messageInput.value = '';
                } else if (!message) {
                    addMessage('⚠️ Please enter a message', 'warning');
                } else {
                    addMessage('⚠️ WebSocket is not connected', 'warning');
                }
            }
            
            function addMessage(message, type = 'info') {
                const div = document.createElement('div');
                const timestamp = new Date().toLocaleTimeString();
                div.innerHTML = `<strong>${timestamp}</strong> - ${message}`;
                
                switch(type) {
                    case 'success': div.style.color = 'green'; break;
                    case 'error': div.style.color = 'red'; break;
                    case 'warning': div.style.color = 'orange'; break;
                    case 'sent': div.style.color = 'blue'; break;
                    case 'received': div.style.color = 'purple'; break;
                }
                
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function resetUI() {
                connectBtn.disabled = false;
                disconnectBtn.disabled = true;
                messageInput.disabled = true;
                sendBtn.disabled = true;
                messageInput.value = '';
            }
            
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Initial message
            addMessage('🚀 WebSocket test page loaded. Click Connect to start!', 'info');
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )
