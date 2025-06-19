import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

if not url or not key:
    print("Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
    exit(1)

# Initialize the Supabase client
client: Client = create_client(url, key)

def test_auth():
    """Test authentication flow with an existing user"""
    try:
        # Use the provided test credentials
        test_email = "test1@gmail.com"
        test_password = "123456"
        
        print(f"Attempting to sign in with: {test_email}")
        
        try:
            # Try to sign in
            sign_in_response = client.auth.sign_in_with_password({
                "email": test_email,
                "password": test_password,
            })
            
            if hasattr(sign_in_response, 'error') and sign_in_response.error:
                print(f"Error during sign in: {sign_in_response.error}")
                return False
            
            print("\n✅ Sign in successful!")
            print(f"User ID: {sign_in_response.user.id}")
            print(f"Email: {sign_in_response.user.email}")
            print(f"Session: {sign_in_response.session}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error during sign in: {e}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during authentication test: {e}")
        return False

def check_tables():
    """Check if tables exist and have data"""
    try:
        print("\nChecking database tables...")
        tables = [
            'courses', 'course_sections', 'lessons', 
            'enrollments', 'course_reviews', 'lesson_completions'
        ]
        
        for table in tables:
            try:
                response = client.table(table).select('*', count='exact').limit(1).execute()
                count = response.count if hasattr(response, 'count') else \
                        len(response.data) if hasattr(response, 'data') else 0
                print(f"- {table}: {count} records")
            except Exception as e:
                print(f"- {table}: Error - {str(e)}")
    except Exception as e:
        print(f"Error checking tables: {e}")

def main():
    print("Supabase Database Check")
    print("=" * 50)
    
    # First, try to authenticate
    if test_auth():
        # If authentication is successful, check the tables
        check_tables()
    
    print("\nNext steps:")
    print("1. Go to the Supabase dashboard")
    print("2. Navigate to the Authentication section")
    print("3. Create a user with email: test1@gmail.com and password: 123456")
    print("4. Run this script again")

if __name__ == "__main__":
    main()
