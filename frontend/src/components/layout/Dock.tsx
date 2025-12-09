/**
 * Dock Navigation - Liquid Glass
 * ------------------------------
 * macOS dock tarzı navigasyon.
 */

import { NavLink } from 'react-router-dom';
import { Home, MessageSquare, BarChart3, Calendar, FileText } from 'lucide-react';
import { clsx } from 'clsx';

const navItems = [
  { path: '/', icon: Home, label: 'Ana Sayfa' },
  { path: '/comments', icon: MessageSquare, label: 'Canlı Yorumlar' },
  { path: '/graphs', icon: BarChart3, label: 'Grafikler' },
  { path: '/plans', icon: Calendar, label: 'Planlar' },
  { path: '/reports', icon: FileText, label: 'Raporlar' },
];

export function Dock() {
  return (
    <nav className="dock-container flex justify-center pb-4">
      <div className="dock glass glass-heavy px-2 py-2 flex gap-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              clsx(
                'dock-item relative p-3 rounded-xl transition-all duration-200',
                'hover:bg-white/20 hover:scale-110',
                isActive && 'bg-white/30 scale-105'
              )
            }
            title={item.label}
          >
            {({ isActive }) => (
              <>
                <item.icon
                  size={24}
                  className={clsx(
                    'transition-colors',
                    isActive ? 'text-accent' : 'text-secondary'
                  )}
                />
                {/* Active indicator */}
                {isActive && (
                  <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-accent" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
