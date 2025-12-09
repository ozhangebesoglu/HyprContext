/**
 * Focus Widget Component
 * ----------------------
 * Odak durumu göstergesi.
 */

import { GlassCard } from '../glass/GlassCard';
import { useFocusStats } from '../../hooks/useApi';
import { useFocusStore } from '../../stores/focusStore';
import { Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import { clsx } from 'clsx';

export function FocusWidget() {
  const { data: stats, isLoading } = useFocusStats();
  const isDistracted = useFocusStore((state) => state.isDistracted);

  if (isLoading || !stats) {
    return (
      <GlassCard className="p-4 animate-pulse">
        <div className="h-32" />
      </GlassCard>
    );
  }

  const percentage = Math.min(stats.percentage, 100);
  const isWarning = percentage > 70;
  const isDanger = percentage > 90 || stats.limit_reached;

  return (
    <GlassCard
      className={clsx(
        'p-4 transition-all duration-300',
        isDistracted && 'ring-2 ring-red-500/50'
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-primary flex items-center gap-2">
          <Clock size={20} />
          Odak Durumu
        </h3>
        {isDistracted ? (
          <AlertTriangle className="text-red-500 animate-pulse" size={20} />
        ) : (
          <CheckCircle className="text-green-500" size={20} />
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="h-3 bg-white/10 rounded-full overflow-hidden">
          <div
            className={clsx(
              'h-full rounded-full transition-all duration-500',
              isDanger ? 'bg-red-500' :
              isWarning ? 'bg-yellow-500' :
              'bg-green-500'
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="flex justify-between mt-1 text-xs text-muted">
          <span>0</span>
          <span>{Math.round(percentage)}%</span>
          <span>100</span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-sm text-muted">Kullanılan</p>
          <p className="text-xl font-bold text-primary">
            {stats.formatted_used}
          </p>
        </div>
        <div>
          <p className="text-sm text-muted">Kalan</p>
          <p className={clsx(
            'text-xl font-bold',
            isDanger ? 'text-red-500' : 'text-primary'
          )}>
            {stats.formatted_remaining}
          </p>
        </div>
      </div>

      {/* Warning Message */}
      {stats.limit_reached && (
        <div className="mt-4 p-2 bg-red-500/20 rounded-lg">
          <p className="text-sm text-red-500 text-center font-medium">
            🛑 Günlük limit doldu!
          </p>
        </div>
      )}
    </GlassCard>
  );
}
