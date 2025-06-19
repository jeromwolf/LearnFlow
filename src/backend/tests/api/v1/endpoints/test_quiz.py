"""
퀴즈 API 엔드포인트 테스트 모듈입니다.

이 모듈은 퀴즈와 관련된 API 엔드포인트를 테스트합니다.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User, Content, Quiz, Question, Choice, QuizAttempt, QuestionAnswer
from app.schemas.quiz import QuestionType, QuizAttemptStatus
from app.tests.utils.utils import get_user_authentication_headers, random_lower_string


def test_create_quiz(
    client: TestClient, db: Session, normal_user_token_headers: dict, instructor_user: User
) -> None:
    """퀴즈 생성 테스트"""
    # 테스트용 콘텐츠 생성
    content = Content(
        title="Test Content",
        description="Test Description",
        content_type="quiz",
        created_by=instructor_user.id,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    
    data = {
        "title": "Test Quiz",
        "description": "Test Quiz Description",
        "content_id": str(content.id),
        "time_limit": 30,
        "max_attempts": 3,
        "passing_score": 70,
        "is_published": True,
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/quizzes/",
        headers=normal_user_token_headers,
        json=data,
    )
    
    # 강사가 아니면 403 오류 발생
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # 강사 권한으로 다시 시도
    instructor_headers = get_user_authentication_headers(client, instructor_user.email, "password")
    response = client.post(
        f"{settings.API_V1_STR}/quizzes/",
        headers=instructor_headers,
        json=data,
    )
    
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == data["title"]
    assert content["content_id"] == data["content_id"]
    assert "id" in content


def test_get_quiz(
    client: TestClient, db: Session, normal_user_token_headers: dict, instructor_user: User
) -> None:
    """퀴즈 조회 테스트"""
    # 테스트용 퀴즈 생성
    content = Content(
        title="Test Content",
        description="Test Description",
        content_type="quiz",
        created_by=instructor_user.id,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    
    quiz = Quiz(
        title="Test Quiz",
        description="Test Quiz Description",
        content_id=content.id,
        created_by=instructor_user.id,
        time_limit=30,
        max_attempts=3,
        passing_score=70,
        is_published=True,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # 퀴즈 조회
    response = client.get(
        f"{settings.API_V1_STR}/quizzes/{quiz.id}",
        headers=normal_user_token_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["id"] == str(quiz.id)
    assert content["title"] == quiz.title


def test_start_quiz_attempt(
    client: TestClient, db: Session, normal_user_token_headers: dict, normal_user: User, instructor_user: User
) -> None:
    """퀴즈 시도 시작 테스트"""
    # 테스트용 퀴즈 생성
    content = Content(
        title="Test Content",
        description="Test Description",
        content_type="quiz",
        created_by=instructor_user.id,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    
    quiz = Quiz(
        title="Test Quiz",
        description="Test Quiz Description",
        content_id=content.id,
        created_by=instructor_user.id,
        time_limit=30,
        max_attempts=3,
        passing_score=70,
        is_published=True,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # 퀴즈 시도 시작
    response = client.post(
        f"{settings.API_V1_STR}/quizzes/{quiz.id}/attempts/start",
        headers=normal_user_token_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["quiz_id"] == str(quiz.id)
    assert content["user_id"] == str(normal_user.id)
    assert content["status"] == QuizAttemptStatus.IN_PROGRESS


def test_submit_quiz_attempt(
    client: TestClient, db: Session, normal_user_token_headers: dict, normal_user: User, instructor_user: User
) -> None:
    """퀴즈 제출 테스트"""
    # 테스트용 퀴즈 및 질문, 선택지 생성
    content = Content(
        title="Test Content",
        description="Test Description",
        content_type="quiz",
        created_by=instructor_user.id,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    
    quiz = Quiz(
        title="Test Quiz",
        description="Test Quiz Description",
        content_id=content.id,
        created_by=instructor_user.id,
        time_limit=30,
        max_attempts=3,
        passing_score=70,
        is_published=True,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    question = Question(
        quiz_id=quiz.id,
        question_text="What is 2+2?",
        question_type=QuestionType.MULTIPLE_CHOICE,
        points=10,
        order=1,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    
    choice1 = Choice(
        question_id=question.id,
        choice_text="3",
        is_correct=False,
        order=1,
    )
    choice2 = Choice(
        question_id=question.id,
        choice_text="4",
        is_correct=True,
        order=2,
    )
    db.add(choice1)
    db.add(choice2)
    db.commit()
    
    # 퀴즈 시도 시작
    response = client.post(
        f"{settings.API_V1_STR}/quizzes/{quiz.id}/attempts/start",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    attempt = response.json()
    
    # 정답 제출
    submit_data = {
        "answers": [
            {
                "question_id": str(question.id),
                "answer_text": "4",
                "selected_choice_ids": [str(choice2.id)],
            }
        ]
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/quizzes/attempts/{attempt['id']}/submit",
        headers=normal_user_token_headers,
        json=submit_data,
    )
    
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["status"] == QuizAttemptStatus.COMPLETED
    assert content["score"] == 10  # 정답이므로 만점


def test_get_quiz_statistics(
    client: TestClient, db: Session, normal_user_token_headers: dict, instructor_user: User
) -> None:
    """퀴즈 통계 조회 테스트"""
    # 테스트용 퀴즈 생성
    content = Content(
        title="Test Content",
        description="Test Description",
        content_type="quiz",
        created_by=instructor_user.id,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    
    quiz = Quiz(
        title="Test Quiz",
        description="Test Quiz Description",
        content_id=content.id,
        created_by=instructor_user.id,
        time_limit=30,
        max_attempts=3,
        passing_score=70,
        is_published=True,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # 강사 권한으로 통계 조회
    instructor_headers = get_user_authentication_headers(client, instructor_user.email, "password")
    response = client.get(
        f"{settings.API_V1_STR}/quizzes/{quiz.id}/statistics",
        headers=instructor_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    stats = response.json()
    assert stats["quiz_id"] == str(quiz.id)
    assert stats["total_attempts"] == 0  # 아직 시도가 없음
    
    # 일반 사용자는 통계 조회 불가
    response = client.get(
        f"{settings.API_V1_STR}/quizzes/{quiz.id}/statistics",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_quiz_progress(
    client: TestClient, db: Session, normal_user_token_headers: dict, normal_user: User, instructor_user: User
) -> None:
    """사용자 퀴즈 진행 상황 조회 테스트"""
    # 테스트용 퀴즈 생성
    content = Content(
        title="Test Content",
        description="Test Description",
        content_type="quiz",
        created_by=instructor_user.id,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    
    quiz = Quiz(
        title="Test Quiz",
        description="Test Quiz Description",
        content_id=content.id,
        created_by=instructor_user.id,
        time_limit=30,
        max_attempts=3,
        passing_score=70,
        is_published=True,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # 사용자 퀴즈 진행 상황 조회
    response = client.get(
        f"{settings.API_V1_STR}/quizzes/{quiz.id}/progress",
        headers=normal_user_token_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    progress = response.json()
    assert progress["quiz_id"] == str(quiz.id)
    assert progress["user_id"] == str(normal_user.id)
    assert progress["attempts_count"] == 0  # 아직 시도가 없음


# 추가 테스트 케이스는 실제 애플리케이션 요구사항에 따라 확장할 수 있습니다.
