"""
CRUD operations for the database
"""

from typing import Optional
from bson import ObjectId
from app.models import Conversation, Message
from app.db.mongodb import get_database


async def get_conversation(conversation_id: str) -> Optional[Conversation]:
    db = await get_database()
    conversation = await db.conversations.find_one(
        {"_id": ObjectId(conversation_id)}
    )
    if conversation:
        return Conversation(**conversation)
    return None


async def create_conversation(conversation: Conversation) -> Conversation:
    db = await get_database()
    await db.conversations.insert_one(conversation.dict(by_alias=True))
    return conversation


async def add_message_to_conversation(conversation_id: str, message: Message):
    db = await get_database()
    await db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$push": {"messages": message.dict(by_alias=True)}}
    )
