# Quick Setup Guide - GameManager Website

## 🚀 5-Minute Setup

### Step 1: Create GitHub Repository (2 minutes)

1. Go to https://github.com/new
2. Repository name: `GameManager`
3. Public repository
4. Click "Create repository"

### Step 2: Upload Files (1 minute)

1. Click "uploading an existing file"
2. Drag ALL files from `GameManager-Website` folder
3. Commit message: "Initial upload"
4. Click "Commit changes"

### Step 3: Enable GitHub Pages (1 minute)

1. Go to Settings → Pages
2. Source: Branch `main`, Folder `/ (root)`
3. Click Save
4. Wait 2 minutes

### Step 4: Upload GameManager.exe (1 minute)

**Best Method: GitHub Releases**

1. Click "Releases" → "Create a new release"
2. Tag: `v1.0.0`
3. Title: `GameManager v1.0.0`
4. Attach file: Your entire `GameManager-win32-x64` folder (zipped)
5. Publish release

### Step 5: Update Download Link (30 seconds)

1. Get your release download URL:
   ```
   https://github.com/YOUR-USERNAME/GameManager/releases/download/v1.0.0/GameManager-win32-x64.zip
   ```

2. Edit `index.html`, find:
   ```html
   <a href="downloads/GameManager-Setup.exe"
   ```

3. Replace with:
   ```html
   <a href="https://github.com/YOUR-USERNAME/GameManager/releases/download/v1.0.0/GameManager-win32-x64.zip"
   ```

4. Commit change

## ✅ Done!

Your website is live at:
```
https://YOUR-USERNAME.github.io/GameManager
```

## 📦 Creating the ZIP File

**Option 1: Using Windows Explorer**
1. Navigate to `F:\GameManager\release-final\`
2. Right-click `GameManager-win32-x64` folder
3. Send to → Compressed (zipped) folder
4. Rename to `GameManager-Setup.zip`

**Option 2: Using 7-Zip**
1. Right-click `GameManager-win32-x64` folder
2. 7-Zip → Add to archive
3. Archive name: `GameManager-Setup.zip`
4. Format: ZIP
5. Click OK

## 🔗 Alternative: Google Drive

If GitHub Releases is too complicated:

1. Upload ZIP to Google Drive
2. Right-click → Share → Anyone with link
3. Get shareable link
4. Replace in `index.html`:
   ```html
   <a href="https://drive.google.com/uc?export=download&id=YOUR-FILE-ID"
   ```

## 🎯 To Get Your FILE-ID from Google Drive:

Your share link looks like:
```
https://drive.google.com/file/d/1A2B3C4D5E6F7G8H9I/view?usp=sharing
```

The FILE-ID is: `1A2B3C4D5E6F7G8H9I`

Use it like:
```
https://drive.google.com/uc?export=download&id=1A2B3C4D5E6F7G8H9I
```

## 🎨 Next Steps (Optional)

- Add screenshots to `images/` folder
- Customize colors in `css/style.css`
- Update content in `index.html`
- Add Google Analytics
- Setup custom domain

## 📞 Need Help?

Check the full `README.md` for detailed instructions!
