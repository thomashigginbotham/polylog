"""
WebSocket connection manager with improved error handling.
"""

import logging
from typing import List, Dict, Optional

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for conversations."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str) -> None:
        """
        Accept WebSocket connection and add to conversation.

        Args:
            websocket: The WebSocket connection to accept
            conversation_id: ID of the conversation to join

        Raises:
            RuntimeError: If WebSocket connection fails
        """
        try: 
            await websocket.accept()
            if conversation_id not in self.active_connections:
                self.active_connections[conversation_id] = []
            self.active_connections[conversation_id].append(websocket)

            connection_count = len(self.active_connections[conversation_id])
            logger.info(
                "WebSocket connected to conversation %s. Total connections: %d",
                conversation_id,
                connection_count
            )
        except Exception as e:
            logger.error(
                "Error connecting WebSocket to %s: %s",
                conversation_id,
                str(e)
            )
            raise RuntimeError(
                "Failed to establish WebSocket connection"
            ) from e

    def disconnect(self, websocket: WebSocket, conversation_id: str) -> None:
        """
        Remove WebSocket connection from conversation.

        Args:
            websocket: The WebSocket connection to remove
            conversation_id: ID of the conversation to leave
        """
        try:
            if conversation_id not in self.active_connections:
                logger.warning(
                    "Attempted to disconnect from non-existent conversation: %s",
                    conversation_id
                )
                return

            if websocket in self.active_connections[conversation_id]:
                self.active_connections[conversation_id].remove(websocket)
                remaining_connections = len(
                    self.active_connections[conversation_id]
                )
                logger.info(
                    "WebSocket disconnected from conversation %s. "
                    "Remaining connections: %d",
                    conversation_id,
                    remaining_connections
                )

                # Clean up empty conversation
                if not self.active_connections[conversation_id]:
                    del self.active_connections[conversation_id]
                    logger.info(
                        "Conversation %s cleaned up - no remaining connections",
                        conversation_id
                    )
        except (KeyError, ValueError) as e:
            logger.warning(
                "Error disconnecting WebSocket from %s: %s",
                conversation_id,
                str(e)
            )
        except Exception as e:
            logger.error(
                "Unexpected error disconnecting WebSocket from %s: %s",
                conversation_id,
                str(e),
                exc_info=True
            )

    async def broadcast(self, message: str, conversation_id: str, exclude_socket: Optional[WebSocket] = None) -> None:
        """
        Broadcast message to all connections in a conversation.

        Args:
            message: The message to broadcast
            conversation_id: ID of the conversation to broadcast to
            exclude_socket: Optional WebSocket to exclude from broadcast
        """
        if conversation_id not in self.active_connections:
            logger.warning(
                "Attempted to broadcast to non-existent conversation: %s",
                conversation_id
            )
            return

        connections_to_remove = []
        successful_sends = 0

        for connection in self.active_connections[conversation_id]:
            # Skip excluded socket
            if exclude_socket and connection == exclude_socket:
                continue

            try:
                await connection.send_text(message)
                successful_sends += 1
            except WebSocketDisconnect:
                logger.info(
                    "WebSocket disconnected during broadcast in %s",
                    conversation_id
                )
                connections_to_remove.append(connection)
            except ConnectionResetError:
                logger.warning(
                    "Connection reset during broadcast in %s",
                    conversation_id
                )
                connections_to_remove.append(connection)
            except Exception as e:
                logger.error(
                    "Error sending message to connection in %s: %s",
                    conversation_id,
                    str(e)
                )
                connections_to_remove.append(connection)

        # Clean up broken connections
        for connection in connections_to_remove:
            self.disconnect(connection, conversation_id)

        logger.info(
            "Broadcasted message to %d connections in %s",
            successful_sends,
            conversation_id
        )

    def get_connection_count(self, conversation_id: str) -> int:
        """
        Get number of active connections for a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(conversation_id, []))

    def get_all_conversations(self) -> List[str]:
        """
        Get list of all active conversation IDs.

        Returns:
            List of conversation IDs with active connections
        """
        return list(self.active_connections.keys())


manager = ConnectionManager()
