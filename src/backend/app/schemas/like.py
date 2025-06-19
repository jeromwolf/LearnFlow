from pydantic import BaseModel
from datetime import datetime

class LikeBase(BaseModel):
    """좋아요 기본 스키마"""
    pass

class LikeCreate(LikeBase):
    """좋아요 생성 스키마"""
    pass

class LikeInDBBase(LikeBase):
    """데이터베이스용 좋아요 스키마"""
    id: int
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class LikeResponse(LikeInDBBase):
    """응답용 좋아요 스키마"""
    pass

class LikeStatus(BaseModel):
    """좋아요 상태 응답 스키마"""
    is_liked: bool
    like_count: int
