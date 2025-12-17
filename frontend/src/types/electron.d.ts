/**
 * Electron API Types
 */

interface ElectronAPI {
  // Window controls
  minimize: () => void;
  maximize: () => void;
  close: () => void;
  
  // Navigation
  onNavigate: (callback: (path: string) => void) => void;
  
  // Tray & Notifications
  updateTrayStats: (stats: { used: string; remaining: string }) => void;
  showNotification: (title: string, body: string) => void;
  
  // File operations
  exportFile: (data: string, filename: string) => Promise<string>;
  
  // Setup / Configuration
  isFirstRun: () => Promise<boolean>;
  getDataPath: () => Promise<string>;
  selectDataFolder: () => Promise<string | null>;
  completeSetup: (dataPath: string) => Promise<{ success: boolean; dataPath?: string; error?: string }>;
  openDataFolder: () => Promise<boolean>;
  
  // Platform
  platform: string;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

export {};
