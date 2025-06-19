"""
Password hashing and verification utilities.
"""
from typing import Optional, Tuple, Union

from passlib.context import CryptContext

# 비밀번호 해싱을 위한 컨텍스트 - Argon2 권장 (설치 필요: pip install argon2-cffi)
try:
    pwd_context = CryptContext(
        schemes=["argon2", "bcrypt"],
        deprecated="auto",
        argon2__time_cost=3,  # 조정 가능 (시간 복잡도, 높을수록 안전하지만 느려짐)
        argon2__memory_cost=65536,  # 64MB (메모리 사용량, 높을수록 안전하지만 메모리 사용량 증가)
        argon2__parallelism=4,  # 병렬 처리 수
        argon2__hash_len=32,  # 해시 길이 (바이트)
    )
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Argon2를 사용할 수 없어 bcrypt로 대체합니다: {e}")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
            return False
            
        # 비밀번호 검증
        if salt:
            to_verify = f"{plain_password}:{salt}"
            is_valid = pwd_context.verify(to_verify, hashed_password)
        else:
            is_valid = pwd_context.verify(plain_password, hashed_password)
        
        return is_valid
        
    except Exception:
        return False
