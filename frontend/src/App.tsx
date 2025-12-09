/**
 * Main App Component
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { HomePage } from './pages/HomePage';
import { CommentsPage } from './pages/CommentsPage';
import { GraphsPage } from './pages/GraphsPage';
import { PlansPage } from './pages/PlansPage';
import { ReportsPage } from './pages/ReportsPage';
import { useWebSocket } from './hooks/useWebSocket';
import { useTheme } from './hooks/useTheme';

export default function App() {
  // WebSocket bağlantısı
  useWebSocket();
  
  // Tema yönetimi
  const { theme } = useTheme();

  return (
    <div className={`app ${theme}`}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="comments" element={<CommentsPage />} />
            <Route path="graphs" element={<GraphsPage />} />
            <Route path="plans" element={<PlansPage />} />
            <Route path="reports" element={<ReportsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}
