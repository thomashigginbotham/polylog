"""
Authentication endpoints
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
from datetime import datetime, timedelta
from jose import jwt

from app.core.config import settings

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class GoogleLoginRequest(BaseModel):
    token: str


@router.post("/login/google", response_model=Token)
async def login_google(request: GoogleLoginRequest):
    # Verify the token with Google
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            params={"access_token": request.token},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google token",
            )
        user_info = response.json()

    # TODO: Create or get user from the database

    # Create a JWT token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user_info["email"],
        "exp": datetime.utcnow() + access_token_expires
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return {"access_token": encoded_jwt, "token_type": "bearer"}
