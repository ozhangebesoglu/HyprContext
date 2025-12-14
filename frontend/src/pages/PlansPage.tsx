/**
 * Plans Page
 * ----------
 * Plan yönetimi ve düzenleme.
 */

import { useState, useEffect } from 'react';
import { GlassCard } from '../components/glass/GlassCard';
import { GlassButton } from '../components/ui/glass-button';
import { PlanEditor } from '../components/features/PlanEditor';
import { PlanList } from '../components/features/PlanList';
import { PageTransition } from '../components/layout/PageTransition';
import { useGeneratePlan, useTodayPlan, usePlan, useExportPlan } from '../hooks/useApi';
import { useSystemStore } from '../stores/systemStore';
import { Wand2, Loader2, Save, FolderOpen, Download, ChevronDown, ChevronUp } from 'lucide-react';

export function PlansPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [obsidianPath, setObsidianPath] = useState<string>('');
  const { data: todayPlan, isLoading: isLoadingToday } = useTodayPlan();
  const { data: selectedPlan, isLoading: isLoadingSelected } = usePlan(selectedDate || '');
  const generatePlan = useGeneratePlan();
  const exportPlan = useExportPlan();
  const addNotification = useSystemStore((state) => state.addNotification);

  // Obsidian path'i profile'den al
  useEffect(() => {
    fetch('http://localhost:8000/api/profile')
      .then(res => res.json())
      .then(data => setObsidianPath(data.obsidian_vault || ''))
      .catch(() => {});
  }, []);

  const handleGeneratePlan = () => {
    generatePlan.mutate({});
  };

  const handleExport = () => {
    const date = selectedDate || new Date().toISOString().split('T')[0];
    if (!obsidianPath) {
      addNotification({
        type: 'warning',
        title: 'Obsidian Dizini',
        message: 'Ayarlardan Obsidian vault dizinini belirleyin.',
      });
      return;
    }
    
    exportPlan.mutate(
      { date, path: obsidianPath },
      {
        onSuccess: () => {
          addNotification({
            type: 'success',
            title: 'Başarılı',
            message: 'Plan Obsidian\'a aktarıldı.',
          });
        },
        onError: () => {
          addNotification({
            type: 'error',
            title: 'Hata',
            message: 'Dışa aktarma başarısız oldu.',
          });
        },
      }
    );
  };

  const currentPlan = selectedDate ? selectedPlan : todayPlan;
  const isLoading = selectedDate ? isLoadingSelected : isLoadingToday;

  return (
    <PageTransition>
      <div className="plans-page h-full flex flex-col lg:flex-row gap-4 lg:gap-6">
        {/* Mobile Toggle */}
        <div className="lg:hidden">
          <GlassButton
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full"
            size="sm"
          >
            <span className="flex items-center justify-between w-full">
              <span className="flex items-center gap-2">
                <FolderOpen size={16} />
                Planlar
              </span>
              {sidebarOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </span>
          </GlassButton>
        </div>

        {/* Sidebar - Plan List */}
        <div className={`${sidebarOpen ? 'flex' : 'hidden'} lg:flex w-full lg:w-80 flex-col gap-4`}>
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
            
            <div className="flex gap-2">
              <GlassButton 
                onClick={handleExport} 
                title="Obsidian'a Aktar"
                disabled={exportPlan.isPending || !currentPlan}
              >
                {exportPlan.isPending ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : (
                  <Download size={18} />
                )}
              </GlassButton>
              <GlassButton title="Kaydet">
                <Save size={18} />
              </GlassButton>
            </div>
          </div>
          
          {/* Editor */}
          <div className="flex-1 overflow-hidden min-h-[400px] lg:min-h-0">
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
    </PageTransition>
  );
}
