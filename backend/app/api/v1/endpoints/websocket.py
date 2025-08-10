"""
WebSocket endpoint with proper disconnect handling
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.ws_manager import manager
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()


def create_simple_message(
    user_name: str, 
    content: str, 
    is_ai_message: bool = False
) -> Dict[str, Any]:
    """Create a simple message dictionary for WebSocket communication."""
    return {
        "id": str(datetime.now(timezone.utc).timestamp()),
        "userId": None,
        "userName": user_name,
        "content": content,
        "isAiMessage": is_ai_message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        websocket: The WebSocket connection
        conversation_id: ID of the conversation to join
    """
    logger.info(
        "WebSocket connection attempt for conversation: %s", 
        conversation_id
    )
    
    try:
        # Connect to WebSocket
        await manager.connect(websocket, conversation_id)
        logger.info(
            "WebSocket connected successfully for conversation: %s", 
            conversation_id
        )
        
        # Send welcome message
        welcome_message = create_simple_message(
            user_name="System",
            content="Connected to conversation {}. Welcome to Polylog!".format(
                conversation_id
            ),
            is_ai_message=True
        )
        
        await websocket.send_text(json.dumps(welcome_message))
        logger.info(
            "Welcome message sent to conversation: %s", 
            conversation_id
        )
        
        # Main message loop with proper disconnect handling
        while True:
            try:
                # Use receive_json with timeout to avoid blocking on disconnected socket
                message_task = asyncio.create_task(websocket.receive_text())
                
                try:
                    # Wait for message with timeout
                    data = await asyncio.wait_for(message_task, timeout=30.0)
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    ping_message = create_simple_message(
                        user_name="System",
                        content="ping",
                        is_ai_message=True
                    )
                    await websocket.send_text(json.dumps(ping_message))
                    continue
                
                logger.info(
                    "Received message in %s: %s", 
                    conversation_id, 
                    data[:100] + "..." if len(data) > 100 else data
                )
                
                # Create user message
                user_message = create_simple_message(
                    user_name="Test User",  # TODO: Get from authentication
                    content=data,
                    is_ai_message=False
                )
                
                # Broadcast user message to all connected clients
                await manager.broadcast(
                    json.dumps(user_message), 
                    conversation_id
                )
                logger.info(
                    "Broadcasted user message in %s", 
                    conversation_id
                )
                
                # Create AI response
                ai_response = create_simple_message(
                    user_name="AI Assistant",
                    content="I received your message: '{}'. This is a test response from the AI!".format(data),
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
                
            except WebSocketDisconnect:
                logger.info(
                    "WebSocket disconnect received in message loop for %s", 
                    conversation_id
                )
                break  # Exit the message loop
                
            except RuntimeError as e:
                if "disconnect message has been received" in str(e):
                    logger.info(
                        "WebSocket already disconnected for %s", 
                        conversation_id
                    )
                    break  # Exit the message loop
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
                break  # Exit on unexpected errors
                
    except WebSocketDisconnect:
        logger.info(
            "WebSocket disconnected for conversation: %s", 
            conversation_id
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
                "WebSocket cleanup completed for conversation: %s", 
                conversation_id
            )
            
            # Notify other users of disconnect
            disconnect_message = create_simple_message(
                user_name="System",
                content="A user has left the conversation",
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
    """Simple WebSocket endpoint for debugging."""
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
