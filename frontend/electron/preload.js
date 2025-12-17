/**
 * Electron Preload Script
 * -----------------------
 * Main process ile renderer arasında güvenli köprü.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Window controls
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),
  
  // Navigation from tray
  onNavigate: (callback) => {
    ipcRenderer.on('navigate', (_, path) => callback(path));
  },
  
  // Capture control
  getCaptureStatus: () => ipcRenderer.invoke('get-capture-status'),
  toggleCapture: () => ipcRenderer.invoke('toggle-capture'),
  onCaptureStatusChanged: (callback) => {
    ipcRenderer.on('capture-status-changed', (_, isRunning) => callback(isRunning));
  },
  
  // Focus stats update
  updateTrayStats: (stats) => {
    ipcRenderer.send('tray:update-stats', stats);
  },
  
  // Notifications
  showNotification: (title, body) => {
    ipcRenderer.send('notification:show', { title, body });
  },
  
  // File operations
  exportFile: (data, filename) => {
    return ipcRenderer.invoke('file:export', { data, filename });
  },
  
  // Setup / Configuration
  isFirstRun: () => ipcRenderer.invoke('setup:isFirstRun'),
  getDataPath: () => ipcRenderer.invoke('setup:getDataPath'),
  selectDataFolder: () => ipcRenderer.invoke('setup:selectFolder'),
  completeSetup: (dataPath) => ipcRenderer.invoke('setup:complete', dataPath),
  openDataFolder: () => ipcRenderer.invoke('setup:openDataFolder'),
  
  // Platform info
  platform: process.platform,
});
