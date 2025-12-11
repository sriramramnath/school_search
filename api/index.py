"""
Vercel serverless function entry point for Django application
"""
import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolsearch.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
