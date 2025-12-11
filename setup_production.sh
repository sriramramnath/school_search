#!/bin/bash
# Production setup script for Vercel deployment
# This script helps set up the database and run migrations

set -e

echo "🚀 School Search - Production Setup"
echo "===================================="
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is not set"
    echo ""
    echo "To fix this:"
    echo "1. Pull environment variables from Vercel:"
    echo "   vercel env pull .env.production"
    echo ""
    echo "2. Load them:"
    echo "   export \$(cat .env.production | xargs)"
    echo ""
    echo "3. Run this script again:"
    echo "   ./setup_production.sh"
    exit 1
fi

echo "✅ DATABASE_URL is set"
echo ""

# Set Django settings
export DJANGO_SETTINGS_MODULE=schoolsearch.settings

# Run migrations
echo "📦 Running database migrations..."
python3 manage.py migrate --noinput

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully!"
else
    echo "❌ Migrations failed. Check the error above."
    exit 1
fi

echo ""
echo "🎉 Setup complete! Your application should now work."
echo ""
echo "Next steps:"
echo "- Deploy to Vercel: vercel --prod"
echo "- Check logs: vercel logs <deployment-url>"
