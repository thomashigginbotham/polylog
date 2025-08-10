"""
Google Vertex AI service for intelligent chat responses
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, ChatSession
    from google.oauth2 import service_account
    from google.auth import default
    import google.auth.exceptions
    VERTEX_AI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Vertex AI libraries not available: {e}")
    VERTEX_AI_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for interacting with Google Vertex AI (Gemini)."""

    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID
        self.location = settings.GCP_LOCATION
        self.model_name = settings.VERTEX_AI_MODEL
        self.max_tokens = settings.AI_MAX_TOKENS
        self.temperature = settings.AI_TEMPERATURE
        self.is_available = False
        self.model = None
        
        # Store chat sessions per conversation for context continuity
        self.chat_sessions: Dict[str, ChatSession] = {}
        
        # Conversation context storage (in-memory for now)
        self.conversation_contexts: Dict[str, List[Dict[str, str]]] = {}

    async def initialize(self) -> bool:
        """Initialize the AI service."""
        if not VERTEX_AI_AVAILABLE:
            logger.warning("Vertex AI client library not available")
            return False

        if not self.project_id:
            logger.warning("GCP_PROJECT_ID not configured - AI responses will be simulated")
            return False

        try:
            # Initialize credentials
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path and os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                logger.info(f"Loaded service account credentials from {credentials_path}")
            else:
                # Fall back to default credentials
                credentials, project = default()
                logger.info("Using default Google Cloud credentials")

            # Initialize Vertex AI
            vertexai.init(
                project=self.project_id,
                location=self.location,
                credentials=credentials
            )

            # Initialize the model
            self.model = GenerativeModel(self.model_name)
            
            # Log model initialization
            logger.info(f"Initialized {self.model_name} model successfully")
            
            logger.info(f"Vertex AI initialized successfully for project {self.project_id} with model {self.model_name}")
            self.is_available = True
            return True

        except google.auth.exceptions.DefaultCredentialsError as e:
            logger.error(f"Google Cloud credentials not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            return False

    def _get_or_create_chat_session(self, conversation_id: str) -> ChatSession:
        """Get existing chat session or create a new one for the conversation."""
        if conversation_id not in self.chat_sessions:
            if not self.model:
                raise ValueError("AI model not initialized")
            
            # Create new chat session with better system instruction
            system_instruction = f"""You are an AI assistant in Polylog, a collaborative chat platform where multiple users can have conversations together.

Key guidelines:
- Be helpful, friendly, and conversational
- Keep responses concise but informative (usually 1-3 sentences unless asked for more detail)
- You're participating in group conversations - be aware that multiple users might be present
- Be engaging and encourage collaboration between users
- If asked about technical topics, be accurate but accessible
- Use a warm, professional tone
- Don't dominate the conversation - let users talk to each other
- Only respond when you can add value or when directly asked

IMPORTANT SOCIAL CUES:
- Respond to greetings (hi, hello, hey) with simple, friendly greetings back
- Don't assume users want information about topics just because their name matches something
- Ask clarifying questions if the user's intent is unclear
- Respond appropriately to the context and tone of the message

Remember: You're facilitating conversation, not leading it."""

            self.chat_sessions[conversation_id] = self.model.start_chat()
            logger.info(f"Created new chat session for conversation {conversation_id}")
        
        return self.chat_sessions[conversation_id]

    async def generate_response(
        self,
        user_message: str,
        user_name: str,
        conversation_id: str
    ) -> str:
        """Generate an AI response to a user message."""
        
        try:
            if not self.is_available:
                return self._generate_fallback_response(user_message, user_name)

            # Get or create chat session for conversation continuity
            chat_session = self._get_or_create_chat_session(conversation_id)
            
            # Format the message with user context
            formatted_message = f"{user_name}: {user_message}"
            
            logger.info(f"Generating AI response for user {user_name} in conversation {conversation_id}")
            
            # Generate response using Vertex AI
            response = await asyncio.to_thread(
                chat_session.send_message,
                formatted_message
            )
            
            ai_response = response.text.strip()
            
            # Update conversation context for tracking
            self._update_conversation_context(
                conversation_id,
                user_message,
                ai_response,
                user_name
            )
            
            logger.info(f"Generated AI response for conversation {conversation_id}: {ai_response[:100]}...")
            return ai_response

        except Exception as e:
            logger.error(f"Error generating AI response: {e}", exc_info=True)
            return self._generate_fallback_response(user_message, user_name)

    async def generate_welcome_message(self, user_name: str) -> str:
        """Generate a personalized welcome message for new users."""
        try:
            if not self.is_available:
                return f"Welcome to Polylog, {user_name}! I'm here to help with any questions or discussions."

            if not self.model:
                return f"Welcome to Polylog, {user_name}! I'm here to help with any questions or discussions."

            prompt = f"""Generate a brief, friendly welcome message for {user_name} who just joined Polylog, a collaborative chat application. Keep it warm and conversational, under 40 words. Don't use their name in the message itself."""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating welcome message: {e}")
            return f"Welcome to Polylog! I'm here to help with any questions or discussions you'd like to have."

    async def generate_conversation_summary(self, messages: list) -> str:
        """Generate a summary for users joining mid-conversation."""
        try:
            if not self.is_available or not messages:
                return "The conversation is ongoing. Feel free to jump in!"

            if not self.model:
                return "The conversation is ongoing. Feel free to jump in!"

            # Format recent messages for context (last 10 messages)
            message_text = "\n".join([
                f"{msg.get('userName', 'User')}: {msg.get('content', '')}" 
                for msg in messages[-10:]
            ])
            
            prompt = f"""Briefly summarize this conversation in 1-2 sentences so a new user can understand the current context:

{message_text}

Summary:"""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return "The conversation is ongoing. Feel free to jump in!"

    def _update_conversation_context(
        self,
        conversation_id: str,
        user_message: str,
        ai_response: str,
        user_name: str
    ):
        """Update conversation context with new messages."""
        if conversation_id not in self.conversation_contexts:
            self.conversation_contexts[conversation_id] = []

        # Add user message
        self.conversation_contexts[conversation_id].append({
            "role": f"User ({user_name})",
            "content": user_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Add AI response
        self.conversation_contexts[conversation_id].append({
            "role": "AI Assistant",
            "content": ai_response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Keep only last 50 messages to prevent context from growing too large
        if len(self.conversation_contexts[conversation_id]) > 50:
            self.conversation_contexts[conversation_id] = \
                self.conversation_contexts[conversation_id][-50:]

    def should_ai_respond(
        self,
        user_message: str,
        user_name: str,
        recent_messages: List[Dict[str, Any]]
    ) -> bool:
        """Determine if the AI should respond to a message."""
        
        message_lower = user_message.lower().strip()

        # Always respond if directly mentioned
        ai_mentions = ["@ai", "ai assistant", "hey ai", "ask ai", "@assistant"]
        if any(mention in message_lower for mention in ai_mentions):
            logger.info(f"AI responding due to direct mention in message: {user_message[:50]}...")
            return True

        # Respond to questions
        if "?" in user_message:
            logger.info(f"AI responding to question: {user_message[:50]}...")
            return True

        # Respond to simple greetings appropriately (but don't over-respond)
        simple_greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
        if message_lower in simple_greetings or any(greeting == message_lower for greeting in simple_greetings):
            # Only respond to greetings if no recent AI greeting response
            recent_ai_greetings = sum(
                1 for msg in recent_messages[-3:]
                if msg.get("userName") == "AI Assistant" and 
                any(greeting in msg.get("content", "").lower() for greeting in ["hello", "hi", "hey", "good"])
            )
            if recent_ai_greetings == 0:
                logger.info(f"AI responding to greeting: {user_message[:50]}...")
                return True
            else:
                logger.info(f"AI skipping greeting response to avoid repetition")
                return False

        # Respond if conversation has been quiet (no AI response in last 3 messages)
        ai_response_count = sum(
            1 for msg in recent_messages[-3:]
            if msg.get("userName") == "AI Assistant"
        )

        if ai_response_count == 0 and len(recent_messages) >= 2:
            logger.info("AI responding due to conversation lull")
            return True

        # Don't respond too frequently (max 1 in 3 messages)
        recent_ai_responses = sum(
            1 for msg in recent_messages[-3:]
            if msg.get("userName") == "AI Assistant"
        )

        if recent_ai_responses >= 2:
            logger.info("AI skipping response to avoid dominating conversation")
            return False

        # Respond with moderate probability for engagement (20% chance, reduced from 30%)
        should_respond = hash(user_message + user_name) % 10 < 2
        if should_respond:
            logger.info(f"AI responding for engagement: {user_message[:50]}...")
        else:
            logger.info(f"AI skipping message for natural conversation flow: {user_message[:50]}...")
        
        return should_respond

    def clear_conversation_context(self, conversation_id: str):
        """Clear conversation context for a conversation."""
        if conversation_id in self.conversation_contexts:
            del self.conversation_contexts[conversation_id]
            logger.info(f"Cleared message context for conversation: {conversation_id}")
            
        if conversation_id in self.chat_sessions:
            del self.chat_sessions[conversation_id]
            logger.info(f"Cleared chat session for conversation: {conversation_id}")

    def reset_conversation_behavior(self, conversation_id: str):
        """Reset conversation behavior - useful after system updates."""
        self.clear_conversation_context(conversation_id)
        logger.info(f"Reset conversation behavior for conversation: {conversation_id}")

    def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """Get a summary of the conversation context."""
        context = self.conversation_contexts.get(conversation_id)
        if not context:
            return None

        message_count = len(context)
        recent_topics = [msg["content"][:50] + "..." for msg in context[-3:]]

        return f"Conversation has {message_count} messages. Recent topics: {', '.join(recent_topics)}"

    def _generate_fallback_response(self, user_message: str, user_name: str) -> str:
        """Generate a fallback response when AI service is not available."""
        
        message_lower = user_message.lower().strip()

        # Simple greetings (exact matches)
        simple_greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        if message_lower in simple_greetings:
            greeting_responses = [
                f"Hello {user_name}! Good to see you in Polylog.",
                f"Hey there, {user_name}! How's your day going?",
                f"Hi {user_name}! Welcome to the conversation.",
                f"Hello {user_name}! What brings you here today?"
            ]
            # Use hash for consistent but varied responses
            response_index = hash(user_message + user_name) % len(greeting_responses)
            return greeting_responses[response_index]

        # Gratitude responses
        thanks = ["thank", "thanks", "appreciate"]
        if any(thank in message_lower for thank in thanks):
            return f"You're very welcome, {user_name}! I'm always here to help. What else can we work on together?"

        # Questions
        if "?" in user_message:
            return f"That's a great question, {user_name}! While I don't have all the answers, I'm here to help you think through it. What specific aspect would you like to explore?"

        # Product mentions
        if "polylog" in message_lower:
            return f"Polylog is designed for collaborative conversations like this one, {user_name}! It brings together multiple voices - humans and AI - in one seamless conversation. Pretty cool, right?"

        # Long messages
        if len(user_message) > 100:
            return f"I can see you've shared a lot of detail, {user_name}. That's really helpful context! Let me know what specific aspect you'd like me to focus on."

        # Default varied responses
        else:
            responses = [
                f"That's interesting, {user_name}! Tell me more about what you're thinking.",
                f"I hear you, {user_name}. What would you like to explore further on this topic?",
                f"Thanks for sharing that, {user_name}. How can I help you with this?",
                f"Good point, {user_name}! What's your take on this?",
                f"I appreciate you bringing this up, {user_name}. What direction would you like to take this conversation?"
            ]

            # Simple hash-based selection for consistency
            response_index = hash(user_message + user_name) % len(responses)
            return responses[response_index]


# Global AI service instance
ai_service = AIService()
