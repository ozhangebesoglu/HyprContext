/**
 * Custom Title Bar
 * ----------------
 * Frameless pencere için özel başlık çubuğu - sadece window controls.
 */

import { Minus, Square, X } from 'lucide-react';
import { useSystemStore } from '../../stores/systemStore';
import CinematicThemeSwitcher from '../ui/cinematic-theme-switcher';

export function TitleBar() {
  const isConnected = useSystemStore((state) => state.isConnected);
  
  const handleMinimize = () => {
    window.electronAPI?.minimize();
  };
  
  const handleMaximize = () => {
    window.electronAPI?.maximize();
  };
  
  const handleClose = () => {
    window.electronAPI?.close();
  };

  return (
    <div className="titlebar h-10 flex items-center justify-between px-3 -webkit-app-region-drag bg-transparent">
      {/* macOS Style Traffic Lights */}
      <div className="flex items-center gap-2 -webkit-app-region-no-drag">
        <button
          onClick={handleClose}
          className="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 transition-colors flex items-center justify-center group"
          title="Kapat"
        >
          <X size={8} className="text-red-900 opacity-0 group-hover:opacity-100" />
        </button>
        <button
          onClick={handleMinimize}
          className="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 transition-colors flex items-center justify-center group"
          title="Küçült"
        >
          <Minus size={8} className="text-yellow-900 opacity-0 group-hover:opacity-100" />
        </button>
        <button
          onClick={handleMaximize}
          className="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 transition-colors flex items-center justify-center group"
          title="Büyüt"
        >
          <Square size={6} className="text-green-900 opacity-0 group-hover:opacity-100" />
        </button>
      </div>
      
      {/* Center - draggable area */}
      <div className="flex-1" />
      
      {/* Right side - Connection status & Theme */}
      <div className="flex items-center gap-3 -webkit-app-region-no-drag">
        {/* Connection Status */}
        <div 
          className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}
          title={isConnected ? 'Bağlı' : 'Bağlantı kesildi'}
        />
        
        {/* Theme Switcher */}
        <CinematicThemeSwitcher size="sm" />
      </div>
    </div>
  );
}
