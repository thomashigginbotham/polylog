"""
Application configuration settings
"""

from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields
    )
    
    # Project Info
    PROJECT_NAME: str = "Polylog"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    PRODUCTION: bool = False
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "polylog"
    
    # MongoDB Collections
    USERS_COLLECTION: str = "users"
    CONVERSATIONS_COLLECTION: str = "conversations"
    USER_SESSIONS_COLLECTION: str = "user_sessions"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PREFIX: str = "polylog"
    REDIS_TTL: int = 3600  # 1 hour
    
    # Google OAuth (Optional)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/callback"
    
    # Google Cloud AI Platform (Optional)
    GCP_PROJECT_ID: str = ""
    GCP_LOCATION: str = "us-central1"
    VERTEX_AI_MODEL: str = "gemini-1.5-pro"
    AI_MAX_TOKENS: int = 2048
    AI_TEMPERATURE: float = 0.7
    AI_TOP_P: float = 0.95
    AI_TOP_K: int = 40
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_MESSAGE_QUEUE_SIZE: int = 100
    WS_MAX_CONNECTIONS_PER_USER: int = 5
    
    # CORS - Simple string that will be parsed
    BACKEND_CORS_ORIGINS_STR: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from string"""
        if not self.BACKEND_CORS_ORIGINS_STR:
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS_STR.split(",") if origin.strip()]
    
    # Rate Limiting
    RATE_LIMIT_MESSAGES_PER_MINUTE: int = 100
    RATE_LIMIT_CONNECTIONS_PER_HOUR: int = 100
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Email (Optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Session
    SESSION_COOKIE_NAME: str = "polylog_session"
    SESSION_COOKIE_MAX_AGE: int = 86400 * 7  # 7 days
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    SESSION_COOKIE_SAMESITE: str = "lax"
    
    # AI Behavior
    AI_RESPONSE_DELAY_MIN: float = 0.5  # seconds
    AI_RESPONSE_DELAY_MAX: float = 2.0  # seconds
    AI_MENTION_TRIGGERS: List[str] = ["@ai", "@assistant", "hey ai", "ok ai"]
    AI_CONVERSATION_LULL_TIMEOUT: int = 30  # seconds
    AI_MAX_CONTEXT_MESSAGES: int = 50
    AI_SUMMARIZE_AFTER_MESSAGES: int = 100
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Feature Flags
    ENABLE_FILE_SHARING: bool = False
    ENABLE_VOICE_MESSAGES: bool = False
    ENABLE_VIDEO_CHAT: bool = False
    ENABLE_REACTIONS: bool = True
    ENABLE_THREADS: bool = False
    ENABLE_SEARCH: bool = True


# Create global settings instance
settings = Settings()
