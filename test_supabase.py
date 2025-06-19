import os
from dotenv import load_dotenv
from supabase import create_client, Client
from supabase.client import ClientOptions

# .env 파일 로드
load_dotenv()

def get_table_structure(supabase, table_name):
    """테이블의 구조를 가져오는 함수"""
    try:
        # 테이블의 첫 번째 행을 가져와서 컬럼 정보 확인
        result = supabase.table(table_name).select('*').limit(1).execute()
        
        if hasattr(result, 'error') and result.error:
            print(f"  Error getting structure for {table_name}: {result.error}")
            return []
            
        if not result.data:
            print(f"  No data in table {table_name}")
            return []
            
        # 첫 번째 행의 키를 컬럼으로 사용
        columns = list(result.data[0].keys())
        
        # 각 컬럼의 타입 확인을 위해 정보 수집
        structure = []
        for col in columns:
            # 간단한 타입 추론 (정확한 타입은 직접 확인 필요)
            if not result.data[0][col] is None:  # 값이 None이 아닌 경우에만 타입 확인
                col_type = type(result.data[0][col]).__name__
                if col_type == 'str':
                    col_type = 'text'
                elif col_type == 'int':
                    col_type = 'integer'
                elif col_type == 'float':
                    col_type = 'float8'
                elif col_type == 'bool':
                    col_type = 'boolean'
                elif col_type == 'dict':
                    col_type = 'jsonb'
            else:
                col_type = 'unknown'  # 값이 NULL인 경우
                
            structure.append({
                'column_name': col,
                'data_type': col_type,
                'is_nullable': 'YES',  # 정확한 정보는 직접 확인 불가
                'column_default': None  # 정확한 정보는 직접 확인 불가
            })
            
        return structure
        
    except Exception as e:
        print(f"  Error getting structure for {table_name}: {e}")
        return []

def get_table_constraints(supabase, table_name):
    """테이블의 제약 조건을 가져오는 함수 (기본 키, 외래 키, 유니크 제약 등)"""
    try:
        # 테이블의 첫 번째 행을 가져와서 제약 조건 유추 (실제로는 제약 조건을 직접 가져올 수 없으므로 임시로 빈 리스트 반환)
        # Supabase에서는 information_schema에 직접 쿼리할 수 없으므로, 테이블 구조를 기반으로 유추
        return []
        
    except Exception as e:
        print(f"  Error getting constraints for {table_name}: {e}")
        return []

def get_table_columns(supabase, table_name):
    """테이블의 컬럼 정보를 가져오는 함수"""
    try:
        # 테이블의 첫 번째 행을 가져와서 컬럼 정보 확인
        result = supabase.table(table_name).select('*').limit(1).execute()
        
        if hasattr(result, 'error') and result.error:
            print(f"  Error getting columns for {table_name}: {result.error}")
            return []
            
        if not result.data:
            # 테이블이 비어있을 경우 컬럼 정보를 직접 정의
            if table_name == 'users':
                return [
                    {'column_name': 'id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'email', 'data_type': 'text', 'is_nullable': 'NO'},
                    {'column_name': 'created_at', 'data_type': 'timestamp', 'is_nullable': 'YES'},
                    {'column_name': 'updated_at', 'data_type': 'timestamp', 'is_nullable': 'YES'}
                ]
            elif table_name == 'courses':
                return [
                    {'column_name': 'id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'title', 'data_type': 'text', 'is_nullable': 'NO'},
                    {'column_name': 'description', 'data_type': 'text', 'is_nullable': 'YES'},
                    {'column_name': 'creator_id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'created_at', 'data_type': 'timestamp', 'is_nullable': 'YES'},
                    {'column_name': 'updated_at', 'data_type': 'timestamp', 'is_nullable': 'YES'}
                ]
            elif table_name == 'course_sections':
                return [
                    {'column_name': 'id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'course_id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'title', 'data_type': 'text', 'is_nullable': 'NO'},
                    {'column_name': 'order_index', 'data_type': 'integer', 'is_nullable': 'NO'},
                    {'column_name': 'created_at', 'data_type': 'timestamp', 'is_nullable': 'YES'}
                ]
            elif table_name == 'lessons':
                return [
                    {'column_name': 'id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'section_id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'title', 'data_type': 'text', 'is_nullable': 'NO'},
                    {'column_name': 'content', 'data_type': 'text', 'is_nullable': 'YES'},
                    {'column_name': 'order_index', 'data_type': 'integer', 'is_nullable': 'NO'},
                    {'column_name': 'created_at', 'data_type': 'timestamp', 'is_nullable': 'YES'}
                ]
            elif table_name == 'enrollments':
                return [
                    {'column_name': 'id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'user_id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'course_id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'enrolled_at', 'data_type': 'timestamp', 'is_nullable': 'YES'}
                ]
            elif table_name == 'course_reviews':
                return [
                    {'column_name': 'id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'user_id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'course_id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'rating', 'data_type': 'integer', 'is_nullable': 'NO'},
                    {'column_name': 'comment', 'data_type': 'text', 'is_nullable': 'YES'},
                    {'column_name': 'created_at', 'data_type': 'timestamp', 'is_nullable': 'YES'}
                ]
            elif table_name == 'lesson_completions':
                return [
                    {'column_name': 'id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'user_id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'lesson_id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                    {'column_name': 'completed_at', 'data_type': 'timestamp', 'is_nullable': 'YES'}
                ]
            return []
            
        # 첫 번째 행의 키를 컬럼으로 사용
        columns = list(result.data[0].keys())
        
        # 각 컬럼의 타입 확인을 위해 정보 수집
        column_info = []
        for col in columns:
            # 간단한 타입 추론 (정확한 타입은 직접 확인 필요)
            col_type = 'unknown'
            if result.data[0][col] is not None:  # 값이 None이 아닌 경우에만 타입 확인
                col_type = type(result.data[0][col]).__name__
                if col_type == 'str':
                    col_type = 'text'
                elif col_type == 'int':
                    col_type = 'integer'
                elif col_type == 'float':
                    col_type = 'float8'
                elif col_type == 'bool':
                    col_type = 'boolean'
                elif col_type == 'dict':
                    col_type = 'jsonb'
            
            column_info.append({
                'column_name': col,
                'data_type': col_type,
                'is_nullable': 'YES'  # 정확한 정보는 직접 확인 불가
            })
            
        return column_info
        
    except Exception as e:
        print(f"  Error getting columns for {table_name}: {e}")
        return []

def test_supabase_connection():
    try:
        # 환경변수에서 Supabase 설정 가져오기
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            print("Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
            return False
            
        print(f"Connecting to Supabase: {url}")
        
        # Supabase 클라이언트 생성
        supabase: Client = create_client(
            url,
            key,
            options=ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                schema="public",
            )
        )
        
        # 알려진 테이블 목록 (Supabase 기본 테이블 + 우리가 생성한 테이블)
        known_tables = [
            'users', 'courses', 'course_sections', 'lessons', 
            'enrollments', 'course_reviews', 'lesson_completions'
        ]
        
        print("\nChecking tables...")
        
        # 각 테이블 확인
        for table in known_tables:
            print(f"\n{'='*80}")
            print(f"TABLE: {table.upper()}")
            print("=" * 40)
            
            try:
                # 테이블 존재 여부 확인
                result = supabase.table(table).select('*').limit(1).execute()
                
                if hasattr(result, 'error') and result.error:
                    print(f"  Table {table} does not exist or access denied")
                    continue
                
                print(f"  Table {table} exists")
                
                # 테이블 구조 가져오기
                structure = get_table_structure(supabase, table)
                
                if not structure:
                    print("  Could not determine table structure")
                else:
                    # 컬럼 정보 가져오기
                    columns = get_table_columns(supabase, table)
                    if columns:
                        print("\n  COLUMNS:")
                        print("  " + "-" * 80)
                        print(f"  {'Column':<30} {'Type':<15} {'Nullable':<10}")
                        print("  " + "-" * 80)
                        for col in columns:
                            print(f"  {col['column_name']:<30} {col['data_type']:<15} {col['is_nullable']}")
                    else:
                        print("  Could not determine table columns")
                
                # 제약 조건 정보 가져오기
                constraints = get_table_constraints(supabase, table)
                if constraints:
                    print("\n  CONSTRAINTS:")
                    print("  " + "-" * 80)
                    for constraint in constraints:
                        if constraint['constraint_type'] == 'FOREIGN KEY':
                            print(f"  {constraint['constraint_type']}: {constraint['column_name']} -> {constraint['foreign_table_name']}({constraint['foreign_column_name']})")
                        else:
                            print(f"  {constraint['constraint_type']}: {constraint.get('column_name', '')}")
                
                # 샘플 데이터 출력 (있을 경우)
                if result.data:
                    print("\n  SAMPLE DATA (first row):")
                    print("  " + "-" * 80)
                    print(f"  {result.data[0]}")
                
            except Exception as e:
                print(f"  Error checking table {table}: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
