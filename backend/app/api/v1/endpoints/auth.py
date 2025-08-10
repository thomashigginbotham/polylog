"""
Enhanced authentication endpoints with proper Google OAuth handling
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import httpx
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Optional
import logging

from app.core.config import settings
from app.db.mongodb import get_users_collection
from app.models import User

logger = logging.getLogger(__name__)
router = APIRouter()

# Security scheme
security = HTTPBearer()


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class GoogleTokenRequest(BaseModel):
    access_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatarUrl: str


async def create_access_token(user_data: dict) -> str:
    """Create JWT access token for authenticated user."""
    to_encode = {
        "sub": user_data["email"],
        "user_id": str(user_data["_id"]),
        "name": user_data["name"],
        "exp": datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def verify_google_token(access_token: str) -> dict:
    """Verify Google OAuth token and return user info."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": "Bearer {}".format(access_token)},
                timeout=10.0
            )

            if response.status_code != 200:
                logger.warning(
                    "Google token verification failed with status: %d",
                    response.status_code
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )

            user_info = response.json()
            logger.info("Google user verified: %s", user_info.get("email"))
            return user_info

    except httpx.TimeoutException:
        logger.error("Google token verification timeout")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Google verification timeout"
        )
    except Exception as e:
        logger.error("Google token verification error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )


async def create_or_update_user(google_user_info: dict) -> dict:
    """Create new user or update existing user from Google info."""
    try:
        users_collection = await get_users_collection()

        # Check if user already exists
        existing_user = await users_collection.find_one({
            "email": google_user_info["email"]
        })

        current_time = datetime.now(timezone.utc)

        if existing_user:
            # Update existing user
            update_data = {
                "name": google_user_info.get("name", ""),
                "avatarUrl": google_user_info.get("picture", ""),
                "updatedAt": current_time,
                "stats.lastSeen": current_time
            }

            await users_collection.update_one(
                {"_id": existing_user["_id"]},
                {"$set": update_data}
            )

            # Return updated user data
            updated_user = await users_collection.find_one({
                "_id": existing_user["_id"]
            })
            logger.info("Updated existing user: %s", updated_user["email"])
            return updated_user
        else:
            # Create new user
            new_user_data = {
                "googleId": google_user_info["sub"],
                "email": google_user_info["email"],
                "name": google_user_info.get("name", ""),
                "avatarUrl": google_user_info.get("picture", ""),
                "profile": {
                    "timezone": "UTC",  # TODO: Get from client
                    "preferences": {
                        "notifications": True,
                        "theme": "light"
                    }
                },
                "stats": {
                    "totalMessages": 0,
                    "conversationsJoined": 0,
                    "firstSeen": current_time,
                    "lastSeen": current_time
                },
                "createdAt": current_time,
                "updatedAt": current_time
            }

            result = await users_collection.insert_one(new_user_data)
            new_user_data["_id"] = result.inserted_id

            logger.info("Created new user: %s", new_user_data["email"])
            return new_user_data

    except Exception as e:
        logger.error("Error creating/updating user: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user from JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])

        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")

        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Get user from database
        users_collection = await get_users_collection()
        user = await users_collection.find_one({"email": email})

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user

    except JWTError as e:
        logger.warning("JWT decode error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error("Error getting current user: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.post("/login/google", response_model=Token)
async def login_google(request: GoogleTokenRequest):
    """Authenticate user with Google OAuth token."""
    try:
        # Verify Google token
        google_user_info = await verify_google_token(request.access_token)

        # Create or update user in database
        user_data = await create_or_update_user(google_user_info)

        # Create JWT token
        access_token = await create_access_token(user_data)

        # Return response
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user_data["_id"]),
                "email": user_data["email"],
                "name": user_data["name"],
                "avatarUrl": user_data["avatarUrl"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        name=current_user["name"],
        avatarUrl=current_user["avatarUrl"]
    )


@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token removal)."""
    # For JWT tokens, logout is handled client-side by removing the token
    # In the future, we could add token blacklisting here
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh JWT token."""
    try:
        new_token = await create_access_token(current_user)
        return {
            "access_token": new_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error("Token refresh error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
