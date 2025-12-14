/**
 * System Store
 * ------------
 * Sistem istatistikleri state yönetimi.
 */

import { create } from 'zustand';

interface SystemStats {
  cpu_percent: number;
  memory_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  disk_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  net_sent_mb: number;
  net_recv_mb: number;
  gpu_percent?: number;
  gpu_memory_percent?: number;
}

interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: Date;
}

interface SystemState {
  stats: SystemStats | null;
  isConnected: boolean;
  notifications: Notification[];
  updateStats: (stats: SystemStats) => void;
  setConnected: (connected: boolean) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

export const useSystemStore = create<SystemState>((set) => ({
  stats: null,
  isConnected: false,
  notifications: [],
  
  updateStats: (stats) => set({ stats }),
  
  setConnected: (connected) => set({ isConnected: connected }),
  
  addNotification: (notification) => set((state) => ({
    notifications: [
      {
        ...notification,
        id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
        timestamp: new Date(),
      },
      ...state.notifications,
    ].slice(0, 10), // Max 10 notification
  })),
  
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter((n) => n.id !== id),
  })),
  
  clearNotifications: () => set({ notifications: [] }),
}));




