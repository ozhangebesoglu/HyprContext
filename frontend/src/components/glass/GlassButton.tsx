/**
 * Glass Button Component
 * ----------------------
 * Liquid Glass buton komponenti.
 */

import { clsx } from 'clsx';
import { ReactNode, ButtonHTMLAttributes } from 'react';

interface GlassButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'default' | 'subtle' | 'solid';
  size?: 'sm' | 'md' | 'lg';
}

export function GlassButton({
  children,
  className,
  variant = 'default',
  size = 'md',
  disabled,
  ...props
}: GlassButtonProps) {
  const variantClasses = {
    default: 'glass glass-light hover:bg-white/30',
    subtle: 'glass glass-subtle hover:bg-white/20',
    solid: 'glass glass-solid hover:bg-white/40',
  };

  const sizeClasses = {
    sm: 'px-2 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={clsx(
        variantClasses[variant],
        sizeClasses[size],
        'rounded-xl transition-all duration-200',
        'flex items-center justify-center gap-2',
        'text-primary font-medium',
        'active:scale-95',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
