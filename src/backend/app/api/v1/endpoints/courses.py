"""
강의 및 수업 관리를 위한 API 엔드포인트입니다.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[schemas.Course])
async def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    is_published: Optional[bool] = None,
    instructor_id: Optional[UUID] = None,
    level: Optional[schemas.CourseLevel] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    강의 목록을 조회합니다.
    
    - **is_published**: 공개 여부로 필터링 (True/False)
    - **instructor_id**: 강사 ID로 필터링
    - **level**: 난이도로 필터링 (beginner/intermediate/advanced)
    """
    # 관리자 또는 강사만 모든 강의 조회 가능
    if not current_user.is_superuser and not deps.is_instructor(current_user):
        is_published = True  # 일반 사용자는 공개된 강의만 조회 가능
    
    courses = crud.course.get_multi(
        db,
        skip=skip,
        limit=limit,
        is_published=is_published,
        instructor_id=instructor_id,
        level=level,
    )
    return courses


@router.post("/", response_model=schemas.Course, status_code=status.HTTP_201_CREATED)
async def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: schemas.CourseCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    새 강의를 생성합니다.
    
    강사 또는 관리자만 접근 가능합니다.
    """
    if not current_user.is_superuser and not deps.is_instructor(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="강의를 생성할 권한이 없습니다.",
        )
    
    # 강사 ID를 현재 사용자로 설정
    course_in_dict = course_in.dict()
    course_in_dict["instructor_id"] = current_user.id
    
    course = crud.course.create(db, obj_in=course_in_dict)
    return course


@router.get("/{course_id}", response_model=schemas.CourseWithLessons)
async def read_course(
    course_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    특정 강의의 상세 정보를 조회합니다.
    
    - 강의 소유자, 관리자 또는 수강생만 접근 가능합니다.
    - 비공개 강의는 소유자와 관리자만 조회 가능합니다.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 강의를 찾을 수 없습니다.",
        )
    
    # 권한 확인
    if not _can_access_course(course, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 강의에 접근할 권한이 없습니다.",
        )
    
    return course


@router.put("/{course_id}", response_model=schemas.Course)
async def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    course_in: schemas.CourseUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    강의 정보를 수정합니다.
    
    강의 소유자 또는 관리자만 접근 가능합니다.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 강의를 찾을 수 없습니다.",
        )
    
    # 권한 확인
    if not _is_course_owner(course, current_user) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 강의를 수정할 권한이 없습니다.",
        )
    
    course = crud.course.update(db, db_obj=course, obj_in=course_in)
    return course


@router.delete("/{course_id}", response_model=schemas.Course)
async def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    강의를 삭제합니다.
    
    강의 소유자 또는 관리자만 접근 가능합니다.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 강의를 찾을 수 없습니다.",
        )
    
    # 권한 확인
    if not _is_course_owner(course, current_user) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 강의를 삭제할 권한이 없습니다.",
        )
    
    course = crud.course.remove(db, id=course_id)
    return course


@router.post("/{course_id}/enroll", response_model=schemas.Enrollment)
async def enroll_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    강의에 수강 신청합니다.
    
    - 공개된 강의만 수강 신청이 가능합니다.
    - 이미 수강 중인 경우 기존 수강 정보를 반환합니다.
    """
    course = crud.course.get(db, id=course_id)
    if not course or not course.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 강의를 찾을 수 없거나 수강 신청이 불가능합니다.",
        )
    
    # 이미 수강 중인지 확인
    existing_enrollment = crud.enrollment.get_by_user_and_course(
        db, user_id=current_user.id, course_id=course_id
    )
    if existing_enrollment:
        return existing_enrollment
    
    # 수강 신청 생성
    enrollment_in = {
        "user_id": current_user.id,
        "course_id": course_id,
        "is_active": True,
    }
    
    enrollment = crud.enrollment.create(db, obj_in=enrollment_in)
    return enrollment


@router.get("/{course_id}/lessons", response_model=List[schemas.Lesson])
async def read_lessons(
    course_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    강의의 수업 목록을 조회합니다.
    
    - 강의 소유자, 관리자 또는 수강생만 접근 가능합니다.
    - 비공개 강의는 소유자와 관리자만 조회 가능합니다.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 강의를 찾을 수 없습니다.",
        )
    
    # 권한 확인
    if not _can_access_course(course, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 강의의 수업 목록을 조회할 권한이 없습니다.",
        )
    
    lessons = crud.lesson.get_multi_by_course(db, course_id=course_id)
    return lessons


@router.post("/{course_id}/lessons", response_model=schemas.Lesson, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    lesson_in: schemas.LessonCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    새로운 수업을 생성합니다.
    
    강의 소유자 또는 관리자만 접근 가능합니다.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 강의를 찾을 수 없습니다.",
        )
    
    # 권한 확인
    if not _is_course_owner(course, current_user) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 강의에 수업을 추가할 권한이 없습니다.",
        )
    
    # 강의 ID 설정
    lesson_in_dict = lesson_in.dict()
    lesson_in_dict["course_id"] = course_id
    
    # 순서가 지정되지 않은 경우, 마지막 순서 + 1로 설정
    if lesson_in_dict.get("order") is None:
        last_lesson = crud.lesson.get_last_lesson(db, course_id=course_id)
        lesson_in_dict["order"] = (last_lesson.order + 1) if last_lesson else 1
    
    lesson = crud.lesson.create(db, obj_in=lesson_in_dict)
    
    # 강의의 총 시간 업데이트
    _update_course_duration(db, course_id)
    
    return lesson


@router.put("/{course_id}/lessons/{lesson_id}", response_model=schemas.Lesson)
async def update_lesson(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    lesson_id: UUID,
    lesson_in: schemas.LessonUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    수업 정보를 수정합니다.
    
    강의 소유자 또는 관리자만 접근 가능합니다.
    """
    # 강의 존재 여부 확인
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 강의를 찾을 수 없습니다.",
        )
    
    # 권한 확인
    if not _is_course_owner(course, current_user) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 수업을 수정할 권한이 없습니다.",
        )
    
    # 수업 존재 여부 확인
    lesson = crud.lesson.get(db, id=lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 수업을 찾을 수 없습니다.",
        )
    
    # 순서 변경이 있는 경우 처리
    if lesson_in.order is not None and lesson_in.order != lesson.order:
        _reorder_lessons(db, course_id, lesson_id, lesson_in.order)
    
    lesson = crud.lesson.update(db, db_obj=lesson, obj_in=lesson_in)
    
    # 강의의 총 시간 업데이트
    _update_course_duration(db, course_id)
    
    return lesson


@router.delete("/{course_id}/lessons/{lesson_id}", response_model=schemas.Lesson)
async def delete_lesson(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    lesson_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    수업을 삭제합니다.
    
    강의 소유자 또는 관리자만 접근 가능합니다.
    """
    # 강의 존재 여부 확인
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 강의를 찾을 수 없습니다.",
        )
    
    # 권한 확인
    if not _is_course_owner(course, current_user) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 수업을 삭제할 권한이 없습니다.",
        )
    
    # 수업 존재 여부 확인
    lesson = crud.lesson.get(db, id=lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 수업을 찾을 수 없습니다.",
        )
    
    lesson = crud.lesson.remove(db, id=lesson_id)
    
    # 남은 수업들의 순서 재정렬
    _reorder_remaining_lessons(db, course_id)
    
    # 강의의 총 시간 업데이트
    _update_course_duration(db, course_id)
    
    return lesson


@router.get("/{course_id}/stats", response_model=schemas.CourseStats)
async def get_course_stats(
    course_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    강의 통계 정보를 조회합니다.
    
    강의 소유자 또는 관리자만 접근 가능합니다.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 강의를 찾을 수 없습니다.",
        )
    
    # 권한 확인
    if not _is_course_owner(course, current_user) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 강의의 통계를 조회할 권한이 없습니다.",
        )
    
    # 통계 정보 조회
    total_students = crud.enrollment.count_by_course(db, course_id=course_id)
    total_lessons = crud.lesson.count_by_course(db, course_id=course_id)
    
    # TODO: 평균 진도율 및 수료율 계산 로직 구현
    avg_progress = 0.0
    completion_rate = 0.0
    
    return {
        "total_students": total_students,
        "total_lessons": total_lessons,
        "total_duration": course.duration * 60,  # 분을 초로 변환
        "avg_progress": avg_progress,
        "completion_rate": completion_rate,
    }


def _is_course_owner(course: models.Course, user: models.User) -> bool:
    """사용자가 강의의 소유자인지 확인합니다."""
    return str(course.instructor_id) == str(user.id)


def _can_access_course(course: models.Course, user: models.User) -> bool:
    """사용자가 강의에 접근할 수 있는지 확인합니다."""
    # 관리자 또는 강의 소유자는 항상 접근 가능
    if user.is_superuser or _is_course_owner(course, user):
        return True
    
    # 공개된 강의는 모두 접근 가능
    if course.is_published:
        return True
    
    # 수강생인 경우 접근 가능
    from app.crud import enrollment
    db = next(enrollment.get_db())
    is_enrolled = enrollment.get_by_user_and_course(
        db, user_id=user.id, course_id=course.id
    )
    
    return is_enrolled is not None


def _update_course_duration(db: Session, course_id: UUID) -> None:
    """강의의 총 재생 시간을 업데이트합니다."""
    from app.crud import lesson
    
    # 모든 수업의 재생 시간 합계 계산 (초 단위)
    lessons = lesson.get_multi_by_course(db, course_id=course_id)
    total_duration_seconds = sum(lesson.duration for lesson in lessons)
    
    # 분 단위로 변환 (올림 처리)
    total_duration_minutes = (total_duration_seconds + 59) // 60
    
    # 강의 정보 업데이트
    from app.crud import course
    course.update(
        db,
        db_obj=course.get(db, id=course_id),
        obj_in={"duration": total_duration_minutes}
    )


def _reorder_lessons(db: Session, course_id: UUID, lesson_id: UUID, new_order: int) -> None:
    """수업의 순서를 변경합니다."""
    from app.crud import lesson
    
    # 현재 수업 조회
    current_lesson = lesson.get(db, id=lesson_id)
    if not current_lesson or current_lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 수업을 찾을 수 없습니다.",
        )
    
    old_order = current_lesson.order
    if new_order == old_order:
        return  # 순서 변경 없음
    
    # 순서 업데이트
    if new_order < old_order:
        # 순서를 앞으로 당기는 경우 (예: 3번을 1번으로)
        db.query(models.Lesson).filter(
            models.Lesson.course_id == course_id,
            models.Lesson.order >= new_order,
            models.Lesson.order < old_order,
            models.Lesson.id != lesson_id
        ).update({"order": models.Lesson.order + 1})
    else:
        # 순서를 뒤로 미는 경우 (예: 1번을 3번으로)
        db.query(models.Lesson).filter(
            models.Lesson.course_id == course_id,
            models.Lesson.order > old_order,
            models.Lesson.order <= new_order,
            models.Lesson.id != lesson_id
        ).update({"order": models.Lesson.order - 1})
    
    # 현재 수업의 순서 업데이트
    current_lesson.order = new_order
    db.commit()


def _reorder_remaining_lessons(db: Session, course_id: UUID) -> None:
    """삭제 후 남은 수업들의 순서를 재정렬합니다."""
    from app.crud import lesson
    
    # 강의의 모든 수업을 순서대로 조회
    lessons = lesson.get_multi_by_course(db, course_id=course_id, order_by="order")
    
    # 순서 재할당
    for index, lesson_obj in enumerate(lessons, start=1):
        if lesson_obj.order != index:
            lesson_obj.order = index
            db.add(lesson_obj)
    
    db.commit()
