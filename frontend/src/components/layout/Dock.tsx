/**
 * Dock Navigation - Liquid Glass
 * ------------------------------
 * macOS Sequoia tarzı dock navigasyonu.
 */

import { NavLink } from 'react-router-dom';
import { Home, MessageSquare, BarChart3, Calendar, FileText, Settings } from 'lucide-react';
import { clsx } from 'clsx';

const navItems = [
  { path: '/', icon: Home, label: 'Ana Sayfa' },
  { path: '/comments', icon: MessageSquare, label: 'Canlı Yorumlar' },
  { path: '/graphs', icon: BarChart3, label: 'Grafikler' },
  { path: '/plans', icon: Calendar, label: 'Planlar' },
  { path: '/reports', icon: FileText, label: 'Raporlar' },
  { path: '/settings', icon: Settings, label: 'Ayarlar' },
];

export function Dock() {
  return (
    <nav className="dock-container flex justify-center pb-5">
      <div className="dock flex gap-2">
        {navItems.map((item, index) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              clsx(
                'dock-item relative p-3 rounded-xl',
                'transition-all duration-300',
                'hover:bg-white/30 dark:hover:bg-white/10',
                isActive && 'bg-white/40 dark:bg-white/15 scale-105'
              )
            }
            title={item.label}
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            {({ isActive }) => (
              <>
                <item.icon
                  size={24}
                  className={clsx(
                    'transition-all duration-300',
                    isActive 
                      ? 'text-accent drop-shadow-lg' 
                      : 'text-secondary hover:text-primary'
                  )}
                  strokeWidth={isActive ? 2.5 : 2}
                />
                {/* Active indicator dot */}
                {isActive && (
                  <span 
                    className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-accent shadow-lg"
                    style={{ boxShadow: '0 0 8px var(--color-accent)' }}
                  />
                )}
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
