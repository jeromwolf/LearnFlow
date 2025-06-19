from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum
from .user import UserResponse

class PostBase(BaseModel):
    """게시글 기본 스키마"""
    title: str = Field(..., min_length=2, max_length=200, description="게시글 제목")
    content: str = Field(..., min_length=1, description="게시글 내용")
    board_id: int = Field(..., description="소속 게시판 ID")
    is_notice: bool = Field(False, description="공지사항 여부")

class PostCreate(PostBase):
    """게시글 생성 스키마"""
    pass

class PostUpdate(BaseModel):
    """게시글 수정 스키마"""
    title: Optional[str] = Field(None, min_length=2, max_length=200, description="게시글 제목")
    content: Optional[str] = Field(None, min_length=1, description="게시글 내용")
    is_notice: Optional[bool] = Field(None, description="공지사항 여부")

class PostInDBBase(PostBase):
    """데이터베이스용 게시글 스키마"""
    id: int
    user_id: str
    view_count: int = 0
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Post(PostInDBBase):
    """응답용 게시글 스키마"""
    author: Optional[UserResponse] = None
    like_count: int = 0
    comment_count: int = 0
    is_liked: bool = False
    is_bookmarked: bool = False

class PostListResponse(BaseModel):
    """게시글 목록 응답 스키마"""
    total: int
    items: List[Post]

class PostSortBy(str, Enum):
    """게시글 정렬 기준"""
    LATEST = "latest"
    POPULAR = "popular"
    COMMENTS = "comments"
    LIKES = "likes"
    VIEWS = "views"
