# Free Production Deployment Guide

Deploy your GameManager app with Telegram bot for **FREE**! ✨

---

## 🎯 Recommended: Render.com (Easiest)

### Step 1: Prepare Your Code

1. **Create requirements.txt** (if not exists):
```txt
Flask>=3.0.0
Flask-CORS>=4.0.0
Flask-SQLAlchemy>=3.1.1
Flask-Login>=0.6.3
Flask-JWT-Extended>=4.6.0
Werkzeug>=3.0.1
bcrypt>=4.1.2
Pillow>=10.2.0
python-dotenv>=1.0.0
requests>=2.31.0
gunicorn>=21.2.0
```

2. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/gamemanager.git
git push -u origin main
```

### Step 2: Deploy Flask App

1. Go to [render.com](https://render.com) and sign up
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Configure:
   - **Name**: `gamemanager-api`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT run:app`
   - **Plan**: Free

### Step 3: Deploy Telegram Bot Worker

1. Click **New → Background Worker**
2. Same repo, configure:
   - **Name**: `gamemanager-telegram-bot`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python telegram_bot_polling.py`
   - **Plan**: Free

### Step 4: Environment Variables

Add to **both** services:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_CHAT_ID=your_chat_id_here
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

### Step 5: Test

Your app is live! 🎉
- API: `https://gamemanager-api.onrender.com`
- Test payment submission → Check Telegram for notification with buttons

---

## 🚀 Alternative: Webhook Mode (Recommended for Production)

**Better than polling** - no background worker needed!

### Step 1: Deploy Flask Only

Deploy to Render/Railway/Fly.io (just the Flask app, **no** polling worker)

### Step 2: Set Webhook

After deployment, run this once:

```bash
curl -X POST https://your-app.onrender.com/api/telegram/set-webhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-app.onrender.com/api/telegram/webhook"}'
```

### Step 3: Verify

```bash
curl https://your-app.onrender.com/api/telegram/webhook-info
```

You should see your webhook URL is set!

**Benefits:**
- ✅ Faster (instant updates)
- ✅ More reliable
- ✅ Lower resource usage
- ✅ Only one service to maintain

---

## 🆓 Other Free Options

### Railway.app

**Pros:** Simple, $5/month free credits, easy setup
**Steps:**
1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Add environment variables
4. Deploy both services in one project

**Command for Flask:**
```
cd backend && gunicorn --bind 0.0.0.0:$PORT run:app
```

**Command for Bot:**
```
cd backend && python telegram_bot_polling.py
```

---

### Fly.io

**Pros:** Always running, no sleep, 3 free VMs
**Steps:**

1. Install flyctl:
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

2. Create `Procfile` in backend folder:
```
web: gunicorn run:app
worker: python telegram_bot_polling.py
```

3. Create `fly.toml`:
```toml
app = "gamemanager"

[build]
  builder = "paketobuildpacks/builder:base"

[[services]]
  internal_port = 5000
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

4. Deploy:
```bash
fly launch
fly deploy
```

---

### PythonAnywhere

**Pros:** Simple for beginners
**Cons:** Background tasks limited on free tier
**Note:** Use webhook mode instead of polling

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload code via Git
3. Configure WSGI
4. Set webhook (no polling worker)

---

## 📋 Pre-Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] Environment variables documented
- [ ] Database configured (SQLite works on most free hosts)
- [ ] `.env` file NOT committed (add to `.gitignore`)
- [ ] Telegram bot token ready
- [ ] Admin chat ID obtained

---

## 🔧 Production Configuration

### Update `config.py` for Production

```python
import os

class Config:
    # ... existing config ...

    # Use environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'change-in-production'

    # Database - use PostgreSQL if provided, else SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Fix postgres:// to postgresql:// for SQLAlchemy
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "gamemanager.db")}'
```

### Create `.gitignore`

```
*.pyc
__pycache__/
*.db
.env
uploads/
scanned_games/
*.log
venv/
.DS_Store
```

### Create `Procfile` (for Heroku-style platforms)

```
web: cd backend && gunicorn run:app
worker: cd backend && python telegram_bot_polling.py
```

### Create `runtime.txt` (optional)

```
python-3.11.0
```

---

## 🎯 Recommended Free Tier Comparison

| Platform | Free Tier | Polling Support | Webhook Support | Uptime |
|----------|-----------|----------------|-----------------|--------|
| **Render.com** | ✅ Forever | ✅ Background worker | ✅ Yes | Spins down after 15min |
| **Railway.app** | $5/month credit | ✅ Multiple services | ✅ Yes | Always on |
| **Fly.io** | 3 VMs free | ✅ Multiple processes | ✅ Yes | Always on |
| **PythonAnywhere** | Limited | ⚠️ Limited | ✅ Yes (better) | Always on |

**Best Choice:**
- **Development/Testing**: Render.com (easiest)
- **Production**: Fly.io or Railway (always on)
- **Method**: Use Webhooks (more efficient than polling)

---

## 🐛 Troubleshooting Production

### App Won't Start

Check logs:
```bash
# Render.com: Check logs in dashboard
# Railway: railway logs
# Fly.io: fly logs
```

### Telegram Bot Not Responding

1. **Check webhook status**:
```bash
curl https://your-app.com/api/telegram/webhook-info
```

2. **Reset webhook**:
```bash
curl -X POST https://your-app.com/api/telegram/set-webhook \
  -d '{"url": "https://your-app.com/api/telegram/webhook"}'
```

3. **Check environment variables** are set correctly

### Database Issues

Make sure your hosting supports persistent storage. Some free tiers reset files on restart. Solutions:
- Use hosted PostgreSQL (Render provides free 90-day instances)
- Use Railway PostgreSQL (included)
- Keep SQLite but backup regularly

---

## 🌟 Final Production Setup (Webhook Mode)

**This is the best setup for production:**

1. ✅ Deploy Flask app to **Render.com** or **Fly.io**
2. ✅ Set environment variables
3. ✅ Set webhook URL (one-time setup)
4. ✅ **No polling service needed!**
5. ✅ Bot responds instantly to button clicks
6. ✅ Lower resource usage = stay within free tier

---

## 💡 Pro Tips

1. **Use webhooks in production** - more reliable and efficient
2. **Keep polling for local development** - easier to debug
3. **Monitor your free tier limits** - most platforms show usage
4. **Enable auto-deploy from GitHub** - push changes, auto-updates
5. **Set up alerts** - get notified if your app goes down

---

Sweet dreams! Your app will be running 24/7 while you sleep 😴✨

Need help? Check the logs or create an issue on GitHub!
