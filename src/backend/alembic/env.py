import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import MetaData, engine_from_config, pool, create_engine
from alembic import context

# .env 파일에서 환경 변수 로드
load_dotenv()

# 프로젝트 루트 경로를 시스템 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 데이터베이스 모델 임포트
from models.user import Base as UserBase
from models.course import Base as CourseBase
from models.community import Base as CommunityBase

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 모든 모델의 메타데이터를 하나로 병합
target_metadata = MetaData()

# 모든 모델의 테이블을 타겟 메타데이터에 추가
for metadata in [UserBase.metadata, CourseBase.metadata, CommunityBase.metadata]:
    for table in metadata.tables.values():
        table.tometadata(target_metadata)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # 환경 변수에서 데이터베이스 URL 가져오기
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/learnflow")
    
    # 엔진 생성
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
