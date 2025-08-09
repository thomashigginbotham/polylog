"""
Redis connection and management
"""

from typing import Optional
import logging
import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis client instance
redis_client: Optional[redis.Redis] = None


async def init_redis() -> None:
    """
    Initialize Redis connection
    """
    global redis_client
    
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Successfully connected to Redis")
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise


async def close_redis() -> None:
    """
    Close Redis connection
    """
    global redis_client
    
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


async def get_redis() -> redis.Redis:
    """
    Get Redis client instance
    """
    if not redis_client:
        await init_redis()
    return redis_client


# Health check
async def check_redis_health() -> bool:
    """
    Check Redis connection health
    """
    if not redis_client:
        return False
    
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False
