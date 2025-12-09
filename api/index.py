"""
Vercel serverless function entry point for Django application.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Vercel environment variable if not set
if not os.environ.get('VERCEL'):
    os.environ['VERCEL'] = '1'

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolsearch.settings')

try:
    # Import Django WSGI application
    # Vercel expects the variable to be named 'app'
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
    
    # Debug: Print ALLOWED_HOSTS
    from django.conf import settings
    print(f"DEBUG: ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
except Exception as e:
    # Log error for debugging
    import traceback
    print(f"Error initializing Django: {e}")
    print(traceback.format_exc())
    raise
