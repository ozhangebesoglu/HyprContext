/**
 * Plan List Component
 * -------------------
 * Plan listesi.
 */

import { usePlans } from '../../hooks/useApi';
import { clsx } from 'clsx';
import { Calendar, CheckCircle } from 'lucide-react';

interface PlanListProps {
  selectedDate: string | null;
  onSelect: (date: string) => void;
}

export function PlanList({ selectedDate, onSelect }: PlanListProps) {
  const { data: plans, isLoading } = usePlans();

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-16 bg-white/10 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (!plans || plans.length === 0) {
    return (
      <div className="text-center py-8">
        <Calendar size={32} className="mx-auto mb-2 text-muted" />
        <p className="text-sm text-muted">Henüz plan yok</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-96 overflow-auto">
      {plans.map((plan: any) => (
        <div
          key={plan.date}
          onClick={() => onSelect(plan.date)}
          className={clsx(
            'p-3 rounded-xl cursor-pointer transition-all duration-200',
            'hover:bg-white/10',
            selectedDate === plan.date && 'bg-white/20 ring-1 ring-accent/50'
          )}
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-primary">
              {formatDate(plan.date)}
            </span>
            <span className="text-xs text-muted">
              {Math.round(plan.completion_rate * 100)}%
            </span>
          </div>
          
          <p className="text-xs text-muted truncate mt-1">
            {plan.mission}
          </p>
          
          {plan.completion_rate === 1 && (
            <CheckCircle size={14} className="text-green-500 mt-1" />
          )}
        </div>
      ))}
    </div>
  );
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const today = new Date();
  
  if (date.toDateString() === today.toDateString()) {
    return 'Bugün';
  }
  
  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'short',
  });
}
