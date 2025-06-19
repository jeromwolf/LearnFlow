from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
import json

from app import models, schemas

def get_quiz(db: Session, quiz_id: int) -> Optional[models.Quiz]:
    """퀴즈 ID로 퀴즈 조회"""
    return db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()

def get_quizzes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    content_id: Optional[int] = None,
    is_published: Optional[bool] = None,
    user_id: Optional[int] = None,
) -> List[models.Quiz]:
    """여러 퀴즈 조회"""
    query = db.query(models.Quiz)
    
    if content_id is not None:
        query = query.filter(models.Quiz.content_id == content_id)
    
    if is_published is not None:
        query = query.filter(models.Quiz.is_published == is_published)
    
    # 사용자 진행 상황과 함께 조회
    if user_id is not None:
        query = query.outerjoin(
            models.UserQuizProgress,
            and_(
                models.UserQuizProgress.quiz_id == models.Quiz.id,
                models.UserQuizProgress.user_id == user_id
            )
        )
    
    return query.offset(skip).limit(limit).all()

def create_quiz(db: Session, quiz: schemas.QuizCreate, creator_id: int) -> models.Quiz:
    """새 퀴즈 생성"""
    db_quiz = models.Quiz(**quiz.dict(exclude={"questions"}))
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    # 질문 및 선택지 추가
    if quiz.questions:
        for q_idx, question in enumerate(quiz.questions):
            db_question = models.Question(
                quiz_id=db_quiz.id,
                question_text=question.question_text,
                question_type=question.question_type,
                points=question.points,
                order_num=question.order_num or q_idx,
                explanation=question.explanation
            )
            db.add(db_question)
            db.commit()
            db.refresh(db_question)
            
            # 선택지 추가
            if question.choices:
                for c_idx, choice in enumerate(question.choices):
                    db_choice = models.Choice(
                        question_id=db_question.id,
                        choice_text=choice.choice_text,
                        is_correct=choice.is_correct,
                        order_num=choice.order_num or c_idx
                    )
                    db.add(db_choice)
        
        db.commit()
    
    return db_quiz

def update_quiz(
    db: Session, 
    db_quiz: models.Quiz, 
    quiz_update: schemas.QuizUpdate
) -> models.Quiz:
    """퀴즈 업데이트"""
    update_data = quiz_update.dict(exclude_unset=True, exclude={"questions"})
    
    for field, value in update_data.items():
        setattr(db_quiz, field, value)
    
    # 질문 업데이트
    if quiz_update.questions is not None:
        # 기존 질문 ID 목록
        existing_question_ids = {q.id for q in db_quiz.questions if q.id}
        updated_question_ids = set()
        
        for q_idx, question in enumerate(quiz_update.questions):
            question_data = question.dict(exclude_unset=True, exclude={"choices"})
            question_data["order_num"] = question_data.get("order_num", q_idx)
            
            # 질문 업데이트 또는 생성
            if question.id and question.id in existing_question_ids:
                db_question = next((q for q in db_quiz.questions if q.id == question.id), None)
                if db_question:
                    for field, value in question_data.items():
                        setattr(db_question, field, value)
                    db.add(db_question)
                    updated_question_ids.add(question.id)
            else:
                question_data["quiz_id"] = db_quiz.id
                db_question = models.Question(**question_data)
                db.add(db_question)
                db.flush()  # DB에 삽입하여 ID 생성
                updated_question_ids.add(db_question.id)
            
            # 선택지 업데이트
            if question.choices is not None:
                existing_choice_ids = {c.id for c in db_question.choices if c.id}
                updated_choice_ids = set()
                
                for c_idx, choice in enumerate(question.choices):
                    choice_data = choice.dict(exclude_unset=True)
                    choice_data["order_num"] = choice_data.get("order_num", c_idx)
                    
                    if choice.id and choice.id in existing_choice_ids:
                        db_choice = next((c for c in db_question.choices if c.id == choice.id), None)
                        if db_choice:
                            for field, value in choice_data.items():
                                setattr(db_choice, field, value)
                            db.add(db_choice)
                            updated_choice_ids.add(choice.id)
                    else:
                        choice_data["question_id"] = db_question.id
                        db_choice = models.Choice(**choice_data)
                        db.add(db_choice)
                        updated_choice_ids.add(db_choice.id)
                
                # 삭제된 선택지 제거
                for choice_id in existing_choice_ids - updated_choice_ids:
                    db.query(models.Choice).filter(models.Choice.id == choice_id).delete()
        
        # 삭제된 질문 제거
        for question_id in existing_question_ids - updated_question_ids:
            db.query(models.Question).filter(models.Question.id == question_id).delete()
    
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

def delete_quiz(db: Session, quiz_id: int) -> None:
    """퀴즈 삭제"""
    db.query(models.Quiz).filter(models.Quiz.id == quiz_id).delete()
    db.commit()

# 퀴즈 시도 관련 함수
def get_quiz_attempt(
    db: Session, 
    attempt_id: int, 
    user_id: Optional[int] = None
) -> Optional[models.QuizAttempt]:
    """퀴즈 시도 조회"""
    query = db.query(models.QuizAttempt).filter(models.QuizAttempt.id == attempt_id)
    
    if user_id is not None:
        query = query.filter(models.QuizAttempt.user_id == user_id)
    
    return query.first()

def get_user_quiz_attempts(
    db: Session,
    user_id: int,
    quiz_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.QuizAttempt]:
    """사용자의 퀴즈 시도 목록 조회"""
    query = db.query(models.QuizAttempt).filter(models.QuizAttempt.user_id == user_id)
    
    if quiz_id is not None:
        query = query.filter(models.QuizAttempt.quiz_id == quiz_id)
    
    if status is not None:
        query = query.filter(models.QuizAttempt.status == status)
    
    return query.order_by(desc(models.QuizAttempt.started_at)).offset(skip).limit(limit).all()

def start_quiz_attempt(
    db: Session, 
    quiz_id: int, 
    user_id: int
) -> models.QuizAttempt:
    """새 퀴즈 시도 시작"""
    # 이전 시도 횟수 확인
    attempt_count = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.quiz_id == quiz_id,
        models.QuizAttempt.user_id == user_id
    ).count()
    
    # 퀴즈 정보 가져오기
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise ValueError("Quiz not found")
    
    # 최대 시도 횟수 확인 (0이면 무제한)
    if quiz.max_attempts > 0 and attempt_count >= quiz.max_attempts:
        raise ValueError("Maximum number of attempts reached")
    
    # 새 시도 생성
    attempt = models.QuizAttempt(
        quiz_id=quiz_id,
        user_id=user_id,
        attempt_number=attempt_count + 1,
        status="in_progress"
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt

def submit_quiz_answers(
    db: Session,
    attempt_id: int,
    user_id: int,
    answers: List[Dict[str, Any]],
    auto_grade: bool = True
) -> models.QuizAttempt:
    """퀴즈 답변 제출 및 자동 채점"""
    # 시도 정보 가져오기
    attempt = get_quiz_attempt(db, attempt_id, user_id)
    if not attempt:
        raise ValueError("Quiz attempt not found")
    
    if attempt.status != "in_progress":
        raise ValueError("This attempt is already completed or abandoned")
    
    # 퀴즈 정보 가져오기
    quiz = get_quiz(db, attempt.quiz_id)
    if not quiz:
        raise ValueError("Quiz not found")
    
    # 기존 답변 삭제
    db.query(models.QuestionAnswer).filter(
        models.QuestionAnswer.attempt_id == attempt.id
    ).delete(synchronize_session=False)
    
    total_points = 0
    max_possible_points = 0
    
    # 각 질문에 대한 답변 처리
    for answer in answers:
        question_id = answer.get("question_id")
        answer_data = answer.get("answer_data", {})
        
        # 질문 정보 가져오기
        question = next((q for q in quiz.questions if q.id == question_id), None)
        if not question:
            continue
        
        max_possible_points += question.points
        is_correct = False
        points_awarded = 0
        
        # 자동 채점 (객관식, 참/거짓)
        if auto_grade and question.question_type in ["multiple_choice", "true_false"]:
            if question.question_type == "multiple_choice":
                # 다중 선택 답변 처리 (선택된 선택지 ID 목록)
                selected_choice_ids = set(answer_data.get("selected_choices", []))
                correct_choice_ids = {c.id for c in question.choices if c.is_correct}
                
                # 정답 여부 확인 (선택한 답이 정답과 완전히 일치해야 함)
                is_correct = (selected_choice_ids == correct_choice_ids)
                
            elif question.question_type == "true_false":
                # 참/거짓 문제 처리
                user_answer = answer_data.get("answer")
                correct_answer = any(c.is_correct for c in question.choices if c.choice_text.lower() == "true")
                is_correct = (user_answer == correct_answer)
            
            # 점수 계산
            points_awarded = question.points if is_correct else 0
            total_points += points_awarded
        
        # 답변 저장
        db_answer = models.QuestionAnswer(
            attempt_id=attempt.id,
            question_id=question_id,
            answer_data=answer_data,
            is_correct=is_correct if auto_grade else None,
            points_awarded=points_awarded
        )
        db.add(db_answer)
    
    # 시도 정보 업데이트
    attempt.completed_at = db.func.now()
    attempt.status = "completed" if auto_grade else "submitted"
    
    if max_possible_points > 0:
        attempt.score = int((total_points / max_possible_points) * 100)
        attempt.passed = (attempt.score >= quiz.passing_score)
    
    # 사용자 진행 상황 업데이트
    progress = db.query(models.UserQuizProgress).filter(
        models.UserQuizProgress.user_id == user_id,
        models.UserQuizProgress.quiz_id == quiz.id
    ).first()
    
    if not progress:
        progress = models.UserQuizProgress(
            user_id=user_id,
            quiz_id=quiz.id,
            completed_attempts=1,
            best_score=attempt.score,
            passed=attempt.passed,
            last_attempt_at=attempt.completed_at
        )
        db.add(progress)
    else:
        progress.completed_attempts += 1
        progress.best_score = max(progress.best_score, attempt.score)
        progress.passed = progress.passed or attempt.passed
        progress.last_attempt_at = attempt.completed_at
    
    db.commit()
    db.refresh(attempt)
    return attempt

def grade_quiz_attempt(
    db: Session,
    attempt_id: int,
    grader_id: int,
    grading_data: Dict[int, Dict[str, Any]]
) -> models.QuizAttempt:
    """수동 채점 (주관식 답변 등)"""
    # 시도 정보 가져오기
    attempt = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.id == attempt_id,
        models.QuizAttempt.status.in_(["completed", "submitted"])
    ).first()
    
    if not attempt:
        raise ValueError("Quiz attempt not found or not ready for grading")
    
    # 각 답변 채점
    total_points = 0
    max_possible_points = 0
    
    for answer in attempt.answers:
        question = answer.question
        max_possible_points += question.points
        
        # 채점 데이터가 있는 경우에만 업데이트
        if answer.question_id in grading_data:
            grade = grading_data[answer.question_id]
            answer.points_awarded = grade["points_awarded"]
            answer.is_correct = grade["is_correct"]
            answer.feedback = grade.get("feedback")
            answer.graded_by = grader_id
            answer.graded_at = db.func.now()
            
            total_points += answer.points_awarded
        else:
            total_points += answer.points_awarded or 0
    
    # 시도 정보 업데이트
    attempt.status = "graded"
    
    if max_possible_points > 0:
        attempt.score = int((total_points / max_possible_points) * 100)
        attempt.passed = (attempt.score >= attempt.quiz.passing_score)
    
    # 사용자 진행 상황 업데이트
    progress = db.query(models.UserQuizProgress).filter(
        models.UserQuizProgress.user_id == attempt.user_id,
        models.UserQuizProgress.quiz_id == attempt.quiz_id
    ).first()
    
    if progress:
        progress.best_score = max(progress.best_score, attempt.score)
        progress.passed = progress.passed or attempt.passed
    
    db.commit()
    db.refresh(attempt)
    return attempt

def get_user_quiz_progress(
    db: Session,
    user_id: int,
    quiz_id: int
) -> Optional[models.UserQuizProgress]:
    """사용자의 퀴즈 진행 상황 조회"""
    return db.query(models.UserQuizProgress).filter(
        models.UserQuizProgress.user_id == user_id,
        models.UserQuizProgress.quiz_id == quiz_id
    ).first()

def get_quiz_statistics(
    db: Session,
    quiz_id: int
) -> Dict[str, Any]:
    """퀴즈 통계 조회"""
    # 기본 통계
    stats = {
        "total_attempts": 0,
        "average_score": 0.0,
        "pass_rate": 0.0,
        "question_stats": {}
    }
    
    # 퀴즈 정보 가져오기
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        return stats
    
    # 질문별 통계 초기화
    for question in quiz.questions:
        stats["question_stats"][question.id] = {
            "question_text": question.question_text,
            "question_type": question.question_type,
            "total_answers": 0,
            "correct_answers": 0,
            "average_score": 0.0,
            "answer_distribution": {}
        }
    
    # 시도 통계
    attempts = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.quiz_id == quiz_id,
        models.QuizAttempt.status.in_(["completed", "graded"])
    ).all()
    
    if not attempts:
        return stats
    
    # 기본 통계 계산
    total_scores = sum(a.score for a in attempts)
    passed_attempts = sum(1 for a in attempts if a.passed)
    
    stats["total_attempts"] = len(attempts)
    stats["average_score"] = total_scores / len(attempts)
    stats["pass_rate"] = (passed_attempts / len(attempts)) * 100
    
    # 질문별 통계 계산
    for attempt in attempts:
        for answer in attempt.answers:
            if answer.question_id not in stats["question_stats"]:
                continue
                
            q_stats = stats["question_stats"][answer.question_id]
            q_stats["total_answers"] += 1
            
            if answer.is_correct:
                q_stats["correct_answers"] += 1
            
            # 답변 분포 (객관식/참거짓)
            if answer.question.question_type in ["multiple_choice", "true_false"]:
                answer_key = str(answer.answer_data.get("selected_choices", []))
                q_stats["answer_distribution"][answer_key] = q_stats["answer_distribution"].get(answer_key, 0) + 1
            
            # 평균 점수
            max_points = answer.question.points
            if max_points > 0:
                q_stats["average_score"] += (answer.points_awarded / max_points) * 100
    
    # 질문별 평균 점수 계산
    for q_id in stats["question_stats"]:
        q_stats = stats["question_stats"][q_id]
        if q_stats["total_answers"] > 0:
            q_stats["average_score"] = q_stats["average_score"] / q_stats["total_answers"]
    
    return stats
