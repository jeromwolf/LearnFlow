import os
import uuid
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Supabase 클라이언트 초기화
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

def create_user_with_email():
    """Create a new user using Supabase Auth"""
    try:
        # Generate a unique email with a standard format
        timestamp = int(datetime.now().timestamp())
        email = f"testuser+{timestamp}@example.com"
        password = "Test123!"  # In a real app, use a secure password generator
        
        print(f"Creating user with email: {email}")
        
        # Create the user using Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
        
        if hasattr(auth_response, 'error') and auth_response.error:
            print(f"Error creating user: {auth_response.error}")
            return None
        
        print(f"User created successfully!")
        print(f"User ID: {auth_response.user.id}")
        print(f"Email: {auth_response.user.email}")
        
        return auth_response.user
        
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def create_sample_course(user_id):
    """Create a sample course"""
    try:
        print("\nCreating sample course...")
        
        course_data = {
            'title': 'Introduction to Python',
            'description': 'Learn Python programming from scratch',
            'creator_id': user_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        response = supabase.table('courses').insert(course_data).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Error creating course: {response.error}")
            return None
        
        course = response.data[0]
        print(f"Course created with ID: {course['id']}")
        return course
        
    except Exception as e:
        print(f"Error creating course: {e}")
        return None

def main():
    print("Starting to create sample data with authentication...")
    
    # 1. Create a user
    user = create_user_with_email()
    if not user:
        print("Failed to create user. Exiting...")
        return
    
    # 2. Create a course
    course = create_sample_course(user.id)
    if not course:
        print("Failed to create course. Exiting...")
        return
    
    print("\n✅ Sample data created successfully!")
    print(f"User ID: {user.id}")
    print(f"Course ID: {course['id']}")

if __name__ == "__main__":
    main()
