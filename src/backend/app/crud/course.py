"""
강의(Course) 관련 CRUD 연산을 처리합니다.
"""
from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate, CourseLevel


class CourseCRUD(CRUDBase[Course, CourseCreate, CourseUpdate]):
    """강의 CRUD 클래스"""
    
    def __init__(self):
        super().__init__(Course)
    
    def get_multi_by_instructor(
        self, db: Session, *, instructor_id: str, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[Course]:
        """강사 ID로 강의 목록 조회"""
        kwargs["instructor_id"] = instructor_id
        return self.get_multi(db, skip=skip, limit=limit, **kwargs)
    
    def get_multi_published(
        self, db: Session, *, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[Course]:
        """공개된 강의 목록 조회"""
        kwargs["is_published"] = True
        return self.get_multi(db, skip=skip, limit=limit, **kwargs)
    
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Course]:
        """슬러그로 강의 조회"""
        return db.query(self.model).filter(self.model.slug == slug).first()
    
    def create_with_owner(
        self, db: Session, *, obj_in: CourseCreate, instructor_id: str
    ) -> Course:
        """새 강의 생성 (강사 ID 포함)"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, instructor_id=instructor_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_duration(self, db: Session, *, db_obj: Course, duration: int) -> Course:
        """강의 총 시간 업데이트"""
        return self.update(db, db_obj=db_obj, obj_in={"duration": duration})
    
    def get_multi_with_lessons(
        self, db: Session, *, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[Course]:
        """수업 목록과 함께 강의 목록 조회"""
        query = db.query(self.model)
        
        # 필터링 조건 적용
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        
        # 수업 목록과 함께 로드 (eager loading)
        query = query.options(
            sqlalchemy.orm.joinedload(self.model.lessons)
            .joinedload(models.Lesson.user_progress)
        )
        
        return query.offset(skip).limit(limit).all()
    
    def search(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[Course]:
        """강의 검색 (제목, 설명에서 검색)"""
        search = f"%{query}%"
        return (
            db.query(self.model)
            .filter(
                (self.model.title.ilike(search)) | 
                (self.model.description.ilike(search))
            )
            .filter_by(**{k: v for k, v in kwargs.items() if v is not None})
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_stats(self, db: Session, course_id: str) -> Dict[str, Any]:
        """강의 통계 정보 조회"""
        from sqlalchemy import func, and_
        from app.models import Enrollment, UserProgress, Lesson
        
        # 총 수강생 수
        total_students = (
            db.query(func.count(Enrollment.id))
            .filter(Enrollment.course_id == course_id)
            .scalar() or 0
        )
        
        # 총 수업 수
        total_lessons = (
            db.query(func.count(Lesson.id))
            .filter(Lesson.course_id == course_id)
            .scalar() or 0
        )
        
        # 평균 진도율 (수강생별 평균)
        avg_progress = 0.0
        if total_students > 0 and total_lessons > 0:
            # 각 수강생의 평균 진도율 계산
            subq = (
                db.query(
                    UserProgress.user_id,
                    func.avg(UserProgress.progress).label('avg_progress')
                )
                .join(Lesson, UserProgress.lesson_id == Lesson.id)
                .filter(Lesson.course_id == course_id)
                .group_by(UserProgress.user_id)
                .subquery()
            )
            
            # 전체 평균 진도율 계산
            result = db.query(
                func.avg(subq.c.avg_progress).label('overall_avg')
            ).scalar()
            
            avg_progress = float(result or 0)
        
        # 수료율 (전체 진도율 100%인 수강생 비율)
        completion_rate = 0.0
        if total_students > 0 and total_lessons > 0:
            # 각 수강생의 전체 진도율 계산 (모든 수업의 평균)
            subq = (
                db.query(
                    UserProgress.user_id,
                    func.avg(UserProgress.progress).label('total_progress')
                )
                .join(Lesson, UserProgress.lesson_id == Lesson.id)
                .filter(Lesson.course_id == course_id)
                .group_by(UserProgress.user_id)
                .subquery()
            )
            
            # 수료한 수강생 수 (전체 진도율 100% 이상)
            completed_students = (
                db.query(func.count(subq.c.user_id))
                .filter(subq.c.total_progress >= 100)
                .scalar() or 0
            )
            
            completion_rate = (completed_students / total_students) * 100
        
        # 강의 총 시간 (초 단위)
        total_duration = (
            db.query(func.sum(Lesson.duration))
            .filter(Lesson.course_id == course_id)
            .scalar() or 0
        )
        
        return {
            "total_students": total_students,
            "total_lessons": total_lessons,
            "total_duration": total_duration,
            "avg_progress": avg_progress,
            "completion_rate": completion_rate,
        }
