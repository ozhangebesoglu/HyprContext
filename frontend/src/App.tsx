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

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch('http://localhost:8000/health', { 
          method: 'GET',
          signal: AbortSignal.timeout(3000)
        });
        if (res.ok) {
          setStatus('connected');
        } else {
          setStatus('disconnected');
        }
      } catch {
        setStatus('disconnected');
      }
    };
    
    checkBackend();
    const interval = setInterval(checkBackend, 5000);
    return () => clearInterval(interval);
  }, []);

  if (status === 'checking') {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-lg">Backend'e bağlanılıyor...</p>
        </div>
      </div>
    );
  }

  if (status === 'disconnected') {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 p-8">
        <div className="max-w-lg text-center">
          <div className="text-6xl mb-6">🔌</div>
          <h1 className="text-2xl font-bold text-white mb-4">Backend Bağlantısı Yok</h1>
          <p className="text-gray-300 mb-6">
            HyprContext uygulaması çalışmak için backend servisine ihtiyaç duyar.
          </p>
          <div className="bg-slate-800 rounded-lg p-4 text-left mb-6">
            <p className="text-gray-400 text-sm mb-2">Backend'i başlatmak için:</p>
            <code className="text-green-400 text-sm">
              cd HyprContext && source venv/bin/activate && uvicorn backend.main:app --port 8000
            </code>
          </div>
          <button 
            onClick={() => setStatus('checking')}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            Tekrar Dene
          </button>
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