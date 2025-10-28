"""
Configuration settings for the backend core module.
"""

import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    app_name: str = "Comment Widget API"
    debug: bool = False
    database_url: str = "sqlite:///./test.db"

    # NoCodeBackend settings
    nocodebackend_url: str = "https://openapi.nocodebackend.com"
    instance: str = os.getenv("INSTANCE", "41300_teste")
    nocodebackend_api_key: str = os.getenv("NOCODEBACKEND_API_KEY", "")
    webhook_url: str = os.getenv("WEBHOOK_URL", "")

    # Application settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")

    # Cache settings
    redis_url: str = os.getenv("REDIS_URL", "")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()