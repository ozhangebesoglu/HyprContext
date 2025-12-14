/**
 * Focus Widget Component
 * ----------------------
 * Odak durumu göstergesi - Liquid Glass style.
 */

import { GlassCard } from '../glass/GlassCard';
import { useFocusStats } from '../../hooks/useApi';
import { useFocusStore } from '../../stores/focusStore';
import { Clock, AlertTriangle, CheckCircle, Zap } from 'lucide-react';
import { clsx } from 'clsx';

export function FocusWidget() {
  const { data: stats, isLoading } = useFocusStats();
  const isDistracted = useFocusStore((state) => state.isDistracted);

  if (isLoading || !stats) {
    return (
      <GlassCard className="p-5 min-h-[220px]">
        <div className="space-y-4">
          <div className="h-6 bg-white/20 rounded-lg w-1/2 shimmer" />
          <div className="h-4 bg-white/10 rounded-full shimmer" />
          <div className="grid grid-cols-2 gap-4">
            <div className="h-16 bg-white/10 rounded-xl shimmer" />
            <div className="h-16 bg-white/10 rounded-xl shimmer" />
          </div>
        </div>
      </GlassCard>
    );
  }

  const percentage = Math.min(stats.percentage, 100);
  const isWarning = percentage > 70;
  const isDanger = percentage > 90 || stats.limit_reached;

  return (
    <GlassCard
      className={clsx(
        'p-5 min-h-[220px] transition-colors duration-500',
        isDistracted && 'ring-2 ring-red-500/50'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-semibold text-primary flex items-center gap-2">
          <div className="stat-icon">
            <Clock size={20} />
          </div>
          <span>Odak Durumu</span>
        </h3>
        <div className={clsx(
          'p-2 rounded-full transition-colors duration-300',
          isDistracted 
            ? 'bg-red-500/20 text-red-500' 
            : 'bg-green-500/20 text-green-500'
        )}>
          {isDistracted ? (
            <AlertTriangle size={18} />
          ) : (
            <CheckCircle size={18} />
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-5">
        <div className="progress-bar h-3">
          <div
            className={clsx(
              'progress-fill h-full',
              isDanger && '!bg-gradient-to-r !from-red-500 !to-red-400',
              isWarning && !isDanger && '!bg-gradient-to-r !from-yellow-500 !to-yellow-400'
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="flex justify-between mt-2 text-xs text-muted">
          <span>0%</span>
          <span className={clsx(
            'font-medium transition-colors',
            isDanger && 'text-red-500',
            isWarning && !isDanger && 'text-yellow-500'
          )}>
            {Math.round(percentage)}%
          </span>
          <span>100%</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        <div className="activity-item text-center">
          <p className="text-xs text-muted mb-1">Kullanılan</p>
          <p className="text-2xl font-bold text-primary">
            {stats.formatted_used}
          </p>
        </div>
        <div className="activity-item text-center">
          <p className="text-xs text-muted mb-1">Kalan</p>
          <p className={clsx(
            'text-2xl font-bold transition-colors',
            isDanger ? 'text-red-500 glow-text' : 'text-primary'
          )}>
            {stats.formatted_remaining}
          </p>
        </div>
      </div>

      {/* Warning Message */}
      {stats.limit_reached && (
        <div className="mt-4 p-3 bg-red-500/20 rounded-xl border border-red-500/30">
          <p className="text-sm text-red-500 text-center font-medium flex items-center justify-center gap-2">
            <Zap size={16} />
            Günlük limit doldu!
          </p>
        </div>
      )}
    </GlassCard>
  );
}
