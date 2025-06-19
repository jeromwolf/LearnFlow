from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_active_admin
from app.schemas.user import UserInToken, UserRole
from app.schemas import quiz as schemas
from app import crud, models

router = APIRouter()

# Helper functions
def check_quiz_owner_or_admin(
    db: Session, 
    quiz_id: int, 
    user: UserInToken
) -> models.Quiz:
    """Check if user is the owner or admin"""
    db_quiz = crud.get_quiz(db, quiz_id=quiz_id)
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # 관리자 또는 콘텐츠 소유자인지 확인
    if user.role != UserRole.ADMIN and db_quiz.content.creator_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this quiz"
        )
    
    return db_quiz

# Quiz endpoints
@router.post("/quizzes/", response_model=schemas.QuizResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(
    quiz: schemas.QuizCreate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    새 퀴즈를 생성합니다.
    강사 또는 관리자만 생성할 수 있습니다.
    """
    if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors or admins can create quizzes"
        )
    
    # 콘텐츠 소유자인지 확인
    db_content = crud.get_content(db, content_id=quiz.content_id)
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if db_content.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create a quiz for this content"
        )
    
    return crud.create_quiz(db=db, quiz=quiz, creator_id=current_user.id)

@router.get("/quizzes/", response_model=List[schemas.QuizListResponse])
def read_quizzes(
    skip: int = 0,
    limit: int = 100,
    content_id: Optional[int] = None,
    is_published: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    퀴즈 목록을 조회합니다.
    관리자: 모든 퀴즈 조회 가능
    강사: 자신이 생성한 콘텐츠의 퀴즈 조회 가능
    일반 사용자: 공개된 퀴즈만 조회 가능
    """
    # 관리자는 모든 퀴즈 조회 가능
    if current_user.role == UserRole.ADMIN:
        return crud.get_quizzes(
            db, 
            skip=skip, 
            limit=limit, 
            content_id=content_id,
            is_published=is_published
        )
    # 강사는 자신이 만든 콘텐츠의 퀴즈만 조회 가능
    elif current_user.role == UserRole.INSTRUCTOR:
        # 자신이 만든 콘텐츠 ID 목록 가져오기
        content_ids = [c.id for c in crud.get_contents(db, creator_id=current_user.id)]
        
        # 자신이 만든 콘텐츠가 없는 경우 빈 목록 반환
        if not content_ids:
            return []
            
        # 자신이 만든 콘텐츠의 퀴즈만 필터링
        quizzes = crud.get_quizzes(
            db, 
            skip=skip, 
            limit=limit, 
            content_id=content_id,
            is_published=is_published
        )
        
        # 자신이 만든 콘텐츠의 퀴즈만 필터링
        return [q for q in quizzes if q.content_id in content_ids]
    # 일반 사용자는 공개된 퀴즈만 조회 가능
    else:
        return crud.get_quizzes(
            db, 
            skip=skip, 
            limit=limit, 
            content_id=content_id,
            is_published=True
        )

@router.get("/quizzes/{quiz_id}", response_model=schemas.QuizResponse)
def read_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    특정 퀴즈를 조회합니다.
    관리자: 모든 퀴즈 조회 가능
    강사: 자신이 생성한 콘텐츠의 퀴즈 조회 가능
    일반 사용자: 공개된 퀴즈만 조회 가능
    """
    db_quiz = crud.get_quiz(db, quiz_id=quiz_id)
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # 관리자는 모든 퀴즈 조회 가능
    if current_user.role == UserRole.ADMIN:
        return db_quiz
    
    # 강사는 자신이 만든 콘텐츠의 퀴즈만 조회 가능
    if current_user.role == UserRole.INSTRUCTOR:
        if db_quiz.content.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this quiz"
            )
    # 일반 사용자는 공개된 퀴즈만 조회 가능
    elif not db_quiz.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This quiz is not published"
        )
    
    return db_quiz

@router.put("/quizzes/{quiz_id}", response_model=schemas.QuizResponse)
def update_quiz(
    quiz_id: int,
    quiz_update: schemas.QuizUpdate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    퀴즈를 업데이트합니다.
    관리자 또는 퀴즈를 생성한 강사만 수정할 수 있습니다.
    """
    db_quiz = check_quiz_owner_or_admin(db, quiz_id, current_user)
    
    # 콘텐츠 ID가 변경되는 경우 권한 확인
    if quiz_update.content_id is not None and quiz_update.content_id != db_quiz.content_id:
        db_content = crud.get_content(db, content_id=quiz_update.content_id)
        if not db_content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        if db_content.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to move quiz to this content"
            )
    
    return crud.update_quiz(db=db, db_quiz=db_quiz, quiz_update=quiz_update)

@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    퀴즈를 삭제합니다.
    관리자 또는 퀴즈를 생성한 강사만 삭제할 수 있습니다.
    """
    check_quiz_owner_or_admin(db, quiz_id, current_user)
    crud.delete_quiz(db=db, quiz_id=quiz_id)
    return None

# Quiz Attempt endpoints
@router.post("/quizzes/{quiz_id}/attempts/start", response_model=schemas.QuizAttemptResponse)
def start_quiz_attempt(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    퀴즈 시도를 시작합니다.
    """
    try:
        return crud.start_quiz_attempt(db=db, quiz_id=quiz_id, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/quiz-attempts/{attempt_id}/submit", response_model=schemas.QuizAttemptResponse)
def submit_quiz_attempt(
    attempt_id: int,
    answers: schemas.QuizAttemptSubmit,
    auto_grade: bool = True,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    퀴즈 답변을 제출하고 자동 채점합니다.
    """
    try:
        return crud.submit_quiz_answers(
            db=db,
            attempt_id=attempt_id,
            user_id=current_user.id,
            answers=[a.dict() for a in answers.answers],
            auto_grade=auto_grade
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/quiz-attempts/{attempt_id}", response_model=schemas.QuizAttemptResponse)
def get_quiz_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    특정 퀴즈 시도 결과를 조회합니다.
    """
    attempt = crud.get_quiz_attempt(db, attempt_id=attempt_id, user_id=current_user.id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    # 관리자 또는 시도한 사용자 본인만 조회 가능
    if attempt.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this attempt"
        )
    
    return attempt

@router.get("/users/me/quiz-attempts/", response_model=List[schemas.QuizAttemptResponse])
def get_user_quiz_attempts(
    quiz_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    현재 사용자의 퀴즈 시도 내역을 조회합니다.
    """
    return crud.get_user_quiz_attempts(
        db=db,
        user_id=current_user.id,
        quiz_id=quiz_id,
        status=status,
        skip=skip,
        limit=limit
    )

@router.get("/users/me/quizzes/{quiz_id}/progress", response_model=schemas.UserQuizProgressResponse)
def get_user_quiz_progress(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    현재 사용자의 특정 퀴즈 진행 상황을 조회합니다.
    """
    progress = crud.get_user_quiz_progress(
        db=db,
        user_id=current_user.id,
        quiz_id=quiz_id
    )
    
    if not progress:
        return {
            "quiz_id": quiz_id,
            "completed_attempts": 0,
            "best_score": 0,
            "passed": False,
            "last_attempt_at": None
        }
    
    return progress

# Admin endpoints
@router.post("/quiz-attempts/{attempt_id}/grade", response_model=schemas.QuizAttemptResponse)
def grade_quiz_attempt(
    attempt_id: int,
    grading: schemas.QuizGrading,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_admin),
):
    """
    퀴즈 답변을 수동으로 채점합니다. (관리자 전용)
    """
    try:
        # 채점 데이터 형식 변환
        grading_data = {
            answer.id: {
                "points_awarded": answer.points_awarded,
                "is_correct": answer.is_correct,
                "feedback": answer.feedback
            }
            for answer in grading.answers
        }
        
        return crud.grade_quiz_attempt(
            db=db,
            attempt_id=attempt_id,
            grader_id=current_user.id,
            grading_data=grading_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/quizzes/{quiz_id}/statistics", response_model=schemas.QuizStatistics)
def get_quiz_statistics(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_admin),
):
    """
    퀴즈 통계를 조회합니다. (관리자 전용)
    """
    # 퀴즈 소유자인지 확인
    check_quiz_owner_or_admin(db, quiz_id, current_user)
    
    return crud.get_quiz_statistics(db=db, quiz_id=quiz_id)
