const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 720,
        minWidth: 1024,
        minHeight: 600,
        frame: false,
        backgroundColor: '#1b2838',
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        }
    });

    mainWindow.loadFile('src/pages/login.html');

    // Open DevTools in development
    if (process.argv.includes('--dev')) {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', function () {
    if (mainWindow === null) {
        createWindow();
    }
});

// IPC Handlers

// Window controls
ipcMain.on('window-minimize', () => {
    mainWindow.minimize();
});

ipcMain.on('window-maximize', () => {
    if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
    } else {
        mainWindow.maximize();
    }
});

ipcMain.on('window-close', () => {
    mainWindow.close();
});

// Navigate to different pages
ipcMain.on('navigate', (event, page) => {
    mainWindow.loadFile(`src/pages/${page}.html`);
});

// Launch game
ipcMain.on('launch-game', (event, gamePath) => {
    if (!fs.existsSync(gamePath)) {
        event.reply('game-launch-error', 'Game executable not found');
        return;
    }

    exec(`"${gamePath}"`, (error) => {
        if (error) {
            event.reply('game-launch-error', error.message);
        } else {
            event.reply('game-launched');
        }
    });
});

// Install game
ipcMain.on('install-game', (event, { gameId, installerPath, installLocation }) => {
    // This is a simplified version - you'd want to handle different installer types
    const installPath = path.join(installLocation, `game_${gameId}`);

    // Create install directory
    if (!fs.existsSync(installPath)) {
        fs.mkdirSync(installPath, { recursive: true });
    }

    // For .exe or .msi installers, we'd run them
    // For .zip files, we'd extract them
    // This is a placeholder - real implementation would be more complex

    exec(`"${installerPath}" /S /D="${installPath}"`, (error) => {
        if (error) {
            event.reply('install-error', error.message);
        } else {
            event.reply('install-complete', { gameId, installPath });
        }
    });
});

// Get system info
ipcMain.handle('get-system-info', async () => {
    const os = require('os');
    return {
        platform: os.platform(),
        arch: os.arch(),
        totalMemory: os.totalmem(),
        freeMemory: os.freemem(),
        cpus: os.cpus()
    };
});

// File operations
ipcMain.handle('select-directory', async () => {
    const { dialog } = require('electron');
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory']
    });
    return result.filePaths[0];
});

ipcMain.handle('file-exists', async (event, filePath) => {
    return fs.existsSync(filePath);
});
