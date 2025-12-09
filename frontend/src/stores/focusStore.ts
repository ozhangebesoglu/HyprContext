/**
 * Focus Store
 * -----------
 * Odak state yönetimi.
 */

import { create } from 'zustand';

interface FocusStats {
  used_seconds: number;
  remaining_seconds: number;
  percentage: number;
  limit_reached: boolean;
  formatted_used: string;
  formatted_remaining: string;
  daily_limit_seconds: number;
}

interface FocusState {
  stats: FocusStats | null;
  isDistracted: boolean;
  distractionKeyword: string | null;
  updateStats: (stats: Partial<FocusStats> & { is_distracted?: boolean; keyword?: string }) => void;
  setDistraction: (isDistracted: boolean, keyword?: string) => void;
}

export const useFocusStore = create<FocusState>((set) => ({
  stats: null,
  isDistracted: false,
  distractionKeyword: null,
  
  updateStats: (data) => set((state) => ({
    stats: state.stats ? { ...state.stats, ...data } : data as FocusStats,
    isDistracted: data.is_distracted ?? state.isDistracted,
    distractionKeyword: data.keyword ?? state.distractionKeyword,
  })),
  
  setDistraction: (isDistracted, keyword) => set({
    isDistracted,
    distractionKeyword: keyword ?? null,
  }),
}));
