# Deploying to Vercel

This Django application is configured to deploy on Vercel. Follow these steps:

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Your project connected to a Git repository (GitHub, GitLab, or Bitbucket)
3. A PostgreSQL database (Supabase recommended, as configured in your settings)

## Deployment Steps

### 1. Install Vercel CLI (Optional)
```bash
npm i -g vercel
```

### 2. Set Environment Variables

In your Vercel project settings, add the following environment variables:

**Required:**
- `SECRET_KEY` - Django secret key (generate a new one for production)
- `DATABASE_URL` - Your PostgreSQL connection string (from Supabase or other provider)
- `ALLOWED_HOSTS` - Your Vercel domain (e.g., `your-app.vercel.app,your-custom-domain.com`)
- `DEBUG` - Set to `False` for production

**Optional (if not using DATABASE_URL):**
- `DB_HOST` - Database host
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_PORT` - Database port (default: 5432)

### 3. Deploy

**Option A: Via Vercel Dashboard**
1. Go to https://vercel.com/new
2. Import your Git repository
3. Vercel will auto-detect the `vercel.json` configuration
4. Add your environment variables in the project settings
5. Deploy!

**Option B: Via CLI**
```bash
vercel
```

### 4. Run Migrations

After deployment, you'll need to run database migrations. You can do this via:
- Vercel CLI: `vercel env pull` then run migrations locally pointing to production DB
- Or use a one-time build command (add to vercel.json if needed)
- Or use Django admin/management commands via a separate script

**Note:** Vercel serverless functions are stateless, so you may need to run migrations separately or use a migration service.

### 5. Collect Static Files

Static files are automatically collected during the build process (configured in `vercel.json`). They will be served from the `/static/` route.

## Important Notes

1. **Database Migrations**: Vercel serverless functions don't persist state. You'll need to run migrations separately, either:
   - Before deployment (pointing to production database)
   - Using a separate migration service
   - Via Django admin if accessible

2. **Media Files**: Media files (user uploads) are not persisted on Vercel. Consider using:
   - AWS S3
   - Cloudinary
   - Vercel Blob Storage
   - Supabase Storage

3. **Static Files**: Static files are collected during build and served via Vercel's CDN.

4. **Cold Starts**: Serverless functions may have cold start delays. Consider:
   - Using Vercel Pro for better performance
   - Implementing caching strategies
   - Using Vercel Edge Functions for static content

5. **Environment Variables**: Make sure all required environment variables are set in Vercel dashboard before deployment.

## Troubleshooting

- **Static files not loading**: Check that `STATIC_ROOT` is set correctly and files are collected
- **Database connection errors**: Verify `DATABASE_URL` is correct and database allows connections from Vercel IPs
- **500 errors**: Check Vercel function logs in the dashboard
- **Migration issues**: Run migrations manually pointing to production database

## Alternative: Consider Railway or Render

For Django applications, you might also consider:
- **Railway** - Better for Django with persistent file systems
- **Render** - Good Django support with managed databases
- **Heroku** - Traditional Django hosting (paid)

These platforms may be easier for Django apps that need:
- Persistent file storage
- Background tasks
- Scheduled jobs
- Easier database migrations
