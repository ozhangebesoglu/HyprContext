/**
 * Main App Component
 */

// DÜZELTME: BrowserRouter yerine HashRouter import ediyoruz.
import { useState, useEffect } from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { HomePage } from './pages/HomePage';
import { CommentsPage } from './pages/CommentsPage';
import { GraphsPage } from './pages/GraphsPage';
import { PlansPage } from './pages/PlansPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';
import { NotificationToast } from './components/features/NotificationToast';
import { useWebSocket } from './hooks/useWebSocket';
import { useTheme } from './hooks/useTheme';

// React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 dakika
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Backend bağlantı kontrolü
function BackendCheck({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch('http://localhost:8000/health', { 
          method: 'GET',
          signal: AbortSignal.timeout(3000)
        });
        if (res.ok) {
          setStatus('connected');
          setRetryCount(0);
        } else {
          setStatus('disconnected');
          setRetryCount(prev => prev + 1);
        }
      } catch {
        setStatus('disconnected');
        setRetryCount(prev => prev + 1);
      }
    };
    
    checkBackend();
    const interval = setInterval(checkBackend, 2000);
    return () => clearInterval(interval);
  }, []);

  // Backend bağlanana kadar loading göster
  if (status !== 'connected') {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-6"></div>
          <h1 className="text-xl font-semibold text-white mb-2">HyprContext Başlatılıyor</h1>
          <p className="text-gray-400">
            {retryCount > 3 
              ? 'Backend başlatılıyor, lütfen bekleyin...' 
              : 'Servisler hazırlanıyor...'}
          </p>
          {retryCount > 10 && (
            <p className="text-amber-400 text-sm mt-4">
              Bağlantı uzun sürüyor. Lütfen uygulamayı yeniden başlatın.
            </p>
          )}
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

export default function App() {
  // WebSocket bağlantısı
  useWebSocket();
  
  // Tema yönetimi
  const { theme } = useTheme();

  return (
    <QueryClientProvider client={queryClient}>
      <BackendCheck>
        <div className={`app ${theme}`}>
          {/* DÜZELTME: BrowserRouter yerine HashRouter kullanıyoruz */}
          <HashRouter>
            <Routes>
              <Route path="/" element={<Layout />}>
                <Route index element={<HomePage />} />
                <Route path="comments" element={<CommentsPage />} />
                <Route path="graphs" element={<GraphsPage />} />
                <Route path="plans" element={<PlansPage />} />
                <Route path="reports" element={<ReportsPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>
            </Routes>
          </HashRouter>
          
          {/* Global Notifications */}
          <NotificationToast />
        </div>
      </BackendCheck>
    </QueryClientProvider>
  );
}