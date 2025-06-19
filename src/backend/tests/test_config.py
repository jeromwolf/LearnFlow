"""
Test configuration for pytest.

This module sets up the test environment before any tests are run.
"""
import os

# Set environment variables before importing any app modules
os.environ["ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key"

# Disable Supabase for testing
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_KEY"] = ""
os.environ["SUPABASE_JWT_SECRET"] = ""

# Use SQLite for testing
os.environ["POSTGRES_SERVER"] = ""
os.environ["POSTGRES_USER"] = ""
os.environ["POSTGRES_PASSWORD"] = ""
os.environ["POSTGRES_DB"] = ""
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
