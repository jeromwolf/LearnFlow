import os
from supabase import create_client
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Supabase 클라이언트 초기화
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

def get_table_info(table_name):
    """Get information about a table's structure"""
    print(f"\n=== {table_name.upper()} TABLE INFO ===")
    
    try:
        # Try to get the table schema
        response = supabase.table(table_name).select('*').limit(1).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Error: {response.error}")
            return
            
        # Print column information
        if response.data:
            print("\nColumns and sample data:")
            print("-" * 50)
            for col_name, value in response.data[0].items():
                col_type = type(value).__name__
                print(f"{col_name}: {col_type} = {value}")
        else:
            print("No data in table")
            
        # Try to get table constraints (this might not work with Supabase's RLS)
        try:
            constraints = supabase.rpc('get_constraints', {'table_name': table_name}).execute()
            if hasattr(constraints, 'data') and constraints.data:
                print("\nConstraints:")
                print("-" * 50)
                for constraint in constraints.data:
                    print(f"{constraint['constraint_name']}: {constraint['constraint_definition']}")
        except Exception as e:
            print(f"\nCould not retrieve constraints (this is normal for Supabase): {e}")
            
    except Exception as e:
        print(f"Error getting table info: {e}")

def main():
    print("Inspecting Supabase database schema...")
    
    # List of tables to inspect
    tables = [
        'users', 'courses', 'course_sections', 
        'lessons', 'enrollments', 'course_reviews', 'lesson_completions'
    ]
    
    for table in tables:
        get_table_info(table)
    
    print("\nInspection complete!")

if __name__ == "__main__":
    main()
