from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator

class UserBase(BaseModel):
    """사용자 기본 모델"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, 
                         regex="^[a-zA-Z0-9_]+$",
                         description="알파벳, 숫자, 밑줄(_)만 사용 가능합니다.")
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    is_active: bool = True
    is_superuser: bool = False

    @validator('username')
    def username_must_be_lowercase(cls, v):
        if v != v.lower():
            raise ValueError('사용자명은 소문자여야 합니다.')
        return v


class UserCreate(BaseModel):
    """사용자 생성 모델"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, 
                         regex="^[a-z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "strongpassword123",
                "full_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg"
            }
        }


class UserUpdate(BaseModel):
    """사용자 정보 업데이트 모델"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=50,
        regex="^[a-z0-9_]+"
    )
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    current_password: Optional[str] = Field(None, min_length=8, max_length=100)
    new_password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "email": "new.email@example.com",
                "username": "newusername",
                "full_name": "New Name",
                "bio": "업데이트된 소개입니다.",
                "avatar_url": "https://example.com/new-avatar.jpg"
            }
        }


class UserInDBBase(BaseModel):
    """데이터베이스용 사용자 기본 모델"""
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = {}

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserResponse(UserInDBBase):
    """API 응답용 사용자 모델"""
    pass


class Token(BaseModel):
    """인증 토큰 모델"""
    access_token: str
    token_type: str
    user: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "username": "johndoe",
                    "full_name": "John Doe",
                    "avatar_url": "https://example.com/avatar.jpg",
                    "is_active": True,
                    "is_superuser": False,
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00"
                }
            }
        }


class PasswordResetRequest(BaseModel):
    """비밀번호 재설정 요청 모델"""
    email: EmailStr
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """비밀번호 재설정 확인 모델"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    class Config:
        schema_extra = {
            "example": {
                "token": "reset-token-here",
                "new_password": "newstrongpassword123"
            }
        }
