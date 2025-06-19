from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="LearnFlow API 서버",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 적절한 도메인으로 제한하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """
    루트 엔드포인트
    
    API 서버가 정상적으로 실행 중임을 확인하는 용도로 사용됩니다.
    """
    return {
        "message": "LearnFlow API 서버가 정상적으로 실행 중입니다.",
        "docs": "/docs",
        "redoc": "/redoc",
    }
