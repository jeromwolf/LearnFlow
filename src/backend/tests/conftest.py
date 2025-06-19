"""Test configuration and fixtures.

This module contains fixtures and configuration for testing the FastAPI application with Supabase.
"""
import os
from datetime import datetime, timedelta
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Set TESTING environment variable before importing app code
os.environ["TESTING"] = "1"

# Import test settings first
from app.core.test_settings import test_settings  # noqa: E402

# Apply test settings
os.environ.update({
    "SUPABASE_URL": test_settings.SUPABASE_URL,
    "SUPABASE_KEY": test_settings.SUPABASE_KEY,
    "SUPABASE_JWT_SECRET": test_settings.SUPABASE_JWT_SECRET,
    "POSTGRES_SERVER": test_settings.POSTGRES_SERVER,
    "POSTGRES_USER": test_settings.POSTGRES_USER,
    "POSTGRES_PASSWORD": test_settings.POSTGRES_PASSWORD,
    "POSTGRES_DB": test_settings.POSTGRES_DB,
    "SQLALCHEMY_DATABASE_URI": test_settings.SQLALCHEMY_DATABASE_URI,
})

# Now import app and models
from app.core.database import Base, get_db  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Choice, Content, Question, Quiz, User  # noqa: E402

# Use test settings
settings = test_settings

# Create test engine with Supabase PostgreSQL
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

# Create test database session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_db():
    """Create test database tables."""
    try:
        # Drop all tables first to ensure clean state
        with engine.connect() as conn:
            conn.execute(text('DROP SCHEMA public CASCADE; CREATE SCHEMA public;'))
            conn.commit()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        print(f"Error creating test database: {e}")
        raise


def drop_test_db():
    """Drop test database tables."""
    try:
        Base.metadata.drop_all(bind=engine)
    except SQLAlchemyError as e:
        print(f"Error dropping test database: {e}")
        raise


def override_get_db():
    """Override get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Set up test client with overridden dependencies
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Set up test database before tests and tear down after."""
    create_test_db()
    yield
    drop_test_db()


@pytest.fixture(scope="function")
def db():
    """Create a new database session for a test."""
    # Start a new transaction
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create a new session bound to this connection
    TestingSessionLocal.configure(bind=connection)
    session = TestingSessionLocal()

    yield session

    # Clean up
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_content(db, test_user):
    """Create test content."""
    content = Content(
        title="Test Content",
        description="Test Description",
        content_type="article",
        created_by=test_user.id,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


@pytest.fixture
def test_quiz(db, test_content, test_user):
    """Create a test quiz."""
    quiz = Quiz(
        title="Test Quiz",
        description="Test Quiz Description",
        content_id=test_content.id,
        created_by=test_user.id,
        is_published=True,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


@pytest.fixture
def test_question(db, test_quiz):
    """Create a test question."""
    question = Question(
        quiz_id=test_quiz.id,
        question_text="What is 2+2?",
        question_type="multiple_choice",
        points=10,
        order=1,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@pytest.fixture
def test_choices(db, test_question):
    """Create test choices for a question."""
    choices = [
        Choice(
            question_id=test_question.id,
            choice_text="3",
            is_correct=False,
            order=1,
        ),
        Choice(
            question_id=test_question.id,
            choice_text="4",
            is_correct=True,
            order=2,
        ),
    ]
    db.add_all(choices)
    db.commit()
    for choice in choices:
        db.refresh(choice)
    return choices


@pytest.fixture
def test_token(test_user):
    """Generate a test token for authentication."""
    expires_delta = timedelta(minutes=30)
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": str(test_user.id),
        "exp": expire,
        "email": test_user.email,
        "username": test_user.username,
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return f"Bearer {encoded_jwt}"


# User role fixtures
@pytest.fixture
def instructor_user(db):
    """Create an instructor user."""
    user = User(
        email="instructor@example.com",
        username="instructor",
        hashed_password=get_password_hash("instructorpassword"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def normal_user(db):
    """Create a normal user."""
    user = User(
        email="user@example.com",
        username="normaluser",
        hashed_password=get_password_hash("userpassword"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Authentication headers
@pytest.fixture
def normal_user_token_headers(client: TestClient, normal_user: User):
    """Get authentication headers for normal user."""
    login_data = {
        "username": normal_user.email,
        "password": "userpassword",
    }
    response = client.post("/api/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def instructor_token_headers(client: TestClient, instructor_user: User):
    """Get authentication headers for instructor user."""
    login_data = {
        "username": instructor_user.email,
        "password": "instructorpassword",
    }
    response = client.post("/api/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
