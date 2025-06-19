"""
Redis 클라이언트 유틸리티 모듈입니다.

이 모듈은 Redis 연결을 관리하고 재사용 가능한 Redis 클라이언트를 제공합니다.
"""
import logging
from typing import Optional

import redis
from redis.asyncio import Redis as AsyncRedis

from app.core.config import settings

# 전역 Redis 클라이언트 인스턴스
redis_client: Optional[redis.Redis] = None
async_redis_client: Optional[AsyncRedis] = None


def init_redis() -> None:
    """Redis 클라이언트를 초기화합니다."""
    global redis_client, async_redis_client
    
    if not settings.REDIS_URL:
        logging.warning("REDIS_URL이 설정되지 않아 Redis를 사용할 수 없습니다.")
        return
    
    try:
        # 동기식 Redis 클라이언트
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
        
        # 비동기식 Redis 클라이언트
        async_redis_client = AsyncRedis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
        
        # 연결 테스트
        redis_client.ping()
        logging.info("Redis 클라이언트가 성공적으로 초기화되었습니다.")
        
    except Exception as e:
        logging.error(f"Redis 연결 중 오류가 발생했습니다: {e}")
        redis_client = None
        async_redis_client = None


def get_redis() -> redis.Redis:
    """Redis 클라이언트를 반환합니다.
    
    Returns:
        redis.Redis: Redis 클라이언트 인스턴스
        
    Raises:
        RuntimeError: Redis가 초기화되지 않은 경우
    """
    if redis_client is None:
        raise RuntimeError("Redis 클라이언트가 초기화되지 않았습니다.")
    return redis_client


async def get_async_redis() -> AsyncRedis:
    """비동기 Redis 클라이언트를 반환합니다.
    
    Returns:
        AsyncRedis: 비동기 Redis 클라이언트 인스턴스
        
    Raises:
        RuntimeError: Redis가 초기화되지 않은 경우
    """
    if async_redis_client is None:
        raise RuntimeError("비동기 Redis 클라이언트가 초기화되지 않았습니다.")
    return async_redis_client


def close_redis() -> None:
    """Redis 연결을 안전하게 종료합니다."""
    global redis_client, async_redis_client
    
    if redis_client:
        redis_client.close()
        redis_client = None
    
    if async_redis_client:
        async_redis_client.close()
        async_redis_client = None


# 애플리케이션 시작 시 Redis 초기화
if settings.REDIS_URL:
    init_redis()
