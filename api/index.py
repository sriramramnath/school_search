"""
Vercel serverless function entry point for Django application
"""
import os
import sys

# Add the project directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolsearch.settings')

# Import Django WSGI application
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Better error handling for debugging
    import traceback
    error_msg = f"Django initialization failed: {str(e)}\n{traceback.format_exc()}"
    
    # Log error details
    print("=" * 80, file=sys.stderr)
    print("DJANGO INITIALIZATION ERROR", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(error_msg, file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(f"PYTHONPATH: {sys.path}", file=sys.stderr)
    print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)
    print(f"Project root: {project_root}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
    # Create a simple error handler that returns JSON
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        import json
        error_response = {
            'error': 'Django initialization failed',
            'message': str(e),
            'type': type(e).__name__,
            'hint': 'Check server logs for full traceback. Ensure migrations are run and DATABASE_URL is set.'
        }
        return [json.dumps(error_response, indent=2).encode()]
