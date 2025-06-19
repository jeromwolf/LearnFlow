from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Enum, DateTime, JSON, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False)
    time_limit = Column(Integer, comment="제한 시간(초), 0이면 무제한")
    max_attempts = Column(Integer, default=1, comment="최대 시도 횟수, 0이면 무제한")
    passing_score = Column(Integer, default=80, comment="합격 점수(0-100)")
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    content = relationship("Content", back_populates="quiz")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, 
                         comment="예: 'multiple_choice', 'true_false', 'short_answer', 'essay'")
    points = Column(Integer, default=1, nullable=False)
    order_num = Column(Integer, default=0, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    choices = relationship("Choice", back_populates="question", cascade="all, delete-orphan")
    answers = relationship("QuestionAnswer", back_populates="question", cascade="all, delete-orphan")


class Choice(Base):
    __tablename__ = "choices"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    choice_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    order_num = Column(Integer, default=0, nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="choices")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    attempt_number = Column(Integer, default=1, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent = Column(Integer, default=0, comment="소요 시간(초)")
    score = Column(Integer, default=0, comment="점수(0-100)")
    passed = Column(Boolean, default=False)
    status = Column(String(20), default="in_progress", 
                   comment="'in_progress', 'completed', 'abandoned', 'graded'")
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User")
    answers = relationship("QuestionAnswer", back_populates="attempt", cascade="all, delete-orphan")


class QuestionAnswer(Base):
    __tablename__ = "question_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    answer_data = Column(JSON, comment="질문 유형에 따른 답변 데이터")
    is_correct = Column(Boolean, nullable=True)
    points_awarded = Column(Integer, default=0, nullable=False)
    feedback = Column(Text, nullable=True)
    graded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    graded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    grader = relationship("User", foreign_keys=[graded_by])


class UserQuizProgress(Base):
    __tablename__ = "user_quiz_progress"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), primary_key=True)
    completed_attempts = Column(Integer, default=0, nullable=False)
    best_score = Column(Integer, default=0, nullable=False)
    passed = Column(Boolean, default=False)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="quiz_progress")
    quiz = relationship("Quiz")
