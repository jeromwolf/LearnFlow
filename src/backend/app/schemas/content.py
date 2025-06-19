from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum
from typing import Optional

# Enums
class ContentType(str, Enum):
    VIDEO = "video"
    ARTICLE = "article"
    QUIZ = "quiz"
    EXERCISE = "exercise"
    DOCUMENT = "document"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

# Base schemas
class ContentBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    content_type: ContentType
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    duration: int = Field(0, ge=0, description="콘텐츠 재생/학습 시간(분)")
    thumbnail_url: Optional[HttpUrl] = None
    content_url: Optional[HttpUrl] = None
    is_published: bool = False
    tags: List[str] = []
    metadata_: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="metadata")
    section_id: Optional[int] = None

    class Config:
        from_attributes = True
        populate_by_name = True

# Create / Update schemas
class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    difficulty: Optional[DifficultyLevel] = None
    duration: Optional[int] = Field(None, ge=0)
    thumbnail_url: Optional[HttpUrl] = None
    content_url: Optional[HttpUrl] = None
    is_published: Optional[bool] = None
    tags: Optional[List[str]] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    section_id: Optional[int] = None

    class Config:
        from_attributes = True
        populate_by_name = True

# Response schemas
class ContentInDBBase(ContentBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Content(ContentInDBBase):
    pass

class ContentInDB(ContentInDBBase):
    pass

# Section schemas
class SectionBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    order: int = 0
    course_id: int

class SectionCreate(SectionBase):
    pass

class SectionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    order: Optional[int] = None

class SectionInDBBase(SectionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Section(SectionInDBBase):
    contents: List[Content] = []

# Course schemas
class CourseBase(BaseModel):
    title: str = Field(..., max_length=200)
    subtitle: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    thumbnail_url: Optional[HttpUrl] = None
    is_published: bool = False
    price: int = Field(0, ge=0)
    discount_price: Optional[int] = Field(None, ge=0)
    instructor_id: int
    category_ids: List[int] = []

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    thumbnail_url: Optional[HttpUrl] = None
    is_published: Optional[bool] = None
    price: Optional[int] = Field(None, ge=0)
    discount_price: Optional[int] = Field(None, ge=0)
    category_ids: Optional[List[int]] = None

class CourseInDBBase(CourseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Course(CourseInDBBase):
    sections: List[Section] = []
    categories: List["Category"] = []

# Category schemas
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryInDBBase(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Category(CategoryInDBBase):
    children: List["Category"] = []
    courses: List[Course] = []

# User progress schemas
class UserContentProgressBase(BaseModel):
    content_id: int
    is_completed: bool = False
    progress: int = Field(0, ge=0, le=100)
    last_position: int = Field(0, ge=0)
    notes: Optional[str] = None

class UserContentProgressCreate(UserContentProgressBase):
    pass

class UserContentProgressUpdate(BaseModel):
    is_completed: Optional[bool] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    last_position: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class UserContentProgressInDBBase(UserContentProgressBase):
    id: int
    user_id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class UserContentProgress(UserContentProgressInDBBase):
    content: Content

# Update forward refs for nested models
Content.model_rebuild()
Course.model_rebuild()
Category.model_rebuild()
