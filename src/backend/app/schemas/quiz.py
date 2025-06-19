from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

# Enums
class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class QuizAttemptStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    GRADED = "graded"

# Base schemas
class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool = False
    order_num: int = 0

    class Config:
        orm_mode = True

class QuestionBase(BaseModel):
    question_text: str
    question_type: QuestionType
    points: int = 1
    order_num: int = 0
    explanation: Optional[str] = None
    choices: Optional[List[ChoiceBase]] = []

    class Config:
        orm_mode = True

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_id: int
    time_limit: Optional[int] = Field(None, ge=0, description="제한 시간(초), 0이면 무제한")
    max_attempts: int = Field(1, ge=0, description="최대 시도 횟수, 0이면 무제한")
    passing_score: int = Field(80, ge=0, le=100, description="합격 점수(0-100)")
    is_published: bool = False

# Create schemas
class ChoiceCreate(ChoiceBase):
    pass

class QuestionCreate(QuestionBase):
    choices: Optional[List[ChoiceBase]] = []

class QuizCreate(QuizBase):
    questions: List[QuestionCreate] = []

class QuizAttemptCreate(BaseModel):
    quiz_id: int

class QuestionAnswerCreate(BaseModel):
    question_id: int
    answer_data: Dict[str, Any]

class QuizAttemptSubmit(BaseModel):
    answers: List[QuestionAnswerCreate]

# Update schemas
class ChoiceUpdate(ChoiceBase):
    id: Optional[int] = None

class QuestionUpdate(QuestionBase):
    id: Optional[int] = None
    choices: Optional[List[ChoiceUpdate]] = []

class QuizUpdate(QuizBase):
    title: Optional[str] = None
    description: Optional[str] = None
    content_id: Optional[int] = None
    time_limit: Optional[int] = None
    max_attempts: Optional[int] = None
    passing_score: Optional[int] = None
    is_published: Optional[bool] = None
    questions: Optional[List[QuestionUpdate]] = []

class QuestionAnswerUpdate(BaseModel):
    id: int
    points_awarded: int
    feedback: Optional[str] = None
    is_correct: bool

class QuizGrading(BaseModel):
    answers: List[QuestionAnswerUpdate]

# Response schemas
class ChoiceResponse(ChoiceBase):
    id: int

    class Config:
        orm_mode = True

class QuestionResponse(QuestionBase):
    id: int
    choices: List[ChoiceResponse] = []

    class Config:
        orm_mode = True

class QuizResponse(QuizBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    questions: List[QuestionResponse] = []

    class Config:
        orm_mode = True

class QuestionAnswerResponse(BaseModel):
    id: int
    question_id: int
    answer_data: Dict[str, Any]
    is_correct: Optional[bool] = None
    points_awarded: int
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True

class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    attempt_number: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    time_spent: int
    score: int
    passed: bool
    status: str
    answers: List[QuestionAnswerResponse] = []

    class Config:
        orm_mode = True

class UserQuizProgressResponse(BaseModel):
    quiz_id: int
    completed_attempts: int
    best_score: int
    passed: bool
    last_attempt_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Statistics
class QuizStatistics(BaseModel):
    total_attempts: int
    average_score: float
    pass_rate: float
    question_stats: Dict[int, Dict[str, Any]] = {}

# For listing
class QuizListResponse(QuizBase):
    id: int
    created_at: datetime
    question_count: int
    user_progress: Optional[UserQuizProgressResponse] = None

    class Config:
        orm_mode = True

# For taking a quiz
class QuizTakeResponse(QuizResponse):
    current_attempt_id: Optional[int] = None
    remaining_attempts: Optional[int] = None
    time_remaining: Optional[int] = None

# For quiz results
class QuizResultResponse(QuizAttemptResponse):
    quiz: QuizResponse
    user_progress: UserQuizProgressResponse
