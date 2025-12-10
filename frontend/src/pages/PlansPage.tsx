/**
 * Plans Page
 * ----------
 * Plan yönetimi ve düzenleme.
 */

import { useState } from 'react';
import { GlassCard } from '../components/glass/GlassCard';
import { GlassButton } from '../components/ui/glass-button';
import { PlanEditor } from '../components/features/PlanEditor';
import { PlanList } from '../components/features/PlanList';
import { useGeneratePlan, useTodayPlan, usePlan } from '../hooks/useApi';
import { Wand2, Loader2, Save, FolderOpen } from 'lucide-react';

export function PlansPage() {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const { data: todayPlan, isLoading: isLoadingToday } = useTodayPlan();
  const { data: selectedPlan, isLoading: isLoadingSelected } = usePlan(selectedDate || '');
  const generatePlan = useGeneratePlan();

  const handleGeneratePlan = () => {
    generatePlan.mutate({});
  };

  const currentPlan = selectedDate ? selectedPlan : todayPlan;
  const isLoading = selectedDate ? isLoadingSelected : isLoadingToday;

  return (
    <div className="plans-page h-full flex gap-6 animate-fade-in">
      {/* Sidebar - Plan List */}
      <div className="w-80 flex flex-col gap-4">
        {/* Action Buttons */}
        <div className="flex gap-2">
          <GlassButton
            onClick={handleGeneratePlan}
            disabled={generatePlan.isPending}
            className="flex-1"
            size="sm"
          >
            <span className="flex items-center gap-2">
              {generatePlan.isPending ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Wand2 size={16} />
              )}
              Yeni Plan Oluştur
            </span>
          </GlassButton>
        </div>
        
        {/* Plan List with FileTree */}
        <PlanList
          selectedDate={selectedDate}
          onSelect={setSelectedDate}
        />
      </div>

      {/* Main - Plan Editor */}
      <div className="flex-1 flex flex-col gap-4">
        <GlassCard className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="stat-icon">
                <FolderOpen size={20} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-primary">
                  {selectedDate ? `Plan: ${selectedDate}` : "Bugünün Planı"}
                </h2>
                <p className="text-xs text-muted">
                  {currentPlan?.mission || 'Misyon belirlenmedi'}
                </p>
              </div>
            </div>
            
            <GlassButton title="Kaydet">
              <Save size={18} />
            </GlassButton>
          </div>
          
          {/* Editor */}
          <div className="flex-1 overflow-hidden">
            {isLoading ? (
              <div className="h-full flex items-center justify-center">
                <Loader2 size={32} className="animate-spin text-accent" />
              </div>
            ) : (
              <PlanEditor
                date={selectedDate || new Date().toISOString().split('T')[0]}
                initialContent={currentPlan?.content || '# Henüz plan oluşturulmadı\n\nYeni plan oluşturmak için sol taraftaki "Yeni Plan Oluştur" butonuna tıklayın.'}
              />
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
