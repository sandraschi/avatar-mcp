"""
Configuration settings for the AvatarMCP server.

This module handles loading configuration from environment variables
and provides a centralized configuration object.
"""

import os
from pathlib import Path
from typing import List
from pydantic import BaseSettings, Field, validator

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server configuration
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")
    DEBUG: bool = Field(False, env="DEBUG")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    
    # VRM Models
    MODELS_DIR: str = Field(
        os.path.join(Path.home(), ".avatarmcp", "models"),
        env="MODELS_DIR"
    )
    
    # OSC Configuration
    OSC_CLIENT_ADDRESS: str = Field("127.0.0.1", env="OSC_CLIENT_ADDRESS")
    OSC_CLIENT_PORT: int = Field(9000, env="OSC_CLIENT_PORT")
    OSC_SERVER_ADDRESS: str = Field("127.0.0.1", env="OSC_SERVER_ADDRESS")
    OSC_SERVER_PORT: int = Field(9001, env="OSC_SERVER_PORT")
    
    # WebSocket Configuration
    WEBSOCKET_ENABLED: bool = Field(True, env="WEBSOCKET_ENABLED")
    WEBSOCKET_PATH: str = Field("/ws", env="WEBSOCKET_PATH")
    
    # Authentication
    API_KEYS: List[str] = Field([], env="API_KEYS")
    
    # Loki Logging
    ENABLE_LOKI: bool = Field(False, env="ENABLE_LOKI")
    LOKI_URL: str = Field("http://localhost:3100", env="LOKI_URL")
    
    @validator('API_KEYS', pre=True)
    def parse_api_keys(cls, v):
        """Parse API keys from comma-separated string to list."""
        if isinstance(v, str):
            return [key.strip() for key in v.split(",") if key.strip()]
        return v or []
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {', '.join(valid_levels)}")
        return v.upper()
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()

# Ensure models directory exists
os.makedirs(settings.MODELS_DIR, exist_ok=True)
