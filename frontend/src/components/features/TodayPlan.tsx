/**
 * Today Plan Component
 * --------------------
 * Bugünün planı özeti.
 */

import { GlassCard } from '../glass/GlassCard';
import { GlassButton } from '../ui/glass-button';
import { useTodayPlan, useGeneratePlan } from '../../hooks/useApi';
import { useNavigate } from 'react-router-dom';
import { Calendar, Target, Loader2, Plus } from 'lucide-react';

export function TodayPlan() {
  const navigate = useNavigate();
  const { data: plan, isLoading, error } = useTodayPlan();
  const generatePlan = useGeneratePlan();

  if (isLoading) {
    return (
      <GlassCard className="p-4 animate-pulse">
        <div className="h-48" />
      </GlassCard>
    );
  }

  if (error || !plan) {
    return (
      <GlassCard className="p-4">
        <h3 className="text-lg font-semibold text-primary mb-4 flex items-center gap-2">
          <Calendar size={20} />
          Bugünün Planı
        </h3>
        
        <div className="text-center py-8">
          <p className="text-muted mb-4">Bugün için plan oluşturulmamış</p>
          <GlassButton
            onClick={() => generatePlan.mutate({})}
            disabled={generatePlan.isPending}
            size="sm"
          >
            <span className="flex items-center gap-2">
              {generatePlan.isPending ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Plus size={16} />
              )}
              Plan Oluştur
            </span>
          </GlassButton>
        </div>
      </GlassCard>
    );
  }

  return (
    <GlassCard
      className="p-4 cursor-pointer"
      interactive
      onClick={() => navigate('/plans')}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-primary flex items-center gap-2">
          <Calendar size={20} />
          Bugünün Planı
        </h3>
        <span className="text-sm text-muted">
          {Math.round(plan.completion_rate * 100)}% tamamlandı
        </span>
      </div>

      {/* Mission */}
      <div className="flex items-start gap-2 mb-4 p-3 rounded-lg bg-white/5">
        <Target size={18} className="text-accent flex-shrink-0 mt-0.5" />
        <p className="text-sm text-primary">{plan.mission}</p>
      </div>

      {/* Progress */}
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full bg-accent rounded-full transition-all duration-500"
          style={{ width: `${plan.completion_rate * 100}%` }}
        />
      </div>

      {/* Tasks Preview */}
      {plan.tasks && plan.tasks.length > 0 && (
        <div className="mt-4 space-y-2">
          {plan.tasks.slice(0, 3).map((task: any, i: number) => (
            <div key={i} className="flex items-center gap-2 text-sm">
              <span className={task.completed ? 'line-through text-muted' : 'text-secondary'}>
                {task.time}: {task.description}
              </span>
            </div>
          ))}
          {plan.tasks.length > 3 && (
            <p className="text-xs text-muted">
              +{plan.tasks.length - 3} görev daha
            </p>
          )}
        </div>
      )}
    </GlassCard>
  );
}
