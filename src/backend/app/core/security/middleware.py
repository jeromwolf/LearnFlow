"""
보안 미들웨어 모듈입니다.

다양한 보안 관련 미들웨어를 제공합니다:
- Rate limiting
- Security headers
- CSRF protection
- Request ID tracking
"""
import time
import uuid
from typing import Callable, List, Optional, Tuple

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.config import settings

# Rate limiter 인스턴스 생성
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"],
)


def setup_security_middleware(app: FastAPI) -> None:
    """보안 미들웨어를 설정합니다.
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
    """
    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # CSRF protection
    app.add_middleware(CSRFProtectionMiddleware)
    
    # Request ID middleware
    app.add_middleware(RequestIDMiddleware)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        expose_headers=settings.CORS_EXPOSE_HEADERS,
        max_age=settings.CORS_MAX_AGE,
    )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더를 추가하는 미들웨어입니다."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        
        # Security headers 추가
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = settings.SECURE_REFERRER_POLICY
        response.headers["Cross-Origin-Opener-Policy"] = settings.SECURE_CROSS_ORIGIN_OPENER_POLICY
        
        # HSTS 헤더 (HTTPS인 경우에만 설정)
        if request.url.scheme == "https":
            hsts_value = f"max-age={settings.SECURE_HSTS_SECONDS}"
            if settings.SECURE_HSTS_INCLUDE_SUBDOMAINS:
                hsts_value += "; includeSubDomains"
            if settings.SECURE_HSTS_PRELOAD:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value
        
        return response


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF 보호를 위한 미들웨어입니다."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 안전한 메서드(GET, HEAD, OPTIONS, TRACE)는 CSRF 검증에서 제외
        if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            return await call_next(request)
        
        # API 요청의 경우 Content-Type이 application/json이어야 함
        content_type = request.headers.get("Content-Type", "")
        if not content_type.startswith("application/json"):
            return JSONResponse(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                content={"detail": "Unsupported Media Type: Must be application/json"},
            )
        
        # Origin/Referer 헤더 검증
        origin = request.headers.get("Origin")
        referer = request.headers.get("Referer")
        
        if not self._is_valid_origin(origin, referer, request):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF verification failed: Invalid Origin or Referer"},
            )
        
        return await call_next(request)
    
    def _is_valid_origin(self, origin: Optional[str], referer: Optional[str], request: Request) -> bool:
        """Origin/Referer 헤더가 유효한지 확인합니다."""
        # Origin/Referer가 없는 경우 (API 클라이언트 등)는 허용
        if not origin and not referer:
            return True
            
        # Origin 검증
        if origin:
            origin_url = origin.rstrip('/')
            if not any(
                str(allowed_origin).rstrip('/') == origin_url
                for allowed_origin in settings.BACKEND_CORS_ORIGINS
            ):
                return False
        
        # Referer 검증
        if referer:
            try:
                from urllib.parse import urlparse
                referer_url = urlparse(referer)
                referer_origin = f"{referer_url.scheme}://{referer_url.netloc}"
                
                if not any(
                    str(allowed_origin).rstrip('/') == referer_origin.rstrip('/')
                    for allowed_origin in settings.BACKEND_CORS_ORIGINS
                ):
                    return False
            except Exception:
                return False
        
        return True


class RequestIDMiddleware(BaseHTTPMiddleware):
    """요청 ID를 생성하고 헤더에 추가하는 미들웨어입니다."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 요청 ID 생성
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # 요청에 요청 ID 추가
        request.state.request_id = request_id
        
        # 응답 가져오기
        response = await call_next(request)
        
        # 응답 헤더에 요청 ID 추가
        response.headers["X-Request-ID"] = request_id
        
        return response
