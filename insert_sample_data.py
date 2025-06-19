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

def insert_sample_data():
    """Insert sample data into all tables"""
    try:
        print("Starting to insert sample data...")
        
        # 1. Insert a user
        print("\n1. Inserting a sample user...")
        user_data = {
            'id': str(uuid.uuid4()),
            'email': f"user_{int(datetime.now().timestamp())}@example.com",
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        response = supabase.table('users').insert(user_data).execute()
        if hasattr(response, 'error') and response.error:
            print(f"Error inserting user: {response.error}")
            return False
        
        user_id = response.data[0]['id']
        print(f"  - Inserted user with ID: {user_id}")
        
        # 2. Insert a course
        print("\n2. Inserting a sample course...")
        course_data = {
            'id': str(uuid.uuid4()),
            'title': 'Introduction to Python',
            'description': 'Learn Python programming from scratch',
            'creator_id': user_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        response = supabase.table('courses').insert(course_data).execute()
        if hasattr(response, 'error') and response.error:
            print(f"Error inserting course: {response.error}")
            return False
        
        course_id = response.data[0]['id']
        print(f"  - Inserted course with ID: {course_id}")
        
        # 3. Insert a course section
        print("\n3. Inserting a sample course section...")
        section_data = {
            'id': str(uuid.uuid4()),
            'course_id': course_id,
            'title': 'Getting Started',
            'order_index': 1,
            'created_at': datetime.now().isoformat()
        }
        response = supabase.table('course_sections').insert(section_data).execute()
        if hasattr(response, 'error') and response.error:
            print(f"Error inserting course section: {response.error}")
            return False
        
        section_id = response.data[0]['id']
        print(f"  - Inserted section with ID: {section_id}")
        
        # 4. Insert a lesson
        print("\n4. Inserting a sample lesson...")
        lesson_data = {
            'id': str(uuid.uuid4()),
            'section_id': section_id,
            'title': 'Python Basics',
            'content': 'Learn about variables, data types, and basic operations in Python.',
            'order_index': 1,
            'created_at': datetime.now().isoformat()
        }
        response = supabase.table('lessons').insert(lesson_data).execute()
        if hasattr(response, 'error') and response.error:
            print(f"Error inserting lesson: {response.error}")
            return False
        
        lesson_id = response.data[0]['id']
        print(f"  - Inserted lesson with ID: {lesson_id}")
        
        # 5. Insert an enrollment
        print("\n5. Creating an enrollment...")
        enrollment_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'course_id': course_id,
            'enrolled_at': datetime.now().isoformat()
        }
        response = supabase.table('enrollments').insert(enrollment_data).execute()
        if hasattr(response, 'error') and response.error:
            print(f"Error creating enrollment: {response.error}")
            return False
        
        print(f"  - Created enrollment with ID: {response.data[0]['id']}")
        
        # 6. Insert a course review
        print("\n6. Adding a course review...")
        review_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'course_id': course_id,
            'rating': 5,
            'comment': 'Great course! Very informative.',
            'created_at': datetime.now().isoformat()
        }
        response = supabase.table('course_reviews').insert(review_data).execute()
        if hasattr(response, 'error') and response.error:
            print(f"Error adding review: {response.error}")
            return False
        
        print(f"  - Added review with ID: {response.data[0]['id']}")
        
        # 7. Mark lesson as completed
        print("\n7. Marking lesson as completed...")
        completion_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'lesson_id': lesson_id,
            'completed_at': datetime.now().isoformat()
        }
        response = supabase.table('lesson_completions').insert(completion_data).execute()
        if hasattr(response, 'error') and response.error:
            print(f"Error marking lesson as completed: {response.error}")
            return False
        
        print(f"  - Marked lesson as completed with ID: {response.data[0]['id']}")
        
        print("\n✅ Sample data inserted successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error inserting sample data: {e}")
        return False

if __name__ == "__main__":
    print("Starting to insert sample data into Supabase...")
    insert_sample_data()
