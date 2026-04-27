# Store 237 - Render Deployment Guide

Complete step-by-step guide to deploy Store 237 on Render.com

## Prerequisites

1. **Render Account** - Sign up at [render.com](https://render.com)
2. **GitHub Account** - Push your code to GitHub
3. **Git** - Installed on your local machine
4. **Store 237 Code** - Extract the downloaded zip file

## Step 1: Push Code to GitHub

### 1.1 Create a GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `store-237`
3. Description: "Store 237 - Retail Management Platform"
4. Choose Public or Private
5. Click "Create repository"

### 1.2 Push Your Code

```bash
# Navigate to your project
cd store-237-python

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Store 237 application"

# Add remote (replace YOUR_USERNAME and YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/store-237.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 2: Set Up PostgreSQL Database on Render

### 2.1 Create PostgreSQL Database

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **PostgreSQL**
3. Fill in the details:
   - **Name**: `store-237-db`
   - **Database**: `store237`
   - **User**: `store237`
   - **Region**: Choose closest to your location
   - **PostgreSQL Version**: 15
4. Click **Create Database**
5. Wait for database to be created (2-3 minutes)
6. Copy the **Internal Database URL** (you'll need this)

## Step 3: Deploy Web Service on Render

### 3.1 Create Web Service

1. In Render Dashboard, click **New +** → **Web Service**
2. Select **Deploy an existing repository**
3. Click **Connect** next to your GitHub repository
4. Fill in the details:
   - **Name**: `store-237`
   - **Environment**: `Python 3`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn "app:create_app()"`

### 3.2 Configure Environment Variables

1. Scroll down to **Environment**
2. Add the following environment variables:

```
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key-here-change-this
DATABASE_URL=postgresql://store237:PASSWORD@YOUR_DB_HOST:5432/store237
UPLOAD_FOLDER=/tmp/uploads
```

**Important:** 
- Replace `PASSWORD` with your database password (from Step 2)
- Replace `YOUR_DB_HOST` with your database host (from Step 2)
- Generate a secure `SECRET_KEY` - use a random string or run:
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```

### 3.3 Complete Deployment

1. Click **Create Web Service**
2. Render will start building and deploying
3. Wait for deployment to complete (5-10 minutes)
4. Once deployed, you'll get a URL like: `https://store-237.onrender.com`

## Step 4: Initialize Database

### 4.1 Access Web Service Shell

1. In Render Dashboard, go to your web service
2. Click **Shell** tab
3. Run the following commands:

```bash
# Initialize database
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Create demo account
python3 -c "
from app import create_app, db
from models import User, Store
app = create_app()
with app.app_context():
    # Create demo user
    demo_user = User(
        username='demo',
        email='demo@store237.com',
        full_name='Demo User',
        is_demo=True
    )
    demo_user.set_password('demo123')
    db.session.add(demo_user)
    db.session.flush()
    
    # Create demo store
    demo_store = Store(
        store_name='Demo Store',
        proprietor_name='John Doe',
        seller_name='Jane Smith',
        owner_id=demo_user.id,
        currency='USD',
        description='Welcome to Store 237 Demo'
    )
    db.session.add(demo_store)
    db.session.commit()
    print('Demo account created successfully!')
"
```

## Step 5: Configure Custom Domain (Optional)

### 5.1 Add Custom Domain

1. In Render Dashboard, go to your web service
2. Click **Settings** → **Custom Domain**
3. Enter your domain (e.g., `store237.com`)
4. Click **Add Custom Domain**
5. Follow DNS configuration instructions

## Step 6: Enable Auto-Deploy

### 6.1 Set Up Auto-Deploy

1. In web service settings, find **Auto-Deploy**
2. Select **Yes** to auto-deploy on every push to main branch
3. Save settings

Now every time you push to GitHub, Render will automatically deploy!

## Troubleshooting

### Issue: Build Fails

**Solution:**
```bash
# Check build logs in Render Dashboard
# Common issues:
# 1. Missing dependencies - update requirements.txt
# 2. Python version mismatch - ensure Python 3.8+
# 3. Environment variables not set
```

### Issue: Database Connection Error

**Solution:**
1. Verify DATABASE_URL is correct
2. Check database is running in Render Dashboard
3. Ensure password is correct
4. Try resetting database connection

### Issue: Static Files Not Loading

**Solution:**
```bash
# Add to app.py before running
import os
os.environ['FLASK_ENV'] = 'production'

# Render serves static files automatically from /static directory
```

### Issue: Uploads Not Persisting

**Solution:**
Render's file system is ephemeral. For persistent uploads:
1. Use AWS S3 or similar cloud storage
2. Or use Render's Persistent Disk feature
3. Update UPLOAD_FOLDER configuration

## Monitoring & Maintenance

### View Logs

1. Go to web service in Render Dashboard
2. Click **Logs** tab
3. View real-time application logs

### Restart Service

1. Go to web service settings
2. Click **Manual Deploy** → **Deploy latest commit**
3. Or click **Restart** button

### Update Application

1. Make changes locally
2. Commit and push to GitHub
3. Render automatically deploys (if auto-deploy enabled)

## Performance Optimization

### 1. Enable Caching

```python
# In app.py
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year
```

### 2. Database Connection Pooling

```python
# In config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### 3. Upgrade Plan if Needed

- Start with Render's free tier for testing
- Upgrade to paid plan for production
- Monitor performance metrics in dashboard

## Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use HTTPS (enabled by default on Render)
- [ ] Set `FLASK_ENV=production`
- [ ] Enable database backups
- [ ] Regularly update dependencies
- [ ] Use strong passwords for all accounts
- [ ] Enable two-factor authentication on Render

## Backup & Recovery

### Automatic Backups

Render provides automatic PostgreSQL backups. To restore:

1. Go to PostgreSQL database in Render Dashboard
2. Click **Backups** tab
3. Select backup to restore
4. Click **Restore**

### Manual Database Export

```bash
# From your local machine
pg_dump DATABASE_URL > backup.sql

# Restore from backup
psql DATABASE_URL < backup.sql
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `production` |
| `SECRET_KEY` | Session encryption key | Random 64-char string |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host/db` |
| `UPLOAD_FOLDER` | File upload directory | `/tmp/uploads` |
| `MAIL_SERVER` | Email server (optional) | `smtp.gmail.com` |
| `MAIL_PORT` | Email port (optional) | `587` |
| `MAIL_USERNAME` | Email username (optional) | `your-email@gmail.com` |
| `MAIL_PASSWORD` | Email password (optional) | `app-password` |

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Flask Docs**: https://flask.palletsprojects.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **GitHub Help**: https://docs.github.com/

## Next Steps

1. ✅ Deploy on Render
2. Test all features with demo account
3. Create your first store
4. Invite team members
5. Start managing your retail business!

---

**Happy Deploying! 🚀**

For issues or questions, refer to Render's support documentation or check application logs.
