from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BoardBase(BaseModel):
    """게시판 기본 스키마"""
    name: str = Field(..., min_length=2, max_length=100, description="게시판 이름")
    description: Optional[str] = Field(None, description="게시판 설명")
    is_active: bool = Field(True, description="게시판 활성화 여부")

class BoardCreate(BoardBase):
    """게시판 생성 스키마"""
    pass

class BoardUpdate(BaseModel):
    """게시판 수정 스키마"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="게시판 이름")
    description: Optional[str] = Field(None, description="게시판 설명")
    is_active: Optional[bool] = Field(None, description="게시판 활성화 여부")

class BoardInDBBase(BoardBase):
    """데이터베이스용 게시판 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Board(BoardInDBBase):
    """응답용 게시판 스키마"""
    pass
