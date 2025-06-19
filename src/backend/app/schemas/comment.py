from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .user import UserResponse

class CommentBase(BaseModel):
    """댓글 기본 스키마"""
    content: str = Field(..., min_length=1, max_length=1000, description="댓글 내용")
    parent_id: Optional[int] = Field(None, description="부모 댓글 ID (대댓글인 경우)")

class CommentCreate(CommentBase):
    """댓글 생성 스키마"""
    pass

class CommentUpdate(BaseModel):
    """댓글 수정 스키마"""
    content: str = Field(..., min_length=1, max_length=1000, description="댓글 내용")

class CommentInDBBase(CommentBase):
    """데이터베이스용 댓글 스키마"""
    id: int
    post_id: int
    user_id: str
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Comment(CommentInDBBase):
    """응답용 댓글 스키마"""
    author: Optional[UserResponse] = None
    like_count: int = 0
    is_liked: bool = False
    replies: List["Comment"] = []

class CommentListResponse(BaseModel):
    """댓글 목록 응답 스키마"""
    total: int
    items: List[Comment]

# 순환 참조 해결을 위한 업데이트
Comment.update_forward_refs()
