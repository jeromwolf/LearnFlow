import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_connection():
    try:
        # 환경변수에서 데이터베이스 URL 가져오기
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("Error: DATABASE_URL not found in .env file")
            return False
            
        print(f"Connecting to database: {db_url.split('@')[-1]}")
        
        # 엔진 생성 및 연결 테스트
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # 간단한 쿼리 실행
            result = conn.execute(text("SELECT version()"))
            db_version = result.scalar()
            print(f"Successfully connected to database!\nVersion: {db_version}")
            
            # 테이블 목록 조회
            print("\nTables in database:")
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            for table in tables:
                print(f"- {table[0]}")
                
        return True
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    test_connection()
