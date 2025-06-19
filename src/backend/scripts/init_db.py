#!/usr/bin/env python3
"""
데이터베이스 초기화 및 관리 스크립트

사용법:
    python -m scripts.init_db          # 데이터베이스 초기화
    python -m scripts.init_db --drop    # 기존 테이블 삭제 후 초기화
"""
import argparse
import logging
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 시스템 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from sqlalchemy_utils import database_exists, create_database, drop_database

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.models.user import User, Role, user_roles, RefreshToken
from app.models.post import Post, Comment, Like, Bookmark, Board
from app.core.security import get_password_hash

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(drop_all: bool = False) -> None:
    """데이터베이스를 초기화합니다.
    
    Args:
        drop_all: True인 경우 기존 테이블을 모두 삭제합니다.
    """
    db_url = str(settings.SQLALCHEMY_DATABASE_URI)
    
    # 데이터베이스가 없으면 생성
    if not database_exists(db_url):
        logger.info(f"Creating database: {db_url}")
        create_database(db_url)
    
    # 기존 테이블 삭제 옵션
    if drop_all:
        logger.warning("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
    
    # 테이블 생성
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    # 초기 데이터 삽입
    logger.info("Inserting initial data...")
    db = SessionLocal()
    
    try:
        # 기본 역할 추가
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(
                id="role_admin",
                name="admin",
                description="시스템 관리자",
                permissions={
                    "users": ["read", "create", "update", "delete"],
                    "posts": ["read", "create", "update", "delete", "moderate"],
                    "comments": ["read", "create", "update", "delete", "moderate"],
                    "boards": ["read", "create", "update", "delete"],
                }
            )
            db.add(admin_role)
            db.commit()
            logger.info("Created admin role")
        
        user_role = db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            user_role = Role(
                id="role_user",
                name="user",
                description="일반 사용자",
                permissions={
                    "users": ["read"],
                    "posts": ["read", "create", "update_own", "delete_own"],
                    "comments": ["read", "create", "update_own", "delete_own"],
                    "boards": ["read"],
                }
            )
            db.add(user_role)
            db.commit()
            logger.info("Created user role")
        
        # 관리자 사용자 추가 (환경변수에서 가져옴)
        if settings.FIRST_SUPERUSER_EMAIL and settings.FIRST_SUPERUSER_PASSWORD:
            admin = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
            if not admin:
                admin = User(
                    id="user_admin_1",  # 실제로는 UUID를 생성하는 것이 좋음
                    email=settings.FIRST_SUPERUSER_EMAIL,
                    username=settings.FIRST_SUPERUSER_USERNAME or "admin",
                    full_name="관리자",
                    hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                    is_active=True,
                    is_verified=True,
                    is_superuser=True,
                )
                admin.roles.append(admin_role)
                db.add(admin)
                db.commit()
                logger.info(f"Created admin user: {settings.FIRST_SUPERUSER_EMAIL}")
        
        # 테스트 게시판 추가
        board = db.query(Board).filter(Board.name == "자유게시판").first()
        if not board:
            board = Board(
                id="board_1",
                name="자유게시판",
                description="자유롭게 글을 작성할 수 있는 게시판입니다.",
                is_active=True,
                order=1,
            )
            db.add(board)
            db.commit()
            logger.info("Created default board")
        
        db.commit()
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="데이터베이스 초기화 스크립트")
    parser.add_argument(
        "--drop", 
        action="store_true", 
        help="기존 테이블을 모두 삭제하고 초기화합니다."
    )
    args = parser.parse_args()
    
    init_db(drop_all=args.drop)
