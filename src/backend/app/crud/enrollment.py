"""
수강 신청(Enrollment) 관련 CRUD 연산을 처리합니다.
"""
from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.course import Enrollment
from app.schemas.course import EnrollmentCreate, EnrollmentUpdate


class EnrollmentCRUD(CRUDBase[Enrollment, EnrollmentCreate, EnrollmentUpdate]):
    """수강 신청 CRUD 클래스"""
    
    def __init__(self):
        super().__init__(Enrollment)
    
    def get_by_user_and_course(
        self, db: Session, *, user_id: str, course_id: str
    ) -> Optional[Enrollment]:
        """사용자 ID와 강의 ID로 수강 신청 정보 조회"""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.course_id == course_id
                )
            )
            .first()
        )
    
    def get_multi_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[Enrollment]:
        """사용자 ID로 수강 신청 목록 조회"""
        kwargs["user_id"] = user_id
        return self.get_multi(db, skip=skip, limit=limit, **kwargs)
    
    def get_multi_by_course(
        self, db: Session, *, course_id: str, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[Enrollment]:
        """강의 ID로 수강 신청 목록 조회"""
        kwargs["course_id"] = course_id
        return self.get_multi(db, skip=skip, limit=limit, **kwargs)
    
    def count_by_course(self, db: Session, *, course_id: str) -> int:
        """강의의 수강생 수 조회"""
        return (
            db.query(self.model)
            .filter(self.model.course_id == course_id)
            .count()
        )
    
    def count_active_by_course(self, db: Session, *, course_id: str) -> int:
        """강의의 활성 수강생 수 조회"""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.course_id == course_id,
                    self.model.is_active == True  # noqa
                )
            )
            .count()
        )
    
    def enroll(
        self, db: Session, *, user_id: str, course_id: str
    ) -> Enrollment:
        """새로운 수강 신청 생성 (중복 확인 포함)"""
        # 이미 수강 중인지 확인
        existing_enrollment = self.get_by_user_and_course(
            db, user_id=user_id, course_id=course_id
        )
        
        if existing_enrollment:
            # 이미 수강 중인 경우 기존 정보 반환
            if not existing_enrollment.is_active:
                # 비활성 상태인 경우 활성화
                existing_enrollment.is_active = True
                db.add(existing_enrollment)
                db.commit()
                db.refresh(existing_enrollment)
            return existing_enrollment
        
        # 새로운 수강 신청 생성
        enrollment_in = {
            "user_id": user_id,
            "course_id": course_id,
            "is_active": True,
        }
        
        return self.create(db, obj_in=enrollment_in)
    
    def unenroll(
        self, db: Session, *, user_id: str, course_id: str
    ) -> Optional[Enrollment]:
        """수강 신청 취소 (비활성화)"""
        enrollment = self.get_by_user_and_course(
            db, user_id=user_id, course_id=course_id
        )
        
        if not enrollment:
            return None
        
        # 수강 신청 비활성화
        enrollment.is_active = False
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        
        return enrollment
    
    def complete_course(
        self, db: Session, *, user_id: str, course_id: str
    ) -> Optional[Enrollment]:
        """강의 수료 처리"""
        from datetime import datetime
        
        enrollment = self.get_by_user_and_course(
            db, user_id=user_id, course_id=course_id
        )
        
        if not enrollment:
            return None
        
        # 수료일자 설정
        enrollment.completed_at = datetime.utcnow()
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        
        return enrollment
    
    def get_user_courses(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[Enrollment]:
        """사용자의 수강 중인 강의 목록 조회 (강의 정보 포함)"""
        from sqlalchemy.orm import joinedload
        
        query = (
            db.query(self.model)
            .options(joinedload(self.model.course))
            .filter(self.model.user_id == user_id)
        )
        
        # 추가 필터링 조건 적용
        if "is_active" in kwargs:
            query = query.filter(self.model.is_active == kwargs["is_active"])
        
        if "completed" in kwargs:
            if kwargs["completed"]:
                query = query.filter(self.model.completed_at.isnot(None))
            else:
                query = query.filter(self.model.completed_at.is_(None))
        
        return query.offset(skip).limit(limit).all()
    
    def get_course_students(
        self, db: Session, *, course_id: str, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[Enrollment]:
        """강의의 수강생 목록 조회 (사용자 정보 포함)"""
        from sqlalchemy.orm import joinedload
        
        query = (
            db.query(self.model)
            .options(joinedload(self.model.user))
            .filter(self.model.course_id == course_id)
        )
        
        # 추가 필터링 조건 적용
        if "is_active" in kwargs:
            query = query.filter(self.model.is_active == kwargs["is_active"])
        
        if "completed" in kwargs:
            if kwargs["completed"]:
                query = query.filter(self.model.completed_at.isnot(None))
            else:
                query = query.filter(self.model.completed_at.is_(None))
        
        return query.offset(skip).limit(limit).all()
    
    def get_user_progress(
        self, db: Session, *, user_id: str, course_id: str
    ) -> Dict[str, Any]:
        """사용자의 강의 진도율 조회"""
        from app.models import Lesson, UserProgress
        
        # 전체 수업 수
        total_lessons = (
            db.query(Lesson)
            .filter(Lesson.course_id == course_id)
            .count()
        )
        
        if total_lessons == 0:
            return {
                "total_lessons": 0,
                "completed_lessons": 0,
                "progress_percentage": 0,
                "last_accessed": None
            }
        
        # 완료된 수업 수
        completed_lessons = (
            db.query(UserProgress)
            .join(Lesson, UserProgress.lesson_id == Lesson.id)
            .filter(
                and_(
                    UserProgress.user_id == user_id,
                    Lesson.course_id == course_id,
                    UserProgress.completed == True  # noqa
                )
            )
            .count()
        )
        
        # 마지막 학습 일시
        last_accessed = (
            db.query(UserProgress.last_accessed)
            .join(Lesson, UserProgress.lesson_id == Lesson.id)
            .filter(
                and_(
                    UserProgress.user_id == user_id,
                    Lesson.course_id == course_id
                )
            )
            .order_by(UserProgress.last_accessed.desc())
            .first()
        )
        
        progress_percentage = int((completed_lessons / total_lessons) * 100)
        
        return {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": progress_percentage,
            "last_accessed": last_accessed[0] if last_accessed else None
        }
