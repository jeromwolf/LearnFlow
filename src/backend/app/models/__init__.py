# Import Base and metadata from db.base
from app.db.base import Base, metadata  # noqa: F401

# Import all models to ensure they are registered with the Base
from .user import User, UserRoleEnum, RefreshToken, Role  # noqa: E402, F401
from .content import Content, Section, Course, Category, UserContentProgress  # noqa: E402, F401
from .quiz import Quiz, Question, Choice, QuizAttempt, QuestionAnswer, UserQuizProgress  # noqa: E402, F401

# 모든 모델을 한 번에 임포트할 수 있도록 __all__ 정의
__all__ = [
    'Base', 'metadata',
    'User', 'UserRoleEnum', 'RefreshToken', 'Role',
    'Content', 'Section', 'Course', 'Category', 'UserContentProgress',
    'Quiz', 'Question', 'Choice', 'QuizAttempt', 'QuestionAnswer', 'UserQuizProgress'
]
