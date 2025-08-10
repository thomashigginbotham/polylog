"""
WebSocket endpoint with authentication support
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.ws_manager import manager
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from jose import jwt, JWTError

from app.core.config import settings
from app.db.mongodb import get_users_collection

logger = logging.getLogger(__name__)
router = APIRouter()


def create_simple_message(
    user_id: Optional[str],
    user_name: str,
    content: str,
    is_ai_message: bool = False
) -> Dict[str, Any]:
    """Create a simple message dictionary for WebSocket communication."""
    return {
        "id": str(datetime.now(timezone.utc).timestamp()),
        "userId": user_id,
        "userName": user_name,
        "content": content,
        "isAiMessage": is_ai_message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


async def authenticate_websocket_user(token: Optional[str]) -> Optional[dict]:
    """Authenticate user from WebSocket token parameter."""
    if not token:
        logger.info("No token provided for WebSocket authentication")
        return None

    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])

        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")

        if not email or not user_id:
            logger.warning("Invalid token payload for WebSocket")
            return None

        # Get user from database
        users_collection = await get_users_collection()
        user = await users_collection.find_one({"email": email})

        if not user:
            logger.warning("User not found for WebSocket token: %s", email)
            return None

        logger.info("WebSocket user authenticated: %s", user["email"])
        return user

    except JWTError as e:
        logger.warning("WebSocket JWT decode error: %s", str(e))
        return None
    except Exception as e:
        logger.error("WebSocket authentication error: %s", str(e))
        return None


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time chat with authentication support.

    Args:
        websocket: The WebSocket connection
        conversation_id: ID of the conversation to join
        token: Optional JWT token for authentication
    """
    logger.info(
        "WebSocket connection attempt for conversation: %s",
        conversation_id
    )

    # Authenticate user (optional for now)
    authenticated_user = await authenticate_websocket_user(token)

    if authenticated_user:
        user_name = authenticated_user["name"]
        user_id = str(authenticated_user["_id"])
        logger.info("Authenticated WebSocket user: %s", user_name)
    else:
        # Fall back to anonymous user for development
        user_name = "Anonymous User"
        user_id = None
        logger.info("Anonymous WebSocket user connected")

    try:
        # Connect to WebSocket
        await manager.connect(websocket, conversation_id)
        logger.info(
            "WebSocket connected successfully for conversation: %s (user: %s)",
            conversation_id,
            user_name
        )

        # Send welcome message
        welcome_message = create_simple_message(
            user_id=None,
            user_name="System",
            content="Connected to conversation {}. Welcome to Polylog, {}!".format(
                conversation_id, user_name
            ),
            is_ai_message=True
        )

        await websocket.send_text(json.dumps(welcome_message))
        logger.info(
            "Welcome message sent to conversation: %s (user: %s)",
            conversation_id,
            user_name
        )

        # Notify other users of join
        if authenticated_user:
            join_message = create_simple_message(
                user_id=None,
                user_name="System",
                content="{} has joined the conversation".format(user_name),
                is_ai_message=True
            )
            await manager.broadcast(
                json.dumps(join_message),
                conversation_id,
                exclude_socket=websocket
            )

        # Main message loop with proper disconnect handling
        while True:
            try:
                # Wait for message with timeout
                message_task = asyncio.create_task(websocket.receive_text())

                try:
                    data = await asyncio.wait_for(message_task, timeout=30.0)
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    ping_message = create_simple_message(
                        user_id=None,
                        user_name="System",
                        content="ping",
                        is_ai_message=True
                    )
                    await websocket.send_text(json.dumps(ping_message))
                    continue

                logger.info(
                    "Received message in %s from %s: %s",
                    conversation_id,
                    user_name,
                    data[:100] + "..." if len(data) > 100 else data
                )

                # Create user message
                user_message = create_simple_message(
                    user_id=user_id,
                    user_name=user_name,
                    content=data,
                    is_ai_message=False
                )

                # Broadcast user message to all connected clients
                await manager.broadcast(
                    json.dumps(user_message),
                    conversation_id
                )
                logger.info(
                    "Broadcasted user message in %s from %s",
                    conversation_id,
                    user_name
                )

                # Create AI response
                ai_response = create_simple_message(
                    user_id=None,
                    user_name="AI Assistant",
                    content="Hello {}! I received your message: '{}'. This is a test response from the AI!".format(
                        user_name, data
                    ),
                    is_ai_message=True
                )

                # Broadcast AI response
                await manager.broadcast(
                    json.dumps(ai_response),
                    conversation_id
                )
                logger.info(
                    "Broadcasted AI response in %s",
                    conversation_id
                )

                # Update user message stats if authenticated
                if authenticated_user:
                    try:
                        users_collection = await get_users_collection()
                        await users_collection.update_one(
                            {"_id": authenticated_user["_id"]},
                            {
                                "$inc": {"stats.totalMessages": 1},
                                "$set": {"stats.lastSeen": datetime.now(timezone.utc)}
                            }
                        )
                    except Exception as stats_error:
                        logger.error(
                            "Error updating user stats: %s",
                            str(stats_error)
                        )

            except WebSocketDisconnect:
                logger.info(
                    "WebSocket disconnect received in message loop for %s (user: %s)",
                    conversation_id,
                    user_name
                )
                break

            except RuntimeError as e:
                if "disconnect message has been received" in str(e):
                    logger.info(
                        "WebSocket already disconnected for %s (user: %s)",
                        conversation_id,
                        user_name
                    )
                    break
                else:
                    logger.error(
                        "Runtime error in message loop for %s: %s",
                        conversation_id,
                        str(e)
                    )
                    break

            except json.JSONDecodeError as e:
                logger.error(
                    "JSON decode error in conversation %s: %s",
                    conversation_id,
                    str(e)
                )
                continue

            except (ConnectionResetError, ConnectionAbortedError) as e:
                logger.warning(
                    "Connection error in conversation %s: %s",
                    conversation_id,
                    str(e)
                )
                break

            except Exception as e:
                logger.error(
                    "Unexpected error in message loop for %s: %s",
                    conversation_id,
                    str(e),
                    exc_info=True
                )
                break

    except WebSocketDisconnect:
        logger.info(
            "WebSocket disconnected for conversation: %s (user: %s)",
            conversation_id,
            user_name
        )

    except Exception as e:
        logger.error(
            "WebSocket error for conversation %s: %s",
            conversation_id,
            str(e),
            exc_info=True
        )

    finally:
        # Ensure cleanup happens
        try:
            manager.disconnect(websocket, conversation_id)
            logger.info(
                "WebSocket cleanup completed for conversation: %s (user: %s)",
                conversation_id,
                user_name
            )

            # Notify other users of disconnect if authenticated
            if authenticated_user:
                disconnect_message = create_simple_message(
                    user_id=None,
                    user_name="System",
                    content="{} has left the conversation".format(user_name),
                    is_ai_message=True
                )
                await manager.broadcast(
                    json.dumps(disconnect_message),
                    conversation_id
                )
        except Exception as cleanup_error:
            logger.error(
                "Error during WebSocket cleanup for %s: %s",
                conversation_id,
                str(cleanup_error)
            )


@router.websocket("/ws-simple/{conversation_id}")
async def websocket_simple_endpoint(websocket: WebSocket, conversation_id: str):
    """Simple WebSocket endpoint for debugging (no authentication)."""
    logger.info(
        "Simple WebSocket connection attempt for conversation: %s",
        conversation_id
    )

    try:
        await websocket.accept()
        logger.info(
            "Simple WebSocket connected for conversation: %s",
            conversation_id
        )

        # Send immediate welcome message
        welcome_msg = {
            "type": "welcome",
            "message": "Connected to simple WebSocket",
            "conversation_id": conversation_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await websocket.send_text(json.dumps(welcome_msg))

        # Simple echo loop with proper disconnect handling
        while True:
            try:
                data = await websocket.receive_text()
                logger.info("Simple WebSocket received: %s", data)

                echo_msg = {
                    "type": "echo",
                    "original": data,
                    "response": "Echo: {}".format(data),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await websocket.send_text(json.dumps(echo_msg))

            except WebSocketDisconnect:
                logger.info(
                    "Simple WebSocket disconnect for conversation: %s",
                    conversation_id
                )
                break

            except RuntimeError as e:
                if "disconnect message has been received" in str(e):
                    logger.info(
                        "Simple WebSocket already disconnected for %s",
                        conversation_id
                    )
                    break
                else:
                    logger.error(
                        "Simple WebSocket runtime error for %s: %s",
                        conversation_id,
                        str(e)
                    )
                    break

    except Exception as e:
        logger.error(
            "Simple WebSocket error for conversation %s: %s",
            conversation_id,
            str(e),
            exc_info=True
        )
