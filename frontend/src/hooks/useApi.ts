/**
 * API Hook
 * --------
 * REST API çağrıları için hook'lar.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

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
  
  return useQuery({
    queryKey: ['activities', date, limit],
    queryFn: () => fetchApi(`/activities?${params}`),
  });
}

export function useSearchActivities(query: string) {
  return useQuery({
    queryKey: ['activities', 'search', query],
    queryFn: () => fetchApi(`/activities/search?q=${encodeURIComponent(query)}`),
    enabled: query.length >= 2,
  });
}

export function useActivityStats() {
  return useQuery({
    queryKey: ['activities', 'stats'],
    queryFn: () => fetchApi('/activities/stats'),
  });
}

// Plans
export function usePlans() {
  return useQuery({
    queryKey: ['plans'],
    queryFn: () => fetchApi('/plans'),
  });
}

export function useTodayPlan() {
  return useQuery({
    queryKey: ['plans', 'today'],
    queryFn: () => fetchApi('/plans/today'),
  });
}

export function usePlan(date: string) {
  return useQuery({
    queryKey: ['plans', date],
    queryFn: () => fetchApi(`/plans/${date}`),
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
  return useQuery({
    queryKey: ['reports'],
    queryFn: () => fetchApi('/reports'),
  });
}

export function useGenerateReport() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (date?: string) =>
      fetchApi('/reports/generate', {
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

// Focus
export function useFocusStats() {
  return useQuery({
    queryKey: ['focus', 'stats'],
    queryFn: () => fetchApi('/focus/stats'),
    refetchInterval: 5000, // 5 saniyede bir güncelle
  });
}

export function useFocusCheck() {
  return useQuery({
    queryKey: ['focus', 'check'],
    queryFn: () => fetchApi('/focus/check'),
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
