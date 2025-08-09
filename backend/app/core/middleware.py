"""
Custom middleware for the application
"""

from fastapi import Request
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url} from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url} - Status: {response.status_code} - Duration: {duration:.3f}s"
        )
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-API-Version"] = "1.0.0"
        
        return response
