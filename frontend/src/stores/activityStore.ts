/**
 * Activity Store
 * --------------
 * Aktivite state yönetimi.
 */

import { create } from 'zustand';

interface Activity {
  id: string;
  timestamp: string;
  summary: string;
  tags: string[];
}

interface ActivityState {
  activities: Activity[];
  addActivity: (activity: Activity) => void;
  setActivities: (activities: Activity[]) => void;
  clearActivities: () => void;
}

export const useActivityStore = create<ActivityState>((set) => ({
  activities: [],
  
  addActivity: (activity) => set((state) => ({
    activities: [activity, ...state.activities].slice(0, 100), // Max 100 aktivite tut
  })),
  
  setActivities: (activities) => set({ activities }),
  
  clearActivities: () => set({ activities: [] }),
}));
