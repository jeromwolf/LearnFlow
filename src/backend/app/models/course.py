"""
강의(Course) 및 수업(Lesson) 모델을 정의합니다.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Float, Text, Enum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Course(Base):
    """강의 모델"""
    __tablename__ = "courses"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    instructor_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    price = Column(Float, default=0.0)
    level = Column(Enum("beginner", "intermediate", "advanced", name="course_level"), default="beginner")
    duration = Column(Integer, default=0)  # 총 강의 시간 (분)
    thumbnail_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    instructor = relationship("User", back_populates="courses_taught")
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course {self.title}>"


class Lesson(Base):
    """수업 모델"""
    __tablename__ = "lessons"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    course_id = Column(PGUUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=True)
    duration = Column(Integer, default=0)  # 재생 시간 (초)
    order = Column(Integer, default=0)  # 강의 내 순서
    is_preview = Column(Boolean, default=False)  # 미리보기 가능 여부
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    course = relationship("Course", back_populates="lessons")
    user_progress = relationship("UserProgress", back_populates="lesson", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lesson {self.title} (Course: {self.course_id})>"


class Enrollment(Base):
    """수강 신청 모델"""
    __tablename__ = "enrollments"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(PGUUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # 관계 설정
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment User: {self.user_id}, Course: {self.course_id}>"


class UserProgress(Base):
    """사용자 학습 진행 상황 모델"""
    __tablename__ = "user_progress"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(PGUUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    lesson_id = Column(PGUUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    completed = Column(Boolean, default=False)
    progress = Column(Integer, default=0)  # 0-100% 진행률
    last_accessed = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # 관계 설정
    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="user_progress")

    def __repr__(self):
        return f"<UserProgress User: {self.user_id}, Lesson: {self.lesson_id}, Progress: {self.progress}%>"
