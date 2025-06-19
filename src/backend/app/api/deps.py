"""
API 엔드포인트에서 사용할 의존성 주입 함수들을 정의합니다.
"""
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, Role
from app.schemas.user import UserInToken, TokenData

# OAuth2 스키마 설정 (토큰이 필요할 때 사용)
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    현재 인증된 사용자를 가져오는 의존성 함수입니다.
    
    Args:
        db: 데이터베이스 세션
        token: JWT 액세스 토큰
        
    Returns:
        User: 인증된 사용자 객체
        
    Raises:
        HTTPException: 인증에 실패한 경우 401 에러 반환
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # JWT 토큰 검증
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenData(**payload)
        
        # 사용자 조회
        user = db.query(User).filter(User.id == token_data.sub).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        # 사용자 활성화 여부 확인
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비활성화된 사용자입니다."
            )
            
        return user
        
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="유효하지 않은 인증 정보입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """활성화된 사용자만 허용하는 의존성 함수입니다."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 사용자입니다.")
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """슈퍼유저만 허용하는 의존성 함수입니다."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, 
            detail="권한이 없습니다. 관리자 계정이 필요합니다."
        )
    return current_user


def has_permission(permission: str, resource: str):
    """
    사용자에게 특정 리소스에 대한 권한이 있는지 확인하는 의존성 함수입니다.
    
    Args:
        permission: 확인할 권한 (예: 'read', 'write', 'delete')
        resource: 리소스 이름 (예: 'users', 'posts')
        
    Returns:
        Callable: 권한 검사 의존성 함수
    """
    def _check_permission(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        # 슈퍼유저는 모든 권한 보유
        if current_user.is_superuser:
            return current_user
            
        # 사용자 역할에서 권한 확인
        for role in current_user.roles:
            if resource in role.permissions:
                if permission in role.permissions[resource]:
                    return current_user
                
        # 권한이 없는 경우
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"'{resource}' 리소스에 대한 '{permission}' 권한이 없습니다."
        )
    
    return _check_permission
