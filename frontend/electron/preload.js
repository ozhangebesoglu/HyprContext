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
  
  // Platform info
  platform: process.platform,
});
