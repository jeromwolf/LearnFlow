from fastapi import APIRouter
from app.api.v1.endpoints import boards, posts, comments, auth, courses, contents, quiz

api_router = APIRouter()

# 인증 관련 라우터
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 게시판 관련 라우터
api_router.include_router(boards.router, prefix="/boards", tags=["게시판"])
api_router.include_router(posts.router, prefix="/posts", tags=["게시글"])
api_router.include_router(comments.router, prefix="/comments", tags=["댓글"])

# 강의 관리 관련 라우터
api_router.include_router(courses.router, prefix="/courses", tags=["강의 관리"])

# 콘텐츠 관리 관련 라우터
api_router.include_router(contents.router, prefix="", tags=["콘텐츠 관리"])

# 퀴즈/테스트 관련 라우터
api_router.include_router(quiz.router, prefix="", tags=["퀴즈/테스트 관리"])
