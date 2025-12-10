/**
 * Custom Title Bar
 * ----------------
 * Frameless pencere için özel başlık çubuğu.
 */

import { Moon, Sun, Minus, Square, X, Wifi, WifiOff } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';
import { useSystemStore } from '../../stores/systemStore';

export function TitleBar() {
  const { theme, toggleTheme } = useTheme();
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
    <div className="titlebar glass glass-subtle h-10 flex items-center justify-between px-4 -webkit-app-region-drag">
      {/* App Title */}
      <div className="flex items-center gap-3">
        <span className="text-sm font-semibold text-primary">HyprContext</span>
        
        {/* Connection Status */}
        <div 
          className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs ${
            isConnected 
              ? 'bg-green-500/20 text-green-500' 
              : 'bg-red-500/20 text-red-400'
          }`}
          title={isConnected ? 'Bağlı' : 'Bağlantı kesildi'}
        >
          {isConnected ? <Wifi size={12} /> : <WifiOff size={12} />}
          <span className="hidden sm:inline">{isConnected ? 'Çevrimiçi' : 'Çevrimdışı'}</span>
        </div>
      </div>
      
      {/* Center - draggable area */}
      <div className="flex-1" />
      
      {/* Controls */}
      <div className="flex items-center gap-1 -webkit-app-region-no-drag">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-white/10 transition-colors"
          title={theme === 'dark' ? 'Açık Tema' : 'Koyu Tema'}
        >
          {theme === 'dark' ? (
            <Sun size={16} className="text-secondary" />
          ) : (
            <Moon size={16} className="text-secondary" />
          )}
        </button>
        
        {/* Window Controls */}
        <button
          onClick={handleMinimize}
          className="p-2 rounded-lg hover:bg-white/10 transition-colors"
          title="Küçült"
        >
          <Minus size={16} className="text-secondary" />
        </button>
        
        <button
          onClick={handleMaximize}
          className="p-2 rounded-lg hover:bg-white/10 transition-colors"
          title="Büyüt"
        >
          <Square size={14} className="text-secondary" />
        </button>
        
        <button
          onClick={handleClose}
          className="p-2 rounded-lg hover:bg-red-500/20 transition-colors"
          title="Kapat"
        >
          <X size={16} className="text-secondary hover:text-red-500" />
        </button>
      </div>
    </div>
  );
}
