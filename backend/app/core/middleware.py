"""
Custom middleware for the application
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
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
            "Request started: %s %s from %s",
            request.method,
            request.url,
            request.client.host if request.client else "unknown",
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            "Request completed: %s %s - Status: %s - Duration: %.3fs",
            request.method,
            request.url,
            response.status_code,
            duration,
        )

        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-API-Version"] = "1.0.0"

        return response
