"""
Vercel serverless function to run Django migrations
This can be called manually or via a webhook
"""
import os
import sys

# Add the project directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolsearch.settings')

def handler(request):
    """Run Django migrations"""
    try:
        from django.core.management import call_command
        from django.core.wsgi import get_wsgi_application
        
        # Initialize Django
        application = get_wsgi_application()
        
        # Run migrations
        call_command('migrate', verbosity=2, interactive=False)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': '{"status": "success", "message": "Migrations completed successfully"}'
        }
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"status": "error", "message": "{error_msg}", "traceback": "{traceback_str}"}}'
        }
