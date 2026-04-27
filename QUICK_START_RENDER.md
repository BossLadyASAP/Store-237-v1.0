# Store 237 - Quick Start for Render Deployment

## 🚀 Deploy in 5 Minutes

### Option 1: One-Click Deploy (Easiest)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Store 237"
   git remote add origin https://github.com/YOUR_USERNAME/store-237.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Click **New +** → **Blueprint**
   - Connect your GitHub repository
   - Select `render.yaml`
   - Click **Create New Services**
   - Wait 5-10 minutes for deployment

3. **Access Your App**
   - Get URL from Render Dashboard
   - Visit: `https://your-app.onrender.com`
   - Demo: `demo` / `demo123`

---

### Option 2: Manual Deploy (More Control)

#### Step 1: Create PostgreSQL Database
1. Render Dashboard → **New +** → **PostgreSQL**
2. Name: `store-237-db`
3. Database: `store237`
4. User: `store237`
5. Click **Create Database**
6. Copy the **Internal Database URL**

#### Step 2: Create Web Service
1. Render Dashboard → **New +** → **Web Service**
2. Connect your GitHub repository
3. Fill in details:
   - **Name**: `store-237`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn "app:create_app()"`

#### Step 3: Add Environment Variables
```
FLASK_ENV=production
SECRET_KEY=<generate-random-string>
DATABASE_URL=<from-step-1>
UPLOAD_FOLDER=/tmp/uploads
```

#### Step 4: Deploy
- Click **Create Web Service**
- Wait for deployment (5-10 minutes)
- Get your URL

---

## 📝 Environment Variables

Copy and paste into Render:

```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-this
DATABASE_URL=postgresql://store237:PASSWORD@YOUR_DB_HOST:5432/store237
UPLOAD_FOLDER=/tmp/uploads
```

**Generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🔧 Initialize Database

After deployment completes:

1. Go to your web service
2. Click **Shell** tab
3. Run:

```bash
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

---

## ✅ Verify Deployment

1. Visit your app URL
2. Try demo login: `demo` / `demo123`
3. Explore dashboard, products, POS, etc.
4. Create your own store

---

## 🎯 Common Issues & Fixes

### Build Fails
```bash
# Check requirements.txt has all dependencies
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### Database Connection Error
- Verify DATABASE_URL is correct
- Check database is running
- Ensure password matches
- Try restarting web service

### App Not Starting
- Check logs in Render Dashboard
- Verify all environment variables are set
- Ensure Python version is 3.8+

---

## 📊 Monitor Your App

**Render Dashboard:**
- View logs in real-time
- Monitor resource usage
- Restart service
- Update environment variables

---

## 🔄 Auto-Deploy from GitHub

1. Go to web service settings
2. Enable **Auto-Deploy**
3. Now every push to main branch auto-deploys!

---

## 💾 Database Backups

Render automatically backs up PostgreSQL daily. To restore:

1. Go to database in Render Dashboard
2. Click **Backups**
3. Select backup and restore

---

## 🎉 You're Live!

Your Store 237 is now running on Render!

**Next Steps:**
1. Create your store
2. Add products
3. Invite team members
4. Start selling!

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Store 237 README**: See README.md
- **Flask Docs**: https://flask.palletsprojects.com/

---

**Happy Selling! 🚀**
