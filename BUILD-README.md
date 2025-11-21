# GameManager Build Instructions

This document explains how to build the GameManager executables.

## Prerequisites

- **Node.js** (v16 or higher) - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js)

## Quick Build (Recommended)

### Option 1: Windows Command Prompt / PowerShell
```cmd
build-all.bat
```

### Option 2: Git Bash / WSL
```bash
bash build-all.sh
```

This will build both applications:
- **GameManager.exe** (User Client)
- **GameManagerAdmin.exe** (Admin Dashboard)

## Build Output Locations

After building, you'll find the executables at:

### GameManager (User Client)
```
F:\GameManager\frontend\dist\win-unpacked\GameManager.exe
```

### GameManagerAdmin (Admin Dashboard)
```
F:\GameManager\admin-dashboard\dist\win-unpacked\GameManagerAdmin.exe
```

## Individual Builds

### Build only GameManager (User Client)
```bash
cd frontend
npm install          # Only needed first time
npm run build:win
```

### Build only GameManagerAdmin (Admin Dashboard)
```bash
cd admin-dashboard
npm install          # Only needed first time
npm run build
```

## Clean Build

If you encounter issues, try a clean build:

```bash
# For GameManager
cd frontend
rmdir /s /q node_modules dist
npm install
npm run build:win

# For GameManagerAdmin
cd admin-dashboard
rmdir /s /q node_modules dist
npm install
npm run build
```

## Build Options

### Using electron-packager (Alternative for Admin)
```bash
cd admin-dashboard
npm run package
```
Output: `F:\GameManager\release\GameManagerAdmin-win32-x64\GameManagerAdmin.exe`

## Troubleshooting

### "npm is not recognized"
- Make sure Node.js is installed and added to PATH
- Restart your terminal after installing Node.js

### Build fails with permission errors
- Run the build script as Administrator
- Close GameManager.exe and GameManagerAdmin.exe if they're running

### Build is very slow
- First build takes longer as it downloads dependencies
- Subsequent builds are faster (uses cache)

### "Cannot find module" errors
- Delete `node_modules` folder
- Run `npm install` again
- Try building again

## Distribution

To distribute the apps:

1. Copy the entire `dist/win-unpacked` folder for each app
2. Users can run the `.exe` directly from that folder
3. Optionally, create installers using electron-builder's installer targets

### Creating Installers (Optional)

Modify `package.json` to use NSIS installer:

```json
"win": {
  "target": ["nsis"],
  "sign": false
}
```

Then run the build scripts again. This will create `.exe` installers.

## Backend Requirements

Remember, the built applications require the Flask backend to be running:

```bash
cd backend
python run.py
```

The backend runs at: `http://localhost:5000`
