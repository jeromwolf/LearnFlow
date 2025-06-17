"""
CRUD (Create, Read, Update, Delete) 연산을 위한 모듈입니다.

이 모듈은 데이터베이스와 상호작용하는 CRUD 연산을 캡슐화하며,
애플리케이션의 비즈니스 로직과 데이터 액세스 계층을 분리합니다.
"""
from __future__ import annotations

# 사용자 관련 CRUD 객체
from .user import user, role, refresh_token

# 강의 관리 관련 CRUD 객체
from .course import CourseCRUD
from .enrollment import EnrollmentCRUD
from .lesson import LessonCRUD
from .user_progress import UserProgressCRUD

# CRUD 객체 인스턴스화
crud_course = CourseCRUD()
crud_lesson = LessonCRUD()
crud_enrollment = EnrollmentCRUD()
crud_user_progress = UserProgressCRUD()

# 외부에서 사용할 수 있도록 노출
__all__ = [
    # 사용자 관련
    "user",
    "role",
    "refresh_token",
    
    # 강의 관리 관련
    "crud_course",
    "crud_lesson",
    "crud_enrollment",
    "crud_user_progress",
]
