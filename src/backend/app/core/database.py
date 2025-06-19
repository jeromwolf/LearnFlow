"""
데이터베이스 연결 및 세션 관리를 위한 모듈입니다.

SQLAlchemy와 Supabase를 사용하여 데이터베이스와 상호작용합니다.
"""
import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import StaticPool

# Import appropriate settings based on environment
if os.getenv("TESTING"):
    from app.core.test_settings import test_settings as settings
else:
    from app.core.config import settings

# Import Base and metadata from db.base
from app.db.base import Base, metadata  # noqa: F401

# 전역 변수
engine: Optional[Engine] = None
SessionLocal: Optional[scoped_session] = None
supabase_client = None


def get_engine() -> Engine:
    """데이터베이스 엔진을 생성하고 반환합니다.

    환경에 따라 SQLite 또는 PostgreSQL 엔진을 반환합니다.

    Returns:
        Engine: SQLAlchemy 엔진 인스턴스
    """
    global engine

    if engine is not None:
        return engine

    # SQLite를 사용하는 경우 (개발용)
    db_uri = settings.SQLALCHEMY_DATABASE_URI
    if db_uri and db_uri.startswith("sqlite"):
        engine = create_engine(
            db_uri,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.DEBUG,
        )
    # PostgreSQL을 사용하는 경우 (운영 환경)
    else:
        engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            pool_pre_ping=True,
            pool_recycle=settings.SQLALCHEMY_POOL_RECYCLE,
            pool_size=settings.SQLALCHEMY_POOL_SIZE,
            max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
            pool_timeout=settings.SQLALCHEMY_POOL_TIMEOUT,
            echo=settings.DEBUG,
        )

    return engine


def get_session() -> scoped_session:
    """세션 팩토리를 반환합니다.

    Returns:
        scoped_session: 스레드 로컬 세션 팩토리
    """
    global SessionLocal

    if SessionLocal is None:
        SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=get_engine(),
            )
        )

    return SessionLocal


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """의존성 주입을 위한 DB 세션 컨텍스트 매니저입니다.

    FastAPI 의존성 주입에 사용됩니다.

    Yields:
        Session: 데이터베이스 세션

    Example:
        ```python
        from fastapi import Depends
        from app.core.database import get_db

        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
        ```
    """
    session = get_session()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_supabase() -> None:
    """Supabase 클라이언트를 초기화합니다.

    Supabase를 사용하는 경우, 이 함수를 호출하여 클라이언트를 초기화합니다.
    """
    global supabase_client

    supabase_url = settings.SUPABASE_URL
    supabase_key = settings.SUPABASE_KEY

    if not supabase_url or not supabase_key:
        print("Supabase URL 또는 키가 설정되어 있지 않습니다.")
        return

    try:
        # Lazy import to avoid requiring supabase package
        from supabase import create_client  # type: ignore

        supabase_client = create_client(
            supabase_url,  # type: ignore
            supabase_key  # type: ignore
        )
    except ImportError:
        print("Supabase 패키지가 설치되어 있지 않습니다. pip install supabase로 설치해주세요.")


def init_db() -> None:
    """데이터베이스 테이블을 생성합니다.

    애플리케이션 시작 시 한 번 호출되어야 합니다.
    """
    # 모델을 등록하기 위해 임포트
    import app.models  # noqa: F401

    # 테이블 생성
    Base.metadata.create_all(bind=get_engine())


@contextmanager
def get_test_db() -> Generator[Session, None, None]:
    """테스트를 위한 DB 세션을 생성합니다.

    테스트 시 메모리 내 SQLite 데이터베이스를 사용합니다.

    Yields:
        Session: 테스트용 데이터베이스 세션
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # 메모리 SQLite 데이터베이스 사용
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 테이블 생성
    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


def setup_database() -> None:
    """데이터베이스 설정을 초기화합니다.

    애플리케이션 시작 시 호출되어야 합니다.
    """
    get_engine()
    get_session()
    init_supabase()
    init_db()
