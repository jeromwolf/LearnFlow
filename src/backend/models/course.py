from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, 
    Boolean, Float, UniqueConstraint, Text, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Course(Base):
    """강의를 나타내는 모델입니다."""
    __tablename__ = "courses"
    __table_args__ = (
        Index('ix_courses_creator_id', 'creator_id'),
        Index('ix_courses_is_published', 'is_published'),
        Index('ix_courses_created_at', 'created_at'),
        {'sqlite_autoincrement': True},
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment='강의 고유 ID'
    )
    title = Column(
        String(200),
        nullable=False,
        index=True,
        comment='강의 제목'
    )
    description = Column(
        Text,
        nullable=False,
        comment='강의 설명'
    )
    thumbnail_url = Column(
        String(500),
        nullable=True,
        comment='썸네일 이미지 URL'
    )
    price = Column(
        Float,
        nullable=False,
        default=0.0,
        comment='가격 (원)'
    )
    creator_id = Column(
        Integer,
        ForeignKey("users.id", ondelete='CASCADE'),
        nullable=False,
        comment='생성자 ID',
        index=True
    )
    difficulty = Column(
        String(20),
        nullable=False,
        default='beginner',
        comment='난이도: beginner, intermediate, advanced, all'
    )
    category = Column(
        String(50),
        nullable=False,
        default='development',
        comment='카테고리'
    )
    estimated_hours = Column(
        Integer,
        nullable=False,
        default=0,
        comment='예상 소요 시간 (시간 단위)'
    )
    is_published = Column(
        Boolean,
        default=False,
        nullable=False,
        comment='게시 여부'
    )
    is_free = Column(
        Boolean,
        default=False,
        nullable=False,
        comment='무료 강의 여부'
    )
    rating = Column(
        Float,
        default=0.0,
        nullable=False,
        comment='평균 평점 (0~5)'
    )
    num_reviews = Column(
        Integer,
        default=0,
        nullable=False,
        comment='리뷰 수'
    )
    student_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment='수강생 수'
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='생성 일시'
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=False,
        comment='수정 일시'
    )

    # Relationships
    creator = relationship("User", back_populates="courses")
    sections = relationship(
        "CourseSection",
        back_populates="course",
        cascade="all, delete-orphan"
    )
    enrollments = relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan"
    )
    reviews = relationship(
        "CourseReview",
        back_populates="course",
        cascade="all, delete-orphan"
    )


class CourseSection(Base):
    """강의의 섹션을 나타내는 모델입니다."""
    __tablename__ = "course_sections"
    __table_args__ = (
        UniqueConstraint(
            'course_id', 'order_index',
            name='_course_section_order_uc'
        ),
        {'sqlite_autoincrement': True},
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment='섹션 고유 ID'
    )
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete='CASCADE'),
        nullable=False,
        comment='강의 ID',
        index=True
    )
    title = Column(
        String(200),
        nullable=False,
        comment='섹션 제목'
    )
    description = Column(
        String(500),
        nullable=True,
        comment='섹션 설명'
    )
    order_index = Column(
        Integer,
        nullable=False,
        default=0,
        comment='정렬 순서'
    )
    is_public = Column(
        Boolean,
        default=True,
        nullable=False,
        comment='공개 여부'
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='생성 일시'
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=False,
        comment='수정 일시'
    )

    # Relationships
    course = relationship("Course", back_populates="sections")
    lessons = relationship(
        "Lesson",
        back_populates="section",
        cascade="all, delete-orphan"
    )


class Lesson(Base):
    """강의 섹션 내의 개별 레슨을 나타내는 모델입니다."""
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint(
            'section_id', 'order_index',
            name='_section_lesson_order_uc'
        ),
        {'sqlite_autoincrement': True},
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment='레슨 고유 ID'
    )
    section_id = Column(
        Integer,
        ForeignKey("course_sections.id", ondelete='CASCADE'),
        nullable=False,
        comment='섹션 ID',
        index=True
    )
    title = Column(
        String(200),
        nullable=False,
        comment='레슨 제목'
    )
    description = Column(
        Text,
        nullable=True,
        comment='레슨 설명'
    )
    content = Column(
        Text,
        nullable=True,
        comment='레슨 내용 (HTML/Markdown)'
    )
    video_url = Column(
        String(500),
        nullable=True,
        comment='비디오 URL'
    )
    duration = Column(
        Integer,
        nullable=False,
        default=0,
        comment='재생 시간 (초)'
    )
    order_index = Column(
        Integer,
        nullable=False,
        default=0,
        comment='정렬 순서'
    )
    is_preview = Column(
        Boolean,
        default=False,
        nullable=False,
        comment='미리보기 가능 여부'
    )
    is_published = Column(
        Boolean,
        default=True,
        nullable=False,
        comment='게시 여부'
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='생성 일시'
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=False,
        comment='수정 일시'
    )

    # Relationships
    section = relationship("CourseSection", back_populates="lessons")
    completions = relationship(
        "LessonCompletion",
        back_populates="lesson",
        cascade="all, delete-orphan"
    )


class Enrollment(Base):
    """사용자의 강의 수강 정보를 나타내는 모델입니다."""
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'course_id',
            name='_user_course_enrollment_uc'
        ),
        {'sqlite_autoincrement': True},
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment='수강 등록 고유 ID'
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete='CASCADE'),
        nullable=False,
        comment='사용자 ID',
        index=True
    )
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete='CASCADE'),
        nullable=False,
        comment='강의 ID',
        index=True
    )
    enrolled_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='수강 신청 일시'
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='수강 완료 일시'
    )
    progress = Column(
        Float,
        default=0.0,
        nullable=False,
        comment='진행률 (0~100)'
    )
    last_accessed_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
        comment='마지막 학습 일시'
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment='활성 상태 여부'
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='생성 일시'
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=False,
        comment='수정 일시'
    )

    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    lesson_completions = relationship(
        "LessonCompletion",
        back_populates="enrollment",
        cascade="all, delete-orphan"
    )


class CourseReview(Base):
    """강의에 대한 리뷰를 나타내는 모델입니다."""
    __tablename__ = "course_reviews"
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'course_id',
            name='_user_course_review_uc'
        ),
        {'sqlite_autoincrement': True},
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment='리뷰 고유 ID'
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete='CASCADE'),
        nullable=False,
        comment='사용자 ID',
        index=True
    )
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete='CASCADE'),
        nullable=False,
        comment='강의 ID',
        index=True
    )
    rating = Column(
        Float,
        nullable=False,
        comment='평점 (1~5)'
    )
    title = Column(
        String(200),
        nullable=True,
        comment='리뷰 제목'
    )
    comment = Column(
        Text,
        nullable=False,
        comment='리뷰 내용'
    )
    is_public = Column(
        Boolean,
        default=True,
        nullable=False,
        comment='공개 여부'
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='생성 일시'
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=False,
        comment='수정 일시'
    )

    # Relationships
    user = relationship("User", back_populates="reviews")
    course = relationship("Course", back_populates="reviews")


class LessonCompletion(Base):
    """사용자의 레슨 완료 정보를 나타내는 모델입니다."""
    __tablename__ = "lesson_completions"
    __table_args__ = (
        UniqueConstraint(
            'enrollment_id', 'lesson_id',
            name='_enrollment_lesson_completion_uc'
        ),
        {'sqlite_autoincrement': True},
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment='레슨 완료 고유 ID'
    )
    enrollment_id = Column(
        Integer,
        ForeignKey("enrollments.id", ondelete='CASCADE'),
        nullable=False,
        comment='수강 등록 ID',
        index=True
    )
    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id", ondelete='CASCADE'),
        nullable=False,
        comment='레슨 ID',
        index=True
    )
    progress = Column(
        Integer,
        nullable=False,
        default=0,
        comment='진행률 (0~100)'
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='완료 일시'
    )
    last_accessed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='마지막 접속 일시'
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='생성 일시'
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=False,
        comment='수정 일시'
    )

    # Relationships
    enrollment = relationship("Enrollment", back_populates="lesson_completions")
    lesson = relationship("Lesson", back_populates="completions")
