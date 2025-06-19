from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.db.base import Base, metadata
from app.utils.password import get_password_hash, verify_password

# 사용자와 역할 간의 다대다 관계 테이블
user_roles = Table(
    'user_roles',
    metadata,
    Column('user_id', String, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', String, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

class User(Base):
    """사용자 모델"""
    __tablename__ = "users"
    
    # 기본 정보
    id = Column(String, primary_key=True, index=True, comment="사용자 고유 ID (UUID)")
    email = Column(String, unique=True, index=True, nullable=False, comment="이메일 주소")
    username = Column(String, unique=True, index=True, nullable=False, comment="사용자명")
    full_name = Column(String, nullable=True, comment="전체 이름")
    hashed_password = Column(String, nullable=True, comment="해시된 비밀번호 (로컬 인증 시 사용)")
    
    # 프로필 정보
    avatar_url = Column(String, nullable=True, comment="프로필 이미지 URL")
    bio = Column(String, nullable=True, comment="자기소개")
    
    # 계정 상태
    is_active = Column(Boolean, default=True, comment="계정 활성화 여부")
    is_verified = Column(Boolean, default=False, comment="이메일 인증 여부")
    is_superuser = Column(Boolean, default=False, comment="슈퍼유저 여부")
    
    # 소셜 로그인 정보
    provider = Column(String, default="email", comment="인증 제공자 (email, google, github 등)")
    provider_id = Column(String, nullable=True, comment="소셜 제공자에서의 사용자 ID")
    
    # 메타데이터
    last_login = Column(DateTime, nullable=True, comment="마지막 로그인 시간")
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성일시")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")
    
    # 관계
    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    
    # 강의 관련 관계
    courses_taught = relationship("Course", back_populates="instructor", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str) -> None:
        """비밀번호를 해시하여 설정합니다."""
        self.hashed_password = get_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        """비밀번호를 검증합니다."""
        if not self.hashed_password:
            return False
        return verify_password(password, self.hashed_password)
    
    def has_role(self, role_name: str) -> bool:
        """사용자가 특정 역할을 가지고 있는지 확인합니다."""
        return any(role.name == role_name for role in self.roles)
    
    def to_dict(self) -> Dict[str, Any]:
        """사용자 정보를 딕셔너리로 변환합니다."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_superuser": self.is_superuser,
            "provider": self.provider,
            "roles": [role.name for role in self.roles],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Role(Base):
    """사용자 역할 모델"""
    __tablename__ = "roles"
    
    id = Column(String, primary_key=True, index=True, comment="역할 고유 ID")
    name = Column(String, unique=True, index=True, nullable=False, comment="역할 이름 (예: admin, user, moderator)")
    description = Column(String, nullable=True, comment="역할 설명")
    permissions = Column(JSON, default={}, comment="권한 목록 (JSON 형식)")
    
    # 관계
    users = relationship("User", secondary=user_roles, back_populates="roles", lazy="selectin")
    
    def to_dict(self) -> Dict[str, Any]:
        """역할 정보를 딕셔너리로 변환합니다."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
        }


class RefreshToken(Base):
    """리프레시 토큰 모델"""
    __tablename__ = "refresh_tokens"
    
    id = Column(String, primary_key=True, index=True, comment="토큰 고유 ID")
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="사용자 ID")
    token = Column(String, unique=True, index=True, nullable=False, comment="리프레시 토큰")
    expires_at = Column(DateTime, nullable=False, comment="만료 일시")
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성 일시")
    user_agent = Column(String, nullable=True, comment="사용자 에이전트")
    ip_address = Column(String, nullable=True, comment="IP 주소")
    is_revoked = Column(Boolean, default=False, comment="취소 여부")
    
    # 관계
    user = relationship("User", backref="refresh_tokens")
    
    def is_expired(self) -> bool:
        """토큰이 만료되었는지 확인합니다."""
        return datetime.utcnow() > self.expires_at
    
    def revoke(self) -> None:
        """토큰을 취소합니다."""
        self.is_revoked = True
    
    def to_dict(self) -> Dict[str, Any]:
        """토큰 정보를 딕셔너리로 변환합니다."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_revoked": self.is_revoked,
        }
