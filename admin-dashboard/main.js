const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1200,
        minHeight: 700,
        frame: false,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        },
        icon: path.join(__dirname, 'src/assets/icon.png')
    });

    mainWindow.loadFile(path.join(__dirname, 'src/pages/login.html'));

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

// IPC Handlers
ipcMain.on('minimize-window', () => {
    if (mainWindow) mainWindow.minimize();
});

ipcMain.on('maximize-window', () => {
    if (mainWindow) {
        if (mainWindow.isMaximized()) {
            mainWindow.unmaximize();
        } else {
            mainWindow.maximize();
        }
    }
});

ipcMain.on('close-window', () => {
    if (mainWindow) mainWindow.close();
});

ipcMain.on('navigate', (event, page) => {
    if (mainWindow) {
        mainWindow.loadFile(path.join(__dirname, 'src/pages', page));
    }
});

// File operations
ipcMain.handle('read-file', async (event, filePath) => {
    try {
        const data = fs.readFileSync(filePath);
        return { success: true, data: data.toString('base64') };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('write-file', async (event, filePath, data) => {
    try {
        const buffer = Buffer.from(data, 'base64');
        fs.writeFileSync(filePath, buffer);
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('delete-file', async (event, filePath) => {
    try {
        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
            return { success: true };
        }
        return { success: false, error: 'File not found' };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('check-file-exists', async (event, filePath) => {
    try {
        return { success: true, exists: fs.existsSync(filePath) };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

// Directory operations
ipcMain.handle('list-directory', async (event, dirPath) => {
    try {
        const files = fs.readdirSync(dirPath);
        const fileStats = files.map(file => {
            const filePath = path.join(dirPath, file);
            const stats = fs.statSync(filePath);
            return {
                name: file,
                path: filePath,
                isDirectory: stats.isDirectory(),
                size: stats.size,
                modified: stats.mtime
            };
        });
        return { success: true, files: fileStats };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

console.log('GameManager Admin Dashboard started');
