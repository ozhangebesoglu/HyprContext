import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Minus, Square, X, Wifi, WifiOff } from 'lucide-react';
import { useSystemStore } from '../../stores/systemStore';
import CinematicThemeSwitcher from './cinematic-theme-switcher';

// Connection Status Component
const ConnectionStatus: React.FC = () => {
  const isConnected = useSystemStore((state) => state.isConnected);
  
  return (
    <div 
      className="flex items-center cursor-pointer hover:opacity-80 transition-opacity duration-150"
      title={isConnected ? 'Bağlı' : 'Bağlantı kesildi'}
    >
      {isConnected ? (
        <Wifi size={16} className="text-green-400" />
      ) : (
        <WifiOff size={16} className="text-red-400" />
      )}
    </div>
  );
};

// Types
interface MenuItemOption {
  label: string;
  action?: string;
  shortcut?: string;
  type?: 'item' | 'separator';
  hasSubmenu?: boolean;
}

interface MenuConfig {
  label: string;
  items: MenuItemOption[];
}

interface MacOSMenuBarProps {
  appName?: string;
  menus?: MenuConfig[];
  onMenuAction?: (action: string) => void;
  className?: string;
}

// HyprContext Menus
const DEFAULT_MENUS: MenuConfig[] = [
  {
    label: 'Dosya',
    items: [
      { label: 'Yeni Plan Oluştur', action: 'new-plan', shortcut: '⌘N' },
      { label: 'Bugünü Raporla', action: 'generate-report', shortcut: '⌘R' },
      { type: 'separator' },
      { label: 'Obsidian\'a Aktar', action: 'export-obsidian', shortcut: '⌘E' },
      { type: 'separator' },
      { label: 'Ayarlar', action: 'settings', shortcut: '⌘,' },
    ],
  },
  {
    label: 'Görünüm',
    items: [
      { label: 'Ana Sayfa', action: 'nav-home', shortcut: '⌘1' },
      { label: 'Grafikler', action: 'nav-graphs', shortcut: '⌘2' },
      { label: 'Planlar', action: 'nav-plans', shortcut: '⌘3' },
      { label: 'Raporlar', action: 'nav-reports', shortcut: '⌘4' },
      { type: 'separator' },
      { label: 'Tam Ekran', action: 'fullscreen', shortcut: '⌃⌘F' },
    ],
  },
  {
    label: 'Kontrol',
    items: [
      { label: 'Takibi Başlat', action: 'start-tracking', shortcut: '⌘S' },
      { label: 'Takibi Durdur', action: 'stop-tracking', shortcut: '⌘P' },
      { type: 'separator' },
      { label: 'Odak Modunu Aç', action: 'focus-mode' },
    ],
  },
  {
    label: 'Yardım',
    items: [
      { label: 'Klavye Kısayolları', action: 'shortcuts' },
      { label: 'Dokümantasyon', action: 'docs' },
      { type: 'separator' },
      { label: 'HyprContext Hakkında', action: 'about' },
    ],
  },
];

// App menu items (replaces Apple menu)
const APP_MENU_ITEMS: MenuItemOption[] = [
  { label: 'HyprContext Hakkında', action: 'about' },
  { type: 'separator' },
  { label: 'Ayarlar...', action: 'settings', shortcut: '⌘,' },
  { type: 'separator' },
  { label: 'Takibi Başlat', action: 'start-tracking' },
  { label: 'Takibi Durdur', action: 'stop-tracking' },
  { type: 'separator' },
  { label: 'Çıkış', action: 'quit', shortcut: '⌘Q' },
];

// MenuDropdown Component (bundled inside)
interface MenuDropdownProps {
  isOpen: boolean;
  onClose: () => void;
  items: MenuItemOption[];
  position: { x: number; y: number };
  onAction?: (action: string) => void;
}

const MenuDropdown: React.FC<MenuDropdownProps> = ({
  isOpen,
  onClose,
  items,
  position,
  onAction
}) => {
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={dropdownRef}
      className="absolute backdrop-blur-md z-[60]"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        background: 'rgba(40, 40, 40, 0.75)',
        border: '1px solid rgba(255, 255, 255, 0.18)',
        borderRadius: '8px',
        boxShadow: `
          0 8px 32px rgba(0, 0, 0, 0.4),
          0 2px 8px rgba(0, 0, 0, 0.3),
          inset 0 1px 0 rgba(255, 255, 255, 0.12)
        `,
        minWidth: '220px',
        animation: 'menuFadeIn 0.15s cubic-bezier(0.23, 1, 0.32, 1) forwards'
      }}
    >
      <div className="py-1">
        {items.map((item, index) => {
          if (item.type === 'separator') {
            return (
              <div
                key={index}
                className="h-px bg-white/15 mx-2 my-1"
              />
            );
          }

          return (
            <div
              key={index}
              className="px-4 py-1 text-white text-sm cursor-pointer hover:bg-white/10 transition-colors duration-100 flex justify-between items-center"
              onClick={() => {
                if (item.action) {
                  onAction?.(item.action);
                }
                onClose();
              }}
            >
              <span className="flex items-center">
                {item.label}
                {item.hasSubmenu && (
                  <span className="ml-2 text-xs opacity-70">▶</span>
                )}
              </span>
              {item.shortcut && (
                <span className="text-xs text-white/60 ml-4">
                  {item.shortcut}
                </span>
              )}
            </div>
          );
        })}
      </div>

      <style jsx>{`
        @keyframes menuFadeIn {
          from {
            opacity: 0;
            transform: scale(0.95) translateY(-5px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

/**
 * MacOS Menu Bar Component
 *
 * An authentic macOS-style menu bar with glassmorphic design, live clock,
 * and customizable menus.
 *
 * @param appName - The application name to display (default: "Finder")
 * @param appIcon - URL to the app icon/logo (default: Apple logo)
 * @param menus - Array of menu configurations (default: Finder menus)
 * @param onMenuAction - Callback when a menu item is clicked
 * @param className - Additional CSS classes
 *
 * @example
 * ```tsx
 * // Basic usage with defaults
 * <MacOSMenuBar />
 *
 * // With custom app name
 * <MacOSMenuBar appName="VS Code" />
 *
 * // With custom menus
 * <MacOSMenuBar
 *   appName="My App"
 *   menus={customMenus}
 *   onMenuAction={(action) => console.log(action)}
 * />
 * ```
 */
const MacOSMenuBar: React.FC<MacOSMenuBarProps> = ({
  appName = 'HyprContext',
  menus = DEFAULT_MENUS,
  onMenuAction,
  className = ''
}) => {
  const [currentTime, setCurrentTime] = useState('');
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [dropdownPosition, setDropdownPosition] = useState({ x: 0, y: 0 });

  const appleLogoRef = useRef<HTMLDivElement>(null);
  const menuRefs = useRef<{ [key: string]: HTMLSpanElement | null }>({});

  // Update clock every minute
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const timeString = now.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
      setCurrentTime(timeString);
    };

    updateTime();
    const interval = setInterval(updateTime, 60000);

    return () => clearInterval(interval);
  }, []);

  const handleAppleMenuClick = useCallback(() => {
    if (activeMenu === 'apple') {
      setActiveMenu(null);
    } else {
      if (appleLogoRef.current) {
        const rect = appleLogoRef.current.getBoundingClientRect();
        const parentRect = appleLogoRef.current.offsetParent?.getBoundingClientRect() || { left: 0, top: 0 };
        setDropdownPosition({
          x: rect.left - parentRect.left,
          y: 34 // Fixed position below the menu bar (32px height + 2px spacing)
        });
      }
      setActiveMenu('apple');
    }
  }, [activeMenu]);

  const handleMenuItemClick = useCallback((menuLabel: string) => {
    if (activeMenu === menuLabel) {
      setActiveMenu(null);
    } else {
      const menuRef = menuRefs.current[menuLabel];
      if (menuRef) {
        const rect = menuRef.getBoundingClientRect();
        const parentRect = menuRef.offsetParent?.getBoundingClientRect() || { left: 0, top: 0 };
        setDropdownPosition({
          x: rect.left - parentRect.left,
          y: 34 // Fixed position below the menu bar (32px height + 2px spacing)
        });
        setActiveMenu(menuLabel);
      }
    }
  }, [activeMenu]);

  const closeDropdown = useCallback(() => {
    setActiveMenu(null);
  }, []);

  const handleMenuAction = useCallback((action: string) => {
    onMenuAction?.(action);
  }, [onMenuAction]);

  return (
    <div style={{ position: 'relative' }}>
      <div
        className={`backdrop-blur-md ${className}`}
        style={{
          height: '32px',
          background: 'rgba(40, 40, 40, 0.65)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: '8px',
          boxShadow: `
            0 2px 8px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.12)
          `
        }}
      >
        <div className="flex justify-between items-center h-full px-3">
          {/* Left section - Traffic lights, App icon and menus */}
          <div className="flex items-center space-x-4">
            {/* macOS Traffic Lights */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => window.electronAPI?.close()}
                className="w-3 h-3 rounded-full bg-[#ff5f57] hover:bg-[#ff4040] transition-colors flex items-center justify-center group"
                title="Kapat"
              >
                <X size={8} className="text-[#990000] opacity-0 group-hover:opacity-100" />
              </button>
              <button
                onClick={() => window.electronAPI?.minimize()}
                className="w-3 h-3 rounded-full bg-[#febc2e] hover:bg-[#e5a000] transition-colors flex items-center justify-center group"
                title="Küçült"
              >
                <Minus size={8} className="text-[#995700] opacity-0 group-hover:opacity-100" />
              </button>
              <button
                onClick={() => window.electronAPI?.maximize()}
                className="w-3 h-3 rounded-full bg-[#28c840] hover:bg-[#1aab29] transition-colors flex items-center justify-center group"
                title="Büyüt"
              >
                <Square size={6} className="text-[#006500] opacity-0 group-hover:opacity-100" />
              </button>
            </div>

            {/* App Icon & Name */}
            <div
              ref={appleLogoRef}
              onClick={handleAppleMenuClick}
              className="cursor-pointer hover:opacity-80 transition-opacity duration-150 flex items-center space-x-2"
            >
              {/* HyprContext Icon */}
              <div className="w-5 h-5 rounded-md bg-gradient-to-br from-amber-400 to-orange-600 flex items-center justify-center">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="white">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" strokeWidth="2" stroke="white" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <span className="text-white text-sm font-semibold">{appName}</span>
            </div>

            {/* Menu Items */}
            <div className="flex items-center space-x-6">
              {menus.map((menu) => (
                <span
                  key={menu.label}
                  ref={(el) => { menuRefs.current[menu.label] = el; }}
                  className="text-white text-sm cursor-pointer hover:opacity-80 transition-opacity duration-150 select-none"
                  onClick={() => handleMenuItemClick(menu.label)}
                >
                  {menu.label}
                </span>
              ))}
            </div>
          </div>

          {/* Right section - connection, theme, clock */}
          <div className="flex items-center space-x-3">
            {/* Connection Status */}
            <ConnectionStatus />

            {/* Theme Switcher */}
            <CinematicThemeSwitcher size="sm" />

            {/* Clock */}
            <span
              className="text-white text-sm font-medium select-none cursor-pointer hover:opacity-80 transition-opacity duration-150"
            >
              {currentTime}
            </span>
          </div>
        </div>
      </div>

      {/* App Menu Dropdown */}
      <MenuDropdown
        isOpen={activeMenu === 'apple'}
        onClose={closeDropdown}
        items={APP_MENU_ITEMS}
        position={dropdownPosition}
        onAction={handleMenuAction}
      />

      {/* Menu Dropdowns */}
      {menus.map((menu) => (
        <MenuDropdown
          key={menu.label}
          isOpen={activeMenu === menu.label}
          onClose={closeDropdown}
          items={menu.items}
          position={dropdownPosition}
          onAction={handleMenuAction}
        />
      ))}
    </div>
  );
};

export default MacOSMenuBar;






