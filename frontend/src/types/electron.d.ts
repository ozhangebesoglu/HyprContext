/**
 * Electron API Types
 */

interface ElectronAPI {
  minimize: () => void;
  maximize: () => void;
  close: () => void;
  onNavigate: (callback: (path: string) => void) => void;
  updateTrayStats: (stats: { used: string; remaining: string }) => void;
  showNotification: (title: string, body: string) => void;
  exportFile: (data: string, filename: string) => Promise<string>;
  platform: string;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

export {};
