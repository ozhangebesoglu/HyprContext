/**
 * Custom Title Bar
 * ----------------
 * Frameless pencere için özel başlık çubuğu.
 */

import { Moon, Sun, Minus, Square, X } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';

export function TitleBar() {
  const { theme, toggleTheme } = useTheme();
  
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
      <div className="flex items-center gap-2">
        <span className="text-sm font-semibold text-primary">HyprContext</span>
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
