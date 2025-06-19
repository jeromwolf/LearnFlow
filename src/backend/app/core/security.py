"""
보안 관련 유틸리티 함수들을 포함합니다.
JWT 토큰 생성/검증, 인증 관련 기능을 제공합니다.
"""

import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, Union

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import redis_client
from app.models.token_blacklist import TokenBlacklist
from app.models.user import User
from app.utils.password import verify_password, get_password_hash

# 로깅 설정
logger = logging.getLogger(__name__)

# 보안 이벤트 로깅
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# OAuth2 스키마 설정
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scopes={
        "me": "사용자 자신의 정보를 읽을 수 있는 권한",
        "items": "아이템을 생성하고 관리할 수 있는 권한",
        "admin": "관리자 권한",
    },
    auto_error=False,
)

# 토큰 블랙리스트 캐시 (메모리 내)
_token_blacklist_cache = set()


class TokenData(BaseModel):
    """토큰에 포함될 데이터 모델"""

    sub: str  # 사용자 식별자 (일반적으로 사용자 ID)
    scopes: list[str] = []  # 토큰의 스코프 목록
    jti: str  # JWT ID (고유 식별자)
    type: str = "access"  # 토큰 유형 (access, refresh, etc.)
    exp: datetime  # 만료 시간
    iat: datetime  # 발급 시간
    nbf: Optional[datetime] = None  # Not Before (이 시간 이전에는 사용 불가)

    class Config:
        json_encoders = {datetime: lambda v: int(v.timestamp())}  # 타임스탬프로 직렬화


def generate_salt(length: int = 16) -> str:
    """보안에 강한 랜덤 솔트를 생성합니다.

    Args:
        length: 솔트 길이 (바이트)

    Returns:
        str: 16진수로 인코딩된 솔트 문자열
    """
    return secrets.token_hex(length)


def generate_secure_password(length: int = 16) -> str:
    """보안에 강한 랜덤 비밀번호를 생성합니다.

    Args:
        length: 비밀번호 길이

    Returns:
        str: 생성된 비밀번호
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        # 최소 하나의 소문자, 대문자, 숫자, 특수문자 포함 확인
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*" for c in password)
        ):
            return password


def get_password_hash(password: str, salt: Optional[str] = None) -> Union[str, Tuple[str, str]]:
    """비밀번호를 해시합니다.

    Args:
        password: 해시할 평문 비밀번호
        salt: 사용할 솔트 (None이면 새로 생성)

    Returns:
        str: salt가 None인 경우 해시된 비밀번호
        Tuple[str, str]: salt가 주어진 경우 (해시된 비밀번호, 사용된 솔트)
    """
    if salt is None:
        # salt 없이 단순 해시 (기본 사용)
        return pwd_context.hash(password)
    
    # salt와 함께 해시 (레거시 호환용)
    to_hash = f"{password}:{salt}"
    hashed = pwd_context.hash(to_hash)
    return hashed, salt


def verify_password(plain_password: str, hashed_password: str, salt: Optional[str] = None) -> bool:
    """평문 비밀번호와 해시된 비밀번호가 일치하는지 확인합니다.

    Args:
        plain_password: 검증할 평문 비밀번호
        hashed_password: 저장된 해시된 비밀번호
        salt: 비밀번호에 사용된 솔트 (선택사항, 레거시 호환용)

    Returns:
        bool: 비밀번호가 일치하면 True, 아니면 False
    """
    if not all([plain_password, hashed_password]):
        return False
    
    try:
        # 저장된 해시 형식이 유효한지 확인
        if not pwd_context.identify(hashed_password):
            security_logger.warning("잘못된 비밀번호 해시 형식")
            return False
            
        # 비밀번호 검증
        if salt:
            to_verify = f"{plain_password}:{salt}"
            is_valid = pwd_context.verify(to_verify, hashed_password)
        else:
            is_valid = pwd_context.verify(plain_password, hashed_password)
        
        # 검증 실패 시 로깅 (보안 로그에만 기록)
        if not is_valid:
            security_logger.warning("잘못된 비밀번호 시도")
        
        return is_valid
        
    except Exception as e:
        # 예상치 못한 오류 로깅
        security_logger.error(f"비밀번호 검증 중 오류: {e}", exc_info=True)
        return False


def create_jwt_token(
    subject: str,
    token_type: str = "access",
    expires_delta: Optional[timedelta] = None,
    scopes: Optional[list[str]] = None,
    jti: Optional[str] = None,
    **extra_data: Any,
) -> Tuple[str, dict]:
    """JWT 토큰을 생성합니다.

    Args:
        subject: 토큰 주제 (일반적으로 사용자 ID)
        token_type: 토큰 유형 (access, refresh 등)
        expires_delta: 토큰 만료 기간 (기본값: 토큰 유형에 따라 다름)
        scopes: 토큰의 권한 범위
        jti: JWT ID (None이면 자동 생성)
        **extra_data: 추가로 인코딩할 데이터

    Returns:
        Tuple[str, dict]: (인코딩된 JWT 토큰, 토큰 클레임)
    """
    now = datetime.utcnow()

    # 토큰 만료 시간 설정
    if not expires_delta:
        if token_type == "refresh":
            expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        else:  # access token
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = now + expires_delta

    # JWT ID 생성 (없는 경우)
    if not jti:
        jti = secrets.token_urlsafe(32)

    # 기본 클레임
    to_encode = {
        "iss": settings.PROJECT_NAME,  # 발급자
        "sub": str(subject),  # 주제 (사용자 ID)
        "exp": expire,  # 만료 시간
        "iat": now,  # 발급 시간
        "nbf": now,  # Not Before (이 시간 이전에는 사용 불가)
        "jti": jti,  # JWT ID
        "type": token_type,  # 토큰 유형
        "scopes": scopes or [],  # 스코프
        "version": "1.0",  # 토큰 버전 (향후 호환성을 위해)
        **extra_data,  # 추가 클레임
    }

    # 토큰 서명
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    # 보안 로깅 (민감한 정보는 제외)
    security_logger.info(
        "JWT token created",
        extra={
            "event": "token_create",
            "token_type": token_type,
            "subject": subject,
            "expires_in": int(expires_delta.total_seconds()),
        },
    )

    return encoded_jwt, to_encode


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    scopes: Optional[list[str]] = None,
    **extra_data: Any,
) -> Tuple[str, dict]:
    """액세스 토큰을 생성합니다.

    Args:
        subject: 토큰 주제 (일반적으로 사용자 ID)
        expires_delta: 토큰 만료 기간 (기본값: 설정값 참조)
        scopes: 토큰의 권한 범위
        **extra_data: 추가로 인코딩할 데이터

    Returns:
        Tuple[str, dict]: (인코딩된 JWT 토큰, 토큰 클레임)
    """
    return create_jwt_token(
        subject=subject,
        token_type="access",
        expires_delta=expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        scopes=scopes,
        **extra_data,
    )


def create_refresh_token(
    subject: str, expires_delta: Optional[timedelta] = None, **extra_data: Any
) -> Tuple[str, dict]:
    """리프레시 토큰을 생성합니다.

    Args:
        subject: 토큰 주제 (일반적으로 사용자 ID)
        expires_delta: 토큰 만료 기간 (기본값: 설정값 참조)
        **extra_data: 추가로 인코딩할 데이터

    Returns:
        Tuple[str, dict]: (인코딩된 JWT 토큰, 토큰 클레임)
    """
    return create_jwt_token(
        subject=subject,
        token_type="refresh",
        expires_delta=expires_delta
        or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        scopes=["refresh_token"],
        **extra_data,
    )


def verify_token(
    token: str,
    expected_type: Optional[str] = None,
    required_scopes: Optional[list[str]] = None,
    request: Optional[Request] = None,
) -> Dict[str, Any]:
    """JWT 토큰을 검증하고 디코딩된 페이로드를 반환합니다.

    Args:
        token: 검증할 JWT 토큰
        expected_type: 예상되는 토큰 유형 (예: "access", "refresh")
        required_scopes: 필요한 스코프 목록
        request: 요청 객체 (로깅용)

    Returns:
        Dict[str, Any]: 디코딩된 토큰 페이로드

    Raises:
        HTTPException: 토큰이 유효하지 않은 경우
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 요청 정보 추출 (로깅용)
    client_ip = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None

    try:
        # 1. 토큰 디코딩
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_aud": False,  # aud 클레임 검증 비활성화
                "verify_iss": True,  # iss 클레임 검증 활성화
                "require_iat": True,  # iat 클레임 필수
                "require_exp": True,  # exp 클레임 필수
            },
            issuer=settings.PROJECT_NAME,  # 발급자 검증
        )

        # 2. 토큰 유형 검증
        if expected_type and payload.get("type") != expected_type:
            security_logger.warning(
                "Invalid token type",
                extra={
                    "event": "token_verify_failed",
                    "reason": f"Expected token type '{expected_type}', got '{payload.get('type')}'",
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                },
            )
            raise credentials_exception

        # 3. 스코프 검증
        if required_scopes:
            token_scopes = payload.get("scopes", [])
            for scope in required_scopes:
                if scope not in token_scopes:
                    security_logger.warning(
                        "Insufficient token scopes",
                        extra={
                            "event": "token_scope_mismatch",
                            "required_scope": scope,
                            "token_scopes": token_scopes,
                            "client_ip": client_ip,
                            "user_agent": user_agent,
                        },
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="권한이 없습니다.",
                        headers={"WWW-Authenticate": f'Bearer scope="{scope}"'},
                    )

        # 4. JTI 검증 (토큰 폐기 확인)
        jti = payload.get("jti")
        if jti and jti in _token_blacklist_cache:
            security_logger.warning(
                "Blacklisted token used",
                extra={
                    "event": "token_blacklisted",
                    "jti": jti,
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                },
            )
            raise credentials_exception

        # 5. 추가 검증 (예: 사용자 상태 확인 등)
        # 여기에 추가 검증 로직을 구현할 수 있습니다.

        # 성공 로깅
        security_logger.info(
            "Token verified successfully",
            extra={
                "event": "token_verified",
                "subject": payload.get("sub"),
                "token_type": payload.get("type"),
                "client_ip": client_ip,
                "user_agent": user_agent,
            },
        )

        return payload

    except JWTError as e:
        # 보안 로깅
        security_logger.warning(
            "Token verification failed",
            extra={
                "event": "token_verify_failed",
                "error": str(e),
                "client_ip": client_ip,
                "user_agent": user_agent,
            },
        )
        raise credentials_exception
    except Exception as e:
        # 예상치 못한 오류 처리
        security_logger.error(
            "Unexpected error during token verification",
            extra={
                "event": "token_verify_error",
                "error": str(e),
                "client_ip": client_ip,
                "user_agent": user_agent,
            },
            exc_info=True,
        )
        raise credentials_exception


def generate_password_reset_token(user_id: str, email: str) -> Tuple[str, dict]:
    """비밀번호 재설정을 위한 토큰을 생성합니다.

    Args:
        user_id: 사용자 ID
        email: 비밀번호를 재설정할 사용자 이메일

    Returns:
        Tuple[str, dict]: (인코딩된 JWT 토큰, 토큰 클레임)
    """
    # 고유한 JTI 생성
    jti = secrets.token_urlsafe(32)

    # 토큰 생성
    return create_jwt_token(
        subject=user_id,
        token_type="password_reset",
        expires_delta=timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS),
        jti=jti,
        email=email,
        scopes=["password_reset"],
    )


def verify_password_reset_token(token: str) -> Optional[dict]:
    """비밀번호 재설정 토큰을 검증하고 토큰 페이로드를 반환합니다.

    Args:
        token: 검증할 JWT 토큰

    Returns:
        Optional[dict]: 토큰이 유효하면 토큰 페이로드, 아니면 None
    """
    try:
        payload = verify_token(token, expected_type="password_reset")
        return payload
    except (JWTError, HTTPException):
        return None
    except Exception as e:
        security_logger.warning(
            "Error verifying password reset token",
            extra={"event": "password_reset_token_error", "error": str(e)},
        )
        return None


def get_password_hash(password: str) -> str:
    """비밀번호를 해시합니다.

    Args:
        password: 해시할 평문 비밀번호

    Returns:
        str: 해시된 비밀번호
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시된 비밀번호가 일치하는지 확인합니다.

    Args:
        plain_password: 검증할 평문 비밀번호
        hashed_password: 저장된 해시된 비밀번호

    Returns:
        bool: 비밀번호가 일치하면 True, 아니면 False
    """
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    request: Request,
    security_scopes: SecurityScopes,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """의존성 주입을 위한 현재 사용자 조회 함수

    Args:
        request: FastAPI 요청 객체
        security_scopes: 보안 스코프 (OAuth2)
        db: 데이터베이스 세션
        token: JWT 토큰

    Returns:
        User: 인증된 사용자 객체

    Raises:
        HTTPException: 인증 실패 시
    """
    if security_scopes.scopes:
        scope_str = " ".join(security_scopes.scope_str)
        authenticate_value = f'Bearer scope="{scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다.",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        # 1. 토큰 검증
        payload = verify_token(
            token,
            expected_type="access",
            required_scopes=security_scopes.scopes,
            request=request,
        )

        # 2. 사용자 ID 추출
        user_id: str = payload.get("sub")
        if not user_id:
            security_logger.warning(
                "Missing user ID in token",
                extra={"event": "invalid_token", "reason": "missing_sub"},
            )
            raise credentials_exception

        # 3. 사용자 조회
        user = crud.user.get(db, id=user_id)
        if not user:
            security_logger.warning(
                "User not found", extra={"event": "user_not_found", "user_id": user_id}
            )
            raise credentials_exception

        # 4. 계정 상태 확인
        if not user.is_active:
            security_logger.warning(
                "Inactive user attempted access",
                extra={"event": "inactive_user", "user_id": user_id},
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="계정이 비활성화되었습니다.",
                headers={"WWW-Authenticate": authenticate_value},
            )

        # 5. 토큰 JTI 검증 (토큰 폐기 확인)
        jti = payload.get("jti")
        if jti and jti in _token_blacklist_cache:
            security_logger.warning(
                "Blacklisted token used",
                extra={
                    "event": "token_blacklisted",
                    "jti": jti,
                    "user_id": user_id,
                    "client_ip": request.client.host,
                    "user_agent": request.headers.get("user-agent"),
                },
            )
            raise credentials_exception

        # 6. 보안 로깅
        security_logger.info(
            "User authenticated successfully",
            extra={
                "event": "user_authenticated",
                "user_id": user_id,
                "scopes": security_scopes.scopes,
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent"),
            },
        )

        return user

    except HTTPException as http_exc:
        # 이미 처리된 HTTP 예외는 그대로 전파
        raise http_exc
    except JWTError as e:
        security_logger.warning(
            "JWT validation failed",
            extra={
                "event": "jwt_validation_failed",
                "error": str(e),
                "client_ip": request.client.host if request else None,
                "user_agent": request.headers.get("user-agent") if request else None,
            },
        )
        raise credentials_exception
    except Exception as e:
        security_logger.error(
            "Unexpected error during authentication",
            extra={
                "event": "authentication_error",
                "error": str(e),
                "client_ip": request.client.host if request else None,
                "user_agent": request.headers.get("user-agent") if request else None,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="인증 처리 중 오류가 발생했습니다.",
            headers={"WWW-Authenticate": authenticate_value},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """활성 사용자만 반환하는 의존성 함수

    get_current_user에서 이미 활성 상태를 확인하므로 여기서는 단순히 사용자를 반환합니다.
    이 함수는 코드 가독성과 명확성을 위해 유지됩니다.

    Args:
        current_user: 현재 인증된 사용자

    Returns:
        User: 활성 사용자 객체
    """
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """슈퍼유저만 반환하는 의존성 함수

    Args:
        current_user: 현재 인증된 사용자

    Returns:
        User: 슈퍼유저 객체

    Raises:
        HTTPException: 사용자가 슈퍼유저가 아닌 경우
    """
    if not current_user.is_superuser:
        security_logger.warning(
            "Unauthorized admin access attempt",
            extra={
                "event": "unauthorized_admin_access",
                "user_id": current_user.id,
                "email": current_user.email,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="관리자 권한이 필요합니다."
        )
    return current_user
