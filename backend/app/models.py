"""
Database models
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class Message(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    userId: Optional[PyObjectId]
    userName: str
    content: str
    isAiMessage: bool
    timestamp: datetime


class Participant(BaseModel):
    userId: PyObjectId
    email: str
    name: str
    avatarUrl: str
    joinedAt: datetime
    leftAt: Optional[datetime]
    isActive: bool
    lastSeen: datetime


class Conversation(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    createdAt: datetime
    lastActivity: datetime
    participants: List[Participant]
    messages: List[Message]


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    googleId: str
    email: str
    name: str
    avatarUrl: str
    createdAt: datetime
    updatedAt: datetime
