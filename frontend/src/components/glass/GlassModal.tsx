/**
 * Glass Modal Component
 * ---------------------
 * Liquid Glass modal komponenti.
 */

import { clsx } from 'clsx';
import { ReactNode, useEffect } from 'react';
import { X } from 'lucide-react';
import { GlassCard } from './GlassCard';

interface GlassModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export function GlassModal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
}: GlassModalProps) {
  // ESC tuşu ile kapat
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    
    if (isOpen) {
      window.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      window.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-2xl',
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm animate-fade-in" />
      
      {/* Modal */}
      <GlassCard
        variant="heavy"
        className={clsx(
          'relative w-full animate-slide-up',
          sizeClasses[size]
        )}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <h3 className="text-lg font-semibold text-primary">{title}</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-white/10 transition-colors"
          >
            <X size={20} className="text-muted" />
          </button>
        </div>
        
        {/* Content */}
        {children}
      </GlassCard>
    </div>
  );
}
