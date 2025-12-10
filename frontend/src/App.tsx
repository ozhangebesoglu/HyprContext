/**
 * Main App Component
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
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
    },
  },
});

export default function App() {
  // WebSocket bağlantısı
  useWebSocket();
  
  // Tema yönetimi
  const { theme } = useTheme();

  return (
    <QueryClientProvider client={queryClient}>
      <div className={`app ${theme}`}>
        <BrowserRouter>
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
        </BrowserRouter>
        
        {/* Global Notifications */}
        <NotificationToast />
      </div>
    </QueryClientProvider>
  );
}
