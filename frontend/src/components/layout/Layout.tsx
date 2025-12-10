/**
 * Main Layout Component
 * ---------------------
 * macOS stili menu bar, dock navigasyonu ve içerik alanı.
 */

import { Outlet, useNavigate } from 'react-router-dom';
import { Dock } from './Dock';
import MacOSMenuBar from '../ui/mac-os-menu-bar';

export function Layout() {
  const navigate = useNavigate();

  const handleMenuAction = (action: string) => {
    switch (action) {
      case 'nav-home':
        navigate('/');
        break;
      case 'nav-graphs':
        navigate('/graphs');
        break;
      case 'nav-plans':
        navigate('/plans');
        break;
      case 'nav-reports':
        navigate('/reports');
        break;
      case 'settings':
        navigate('/settings');
        break;
      case 'new-plan':
        navigate('/plans');
        // TODO: trigger plan generation
        break;
      case 'generate-report':
        navigate('/reports');
        // TODO: trigger report generation
        break;
      case 'about':
        console.log('HyprContext v0.1.0');
        break;
      case 'quit':
        window.electronAPI?.close();
        break;
      case 'fullscreen':
        window.electronAPI?.maximize();
        break;
      default:
        console.log('Menu action:', action);
    }
  };

  return (
    <div className="layout h-full flex flex-col">
      {/* macOS Style Menu Bar (includes traffic lights & theme) */}
      <div className="px-3 pt-2 pb-1 -webkit-app-region-drag">
        <MacOSMenuBar onMenuAction={handleMenuAction} />
      </div>
      
      {/* Main Content */}
      <main className="flex-1 overflow-hidden p-4">
        <Outlet />
      </main>
      
      {/* Dock Navigation */}
      <Dock />
    </div>
  );
}
