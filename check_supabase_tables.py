import os
import uuid
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Supabase 클라이언트 초기화
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

def list_tables():
    """List all tables in the database"""
    try:
        # Get the first row from each table to check if it exists
        tables = [
            'users', 'courses', 'course_sections', 
            'lessons', 'enrollments', 'course_reviews', 'lesson_completions'
        ]
        
        existing_tables = []
        for table in tables:
            try:
                # Try to get a single row from the table
                response = supabase.table(table).select('*').limit(1).execute()
                if hasattr(response, 'error') and response.error:
                    print(f"  Table {table} exists but is empty or has an error: {response.error}")
                else:
                    existing_tables.append(table)
            except Exception as e:
                print(f"  Error checking table {table}: {e}")
        
        return existing_tables
        
    except Exception as e:
        print(f"Error listing tables: {e}")
        return []

def get_table_columns(table_name):
    """Get column information for a specific table"""
    try:
        # Get a single row to infer column names and types
        response = supabase.table(table_name).select('*').limit(1).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"  Error getting columns for {table_name}: {response.error}")
            return []
            
        if not response.data:
            print(f"  No data in table {table_name}")
            return []
            
        # Get column names and types from the first row
        columns = []
        first_row = response.data[0] if response.data else {}
        
        for col_name, value in first_row.items():
            col_type = type(value).__name__
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
                
            columns.append({
                'name': col_name,
                'type': col_type,
                'nullable': True  # We can't determine this without schema info
            })
            
        return columns
        
    except Exception as e:
        print(f"  Error getting columns for {table_name}: {e}")
        return []

def get_table_structure(table_name):
    """Get and display the structure of a table"""
    try:
        print(f"\nTable: {table_name}")
        print("=" * 80)
        
        # Get column information
        columns = get_table_columns(table_name)
        
        if not columns:
            print("  No columns found or table is empty")
            return False
            
        # Print column information
        print(f"  {'Column':<30} {'Type':<15} {'Nullable'}")
        print("  " + "-" * 60)
        for col in columns:
            print(f"  {col['name']:<30} {col['type']:<15} {'YES' if col['nullable'] else 'NO'}")
        
        # Get a sample row if available
        response = supabase.table(table_name).select('*').limit(1).execute()
        if response.data:
            print("\n  Sample Row:")
            print("  " + "-" * 60)
            for key, value in response.data[0].items():
                value_str = str(value)
                if len(value_str) > 50:
                    value_str = value_str[:47] + '...'
                print(f"  {key}: {value_str}")
        
        return True
        
    except Exception as e:
        print(f"  Error getting structure for {table_name}: {e}")
        return False

def main():
    print(f"Connecting to Supabase: {url}")
    
    # List all tables
    print("\nListing all tables...")
    tables = list_tables()
    
    if not tables:
        print("No tables found in the database.")
        return
    
    print("\nFound tables:", ", ".join(tables) if tables else "None")
    
    # Get structure for each table
    print("\nGetting table structures...")
    for table in tables:
        print("\n" + "=" * 80)
        print(f"TABLE: {table.upper()}")
        print("=" * 80)
        get_table_structure(table)

if __name__ == "__main__":
    main()
