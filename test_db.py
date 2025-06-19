import os
import sys
from sqlalchemy import create_engine

# 환경 변수에서 데이터베이스 URL 가져오기
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:uzFqtXBEnv7z19sv@fmxaeivobwmhjrpazkxk.supabase.co:5432/postgres')

try:
    print(f"Connecting to database: {DATABASE_URL.split('@')[-1]}")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("Connection successful!")
        print(f"Test query result: {result.scalar()}")
except Exception as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)
