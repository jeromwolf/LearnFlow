"""
JWT 토큰 블랙리스트 모델입니다.

이 모듈은 폐기된 JWT 토큰을 추적하기 위한 데이터베이스 모델을 정의합니다.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, func, Index

from app.core.database import Base


class TokenBlacklist(Base):
    """JWT 토큰 블랙리스트 모델입니다.
    
    이 모델은 폐기된 JWT 토큰을 추적하여 재사용을 방지합니다.
    """
    __tablename__ = "token_blacklist"
    
    id = Column(String, primary_key=True, index=True, comment="고유 ID")
    token = Column(Text, nullable=False, index=True, comment="블랙리스트된 토큰")
    jti = Column(String, index=True, comment="JWT ID (JTI)")
    user_id = Column(String, index=True, comment="사용자 ID")
    token_type = Column(String(20), default="access", comment="토큰 유형 (access, refresh, etc.)")
    reason = Column(Text, nullable=True, comment="블랙리스트 사유")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="생성 일시")
    expires_at = Column(DateTime, nullable=False, index=True, comment="만료 일시")
    
    # 복합 인덱스
    __table_args__ = (
        Index('idx_token_blacklist_user_token_type', 'user_id', 'token_type'),
    )
    
    def __repr__(self) -> str:
        return f"<TokenBlacklist {self.id} user={self.user_id} type={self.token_type}>"
    
    def to_dict(self) -> dict:
        """객체를 딕셔너리로 변환합니다."""
        return {
            "id": self.id,
            "jti": self.jti,
            "user_id": self.user_id,
            "token_type": self.token_type,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
