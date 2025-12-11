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

# Flag to track if migrations have been attempted
_migrations_attempted = False

def ensure_migrations():
    """Run migrations if needed (only once per cold start)"""
    global _migrations_attempted
    if _migrations_attempted:
        return
    
    _migrations_attempted = True
    
    try:
        from django.core.management import call_command
        from django.db import connection
        
        # Check if we can connect to database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Try to run migrations (non-interactive, fail silently if already up to date)
        call_command('migrate', verbosity=0, interactive=False, run_syncdb=False)
        print("Migrations check completed", file=sys.stderr)
    except Exception as e:
        # Log but don't fail - migrations might already be applied
        print(f"Migration check failed (this is OK if migrations are already applied): {e}", file=sys.stderr)

# Import Django WSGI application
try:
    from django.core.wsgi import get_wsgi_application
    
    # Initialize Django (this calls django.setup() internally)
    application = get_wsgi_application()
    
    # Attempt to run migrations on first load (after Django is initialized)
    ensure_migrations()
    
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
    print(f"DATABASE_URL set: {bool(os.environ.get('DATABASE_URL'))}", file=sys.stderr)
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
            'hint': 'Check server logs for full traceback. Ensure migrations are run and DATABASE_URL is set.',
            'troubleshooting': {
                'check_database_url': 'Ensure DATABASE_URL is set in Vercel environment variables',
                'run_migrations': 'Run: vercel env pull .env.production && export $(cat .env.production | xargs) && python manage.py migrate',
                'check_logs': 'Run: vercel logs <deployment-url>'
            }
        }
        return [json.dumps(error_response, indent=2).encode()]
