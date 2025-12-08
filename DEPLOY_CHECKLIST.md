# Quick Deployment Checklist

## ⚠️ BEFORE YOU GIT PUSH:

### 1. Connect Repository to Vercel (One-time setup)
   - Go to https://vercel.com/new
   - Import your Git repository
   - Vercel will auto-detect the `vercel.json` configuration

### 2. Set Environment Variables in Vercel Dashboard
   Go to your project settings → Environment Variables and add:

   **REQUIRED:**
   - `SECRET_KEY` - Generate a new Django secret key (don't use the default!)
     ```bash
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```
   - `DATABASE_URL` - Your PostgreSQL connection string
     - Format: `postgresql://user:password@host:port/database`
     - If using Supabase: Get it from your Supabase project settings
   - `ALLOWED_HOSTS` - Your Vercel domain
     - Example: `your-app.vercel.app,your-custom-domain.com`
   - `DEBUG` - Set to `False` for production

   **OPTIONAL (if not using DATABASE_URL):**
   - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

### 3. Run Database Migrations
   **IMPORTANT:** Vercel serverless functions can't run migrations automatically.
   
   You need to run migrations BEFORE or AFTER deployment:
   
   **Option A: Before deployment (recommended)**
   ```bash
   # Set your production DATABASE_URL locally
   export DATABASE_URL="your-production-database-url"
   python manage.py migrate
   ```
   
   **Option B: After deployment**
   - Use Vercel CLI: `vercel env pull` to get env vars
   - Run migrations locally pointing to production DB
   - Or use a database migration service

### 4. Load Initial Data (if needed)
   ```bash
   python manage.py loaddata fixtures/facilities.json
   python manage.py loaddata fixtures/schools.json
   python manage.py loaddata fixtures/reviews.json
   python manage.py loaddata fixtures/curricula.json
   ```

### 5. Now You Can Git Push!
   ```bash
   git add .
   git commit -m "Configure for Vercel deployment"
   git push
   ```

   Vercel will automatically:
   - Detect the push
   - Install dependencies from `requirements.txt`
   - Collect static files
   - Deploy your app

## ✅ After Deployment:

1. **Check the deployment logs** in Vercel dashboard
2. **Visit your app** at `https://your-app.vercel.app`
3. **Test static files** - CSS and JS should load
4. **Test database** - Make sure database connection works
5. **Run migrations** if you haven't already

## 🐛 Common Issues:

- **Static files 404**: Check that `collectstatic` ran successfully in build logs
- **Database errors**: Verify `DATABASE_URL` is correct and database allows Vercel IPs
- **500 errors**: Check function logs in Vercel dashboard
- **Migrations needed**: Run them manually (see step 3 above)

## 📝 Notes:

- Media files (user uploads) won't persist on Vercel - consider using S3, Cloudinary, or Supabase Storage
- First request might be slow (cold start) - subsequent requests will be faster
- Consider Vercel Pro plan for better performance and features
