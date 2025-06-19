from datetime import datetime
from typing import List, Optional
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base

class ContentType(str, Enum):
    """콘텐츠 유형"""
    VIDEO = "video"
    ARTICLE = "article"
    QUIZ = "quiz"
    EXERCISE = "exercise"
    DOCUMENT = "document"

class DifficultyLevel(str, Enum):
    """난이도 레벨"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Content(Base):
    """학습 콘텐츠 모델"""
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    duration = Column(Integer, default=0, comment="콘텐츠 재생/학습 시간(분)")
    thumbnail_url = Column(String(500), nullable=True)
    content_url = Column(String(500), nullable=True, comment="실제 콘텐츠 URL 또는 경로")
    is_published = Column(Boolean, default=False, index=True)
    tags = Column(JSON, default=[], comment="태그 목록")
    metadata_ = Column("metadata", JSON, default={}, comment="추가 메타데이터")
    
    # 관계
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="contents_created")
    
    # 섹션 관계 (선택적)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)
    section = relationship("Section", back_populates="contents")
    
    # 수강 이력
    user_progress = relationship("UserContentProgress", back_populates="content")
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Section(Base):
    """콘텐츠 섹션(챕터) 모델"""
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0, comment="섹션 정렬 순서")
    
    # 관계
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    course = relationship("Course", back_populates="sections")
    contents = relationship("Content", back_populates="section", order_by="Content.id")
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Course(Base):
    """강의/코스 모델"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    subtitle = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False, index=True)
    price = Column(Integer, default=0, comment="가격 (원)")
    discount_price = Column(Integer, nullable=True, comment="할인 가격 (원)")
    
    # 관계
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    instructor = relationship("User", back_populates="courses_taught")
    
    # 섹션
    sections = relationship("Section", back_populates="course", order_by="Section.order")
    
    # 카테고리 (다대다 관계를 위한 연결 테이블 필요)
    categories = relationship("Category", secondary="course_categories", back_populates="courses")
    
    # 수강생
    students = relationship("User", secondary="enrollments", back_populates="enrolled_courses")
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Category(Base):
    """콘텐츠 카테고리"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # 관계
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent")
    courses = relationship("Course", secondary="course_categories", back_populates="categories")
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 다대다 관계 테이블
course_categories = Table(
    "course_categories",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow)
)

class UserContentProgress(Base):
    """사용자별 콘텐츠 학습 진행 상황"""
    __tablename__ = "user_content_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False, index=True)
    is_completed = Column(Boolean, default=False)
    progress = Column(Integer, default=0, comment="진행률 (0-100)")
    last_position = Column(Integer, default=0, comment="마지막 재생/학습 위치 (초)")
    notes = Column(Text, nullable=True, comment="사용자 노트")
    
    # 관계
    user = relationship("User", back_populates="content_progress")
    content = relationship("Content", back_populates="user_progress")
    
    # 타임스탬프
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 복합 고유 키 설정
    __table_args__ = (
        UniqueConstraint('user_id', 'content_id', name='_user_content_uc'),
    )
