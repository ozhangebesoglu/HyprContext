/**
 * Main Layout Component
 * ---------------------
 * Dock navigasyonu ve içerik alanı.
 */

import { Outlet } from 'react-router-dom';
import { Dock } from './Dock';
import { TitleBar } from './TitleBar';

export function Layout() {
  return (
    <div className="layout h-full flex flex-col">
      {/* Custom Title Bar */}
      <TitleBar />
      
      {/* Main Content */}
      <main className="flex-1 overflow-hidden p-4">
        <Outlet />
      </main>
      
      {/* Dock Navigation */}
      <Dock />
    </div>
  );
}
