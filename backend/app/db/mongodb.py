"""
MongoDB database connection and management using Motor
"""

from typing import Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global MongoDB client and database instances
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb: Optional[AsyncIOMotorDatabase] = None


async def init_mongodb() -> None:
    """
    Initialize MongoDB connection
    """
    global mongodb_client, mongodb
    try:
        # Create Motor client
        mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            maxPoolSize=50,
            minPoolSize=10,
        )
        # Test connection
        await mongodb_client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")
        # Get database
        mongodb = mongodb_client[settings.MONGODB_DB_NAME]
        # Try to create indexes (but don't fail if it doesn't work)
        try:
            await create_indexes()
        except Exception:
            logger.warning("Could not create indexes", exc_info=True)
    except Exception:
        logger.exception("Failed to connect to MongoDB")
        raise


async def close_mongodb() -> None:
    """
    Close MongoDB connection
    """
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")


async def create_indexes() -> None:
    """
    Create database indexes for optimal performance
    """
    if mongodb is None:
        raise RuntimeError("MongoDB not initialized")
    try:
        # For now, just create basic indexes
        # We'll add more indexes as we implement features
        logger.info("Creating database indexes...")
        # Users collection indexes
        users_collection = mongodb[settings.USERS_COLLECTION]
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("googleId", unique=True)
        logger.info("Database indexes created successfully")
    except Exception:
        logger.exception("Failed to create indexes")
        raise


async def get_database() -> AsyncIOMotorDatabase:
    """
    Get MongoDB database instance
    """
    if mongodb is None:
        await init_mongodb()
    return mongodb


async def get_collection(collection_name: str):
    """
    Get a specific MongoDB collection
    """
    db = await get_database()
    return db[collection_name]


# Collection helper functions
async def get_users_collection():
    """Get users collection"""
    return await get_collection(settings.USERS_COLLECTION)


async def get_conversations_collection():
    """Get conversations collection"""
    return await get_collection(settings.CONVERSATIONS_COLLECTION)


async def get_sessions_collection():
    """Get user sessions collection"""
    return await get_collection(settings.USER_SESSIONS_COLLECTION)


# Health check
async def check_mongodb_health() -> bool:
    """
    Check MongoDB connection health
    """
    if mongodb_client is None:
        return False
    try:
        await mongodb_client.admin.command("ping")
        return True
    except Exception:
        return False
