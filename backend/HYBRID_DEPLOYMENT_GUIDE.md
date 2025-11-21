# GameManager Hybrid Deployment Guide

Complete guide for deploying GameManager with a hybrid architecture:
- **Backend API** → Render.com (free tier)
- **File Storage** → Local server via Cloudflare Tunnel (free)
- **Frontend Website** → GitHub Pages (free)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     GameManager System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐    ┌────────────┐ │
│  │   Frontend   │      │  Backend API │    │    File    │ │
│  │   (GitHub    │─────▶│  (Render.com)│◀───│  Storage   │ │
│  │    Pages)    │      │              │    │ (Cloudflare│ │
│  └──────────────┘      └──────────────┘    │   Tunnel)  │ │
│         │                     │             └────────────┘ │
│         │                     │                    │        │
│         └─────────────────────┴────────────────────┘        │
│                            │                                │
│                     ┌──────▼──────┐                        │
│                     │  PostgreSQL │                        │
│                     │  (Render)   │                        │
│                     └─────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

1. **Backend on Render.com** ✅
   - Free tier with auto-deploy from GitHub
   - Managed PostgreSQL database
   - HTTPS included
   - **Limitation:** Ephemeral file system (files deleted on restart)

2. **File Storage via Cloudflare Tunnel** ✅
   - Runs on your local machine (persistent storage)
   - Free Cloudflare Tunnel exposes local server to internet
   - No port forwarding needed
   - Secure HTTPS tunnel
   - **Perfect for:** Payment screenshots, game files, cover images

3. **Frontend on GitHub Pages** ✅
   - Free static website hosting
   - CDN-backed (fast globally)
   - Auto-deploy from GitHub
   - Custom domain support

---

## 📋 Prerequisites

- GitHub account
- Render.com account (free)
- Cloudflare account (free)
- Python 3.9+ installed locally
- Git installed

---

## 🚀 Part 1: Deploy Backend API to Render.com

### Step 1.1: Prepare Your Repository

1. **Ensure `.gitignore` excludes sensitive files:**
   ```gitignore
   .env
   *.db
   __pycache__/
   uploads/
   scanned_games/
   ```

2. **Create `requirements.txt`** (should already exist):
   ```bash
   cd backend
   pip freeze > requirements.txt
   ```

3. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

### Step 1.2: Deploy to Render

1. Go to [render.com](https://render.com) → Sign up/Login

2. Click **"New +"** → **"Web Service"**

3. **Connect your GitHub repository**

4. **Configure the service:**
   - **Name:** `gamemanager-api`
   - **Region:** Choose closest to your location
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     gunicorn --bind 0.0.0.0:$PORT run:app
     ```
   - **Plan:** `Free`

5. **Add Environment Variables** (click "Advanced" → "Add Environment Variable"):
   ```
   SECRET_KEY=<generate-with-python-secrets>
   JWT_SECRET_KEY=<generate-with-python-secrets>
   TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
   TELEGRAM_ADMIN_CHAT_ID=<your-telegram-chat-id>
   GCASH_MERCHANT_NUMBER=<your-gcash-number>
   RAWG_API_KEY=<your-rawg-api-key>
   API_BASE_URL=https://gamemanager-api.onrender.com
   ```

   **Generate secret keys:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

6. Click **"Create Web Service"**

7. **Wait for deployment** (5-10 minutes)

8. **Your API will be live at:**
   ```
   https://gamemanager-api.onrender.com
   ```

9. **Test it:**
   ```bash
   curl https://gamemanager-api.onrender.com/api/telegram/webhook-info
   ```

### Step 1.3: Add PostgreSQL Database (Optional but Recommended)

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**

2. **Configure:**
   - **Name:** `gamemanager-db`
   - **Plan:** `Free`

3. Click **"Create Database"**

4. **Copy the Internal Database URL**

5. **Add to your Web Service:**
   - Go to your `gamemanager-api` service
   - Environment → Add Variable:
     ```
     DATABASE_URL=<paste-internal-database-url>
     ```

---

## 🌐 Part 2: Setup File Storage with Cloudflare Tunnel

This runs on your **local machine** and exposes your file storage to the internet securely.

### Step 2.1: Install Cloudflare Tunnel

**Windows:**
```powershell
winget install --id Cloudflare.cloudflared
```

**macOS:**
```bash
brew install cloudflare/cloudflare/cloudflared
```

**Linux:**
```bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### Step 2.2: Authenticate Cloudflare

```bash
cloudflared tunnel login
```

This opens your browser to authenticate with Cloudflare.

### Step 2.3: Create a Tunnel

```bash
cloudflared tunnel create gamemanager-storage
```

**Save the tunnel ID** that appears (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

### Step 2.4: Create Tunnel Configuration

Create `cloudflare-tunnel-config.yml`:

```yaml
tunnel: a1b2c3d4-e5f6-7890-abcd-ef1234567890  # Your tunnel ID
credentials-file: /path/to/.cloudflared/a1b2c3d4-e5f6-7890-abcd-ef1234567890.json

ingress:
  # Route all traffic to your local backend
  - hostname: gamemanager-storage.yourdomain.com  # Optional custom domain
    service: http://localhost:5000
  # Or use trycloudflare.com (no custom domain needed)
  - service: http://localhost:5000
```

**For quick setup without custom domain:**
```yaml
tunnel: a1b2c3d4-e5f6-7890-abcd-ef1234567890
credentials-file: C:\Users\YourUser\.cloudflared\a1b2c3d4-e5f6-7890-abcd-ef1234567890.json

ingress:
  - service: http://localhost:5000
```

### Step 2.5: Run Your Local Backend

In one terminal, start your Flask backend:

```bash
cd backend
python run.py
```

Your backend should be running on `http://localhost:5000`

### Step 2.6: Start the Tunnel

In another terminal:

```bash
cloudflared tunnel --config cloudflare-tunnel-config.yml run gamemanager-storage
```

**You'll see output like:**
```
Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):
https://abc-def-ghi.trycloudflare.com
```

**Copy this URL!** This is your `STORAGE_BASE_URL`

### Step 2.7: Update Render Environment Variables

1. Go to Render dashboard → `gamemanager-api` service
2. Environment → Add variable:
   ```
   STORAGE_BASE_URL=https://abc-def-ghi.trycloudflare.com
   ```
3. Save → Redeploy

### Step 2.8: Test File Storage

```bash
# Test if files are accessible
curl https://abc-def-ghi.trycloudflare.com/static/gcash_qr.jpg
```

---

## 📱 Part 3: Deploy Frontend to GitHub Pages

### Step 3.1: Prepare Website Files

Navigate to `GameManager-Website/` directory.

See `GameManager-Website/README.md` for complete instructions.

**Quick setup:**

1. Update `index.html` with your API URL:
   ```javascript
   const API_URL = 'https://gamemanager-api.onrender.com';
   ```

2. Update download links to point to GitHub Releases or your hosting

### Step 3.2: Push to GitHub

```bash
cd GameManager-Website
git init
git add .
git commit -m "Initial website"
git branch -M main
git remote add origin https://github.com/yourusername/gamemanager-website.git
git push -u origin main
```

### Step 3.3: Enable GitHub Pages

1. Repository → **Settings** → **Pages**
2. Source: **main branch** / **/ (root)**
3. Click **Save**
4. Wait 2-5 minutes

**Your site will be live at:**
```
https://yourusername.github.io/gamemanager-website
```

---

## ⚙️ Configuration Summary

### Local Development `.env`
```bash
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret
API_BASE_URL=
STORAGE_BASE_URL=
# Leave blank - auto-detects localhost:5000
```

### Production Backend (Render.com) Environment Variables
```bash
SECRET_KEY=<secure-random-key>
JWT_SECRET_KEY=<secure-random-key>
API_BASE_URL=https://gamemanager-api.onrender.com
STORAGE_BASE_URL=https://abc-def-ghi.trycloudflare.com
DATABASE_URL=<render-postgresql-url>
TELEGRAM_BOT_TOKEN=<your-token>
TELEGRAM_ADMIN_CHAT_ID=<your-chat-id>
GCASH_MERCHANT_NUMBER=<your-number>
RAWG_API_KEY=<your-key>
```

### Local File Storage Server
- Runs on your machine (persistent storage)
- Exposed via Cloudflare Tunnel
- Same Flask backend but serves files

---

## 🔄 How It Works

### Game Cover Image Flow

1. **Upload:**
   ```
   User → Frontend → Render API → Database (filename only)
   User → Local server (Cloudflare Tunnel) → Saves file to uploads/
   ```

2. **Retrieval:**
   ```
   Frontend → Render API → Returns: {
     "cover_image": "https://abc.trycloudflare.com/uploads/covers/12345.jpg",
     "cover_image_filename": "12345.jpg"
   }
   Frontend → Displays image from Cloudflare Tunnel URL
   ```

### Payment Screenshot Flow

1. **Upload:**
   ```
   User submits payment screenshot
   → Sent to Cloudflare Tunnel (local server)
   → Saved to backend/static/
   → URL: https://abc.trycloudflare.com/static/payment_12345.jpg
   ```

2. **Telegram Notification:**
   ```
   Render API → Sends notification to Telegram
   Image URL → https://abc.trycloudflare.com/static/payment_12345.jpg
   Admin clicks → Views image from Cloudflare Tunnel
   ```

---

## 🐛 Troubleshooting

### Backend Not Starting on Render

**Check logs:**
- Render Dashboard → Your Service → Logs tab

**Common issues:**
- Missing environment variables
- Wrong start command
- Database connection error

**Fix:**
- Verify all environment variables are set
- Ensure gunicorn is in requirements.txt
- Check DATABASE_URL format

### Cloudflare Tunnel Disconnects

**Issue:** Tunnel URL changes when restarted

**Solution:** Use a persistent tunnel with custom domain
```bash
# Create persistent tunnel
cloudflared tunnel create my-tunnel

# Route a domain
cloudflared tunnel route dns my-tunnel storage.yourdomain.com

# Run with config
cloudflared tunnel --config config.yml run my-tunnel
```

### Files Not Loading

**Check:**
1. Is Cloudflare Tunnel running?
   ```bash
   curl https://your-tunnel.trycloudflare.com/static/gcash_qr.jpg
   ```

2. Is `STORAGE_BASE_URL` set correctly on Render?

3. Are files in the correct folders?
   - `backend/uploads/covers/`
   - `backend/uploads/games/`
   - `backend/static/`

### Telegram Bot Not Responding

**Set webhook:**
```bash
curl -X POST https://gamemanager-api.onrender.com/api/telegram/set-webhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://gamemanager-api.onrender.com/api/telegram/webhook"}'
```

**Check webhook status:**
```bash
curl https://gamemanager-api.onrender.com/api/telegram/webhook-info
```

---

## 💰 Cost Breakdown (All FREE!)

| Service | Free Tier | Cost |
|---------|-----------|------|
| **Render (Backend API)** | 750 hours/month | $0 |
| **Render (PostgreSQL)** | 1GB, 90-day expiry | $0 |
| **Cloudflare Tunnel** | Unlimited | $0 |
| **GitHub Pages** | 1GB storage, 100GB bandwidth | $0 |
| **Total** | | **$0/month** |

**Note:** Render free tier sleeps after 15 minutes of inactivity (cold start ~30 seconds)

---

## 🔒 Security Best Practices

1. **Never commit .env files** to GitHub
2. **Use strong secret keys** (32+ bytes random)
3. **Enable HTTPS** everywhere (all services provide this)
4. **Rotate keys** periodically
5. **Monitor access logs** on Render
6. **Use environment variables** for all secrets

---

## 📊 Monitoring

### Render Dashboard
- **Metrics:** CPU, Memory, Response time
- **Logs:** Real-time application logs
- **Events:** Deploy history

### Cloudflare Tunnel
- **Status:** Check if tunnel is connected
  ```bash
  cloudflared tunnel info gamemanager-storage
  ```

### GitHub Pages
- **Traffic:** Repository → Insights → Traffic
- **Build Status:** Actions tab

---

## 🎯 Production Checklist

- [ ] Backend deployed to Render.com
- [ ] PostgreSQL database created and connected
- [ ] All environment variables set on Render
- [ ] Cloudflare Tunnel running on local machine
- [ ] Local backend serving files on port 5000
- [ ] `STORAGE_BASE_URL` set to Cloudflare Tunnel URL
- [ ] Website deployed to GitHub Pages
- [ ] Telegram webhook configured
- [ ] Test payment flow end-to-end
- [ ] Test file uploads (covers, games)
- [ ] Test game downloads
- [ ] Verify QR code displays
- [ ] Monitor Render logs for errors

---

## 🚦 Going Live

1. **Set Telegram Webhook:**
   ```bash
   curl -X POST https://gamemanager-api.onrender.com/api/telegram/set-webhook \
     -H "Content-Type: application/json" \
     -d '{"url": "https://gamemanager-api.onrender.com/api/telegram/webhook"}'
   ```

2. **Test the full flow:**
   - Visit your GitHub Pages site
   - Browse games
   - Initiate a payment
   - Check Telegram for notification
   - Verify/reject payment via Telegram buttons
   - Confirm game added to library

3. **Share your website:**
   ```
   https://yourusername.github.io/gamemanager-website
   ```

---

## 📞 Support

- **Backend Issues:** Check Render logs
- **File Storage Issues:** Check Cloudflare Tunnel status
- **Frontend Issues:** Check browser console
- **General:** Open GitHub issue

---

## 🎉 You're Done!

Your GameManager is now running with:
- ✅ API in the cloud (Render)
- ✅ Files on your local machine (Cloudflare Tunnel)
- ✅ Website hosted for free (GitHub Pages)
- ✅ Everything connected and working!

**Next Steps:**
- Customize your website design
- Add more games
- Promote to users
- Monitor and maintain

Happy gaming! 🎮✨
