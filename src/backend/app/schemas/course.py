"""
강의 및 수업 관련 Pydantic 모델을 정의합니다.
"""
from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum


class CourseLevel(str, Enum):
    """강의 난이도"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseBase(BaseModel):
    """강의 기본 스키마"""
    title: str = Field(..., max_length=200, description="강의 제목")
    description: Optional[str] = Field(None, description="강의 설명")
    price: float = Field(0.0, ge=0, description="가격")
    level: CourseLevel = Field(
        CourseLevel.BEGINNER, 
        description="강의 난이도 (beginner/intermediate/advanced)"
    )
    thumbnail_url: Optional[str] = Field(None, description="썸네일 이미지 URL")
    is_published: bool = Field(False, description="공개 여부")

    class Config:
        schema_extra = {
            "example": {
                "title": "파이썬으로 배우는 웹 개발",
                "description": "초보자를 위한 웹 개발 강의입니다.",
                "price": 59000,
                "level": "beginner",
                "thumbnail_url": "https://example.com/thumbnail.jpg",
                "is_published": True
            }
        }


class CourseCreate(CourseBase):
    """강의 생성 스키마"""
    pass


class CourseUpdate(BaseModel):
    """강의 수정 스키마"""
    title: Optional[str] = Field(None, max_length=200, description="강의 제목")
    description: Optional[str] = Field(None, description="강의 설명")
    price: Optional[float] = Field(None, ge=0, description="가격")
    level: Optional[CourseLevel] = Field(None, description="강의 난이도")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 이미지 URL")
    is_published: Optional[bool] = Field(None, description="공개 여부")

    class Config:
        schema_extra = {
            "example": {
                "title": "파이썬으로 배우는 웹 개발 (개정판)",
                "description": "초보자를 위한 웹 개발 강의입니다. 업데이트된 내용이 반영되었습니다.",
                "price": 69000,
                "level": "intermediate",
                "is_published": True
            }
        }


class CourseInDBBase(CourseBase):
    """데이터베이스용 강의 기본 스키마"""
    id: UUID
    instructor_id: UUID
    duration: int = Field(0, description="총 강의 시간 (분)")
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Course(CourseInDBBase):
    """응답용 강의 스키마"""
    pass


class CourseInDB(CourseInDBBase):
    """데이터베이스 조회용 강의 스키마"""
    pass


class LessonBase(BaseModel):
    """수업 기본 스키마"""
    title: str = Field(..., max_length=200, description="수업 제목")
    description: Optional[str] = Field(None, description="수업 설명")
    video_url: Optional[str] = Field(None, description="동영상 URL")
    duration: int = Field(0, ge=0, description="재생 시간 (초)")
    order: int = Field(0, ge=0, description="강의 내 순서")
    is_preview: bool = Field(False, description="미리보기 가능 여부")

    class Config:
        schema_extra = {
            "example": {
                "title": "파이썬 기초 문법",
                "description": "파이썬의 기본 문법을 배웁니다.",
                "video_url": "https://example.com/videos/1",
                "duration": 1200,
                "order": 1,
                "is_preview": True
            }
        }


class LessonCreate(LessonBase):
    """수업 생성 스키마"""
    pass


class LessonUpdate(BaseModel):
    """수업 수정 스키마"""
    title: Optional[str] = Field(None, max_length=200, description="수업 제목")
    description: Optional[str] = Field(None, description="수업 설명")
    video_url: Optional[str] = Field(None, description="동영상 URL")
    duration: Optional[int] = Field(None, ge=0, description="재생 시간 (초)")
    order: Optional[int] = Field(None, ge=0, description="강의 내 순서")
    is_preview: Optional[bool] = Field(None, description="미리보기 가능 여부")


class LessonInDBBase(LessonBase):
    """데이터베이스용 수업 기본 스키마"""
    id: UUID
    course_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Lesson(LessonInDBBase):
    """응답용 수업 스키마"""
    pass


class LessonInDB(LessonInDBBase):
    """데이터베이스 조회용 수업 스키마"""
    pass


class CourseWithLessons(Course):
    """수업 목록이 포함된 강의 스키마"""
    lessons: List[Lesson] = []


class EnrollmentBase(BaseModel):
    """수강 신청 기본 스키마"""
    user_id: UUID
    course_id: UUID
    is_active: bool = True


class EnrollmentCreate(EnrollmentBase):
    """수강 신청 생성 스키마"""
    pass


class EnrollmentUpdate(BaseModel):
    """수강 신청 수정 스키마"""
    is_active: Optional[bool] = None
    completed_at: Optional[datetime] = None


class EnrollmentInDBBase(EnrollmentBase):
    """데이터베이스용 수강 신청 기본 스키마"""
    id: UUID
    enrolled_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Enrollment(EnrollmentInDBBase):
    """응답용 수강 신청 스키마"""
    pass


class UserProgressBase(BaseModel):
    """학습 진행 상황 기본 스키마"""
    user_id: UUID
    course_id: UUID
    lesson_id: UUID
    completed: bool = False
    progress: int = Field(0, ge=0, le=100, description="진행률 (0-100%)")


class UserProgressCreate(UserProgressBase):
    """학습 진행 상황 생성 스키마"""
    pass


class UserProgressUpdate(BaseModel):
    """학습 진행 상황 수정 스키마"""
    completed: Optional[bool] = None
    progress: Optional[int] = Field(None, ge=0, le=100, description="진행률 (0-100%)")


class UserProgressInDBBase(UserProgressBase):
    """데이터베이스용 학습 진행 상황 기본 스키마"""
    id: UUID
    last_accessed: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserProgress(UserProgressInDBBase):
    """응답용 학습 진행 상황 스키마"""
    pass


class CourseStats(BaseModel):
    """강의 통계 정보"""
    total_students: int = 0
    total_lessons: int = 0
    total_duration: int = 0  # 초 단위
    avg_progress: float = 0.0  # 평균 진도율 (0-100%)
    completion_rate: float = 0.0  # 수료율 (0-100%)
