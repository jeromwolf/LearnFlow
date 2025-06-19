"""Test-specific configuration overrides.

This module provides test-specific configuration that overrides the main settings
when running tests.
"""
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from pydantic import PostgresDsn

from .config import Settings

# Load test environment variables from test.env
env_path = Path(__file__).parent.parent.parent.parent / "test.env"
load_dotenv(dotenv_path=env_path)


class TestSettings(Settings):
    """Test settings that override the main settings for testing."""

    # Override required fields with test defaults
    SUPABASE_URL: str = "https://test-supabase.co"
    SUPABASE_KEY: str = "test-supabase-key"
    SUPABASE_JWT_SECRET: str = "test-jwt-secret"
    POSTGRES_SERVER: str = "test-db"
    POSTGRES_USER: str = "test"
    POSTGRES_PASSWORD: str = "test"
    POSTGRES_DB: str = "test"
    SQLALCHEMY_DATABASE_URI: PostgresDsn = "postgresql://test:test@test-db/test"
    
    # Test-specific settings
    TESTING: bool = True
    DEBUG: bool = True
    ENV: str = "test"
    
    # Override the database URI validator to accept our test values
    @classmethod
    def _enrich_kwargs(
        cls,
        kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Override to skip validation for test settings."""
        return kwargs

    class Config:
        """Test settings configuration."""
        env_file = env_path
        env_file_encoding = "utf-8"
        extra = "ignore"
        validate_assignment = True


def get_test_settings() -> TestSettings:
    """Get test settings.

    Returns:
        TestSettings: The test settings instance.
    """
    return TestSettings()
