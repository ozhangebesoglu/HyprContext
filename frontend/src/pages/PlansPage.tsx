/**
 * Plans Page
 * ----------
 * Plan yönetimi ve düzenleme.
 */

import { useState } from 'react';
import { GlassCard } from '../components/glass/GlassCard';
import { GlassButton } from '../components/glass/GlassButton';
import { PlanEditor } from '../components/features/PlanEditor';
import { PlanList } from '../components/features/PlanList';
import { useGeneratePlan, useTodayPlan } from '../hooks/useApi';
import { Plus, Wand2, Loader2 } from 'lucide-react';

export function PlansPage() {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const { data: todayPlan, isLoading: isLoadingToday } = useTodayPlan();
  const generatePlan = useGeneratePlan();

  const handleGeneratePlan = () => {
    generatePlan.mutate({});
  };

  return (
    <div className="plans-page h-full flex gap-4">
      {/* Sidebar - Plan List */}
      <div className="w-72 flex flex-col gap-4">
        <GlassCard className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-primary">📅 Planlar</h3>
            <GlassButton
              onClick={handleGeneratePlan}
              disabled={generatePlan.isPending}
              title="Yeni Plan Oluştur"
            >
              {generatePlan.isPending ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Wand2 size={18} />
              )}
            </GlassButton>
          </div>
          
          <PlanList
            selectedDate={selectedDate}
            onSelect={setSelectedDate}
          />
        </GlassCard>
      </div>

      {/* Main - Plan Editor */}
      <div className="flex-1">
        <GlassCard className="h-full flex flex-col">
          <div className="p-4 border-b border-white/10">
            <h2 className="text-xl font-semibold text-primary">
              {selectedDate || 'Bugünün Planı'}
            </h2>
          </div>
          
          <div className="flex-1 overflow-hidden">
            {isLoadingToday ? (
              <div className="h-full flex items-center justify-center">
                <Loader2 size={32} className="animate-spin text-accent" />
              </div>
            ) : (
              <PlanEditor
                date={selectedDate || new Date().toISOString().split('T')[0]}
                initialContent={todayPlan?.content || ''}
              />
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
