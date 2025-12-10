/**
 * Main Layout Component
 * ---------------------
 * macOS stili menu bar, dock navigasyonu ve içerik alanı.
 */

import { Outlet, useNavigate } from 'react-router-dom';
import { Dock } from './Dock';
import { TitleBar } from './TitleBar';
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
      {/* Custom Title Bar with Window Controls */}
      <TitleBar />
      
      {/* macOS Style Menu Bar */}
      <div className="px-3 py-1.5">
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
