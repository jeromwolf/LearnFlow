"""
API 엔드포인트 패키지 초기화 파일

이 패키지는 API 버전 1의 모든 엔드포인트 라우터를 포함합니다.
"""

# 라우터 임포트
from . import auth, boards, posts, comments, courses, contents, quiz

# 모든 라우터를 한 곳에서 임포트할 수 있도록 __all__ 정의
__all__ = [
    'auth',
    'boards',
    'posts',
    'comments',
    'courses',
    'contents',
    'quiz',
]
