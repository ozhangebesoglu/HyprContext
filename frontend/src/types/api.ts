/**
 * API Types
 * ---------
 * Backend API'den gelen veri tipleri.
 */

// Activity
export interface Activity {
  id: string;
  timestamp: string;
  summary: string;
  tags: string[];
  window_title?: string;
  app_name?: string;
}

export interface DayData {
  day: string;
  activities: number;
}

export interface ActivityStats {
  total_activities: number;
  total_days: number;
  activities_per_day: number;
  top_tags: [string, number][];
  today_count?: number;
  by_hour?: Record<string, number>;
  by_day?: DayData[];
}

// Focus
export interface FocusStats {
  percentage: number;
  used_seconds: number;
  daily_limit_seconds: number;
  remaining_seconds: number;
  limit_reached: boolean;
  formatted_used: string;
  formatted_remaining: string;
}

export interface FocusCheck {
  is_distracted: boolean;
  keyword?: string;
  message?: string;
}

// Plan
export interface Plan {
  date: string;
  mission?: string;
  content: string;
  tasks?: PlanTask[];
  created_at?: string;
  updated_at?: string;
}

export interface PlanTask {
  time: string;
  task: string;
  completed: boolean;
}

// Report
export interface Report {
  id: string;
  date: string;
  summary: string;
  content: string;
  technologies: string[];
  activity_count: number;
  focus_percentage?: number;
  created_at?: string;
}

// Profile
export interface Profile {
  user: {
    name: string;
    profession: string;
  };
  daily_limits: {
    distraction_minutes: number;
  };
  banned_keywords: string[];
  courses: Course[];
}

export interface Course {
  name: string;
  platform: string;
  progress: number;
  active?: boolean;
}

// System
export interface SystemStats {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
}

export interface ControlStatus {
  is_running: boolean;
  capture_interval: number;
  last_capture?: string;
}

// Notification
export interface AppNotification {
  id?: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp?: string;
}

// WebSocket Messages
export interface WSMessage {
  type: 'activity' | 'focus_update' | 'distraction_warning' | 'system_stats' | 'course_detected' | 'pong';
  data?: any;
}
