"""
사용자 학습 진행 상황(UserProgress) 관련 CRUD 연산을 처리합니다.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.crud.base import CRUDBase
from app.models.course import UserProgress, Lesson, Course, Enrollment
from app.schemas.course import UserProgressCreate, UserProgressUpdate


class UserProgressCRUD(CRUDBase[UserProgress, UserProgressCreate, UserProgressUpdate]):
    """사용자 학습 진행 상황 CRUD 클래스"""
    
    def __init__(self):
        super().__init__(UserProgress)
    
    def get_by_user_and_lesson(
        self, db: Session, *, user_id: str, lesson_id: str
    ) -> Optional[UserProgress]:
        """사용자 ID와 수업 ID로 학습 진행 상황 조회"""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.lesson_id == lesson_id
                )
            )
            .first()
        )
    
    def get_multi_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[UserProgress]:
        """사용자 ID로 학습 진행 상황 목록 조회"""
        kwargs["user_id"] = user_id
        return self.get_multi(db, skip=skip, limit=limit, **kwargs)
    
    def get_multi_by_lesson(
        self, db: Session, *, lesson_id: str, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[UserProgress]:
        """수업 ID로 학습 진행 상황 목록 조회"""
        kwargs["lesson_id"] = lesson_id
        return self.get_multi(db, skip=skip, limit=limit, **kwargs)
    
    def get_multi_by_course(
        self, db: Session, *, user_id: str, course_id: str, **kwargs
    ) -> List[UserProgress]:
        """사용자와 강의에 대한 모든 학습 진행 상황 조회"""
        return (
            db.query(self.model)
            .join(Lesson, self.model.lesson_id == Lesson.id)
            .filter(
                and_(
                    self.model.user_id == user_id,
                    Lesson.course_id == course_id
                )
            )
            .order_by(Lesson.order.asc())
            .all()
        )
    
    def update_progress(
        self,
        db: Session,
        *,
        user_id: str,
        lesson_id: str,
        progress: int,
        is_completed: Optional[bool] = None
    ) -> Tuple[UserProgress, bool]:
        """학습 진행 상황 업데이트 (없는 경우 생성)
        
        Returns:
            Tuple[UserProgress, bool]: (업데이트된 UserProgress 객체, 새로 생성되었는지 여부)
        """
        db_obj = self.get_by_user_and_lesson(db, user_id=user_id, lesson_id=lesson_id)
        now = datetime.utcnow()
        
        if db_obj:
            # 기존 진행 상황 업데이트
            update_data = {
                "progress": min(max(progress, 0), 100),  # 0-100% 범위 제한
                "last_accessed": now
            }
            
            if is_completed is not None:
                update_data["completed"] = is_completed
                if is_completed and not db_obj.completed_at:
                    update_data["completed_at"] = now
            
            db_obj = self.update(db, db_obj=db_obj, obj_in=update_data)
            return db_obj, False
        else:
            # 새로운 진행 상황 생성
            progress_data = {
                "user_id": user_id,
                "lesson_id": lesson_id,
                "progress": min(max(progress, 0), 100),  # 0-100% 범위 제한
                "completed": is_completed if is_completed is not None else False,
                "last_accessed": now,
                "completed_at": now if is_completed else None
            }
            
            # 강의 ID 설정 (성능을 위해 중복 저장)
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                progress_data["course_id"] = lesson.course_id
            
            db_obj = self.create(db, obj_in=progress_data)
            return db_obj, True
    
    def mark_as_completed(
        self, db: Session, *, user_id: str, lesson_id: str
    ) -> UserProgress:
        """수업을 완료 상태로 표시"""
        return self.update_progress(
            db,
            user_id=user_id,
            lesson_id=lesson_id,
            progress=100,
            is_completed=True
        )[0]
    
    def mark_as_incomplete(
        self, db: Session, *, user_id: str, lesson_id: str
    ) -> UserProgress:
        """수업을 미완료 상태로 표시"""
        return self.update_progress(
            db,
            user_id=user_id,
            lesson_id=lesson_id,
            progress=0,
            is_completed=False
        )[0]
    
    def get_course_progress(
        self, db: Session, *, user_id: str, course_id: str
    ) -> Dict[str, Any]:
        """강의별 전체 진도율 및 완료 상태 조회"""
        # 강의의 모든 수업 조회
        lessons = (
            db.query(Lesson)
            .filter(Lesson.course_id == course_id)
            .order_by(Lesson.order.asc())
            .all()
        )
        
        if not lessons:
            return {
                "total_lessons": 0,
                "completed_lessons": 0,
                "progress_percentage": 0,
                "last_accessed": None,
                "lessons": []
            }
        
        # 사용자의 학습 진행 상황 조회 (한 번의 쿼리로 최적화)
        progress_records = {
            str(record.lesson_id): record 
            for record in self.get_multi_by_course(db, user_id=user_id, course_id=course_id)
        }
        
        # 결과 계산
        completed_lessons = 0
        last_accessed = None
        lesson_progress = []
        
        for lesson in lessons:
            progress = progress_records.get(str(lesson.id))
            is_completed = progress.completed if progress else False
            
            if is_completed:
                completed_lessons += 1
            
            if progress and (last_accessed is None or progress.last_accessed > last_accessed):
                last_accessed = progress.last_accessed
            
            lesson_progress.append({
                "lesson_id": str(lesson.id),
                "title": lesson.title,
                "order": lesson.order,
                "is_completed": is_completed,
                "progress": progress.progress if progress else 0,
                "last_accessed": progress.last_accessed if progress else None
            })
        
        total_lessons = len(lessons)
        progress_percentage = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        
        # 강의 완료 여부 확인 및 업데이트
        if completed_lessons == total_lessons and total_lessons > 0:
            from app.crud import enrollment
            enrollment.crud.enrollment.complete_course(
                db, user_id=user_id, course_id=course_id
            )
        
        return {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": progress_percentage,
            "last_accessed": last_accessed,
            "lessons": lesson_progress
        }
    
    def get_user_stats(
        self, db: Session, *, user_id: str
    ) -> Dict[str, Any]:
        """사용자의 전체 학습 통계 조회"""
        # 총 수강 중인 강의 수
        total_enrolled_courses = (
            db.query(Enrollment)
            .filter(
                and_(
                    Enrollment.user_id == user_id,
                    Enrollment.is_active == True  # noqa
                )
            )
            .count()
        )
        
        # 완료한 강의 수
        completed_courses = (
            db.query(Enrollment)
            .filter(
                and_(
                    Enrollment.user_id == user_id,
                    Enrollment.completed_at.isnot(None)
                )
            )
            .count()
        )
        
        # 총 학습 시간 (분 단위)
        total_study_time = (
            db.query(func.sum(Lesson.duration))
            .join(self.model, self.model.lesson_id == Lesson.id)
            .filter(self.model.user_id == user_id)
            .scalar() or 0
        )
        
        # 총 완료한 수업 수
        completed_lessons = (
            db.query(self.model)
            .filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.completed == True  # noqa
                )
            )
            .count()
        )
        
        # 최근 학습한 강의
        recent_lessons = (
            db.query(self.model, Lesson, Course)
            .join(Lesson, self.model.lesson_id == Lesson.id)
            .join(Course, Lesson.course_id == Course.id)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.last_accessed.desc())
            .limit(5)
            .all()
        )
        
        recent_activities = []
        for progress, lesson, course in recent_lessons:
            recent_activities.append({
                "course_id": str(course.id),
                "course_title": course.title,
                "lesson_id": str(lesson.id),
                "lesson_title": lesson.title,
                "last_accessed": progress.last_accessed,
                "progress": progress.progress,
                "is_completed": progress.completed
            })
        
        return {
            "total_enrolled_courses": total_enrolled_courses,
            "completed_courses": completed_courses,
            "total_study_time_minutes": total_study_time,
            "completed_lessons": completed_lessons,
            "recent_activities": recent_activities
        }
    
    def get_lesson_stats(
        self, db: Session, *, lesson_id: str
    ) -> Dict[str, Any]:
        """수업별 학습 통계 (강사용)"""
        # 수업 정보 조회
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 수업을 찾을 수 없습니다.",
            )
        
        # 총 수강생 수
        total_students = (
            db.query(Enrollment)
            .filter(
                and_(
                    Enrollment.course_id == lesson.course_id,
                    Enrollment.is_active == True  # noqa
                )
            )
            .count()
        )
        
        if total_students == 0:
            return {
                "total_students": 0,
                "completed_students": 0,
                "completion_rate": 0.0,
                "avg_progress": 0.0,
                "total_views": 0
            }
        
        # 수업을 완료한 수강생 수
        completed_students = (
            db.query(self.model)
            .filter(
                and_(
                    self.model.lesson_id == lesson_id,
                    self.model.completed == True  # noqa
                )
            )
            .count()
        )
        
        # 평균 진도율
        avg_progress = (
            db.query(func.avg(self.model.progress))
            .filter(self.model.lesson_id == lesson_id)
            .scalar() or 0
        )
        
        # 총 조회 수 (고유 사용자 수)
        total_views = (
            db.query(self.model)
            .filter(self.model.lesson_id == lesson_id)
            .count()
        )
        
        return {
            "total_students": total_students,
            "completed_students": completed_students,
            "completion_rate": (completed_students / total_students) * 100,
            "avg_progress": float(avg_progress),
            "total_views": total_views
        }
