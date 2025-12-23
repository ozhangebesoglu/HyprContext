/**
 * API Hook
 * --------
 * REST API çağrıları için hook'lar.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { Activity, ActivityStats, FocusStats, FocusCheck, Plan, Report, Profile } from '../types/api';

const API_BASE = 'http://localhost:8000/api';

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Bir hata oluştu' }));
    throw new Error(error.detail || 'API hatası');
  }

  return response.json();
}

// Activities
export function useActivities(date?: string, limit = 50) {
  const params = new URLSearchParams();
  if (date) params.append('date', date);
  params.append('limit', String(limit));
  
  return useQuery<Activity[]>({
    queryKey: ['activities', date, limit],
    queryFn: () => fetchApi<Activity[]>(`/activities?${params}`),
  });
}

export function useSearchActivities(query: string) {
  return useQuery<Activity[]>({
    queryKey: ['activities', 'search', query],
    queryFn: () => fetchApi<Activity[]>(`/activities/search?q=${encodeURIComponent(query)}`),
    enabled: query.length >= 2,
  });
}

export function useActivityStats() {
  return useQuery<ActivityStats>({
    queryKey: ['activities', 'stats'],
    queryFn: () => fetchApi<ActivityStats>('/activities/stats'),
  });
}

// Plans
export function usePlans() {
  return useQuery<Plan[]>({
    queryKey: ['plans'],
    queryFn: () => fetchApi<Plan[]>('/plans'),
  });
}

export function useTodayPlan() {
  return useQuery<Plan>({
    queryKey: ['plans', 'today'],
    queryFn: () => fetchApi<Plan>('/plans/today'),
  });
}

export function usePlan(date: string) {
  return useQuery<Plan>({
    queryKey: ['plans', date],
    queryFn: () => fetchApi<Plan>(`/plans/${date}`),
    enabled: !!date,
  });
}

export function useGeneratePlan() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { user_note?: string; active_course?: string; weather?: string }) =>
      fetchApi('/plans/generate', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
    },
  });
}

export function useUpdatePlan() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ date, content, mission }: { date: string; content: string; mission?: string }) =>
      fetchApi(`/plans/${date}`, {
        method: 'PUT',
        body: JSON.stringify({ content, mission }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
    },
  });
}

// Reports
export function useReports() {
  return useQuery<Report[]>({
    queryKey: ['reports'],
    queryFn: () => fetchApi<Report[]>('/reports'),
  });
}

export function useReport(date: string) {
  return useQuery<Report>({
    queryKey: ['reports', date],
    queryFn: () => fetchApi<Report>(`/reports/${date}`),
    enabled: !!date,
  });
}

export function useGenerateReport() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (date?: string) =>
      fetchApi<Report>('/reports/generate', {
        method: 'POST',
        body: JSON.stringify({ date }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
  });
}

export function useExportReport() {
  return useMutation({
    mutationFn: ({ date, path }: { date: string; path: string }) =>
      fetchApi(`/reports/${date}/export`, {
        method: 'POST',
        body: JSON.stringify({ path }),
      }),
  });
}

export function useExportPlan() {
  return useMutation({
    mutationFn: ({ date, path }: { date: string; path: string }) =>
      fetchApi(`/plans/${date}/export`, {
        method: 'POST',
        body: JSON.stringify({ path }),
      }),
  });
}

// Focus
export function useFocusStats() {
  return useQuery<FocusStats>({
    queryKey: ['focus', 'stats'],
    queryFn: () => fetchApi<FocusStats>('/focus/stats'),
    refetchInterval: 5000, // 5 saniyede bir güncelle
  });
}

export function useFocusCheck() {
  return useQuery<FocusCheck>({
    queryKey: ['focus', 'check'],
    queryFn: () => fetchApi<FocusCheck>('/focus/check'),
    refetchInterval: 1000, // Her saniye kontrol
  });
}

// Chat
export function useChat() {
  return useMutation({
    mutationFn: (data: { message: string; context?: string; include_memory?: boolean }) =>
      fetchApi('/chat', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  });
}

// Control - Capture başlat/durdur
export interface ControlStatus {
  running: boolean;
  capture_active: boolean;
  focus_active: boolean;
  uptime_seconds?: number | null;
  last_activity?: string;
  today_count?: number;
}

export function useControlStatus() {
  return useQuery<ControlStatus>({
    queryKey: ['control', 'status'],
    queryFn: () => fetchApi<ControlStatus>('/control/status'),
    refetchInterval: 3000, // 3 saniyede bir güncelle
  });
}

export function useStartCapture() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () =>
      fetchApi('/control/start', {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['control', 'status'] });
    },
  });
}

export function useStopCapture() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      fetchApi('/control/stop', {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['control', 'status'] });
    },
  });
}

export function useRestartCapture() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      fetchApi('/control/restart', {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['control', 'status'] });
    },
  });
}

// Profile - Courses
export interface Course {
  isim: string;
  durum: string;
  sure?: string;
  platform?: string;
}

export function useCourses() {
  return useQuery<{ courses: Course[] }>({
    queryKey: ['profile', 'courses'],
    queryFn: () => fetchApi<{ courses: Course[] }>('/profile/courses'),
  });
}

export function useAddCourse() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (course: { isim: string; platform: string; durum?: string }) =>
      fetchApi('/profile/courses', {
        method: 'POST',
        body: JSON.stringify(course),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile', 'courses'] });
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });
}

export function useDeleteCourse() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (courseName: string) =>
      fetchApi(`/profile/courses/${encodeURIComponent(courseName)}`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile', 'courses'] });
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });
}

// Profile - Banned Keywords
export function useBannedKeywords() {
  return useQuery<string[]>({
    queryKey: ['profile', 'banned-keywords'],
    queryFn: () => fetchApi<string[]>('/profile/banned-keywords'),
  });
}

export function useUpdateBannedKeywords() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (keywords: string[]) =>
      fetchApi('/profile/banned-keywords', {
        method: 'PUT',
        body: JSON.stringify({ keywords }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile', 'banned-keywords'] });
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });
}

// Focus - Reset
export function useFocusReset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      fetchApi('/focus/reset', {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['focus'] });
    },
  });
}

// Config - Data Path
export interface ConfigDataPath {
  data_path: string;
  screenshots_dir: string;
  plans_dir: string;
  reports_dir: string;
  chroma_db_path: string;
}

export function useConfigDataPath() {
  return useQuery<ConfigDataPath>({
    queryKey: ['config', 'data-path'],
    queryFn: () => fetchApi<ConfigDataPath>('/config/data-path'),
  });
}

export function useUpdateConfigDataPath() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (dataPath: string) =>
      fetchApi('/config/data-path', {
        method: 'POST',
        body: JSON.stringify({ data_path: dataPath }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['config'] });
    },
  });
}

// Chat - Streaming
export function useChatStream() {
  return {
    streamChat: async function* (data: { message: string; context?: string; include_memory?: boolean }) {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Stream başlatılamadı');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Stream okunamadı');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        yield chunk;
      }
    },
  };
}
