/**
 * Glass Card Component
 * --------------------
 * Liquid Glass kart komponenti.
 */

import { clsx } from 'clsx';
import { ReactNode } from 'react';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'subtle' | 'light' | 'solid' | 'heavy';
  interactive?: boolean;
  onClick?: () => void;
}

export function GlassCard({
  children,
  className,
  variant = 'default',
  interactive = false,
  onClick,
}: GlassCardProps) {
  const variantClasses = {
    default: 'glass',
    subtle: 'glass glass-subtle',
    light: 'glass glass-light',
    solid: 'glass glass-solid',
    heavy: 'glass glass-heavy',
  };

  return (
    <div
      className={clsx(
        variantClasses[variant],
        interactive && 'glass-interactive',
        className
      )}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {children}
    </div>
  );
}
