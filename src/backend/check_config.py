"""Check if the test configuration is working correctly."""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    from app.core.test_settings import test_settings
    
    # Print settings for verification
    print("Test configuration loaded successfully!")
    print("=" * 40)
    print(f"ENV: {test_settings.ENV}")
    print(f"DEBUG: {test_settings.DEBUG}")
    print(f"TESTING: {test_settings.TESTING}")
    print(f"SQLALCHEMY_DATABASE_URI: {test_settings.SQLALCHEMY_DATABASE_URI}")
    print(f"SUPABASE_URL: {test_settings.SUPABASE_URL}")
    print(f"SECRET_KEY: {'*' * len(test_settings.SECRET_KEY) if test_settings.SECRET_KEY else 'Not set'}")
    
except Exception as e:
    print(f"Error loading test configuration: {e}", file=sys.stderr)
    raise  # Re-raise the exception to see the full traceback
    sys.exit(1)
