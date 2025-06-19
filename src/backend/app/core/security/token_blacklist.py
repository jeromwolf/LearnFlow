"""
JWT 토큰 블랙리스트 관리를 위한 모듈입니다.

이 모듈은 폐기된 JWT 토큰을 추적하고 검증하는 기능을 제공합니다.
"""
import time
from datetime import datetime, timedelta
from typing import Optional, Set, Tuple

from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis import redis_client
from app.models.token_blacklist import TokenBlacklist

# 인메모리 블랙리스트 (서버 재시작 시 초기화됨)
_memory_blacklist: Set[str] = set()


def add_to_blacklist(
    token: str,
    db: Session,
    expires_at: Optional[datetime] = None,
    reason: Optional[str] = None,
) -> None:
    """토큰을 블랙리스트에 추가합니다.
    
    Args:
        token: 블랙리스트에 추가할 JWT 토큰
        db: 데이터베이스 세션
        expires_at: 토큰 만료 시간 (기본값: 토큰의 exp 클레임 또는 24시간 후)
        reason: 블랙리스트에 추가된 이유 (선택 사항)
    """
    try:
        # 토큰에서 페이로드 추출 (검증 없이 디코딩)
        payload = jwt.get_unverified_claims(token)
        
        # 만료 시간 설정
        if not expires_at:
            if "exp" in payload:
                expires_at = datetime.utcfromtimestamp(payload["exp"])
            else:
                expires_at = datetime.utcnow() + timedelta(days=1)
        
        # Redis에 저장 (만료 시간 설정)
        if redis_client:
            redis_key = f"token_blacklist:{token}"
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                redis_client.setex(redis_key, ttl, reason or "")
        
        # 데이터베이스에 저장 (감사 목적)
        db_token = TokenBlacklist(
            token=token,
            expires_at=expires_at,
            reason=reason,
            jti=payload.get("jti"),
            user_id=payload.get("sub"),
            token_type=payload.get("type", "access"),
        )
        db.add(db_token)
        db.commit()
        
        # 인메모리 블랙리스트에도 추가 (서버 재시작 시 초기화됨)
        _memory_blacklist.add(token)
        
    except Exception as e:
        db.rollback()
        # 로깅은 상위 레이어에서 처리
        raise


def is_token_blacklisted(token: str, db: Session) -> Tuple[bool, Optional[str]]:
    """토큰이 블랙리스트에 있는지 확인합니다.
    
    Args:
        token: 확인할 JWT 토큰
        db: 데이터베이스 세션
        
    Returns:
        Tuple[bool, Optional[str]]: (블랙리스트 여부, 사유)
    """
    # 인메모리 블랙리스트 확인 (빠른 확인)
    if token in _memory_blacklist:
        return True, "Token is blacklisted (in-memory)"
    
    # Redis 확인
    if redis_client:
        redis_key = f"token_blacklist:{token}"
        reason = redis_client.get(redis_key)
        if reason is not None:
            # Redis에 있으면 인메모리 블랙리스트에도 추가
            _memory_blacklist.add(token)
            return True, reason.decode() if reason else "Token is blacklisted (Redis)"
    
    # 데이터베이스 확인 (최후의 수단)
    db_token = db.query(TokenBlacklist).filter(
        TokenBlacklist.token == token,
        TokenBlacklist.expires_at > datetime.utcnow()
    ).first()
    
    if db_token:
        # 데이터베이스에 있으면 Redis와 인메모리 블랙리스트에도 추가
        if redis_client:
            ttl = int((db_token.expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                redis_key = f"token_blacklist:{token}"
                redis_client.setex(redis_key, ttl, db_token.reason or "")
        _memory_blacklist.add(token)
        return True, db_token.reason or "Token is blacklisted (database)"
    
    return False, None


def cleanup_expired_tokens(db: Session) -> int:
    """만료된 토큰을 정리합니다.
    
    Args:
        db: 데이터베이스 세션
        
    Returns:
        int: 삭제된 토큰 수
    """
    # 데이터베이스에서 만료된 토큰 삭제
    result = db.query(TokenBlacklist).filter(
        TokenBlacklist.expires_at <= datetime.utcnow()
    ).delete()
    db.commit()
    
    # Redis에서 만료된 토큰은 자동으로 삭제됨 (TTL 기반)
    
    return result
