"""
WebSocket Connection Manager
Manages WebSocket connections and message broadcasting
"""

from typing import Dict, Set, List, Optional
from datetime import datetime, timezone
import json
import asyncio
import logging
from fastapi import WebSocket, WebSocketDisconnect

from app.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time communication
    """
    
    def __init__(self):
        # Active connections: {user_id: {socket_id: WebSocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # User to conversation mapping: {user_id: conversation_id}
        self.user_conversations: Dict[str, str] = {}
        # Conversation to users mapping: {conversation_id: Set[user_id]}
        self.conversation_users: Dict[str, Set[str]] = {}
        # Socket ID to user mapping: {socket_id: user_id}
        self.socket_users: Dict[str, str] = {}
        # Heartbeat tasks
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
        
    async def initialize(self):
        """Initialize the connection manager"""
        logger.info("WebSocket connection manager initialized")
        
    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        conversation_id: str,
        socket_id: str
    ) -> bool:
        """
        Connect a user to a WebSocket
        
        Args:
            websocket: The WebSocket connection
            user_id: The user's ID
            conversation_id: The conversation ID
            socket_id: Unique socket identifier
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Check max connections per user
            if user_id in self.active_connections:
                if len(self.active_connections[user_id]) >= settings.WS_MAX_CONNECTIONS_PER_USER:
                    await websocket.close(code=4008, reason="Max connections exceeded")
                    return False
            
            # Accept the WebSocket connection
            await websocket.accept()
            
            # Store connection
            if user_id not in self.active_connections:
                self.active_connections[user_id] = {}
            self.active_connections[user_id][socket_id] = websocket
            
            # Update mappings
            self.user_conversations[user_id] = conversation_id
            self.socket_users[socket_id] = user_id
            
            if conversation_id not in self.conversation_users:
                self.conversation_users[conversation_id] = set()
            self.conversation_users[conversation_id].add(user_id)
            
            # Start heartbeat
            self.heartbeat_tasks[socket_id] = asyncio.create_task(
                self._heartbeat(websocket, socket_id)
            )
            
            # Notify other users
            await self.broadcast_user_joined(user_id, conversation_id)
            
            logger.info(f"User {user_id} connected to conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting user {user_id}: {e}")
            return False
    
    async def disconnect(self, socket_id: str):
        """
        Disconnect a user from WebSocket
        
        Args:
            socket_id: The socket identifier
        """
        try:
            # Get user ID from socket
            user_id = self.socket_users.get(socket_id)
            if not user_id:
                return
            
            # Get conversation ID
            conversation_id = self.user_conversations.get(user_id)
            
            # Cancel heartbeat task
            if socket_id in self.heartbeat_tasks:
                self.heartbeat_tasks[socket_id].cancel()
                del self.heartbeat_tasks[socket_id]
            
            # Remove connection
            if user_id in self.active_connections:
                if socket_id in self.active_connections[user_id]:
                    del self.active_connections[user_id][socket_id]
                
                # If no more connections for this user
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    
                    # Remove from conversation
                    if conversation_id and conversation_id in self.conversation_users:
                        self.conversation_users[conversation_id].discard(user_id)
                        if not self.conversation_users[conversation_id]:
                            del self.conversation_users[conversation_id]
                    
                    # Remove user conversation mapping
                    if user_id in self.user_conversations:
                        del self.user_conversations[user_id]
                    
                    # Notify other users
                    if conversation_id:
                        await self.broadcast_user_left(user_id, conversation_id)
            
            # Remove socket user mapping
            if socket_id in self.socket_users:
                del self.socket_users[socket_id]
            
            logger.info(f"User {user_id} disconnected from socket {socket_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting socket {socket_id}: {e}")
    
    async def send_personal_message(self, message: str, user_id: str):
        """
        Send a message to a specific user
        
        Args:
            message: The message to send
            user_id: The user's ID
        """
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id].values():
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
    
    async def broadcast_to_conversation(
        self,
        message: str,
        conversation_id: str,
        exclude_user: Optional[str] = None
    ):
        """
        Broadcast a message to all users in a conversation
        
        Args:
            message: The message to broadcast
            conversation_id: The conversation ID
            exclude_user: User ID to exclude from broadcast
        """
        if conversation_id not in self.conversation_users:
            return
        
        for user_id in self.conversation_users[conversation_id]:
            if user_id != exclude_user:
                await self.send_personal_message(message, user_id)
    
    async def broadcast_user_joined(self, user_id: str, conversation_id: str):
        """Broadcast when a user joins a conversation"""
        message = json.dumps({
            "type": "user_joined",
            "userId": user_id,
            "conversationId": conversation_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        await self.broadcast_to_conversation(message, conversation_id, exclude_user=user_id)
    
    async def broadcast_user_left(self, user_id: str, conversation_id: str):
        """Broadcast when a user leaves a conversation"""
        message = json.dumps({
            "type": "user_left",
            "userId": user_id,
            "conversationId": conversation_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        await self.broadcast_to_conversation(message, conversation_id)
    
    async def disconnect_all(self):
        """Disconnect all active connections"""
        for user_id in list(self.active_connections.keys()):
            for socket_id in list(self.active_connections[user_id].keys()):
                await self.disconnect(socket_id)
    
    async def _heartbeat(self, websocket: WebSocket, socket_id: str):
        """
        Send periodic heartbeat to keep connection alive
        
        Args:
            websocket: The WebSocket connection
            socket_id: The socket identifier
        """
        try:
            while True:
                await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
                await websocket.send_json({"type": "ping"})
        except WebSocketDisconnect:
            await self.disconnect(socket_id)
        except Exception as e:
            logger.error(f"Heartbeat error for socket {socket_id}: {e}")
            await self.disconnect(socket_id)
