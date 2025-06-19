"""
수업(Lesson) 관련 CRUD 연산을 처리합니다.
"""
from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_

from app.crud.base import CRUDBase
from app.models.course import Lesson, Course
from app.schemas.course import LessonCreate, LessonUpdate


class LessonCRUD(CRUDBase[Lesson, LessonCreate, LessonUpdate]):
    """수업 CRUD 클래스"""
    
    def __init__(self):
        super().__init__(Lesson)
    
    def get_multi_by_course(
        self, db: Session, *, course_id: str, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[Lesson]:
        """강의 ID로 수업 목록 조회 (순서대로 정렬)"""
        query = (
            db.query(self.model)
            .filter(self.model.course_id == course_id)
            .order_by(self.model.order.asc())
        )
        
        # 추가 필터링 조건 적용
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def get_last_lesson(
        self, db: Session, *, course_id: str
    ) -> Optional[Lesson]:
        """강의의 마지막 수업 조회 (순서 기준)"""
        return (
            db.query(self.model)
            .filter(self.model.course_id == course_id)
            .order_by(self.model.order.desc())
            .first()
        )
    
    def get_next_lesson(
        self, db: Session, *, course_id: str, current_order: int
    ) -> Optional[Lesson]:
        """현재 수업의 다음 수업 조회"""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.course_id == course_id,
                    self.model.order > current_order
                )
            )
            .order_by(self.model.order.asc())
            .first()
        )
    
    def get_previous_lesson(
        self, db: Session, *, course_id: str, current_order: int
    ) -> Optional[Lesson]:
        """현재 수업의 이전 수업 조회"""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.course_id == course_id,
                    self.model.order < current_order
                )
            )
            .order_by(self.model.order.desc())
            .first()
        )
    
    def reorder_lessons(
        self, db: Session, *, course_id: str, old_order: int, new_order: int
    ) -> None:
        """수업 순서 변경"""
        if old_order == new_order:
            return
        
        # 순서 업데이트
        if new_order < old_order:
            # 순서를 앞으로 당기는 경우 (예: 3번을 1번으로)
            db.query(self.model).filter(
                self.model.course_id == course_id,
                self.model.order >= new_order,
                self.model.order < old_order
            ).update({"order": self.model.order + 1})
        else:
            # 순서를 뒤로 미는 경우 (예: 1번을 3번으로)
            db.query(self.model).filter(
                self.model.course_id == course_id,
                self.model.order > old_order,
                self.model.order <= new_order
            ).update({"order": self.model.order - 1})
        
        db.commit()
    
    def get_with_course(
        self, db: Session, *, id: str
    ) -> Optional[Lesson]:
        """강의 정보와 함께 수업 조회"""
        return (
            db.query(self.model)
            .options(joinedload(self.model.course))
            .filter(self.model.id == id)
            .first()
        )
    
    def update_video_duration(
        self, db: Session, *, db_obj: Lesson, duration: int
    ) -> Lesson:
        """동영상 재생 시간 업데이트"""
        return self.update(db, db_obj=db_obj, obj_in={"duration": duration})
    
    def toggle_preview(
        self, db: Session, *, db_obj: Lesson, is_preview: bool
    ) -> Lesson:
        """미리보기 여부 토글"""
        return self.update(db, db_obj=db_obj, obj_in={"is_preview": is_preview})
    
    def get_preview_lessons(
        self, db: Session, *, course_id: str, limit: int = 3
    ) -> List[Lesson]:
        """미리보기 가능한 수업 목록 조회"""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.course_id == course_id,
                    self.model.is_preview == True  # noqa
                )
            )
            .order_by(self.model.order.asc())
            .limit(limit)
            .all()
        )
    
    def search(
        self, db: Session, *, query: str, course_id: Optional[str] = None, 
        skip: int = 0, limit: int = 100, **kwargs
    ) -> List[Lesson]:
        """수업 검색 (제목, 설명에서 검색)"""
        search = f"%{query}%"
        query = db.query(self.model).filter(
            (self.model.title.ilike(search)) | 
            (self.model.description.ilike(search))
        )
        
        if course_id is not None:
            query = query.filter(self.model.course_id == course_id)
        
        # 추가 필터링 조건 적용
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def get_lesson_progress(
        self, db: Session, *, user_id: str, course_id: str
    ) -> Dict[str, Any]:
        """사용자의 수업별 진행 상황 조회"""
        from app.models import UserProgress
        
        # 수업 목록 조회 (진행 상황 포함)
        lessons = (
            db.query(
                self.model,
                UserProgress.progress,
                UserProgress.completed,
                UserProgress.last_accessed
            )
            .outerjoin(
                UserProgress,
                and_(
                    UserProgress.lesson_id == self.model.id,
                    UserProgress.user_id == user_id
                )
            )
            .filter(self.model.course_id == course_id)
            .order_by(self.model.order.asc())
            .all()
        )
        
        # 전체 진행률 계산
        total_lessons = len(lessons)
        if total_lessons == 0:
            return {
                "total_lessons": 0,
                "completed_lessons": 0,
                "progress_percentage": 0,
                "lessons": []
            }
        
        completed_lessons = sum(1 for l in lessons if l.completed)
        progress_percentage = int((completed_lessons / total_lessons) * 100)
        
        # 결과 포맷팅
        formatted_lessons = []
        for lesson, progress, completed, last_accessed in lessons:
            formatted_lessons.append({
                "id": str(lesson.id),
                "title": lesson.title,
                "order": lesson.order,
                "duration": lesson.duration,
                "is_preview": lesson.is_preview,
                "progress": progress or 0,
                "completed": completed or False,
                "last_accessed": last_accessed
            })
        
        return {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": progress_percentage,
            "lessons": formatted_lessons
        }
