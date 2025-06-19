import os
from pydantic_settings import BaseSettings
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, validator, PostgresDsn, Field, field_validator


class Settings(BaseSettings):
    # API 설정
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LearnFlow"
    
    # JWT 설정
    SECRET_KEY: str = Field(
        default="your-secret-key-here-please-change-in-production",
        description="JWT 서명에 사용되는 시크릿 키. 안전한 랜덤 문자열로 변경해야 합니다."
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7일
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30일
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        AnyHttpUrl("http://localhost:3000"),  # 프론트엔드 개발 서버
        AnyHttpUrl("http://localhost:8000"),  # 백엔드 개발 서버
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[AnyHttpUrl]:
        if isinstance(v, str) and not v.startswith("["):
            return [AnyHttpUrl(i.strip()) for i in v.split(",")]
        elif isinstance(v, list):
            return [AnyHttpUrl(url) if isinstance(url, str) else url for url in v]
        raise ValueError(v)

    # 데이터베이스 설정 (Supabase)
    SUPABASE_URL: str = Field(..., description="Supabase 프로젝트 URL")
    SUPABASE_KEY: str = Field(..., description="Supabase anon/public 키")
    SUPABASE_JWT_SECRET: str = Field(..., description="JWT 시크릿 (Supabase 설정에서 확인 가능)")
    
    # 데이터베이스 연결 (Supabase PostgreSQL)
    POSTGRES_SERVER: str = Field(..., description="PostgreSQL 서버 주소")
    POSTGRES_USER: str = Field(..., description="PostgreSQL 사용자 이름")
    POSTGRES_PASSWORD: str = Field(..., description="PostgreSQL 비밀번호")
    POSTGRES_DB: str = Field(..., description="PostgreSQL 데이터베이스 이름")
    
    # SQLAlchemy 데이터베이스 URL (자동 생성)
    SQLALCHEMY_DATABASE_URI: Optional[Union[PostgresDsn, str]] = None
    
    # Redis 설정
    REDIS_URL: str = Field("redis://localhost:6379/0", 
                         description="Redis 서버 URL (예: redis://:password@localhost:6379/0)")
    REDIS_PASSWORD: Optional[str] = Field(
        None, 
        description="Redis 서버 비밀번호 (URL에 포함된 경우 생략 가능)"
    )
    REDIS_DB: int = Field(0, description="사용할 Redis 데이터베이스 번호")
    
    # Test mode flag
    TESTING: bool = False

    @field_validator("SQLALCHEMY_DATABASE_URI", mode='before')
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        # If in test mode, return SQLite URL directly
        if os.getenv("TESTING") == "1":
            return "sqlite:///./test.db"
            
        # For non-test environments, use PostgreSQL
        if isinstance(v, str):
            return v
            
        # Build PostgreSQL URL from components
        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # 이메일 설정 (선택 사항)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_TEMPLATES_DIR: str = "/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    # 개발 및 테스트 설정
    DEBUG: bool = False
    TESTING: bool = False
    
    # 첫 번째 관리자 계정 (선택 사항, 초기 설정 시 사용)
    FIRST_SUPERUSER_EMAIL: Optional[EmailStr] = None
    FIRST_SUPERUSER_PASSWORD: Optional[str] = None
    FIRST_SUPERUSER_USERNAME: Optional[str] = "admin"
    
    # 사용자 등록 허용 여부
    USERS_OPEN_REGISTRATION: bool = True
    
    # 세션 설정
    SESSION_COOKIE_SECURE: bool = Field(
        default=not DEBUG,
        description="세션 쿠키에 Secure 플래그 사용 여부 (HTTPS에서만 전송)"
    )
    SESSION_COOKIE_HTTPONLY: bool = Field(
        default=True,
        description="JavaScript에서 세션 쿠키 접근 방지"
    )
    SESSION_COOKIE_SAMESITE: str = Field(
        default="lax",
        description="SameSite 쿠키 정책 (lax, strict, none)"
    )
    
    # 보안 헤더 설정
    SECURE_HSTS_SECONDS: int = Field(
        default=31536000,  # 1년
        description="HSTS 헤더의 max-age 값(초)"
    )
    SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = Field(
        default=True,
        description="HSTS 헤더에 includeSubDomains 지시어 포함 여부"
    )
    SECURE_HSTS_PRELOAD: bool = Field(
        default=False,
        description="HSTS 헤더에 preload 지시어 포함 여부"
    )
    SECURE_REFERRER_POLICY: str = Field(
        default="same-origin",
        description="Referrer-Policy 헤더 값"
    )
    SECURE_CONTENT_TYPE_NOSNIFF: bool = Field(
        default=True,
        description="X-Content-Type-Options: nosniff 헤더 사용 여부"
    )
    SECURE_BROWSER_XSS_FILTER: bool = Field(
        default=True,
        description="X-XSS-Protection: 1; mode=block 헤더 사용 여부"
    )
    SECURE_CROSS_ORIGIN_OPENER_POLICY: str = Field(
        default="same-origin",
        description="Cross-Origin-Opener-Policy 헤더 값"
    )
    
    # CORS 설정
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="자격 증명(쿠키, 인증 헤더 등)을 허용할지 여부"
    )
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["*"],
        description="허용할 HTTP 메서드 목록"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"],
        description="허용할 HTTP 헤더 목록"
    )
    CORS_EXPOSE_HEADERS: List[str] = Field(
        default=[],
        description="클라이언트에 노출할 헤더 목록"
    )
    CORS_MAX_AGE: int = Field(
        default=600,
        description="preflight 요청 결과를 캐시할 시간(초)"
    )

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스
settings = Settings()
