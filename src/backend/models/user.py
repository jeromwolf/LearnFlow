from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum, Table, JSON, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from database import Base
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
import re
from enum import Enum as PyEnum

# 사용자 역할 정의
class UserRole(str, PyEnum):
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"
    MODERATOR = "moderator"

# 사용자-역할 매핑 테이블 (다대다 관계용)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("granted_by", Integer, ForeignKey("users.id")),
    Index("idx_user_roles_user_id", "user_id"),
    Index("idx_user_roles_role_id", "role_id")
)

# 역할 모델
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")

# 권한 모델
class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

# 역할-권한 매핑 테이블 (다대다 관계용)
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Index("idx_role_permissions_role_id", "role_id"),
    Index("idx_role_permissions_permission_id", "permission_id")
)

# 사용자 모델
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth_id = Column(String(255), unique=True, index=True)  # Supabase auth id
    email = Column(String(255), unique=True, index=True, nullable=False)
    email_verified = Column(Boolean, default=False, index=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    password_hash = Column(String(255), nullable=True)  # OAuth 사용자는 null 가능
    password_reset_token = Column(String(255), unique=True, index=True, nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # 프로필 정보
    username = Column(String(50), unique=True, index=True, nullable=True)
    full_name = Column(String(100), index=True)
    display_name = Column(String(100), index=True, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    phone_number = Column(String(20), nullable=True, index=True)
    phone_verified = Column(Boolean, default=False, index=True)
    date_of_birth = Column(DateTime(timezone=True), nullable=True, index=True)
    gender = Column(String(20), nullable=True, index=True)
    country = Column(String(100), nullable=True, index=True)
    timezone = Column(String(50), nullable=True, default="Asia/Seoul")
    preferred_language = Column(String(10), nullable=True, default="ko")
    
    # 계정 상태
    is_active = Column(Boolean, default=True, index=True)
    is_superuser = Column(Boolean, default=False, index=True)
    is_email_public = Column(Boolean, default=False)
    is_phone_public = Column(Boolean, default=False)
    is_profile_public = Column(Boolean, default=True)
    
    # 활동 정보
    last_login_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_login_ip = Column(String(45), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=True, index=True)
    login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # 소셜 미디어 링크 (JSON 형식으로 저장)
    social_links = Column(JSON, nullable=True, default=dict)
    
    # 관계
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="creator", cascade="all, delete-orphan")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    
    # 인덱스
    __table_args__ = (
        Index('idx_users_auth_id', 'auth_id', postgresql_using='hash'),
        Index('idx_users_email', 'email', postgresql_using='hash'),
        Index('idx_users_username', 'username', postgresql_using='hash'),
        Index('idx_users_created_at', 'created_at', postgresql_using='brin'),
        Index('idx_users_updated_at', 'updated_at', postgresql_using='brin'),
    )
    
    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email is required")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        return email.lower()
    
    @validates('username')
    def validate_username(self, key, username):
        if username and not re.match(r'^[a-zA-Z0-9_]{3,50}$', username):
            raise ValueError("Username must be 3-50 characters long and contain only letters, numbers, and underscores")
        return username
    
    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        if phone_number and not re.match(r'^\+?[0-9\s-]{10,20}$', phone_number):
            raise ValueError("Invalid phone number format")
        return phone_number

# 사용자 활동 유형
class ActivityType(str, PyEnum):
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PROFILE_UPDATE = "profile_update"
    EMAIL_VERIFICATION = "email_verification"
    PHONE_VERIFICATION = "phone_verification"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    ROLE_CHANGE = "role_change"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    LOGIN_ATTEMPT = "login_attempt"

# 사용자 활동 로그 모델
class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    activity_type = Column(String(50), index=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_info = Column(JSON, nullable=True)
    location = Column(JSON, nullable=True)
    activity_metadata = Column(JSON, nullable=True, comment="추가 메타데이터 (JSON 형식)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 관계
    user = relationship("User", back_populates="activities")
    
    # 인덱스
    __table_args__ = (
        Index('idx_user_activities_user_id_created_at', 'user_id', 'created_at'),
        Index('idx_user_activities_activity_type_created_at', 'activity_type', 'created_at'),
    )

# Pydantic 모델 (API 요청/응답용)
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=50, 
        pattern=r'^[a-zA-Z0-9_]+$',
        description="사용자 이름 (영문자, 숫자, 밑줄만 허용)"
    )
    full_name: str = Field(..., min_length=2, max_length=100)
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "display_name": "John"
            }
        }

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('password must contain at least one number')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('password must contain at least one special character')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    phone_number: Optional[str] = Field(
        None, 
        pattern=r'^\+?[1-9]\d{1,14}$',
        description="E.164 형식의 전화번호"
    )
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    preferred_language: Optional[str] = Field(None, max_length=10)
    is_email_public: Optional[bool] = None
    is_phone_public: Optional[bool] = None
    is_profile_public: Optional[bool] = None
    avatar_url: Optional[HttpUrl] = None
    social_links: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "display_name": "John",
                "bio": "Software Developer",
                "phone_number": "+821012345678",
                "date_of_birth": "1990-01-01",
                "gender": "male",
                "country": "South Korea",
                "timezone": "Asia/Seoul",
                "preferred_language": "ko",
                "is_email_public": True,
                "is_phone_public": False,
                "is_profile_public": True,
                "avatar_url": "https://example.com/avatar.jpg",
                "social_links": {
                    "github": "https://github.com/username",
                    "twitter": "https://twitter.com/username"
                }
            }
        }

class UserInDB(UserBase):
    id: int
    auth_id: str
    email_verified: bool
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserPublic(UserBase):
    id: int
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    is_profile_public: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

# 역할 및 권한 관련 Pydantic 모델
class RoleBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-z_]+$')
    description: Optional[str] = Field(None, max_length=500)
    is_default: bool = False

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=500)
    is_default: Optional[bool] = None

class RoleInDB(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PermissionBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, pattern=r'^[a-z_]+$')
    description: Optional[str] = Field(None, max_length=500)

class PermissionCreate(PermissionBase):
    pass

class PermissionInDB(PermissionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 사용자 활동 로그 Pydantic 모델
class UserActivityBase(BaseModel):
    activity_type: ActivityType
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class UserActivityCreate(UserActivityBase):
    pass

class UserActivityInDB(UserActivityBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
