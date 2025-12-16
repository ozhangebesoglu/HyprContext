/**
 * Electron Main Process
 * ---------------------
 * Masaüstü uygulaması ana pencere yönetimi.
 */

const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain } = require('electron');
const path = require('path');
const http = require('http');

let mainWindow = null;
let tray = null;
let isCapturing = false;

// DÜZELTİLDİ: Uygulama paketlenmişse (AppImage) production modunda çalışır.
const isDev = !app.isPackaged;

const API_BASE = 'http://localhost:8000/api';

// --- Yardımcı Fonksiyonlar ---

function apiRequest(endpoint, method = 'GET') {
  return new Promise((resolve, reject) => {
    const url = new URL(`${API_BASE}${endpoint}`);
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: method,
      headers: { 'Content-Type': 'application/json' },
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch {
          resolve(data);
        }
      });
    });

    req.on('error', reject);
    req.end();
  });
}

// Check capture status periodically
async function updateCaptureStatus() {
  try {
    const status = await apiRequest('/control/status');
    // Eğer status.running undefined gelirse false varsayalım
    isCapturing = status ? status.running : false;
    updateTrayMenu();
  } catch (error) {
    console.error('Failed to get capture status:', error);
  }
}

// --- Pencere ve Tray Yönetimi ---

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    frame: false, // Özel başlık çubuğu için çerçevesiz
    transparent: true, 
    vibrancy: 'under-window', 
    visualEffectState: 'active',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    // İkon yolu: Dev modunda src'den, Prod modunda dist'ten veya build resources'dan
    icon: path.join(__dirname, isDev ? '../src/assets/icon.png' : '../dist/assets/icon.png'),
  });

  // URL Yükleme Mantığı (DÜZELTİLDİ)
  if (isDev) {
    console.log('Geliştirme Modu: localhost yükleniyor...');
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    console.log('Production Modu: index.html yükleniyor...');
    // dist klasöründeki dosyayı yükle
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createTray() {
  const iconPath = path.join(__dirname, '../src/assets/tray-icon.png');
  let icon;
  try {
    icon = nativeImage.createFromPath(iconPath);
    if (icon.isEmpty()) {
      icon = nativeImage.createEmpty();
    }
  } catch {
    icon = nativeImage.createEmpty();
  }
  
  tray = new Tray(icon.isEmpty() ? nativeImage.createEmpty() : icon.resize({ width: 16, height: 16 }));
  tray.setToolTip('HyprContext');
  updateTrayMenu();

  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

function updateTrayMenu() {
  if (!tray) return;
  
  const iconName = isCapturing ? 'tray-icon-active.png' : 'tray-icon.png';
  const iconPath = path.join(__dirname, '../src/assets/', iconName);
  try {
    const icon = nativeImage.createFromPath(iconPath);
    if (!icon.isEmpty()) {
      tray.setImage(icon.resize({ width: 16, height: 16 }));
    }
  } catch (error) {
    console.error('Failed to update tray icon:', error);
  }
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '📊 Göster',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      },
    },
    { type: 'separator' },
    {
      label: isCapturing ? '⏸️ Durdur' : '▶️ Başlat',
      click: async () => {
        try {
          const endpoint = isCapturing ? '/control/stop' : '/control/start';
          await apiRequest(endpoint, 'POST');
          isCapturing = !isCapturing;
          updateTrayMenu();
          if (mainWindow) {
            mainWindow.webContents.send('capture-status-changed', isCapturing);
          }
        } catch (error) {
          console.error('Failed to toggle capture:', error);
        }
      },
    },
    {
      label: isCapturing ? '🟢 Çalışıyor' : '🔴 Durdu',
      enabled: false,
    },
    { type: 'separator' },
    {
      label: '📅 Planlar',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.webContents.send('navigate', '/plans');
        }
      },
    },
    {
      label: '📄 Raporlar',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.webContents.send('navigate', '/reports');
        }
      },
    },
    { type: 'separator' },
    {
      label: '⚙️ Ayarlar',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.webContents.send('navigate', '/settings');
        }
      },
    },
    { type: 'separator' },
    {
      label: '❌ Çıkış',
      click: () => {
        app.isQuitting = true;
        app.quit();
      },
    },
  ]);

  tray.setContextMenu(contextMenu);
  tray.setToolTip(`HyprContext - ${isCapturing ? 'Çalışıyor' : 'Durdu'}`);
}

// --- Uygulama Döngüsü ---

app.whenReady().then(() => {
  createWindow();
  createTray();
  
  // İlk durum kontrolü
  if (typeof updateCaptureStatus === 'function') {
      updateCaptureStatus();
      setInterval(updateCaptureStatus, 5000);
  } else {
      console.error("KRİTİK HATA: updateCaptureStatus fonksiyonu bulunamadı!");
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// --- IPC Handlers ---

ipcMain.handle('get-capture-status', async () => {
  try {
    const status = await apiRequest('/control/status');
    return status;
  } catch (error) {
    return { running: false, error: error.message };
  }
});

ipcMain.handle('toggle-capture', async () => {
  try {
    const endpoint = isCapturing ? '/control/stop' : '/control/start';
    await apiRequest(endpoint, 'POST');
    isCapturing = !isCapturing;
    updateTrayMenu();
    return { success: true, running: isCapturing };
  } catch (error) {
    return { success: false, error: error.message };
  }
});