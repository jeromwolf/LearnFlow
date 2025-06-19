"""
Test utilities for the application.

This module contains utility functions and classes that are used across multiple test modules.
"""
from typing import Dict, Optional

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User
from app.schemas.user import UserCreate


def get_user_authentication_headers(
    client: TestClient, email: str, password: str
) -> Dict[str, str]:
    """Get authentication headers for a test user.
    
    Args:
        client: TestClient instance
        email: User email
        password: User password
        
    Returns:
        Dict containing the Authorization header
    """
    login_data = {
        "username": email,
        "password": password,
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login/access-token", data=login_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


def create_random_user(db: Session, **kwargs) -> User:
    """Create a random user for testing.
    
    Args:
        db: Database session
        **kwargs: Override default user attributes
        
    Returns:
        Created user
    """
    from app.core.security import get_password_hash
    from uuid import uuid4
    
    email = kwargs.pop("email", f"user-{uuid4().hex}@example.com")
    password = kwargs.pop("password", "password")
    full_name = kwargs.pop("full_name", "Test User")
    role = kwargs.pop("role", "user")
    is_active = kwargs.pop("is_active", True)
    
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        role=role,
        is_active=is_active,
        **kwargs
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_random_quiz(
    db: Session, created_by: int, content_id: Optional[int] = None, **kwargs
):
    """Create a random quiz for testing.
    
    Args:
        db: Database session
        created_by: ID of the user creating the quiz
        content_id: Optional content ID to associate with the quiz
        **kwargs: Override default quiz attributes
        
    Returns:
        Created quiz
    """
    from uuid import uuid4
    from app.models import Quiz
    
    title = kwargs.pop("title", f"Test Quiz {uuid4().hex[:8]}")
    description = kwargs.pop("description", "Test Quiz Description")
    
    quiz = Quiz(
        title=title,
        description=description,
        content_id=content_id,
        created_by=created_by,
        time_limit=30,
        max_attempts=3,
        passing_score=70,
        is_published=True,
        **kwargs
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def create_random_question(
    db: Session, quiz_id: int, **kwargs
):
    """Create a random question for testing.
    
    Args:
        db: Database session
        quiz_id: ID of the quiz this question belongs to
        **kwargs: Override default question attributes
        
    Returns:
        Created question
    """
    from app.models import Question
    
    question_text = kwargs.pop("question_text", "What is 2+2?")
    question_type = kwargs.pop("question_type", "multiple_choice")
    points = kwargs.pop("points", 10)
    order = kwargs.pop("order", 1)
    
    question = Question(
        quiz_id=quiz_id,
        question_text=question_text,
        question_type=question_type,
        points=points,
        order=order,
        **kwargs
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def create_random_choice(
    db: Session, question_id: int, is_correct: bool = False, **kwargs
):
    """Create a random choice for testing.
    
    Args:
        db: Database session
        question_id: ID of the question this choice belongs to
        is_correct: Whether this is the correct choice
        **kwargs: Override default choice attributes
        
    Returns:
        Created choice
    """
    from app.models import Choice
    from uuid import uuid4
    
    choice_text = kwargs.pop("choice_text", f"Choice {uuid4().hex[:4]}")
    order = kwargs.pop("order", 1)
    
    choice = Choice(
        question_id=question_id,
        choice_text=choice_text,
        is_correct=is_correct,
        order=order,
        **kwargs
    )
    db.add(choice)
    db.commit()
    db.refresh(choice)
    return choice
