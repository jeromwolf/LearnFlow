# 스키마 패키지 초기화 파일

# 사용자 관련 스키마
from .user import User, UserCreate, UserInDB, UserUpdate, UserInToken, UserRole, UserResponse

# 토큰 관련 스키마
from .token import Token, TokenPayload, RefreshToken

# 콘텐츠 관련 스키마
from .content import (
    Content, ContentCreate, ContentUpdate, ContentInDB, ContentResponse,
    Section, SectionCreate, SectionUpdate, SectionInDB, SectionResponse,
    Course, CourseCreate, CourseUpdate, CourseInDB, CourseResponse,
    Category, CategoryCreate, CategoryUpdate, CategoryInDB, CategoryResponse,
    UserContentProgress, UserContentProgressCreate, UserContentProgressUpdate, UserContentProgressResponse
)

# 퀴즈 관련 스키마
from .quiz import (
    Quiz, QuizCreate, QuizUpdate, QuizResponse, QuizListResponse,
    Question, QuestionCreate, QuestionUpdate, QuestionResponse,
    Choice, ChoiceCreate, ChoiceUpdate, ChoiceResponse,
    QuizAttempt, QuizAttemptCreate, QuizAttemptResponse, QuizAttemptSubmit,
    QuestionAnswer, QuestionAnswerCreate, QuestionAnswerUpdate, QuestionAnswerResponse,
    UserQuizProgress, UserQuizProgressResponse,
    QuizStatistics, QuizTakeResponse, QuizResultResponse,
    QuestionType, QuizAttemptStatus
)

# 모든 스키마를 한 곳에서 임포트할 수 있도록 __all__ 정의
__all__ = [
    # 사용자
    'User', 'UserCreate', 'UserInDB', 'UserUpdate', 'UserInToken', 'UserRole', 'UserResponse',
    
    # 토큰
    'Token', 'TokenPayload', 'RefreshToken',
    
    # 콘텐츠
    'Content', 'ContentCreate', 'ContentUpdate', 'ContentInDB', 'ContentResponse',
    'Section', 'SectionCreate', 'SectionUpdate', 'SectionInDB', 'SectionResponse',
    'Course', 'CourseCreate', 'CourseUpdate', 'CourseInDB', 'CourseResponse',
    'Category', 'CategoryCreate', 'CategoryUpdate', 'CategoryInDB', 'CategoryResponse',
    'UserContentProgress', 'UserContentProgressCreate', 'UserContentProgressUpdate', 'UserContentProgressResponse',
    
    # 퀴즈
    'Quiz', 'QuizCreate', 'QuizUpdate', 'QuizResponse', 'QuizListResponse',
    'Question', 'QuestionCreate', 'QuestionUpdate', 'QuestionResponse',
    'Choice', 'ChoiceCreate', 'ChoiceUpdate', 'ChoiceResponse',
    'QuizAttempt', 'QuizAttemptCreate', 'QuizAttemptResponse', 'QuizAttemptSubmit',
    'QuestionAnswer', 'QuestionAnswerCreate', 'QuestionAnswerUpdate', 'QuestionAnswerResponse',
    'UserQuizProgress', 'UserQuizProgressResponse',
    'QuizStatistics', 'QuizTakeResponse', 'QuizResultResponse',
    'QuestionType', 'QuizAttemptStatus'
]
