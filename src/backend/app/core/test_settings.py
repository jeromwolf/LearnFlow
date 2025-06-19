"""Test-specific settings for the application.

This module provides test-specific settings that bypass validation
for testing purposes.
"""
from typing import Optional

from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """Test settings that override the main settings for testing."""
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LearnFlow-Test"

    # JWT settings
    SECRET_KEY: str = "test-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days

    # CORS settings
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000"
    ]

    # Database settings (SQLite for testing, but use PostgreSQL URL format)
    SQLALCHEMY_DATABASE_URI: str = "postgresql+psycopg2://test:test@localhost/test"
    
    # Actual SQLite URL for testing (will be used in conftest.py)
    SQLITE_TEST_DATABASE_URI: str = "sqlite:///./test.db"

    # Supabase settings (required for imports but not used in tests)
    SUPABASE_URL: str = "https://test-supabase.co"
    SUPABASE_KEY: str = "test-supabase-key"
    SUPABASE_JWT_SECRET: str = "test-jwt-secret"

    # PostgreSQL settings (required for imports but not used in tests)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "test"
    POSTGRES_PASSWORD: str = "test"
    POSTGRES_DB: str = "test"

    # Redis settings (required for imports but not used in tests)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # Test settings
    TESTING: bool = True
    DEBUG: bool = True
    ENV: str = "test"

    class Config:
        """Test settings configuration."""
        env_file = "test.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global test settings instance
test_settings = TestSettings()
