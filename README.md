# GameManager Download Website

A beautiful, modern landing page for GameManager - your personal game library and store with GCash payment integration.

## 🌐 Live Demo

Once deployed, your website will be available at: `https://YOUR-USERNAME.github.io/GameManager`

## 🎮 About GameManager

GameManager is a comprehensive game library and store platform that allows users to:
- Browse and purchase games with GCash payment integration
- Manage their personal game library with automatic cover artwork
- Connect with friends and see what they're playing
- Request new games to be added to the store
- Track payment history and download receipts
- Auto-detect and scan games from folders

## ✨ Website Features

- **Modern Design**: Beautiful, dark-themed UI inspired by gaming platforms
- **Responsive**: Works perfectly on desktop, tablet, and mobile devices
- **Fast Loading**: Lightweight and optimized for performance
- **SEO Optimized**: Proper meta tags and semantic HTML for Philippines market
- **Interactive**: Smooth animations and FAQ accordion
- **Download Ready**: Direct download link for GameManager installer
- **Complete Documentation**: Comprehensive FAQ covering payments, features, and setup

## 📁 Project Structure

```
GameManager-Website/
├── index.html           # Main landing page
├── css/
│   └── style.css       # Styles and animations
├── js/
│   └── script.js       # Interactive features
├── images/             # Images and screenshots (add your own)
├── downloads/          # GameManager.exe goes here
└── README.md           # This file
```

## 🚀 Setup Instructions

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the **"+"** icon → **"New repository"**
3. Repository name: `GameManager` (or any name you prefer)
4. Description: "Your personal game library manager"
5. Make it **Public**
6. Click **"Create repository"**

### Step 2: Upload Website Files

**Option A: Using GitHub Web Interface**

1. In your new repository, click **"uploading an existing file"**
2. Drag and drop all files from `GameManager-Website` folder:
   - `index.html`
   - `css/` folder with `style.css`
   - `js/` folder with `script.js`
   - `images/` folder (add screenshots if you have)
   - `README.md`
3. Commit message: "Initial website upload"
4. Click **"Commit changes"**

**Option B: Using Git Command Line**

```bash
cd F:\GameManager\GameManager-Website

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial website upload"

# Add remote (replace YOUR-USERNAME and REPO-NAME)
git remote add origin https://github.com/YOUR-USERNAME/GameManager.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Upload GameManager.exe

Since GitHub has a 100MB file size limit for regular files, you have **3 options**:

#### Option 1: GitHub Releases (Recommended)

1. In your repository, click **"Releases"** → **"Create a new release"**
2. Tag version: `v1.0.0`
3. Release title: `GameManager v1.0.0`
4. Description: Add release notes
5. Click **"Attach binaries by dropping them here"**
6. Upload **entire folder**: `GameManager-win32-x64`
7. Or create a ZIP:
   ```bash
   # Navigate to release-final folder
   cd F:\GameManager\release-final

   # Create ZIP of GameManager folder
   # (Use 7-Zip or WinRAR to create: GameManager-Setup.zip)
   ```
8. Upload the ZIP file
9. Click **"Publish release"**

The download URL will be:
```
https://github.com/YOUR-USERNAME/GameManager/releases/download/v1.0.0/GameManager-Setup.zip
```

#### Option 2: Git LFS (Large File Storage)

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.exe"
git lfs track "*.zip"

# Add .gitattributes
git add .gitattributes

# Add your GameManager.exe
cd downloads
# Copy GameManager.exe here
git add GameManager-Setup.exe
git commit -m "Add GameManager executable"
git push
```

#### Option 3: External Hosting

Host the file on:
- **Google Drive** (make public link)
- **Dropbox** (create share link)
- **OneDrive** (get share link)
- **MediaFire** (upload and get link)

Then update the download link in `index.html`.

### Step 4: Enable GitHub Pages

1. Go to your repository **Settings**
2. Scroll to **"Pages"** section (left sidebar)
3. Under **"Source"**, select:
   - Branch: `main`
   - Folder: `/ (root)`
4. Click **"Save"**
5. Wait 1-2 minutes
6. Your site will be live at: `https://YOUR-USERNAME.github.io/GameManager`

### Step 5: Update Download Links

1. Open `index.html`
2. Find all instances of:
   ```html
   <a href="downloads/GameManager-Setup.exe" ...>
   ```

3. Replace with your actual download URL:

   **If using GitHub Releases:**
   ```html
   <a href="https://github.com/YOUR-USERNAME/GameManager/releases/download/v1.0.0/GameManager-Setup.zip" ...>
   ```

   **If using Google Drive:**
   ```html
   <a href="https://drive.google.com/uc?export=download&id=YOUR-FILE-ID" ...>
   ```

   **If using Dropbox:**
   ```html
   <a href="https://www.dropbox.com/s/YOUR-LINK/GameManager-Setup.zip?dl=1" ...>
   ```

4. Commit and push the changes:
   ```bash
   git add index.html
   git commit -m "Update download links"
   git push
   ```

## 🎨 Customization

### Add Screenshots

1. Take screenshots of GameManager running
2. Save them in the `images/` folder
3. Update `index.html` to include them:
   ```html
   <img src="images/screenshot-1.png" alt="GameManager Library">
   ```

### Change Colors

Edit `css/style.css` and modify the CSS variables:

```css
:root {
    --primary-color: #5865F2;  /* Change to your brand color */
    --background: #0F1419;     /* Main background */
    /* ... other colors ... */
}
```

### Update Content

Edit `index.html` to change:
- Feature descriptions
- FAQ answers
- System requirements
- Download size and version number

### Add Analytics (Optional)

Add Google Analytics or similar:

```html
<!-- Add before </head> in index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR-GA-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR-GA-ID');
</script>
```

## 📝 Updating the Website

Whenever you want to update the website:

```bash
# Make your changes to the files

# Commit
git add .
git commit -m "Your update message"

# Push to GitHub
git push

# GitHub Pages will automatically update in 1-2 minutes
```

## 🔗 Download Link Best Practices

### Option 1: GitHub Releases (Best for Version Control)

✅ **Pros:**
- Proper versioning (v1.0.0, v1.1.0, etc.)
- Changelog support
- Download statistics
- Professional appearance
- No file size limits (within reason)

❌ **Cons:**
- Requires manual upload for each version

**How to use:**
1. Create releases as shown in Step 3
2. Update download link in HTML:
   ```html
   <a href="https://github.com/YOUR-USERNAME/GameManager/releases/latest/download/GameManager-Setup.zip">
   ```

### Option 2: Direct Link (Simplest)

If your EXE is under 100MB:

```bash
# Add to downloads folder
cd GameManager-Website/downloads
# Copy your GameManager.exe here

# Commit
git add downloads/
git commit -m "Add GameManager executable"
git push
```

Update HTML:
```html
<a href="downloads/GameManager.exe" download>
```

### Option 3: Cloud Storage (Most Flexible)

Use for large files or frequent updates:

1. Upload to Google Drive/Dropbox
2. Get shareable link
3. Update HTML with the link

## 🐛 Troubleshooting

### Website not showing up?

1. Check GitHub Pages settings (Settings → Pages)
2. Ensure branch is set to `main` and folder to `/ (root)`
3. Wait 2-5 minutes after first setup
4. Clear browser cache and try again

### Download not working?

1. Check if file exists at the specified path
2. Verify file size is under GitHub's limits
3. Test the download URL directly in browser
4. Check browser console for errors (F12)

### Styling looks broken?

1. Check if `css/style.css` is uploaded correctly
2. Verify file paths in `index.html`
3. Clear browser cache
4. Check browser console for 404 errors

### Images not loading?

1. Ensure images are in the `images/` folder
2. Check file paths are correct
3. File names are case-sensitive on GitHub Pages

## 📊 Monitoring

Track your website's performance:

1. **GitHub Traffic**
   - Repository → Insights → Traffic
   - See page views and unique visitors

2. **Download Statistics** (GitHub Releases)
   - Repository → Releases
   - Each release shows download count

3. **Google Analytics** (if added)
   - Real-time visitor tracking
   - Geographic data
   - User behavior

## 🔒 Security Notes

- Never commit sensitive information (API keys, passwords)
- Don't upload your backend `.env` file
- Keep your database file local
- Use environment variables for secrets

## 📱 Mobile Optimization

The website is already responsive, but test on:
- iPhone (Safari)
- Android (Chrome)
- iPad (Safari)
- Various screen sizes

Use browser DevTools to test:
- Press F12
- Click "Toggle Device Toolbar" (Ctrl+Shift+M)
- Test different device sizes

## 🚀 Going Live Checklist

Before announcing your website:

- [ ] All download links work
- [ ] Screenshots/images look good
- [ ] FAQ section is complete
- [ ] System requirements are accurate
- [ ] Contact information is correct
- [ ] All links work (no 404s)
- [ ] Tested on mobile devices
- [ ] Tested on different browsers
- [ ] Version numbers are correct
- [ ] Added analytics (optional)
- [ ] Custom domain setup (optional)

## 🌐 Custom Domain (Optional)

Want `gamemanager.com` instead of `username.github.io/GameManager`?

1. Buy a domain (Namecheap, GoDaddy, Google Domains)
2. In repository Settings → Pages
3. Add custom domain
4. Update DNS records as instructed
5. Enable HTTPS

## 💡 Tips

1. **Update regularly**: Keep version numbers current
2. **Add changelog**: List what's new in each version
3. **Screenshots**: Show your app in action
4. **Testimonials**: Add user reviews (if available)
5. **Social proof**: Add GitHub stars badge

## 📞 Support

If you need help:
1. Check GitHub Pages documentation
2. Open an issue in your repository
3. Check browser console for errors
4. Test in incognito/private mode

## 🎉 You're Done!

Your website is now live and ready to share!

**Share your website:**
```
https://YOUR-USERNAME.github.io/GameManager
```

**Promote on:**
- Social media
- Gaming forums
- Reddit
- Discord servers
- Gaming communities

Good luck with your GameManager project! 🎮✨
