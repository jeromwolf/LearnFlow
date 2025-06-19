from pydantic import BaseModel
from datetime import datetime

class BookmarkBase(BaseModel):
    """북마크 기본 스키마"""
    pass

class BookmarkCreate(BookmarkBase):
    """북마크 생성 스키마"""
    pass

class BookmarkInDBBase(BookmarkBase):
    """데이터베이스용 북마크 스키마"""
    id: int
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class BookmarkResponse(BookmarkInDBBase):
    """응답용 북마크 스키마"""
    pass

class BookmarkStatus(BaseModel):
    """북마크 상태 응답 스키마"""
    is_bookmarked: bool
