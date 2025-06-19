import os
from supabase import create_client
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Supabase 클라이언트 초기화
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

def check_auth_users():
    """Check the auth.users table"""
    print("Checking auth.users table...")
    try:
        # Try to get a user from auth.users
        response = supabase.table('auth.users').select('*').limit(1).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Error accessing auth.users: {response.error}")
            return False
            
        if response.data:
            print("\nAuth users found:")
            for user in response.data:
                print(f"- {user.get('email', 'No email')} (ID: {user.get('id', 'No ID')})")
        else:
            print("No users found in auth.users")
            
        return True
        
    except Exception as e:
        print(f"Error checking auth.users: {e}")
        return False

def check_public_users():
    """Check the public.users table"""
    print("\nChecking public.users table...")
    try:
        # Try to get a user from public.users
        response = supabase.table('users').select('*').limit(1).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Error accessing public.users: {response.error}")
            return False
            
        if response.data:
            print("\nPublic users found:")
            for user in response.data:
                print(f"- {user.get('email', 'No email')} (ID: {user.get('id', 'No ID')})")
        else:
            print("No users found in public.users")
            
        return True
        
    except Exception as e:
        print(f"Error checking public.users: {e}")
        return False

if __name__ == "__main__":
    print("Checking Supabase users...")
    check_auth_users()
    check_public_users()
