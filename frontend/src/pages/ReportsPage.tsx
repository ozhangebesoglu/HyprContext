/**
 * Reports Page
 * ------------
 * Rapor görüntüleme ve oluşturma.
 */

import { useState, useEffect } from 'react';
import { GlassCard } from '../components/glass/GlassCard';
import { GlassButton } from '../components/ui/glass-button';
import { GlassModal } from '../components/glass/GlassModal';
import { ReportList } from '../components/features/ReportList';
import { ReportViewer } from '../components/features/ReportViewer';
import { PageTransition } from '../components/layout/PageTransition';
import { useGenerateReport, useExportReport, useReports, useReport } from '../hooks/useApi';
import { useSystemStore } from '../stores/systemStore';
import { FileText, Download, Loader2, AlertCircle, FileOutput, FolderOpen, ChevronDown, ChevronUp } from 'lucide-react';

export function ReportsPage() {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportPath, setExportPath] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const { data: reports, isLoading } = useReports();
  const { data: selectedReport, isLoading: isLoadingReport } = useReport(selectedDate || '');
  const generateReport = useGenerateReport();
  const exportReport = useExportReport();
  const addNotification = useSystemStore((state) => state.addNotification);

  // Obsidian path'i profile'den al
  useEffect(() => {
    fetch('http://localhost:8000/api/profile')
      .then(res => res.json())
      .then(data => setExportPath(data.obsidian_vault || ''))
      .catch(() => {});
  }, []);

  const handleGenerateClick = () => {
    setShowConfirmModal(true);
  };

  const handleConfirmGenerate = () => {
    setShowConfirmModal(false);
    generateReport.mutate(undefined);
  };

  const handleExport = () => {
    if (selectedDate && exportPath) {
      exportReport.mutate(
        { date: selectedDate, path: exportPath },
        {
          onSuccess: () => {
            setShowExportModal(false);
            addNotification({
              type: 'success',
              title: 'Başarılı',
              message: 'Rapor Obsidian\'a aktarıldı.',
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
    }
  };

  // Liste özetinden sadece summary al
  const reportSummary = reports?.find((r: any) => r.date === selectedDate)?.summary;

  return (
    <PageTransition>
      <div className="reports-page h-full flex flex-col lg:flex-row gap-4 lg:gap-6">
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
                Raporlar
              </span>
              {sidebarOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </span>
          </GlassButton>
        </div>

        {/* Sidebar - Report List */}
        <div className={`${sidebarOpen ? 'flex' : 'hidden'} lg:flex w-full lg:w-80 flex-col gap-4`}>
          {/* Action Button */}
          <GlassButton
            onClick={handleGenerateClick}
            disabled={generateReport.isPending}
            size="sm"
          >
            <span className="flex items-center gap-2">
              {generateReport.isPending ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <FileText size={16} />
            )}
            Bugünü Raporla
          </span>
        </GlassButton>
        
        {/* Report List with FileTree */}
        <ReportList
          reports={reports || []}
          selectedDate={selectedDate}
          onSelect={setSelectedDate}
          isLoading={isLoading}
        />
      </div>

      {/* Main - Report Viewer */}
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
                  {selectedDate ? `Rapor: ${selectedDate}` : 'Rapor Seçin'}
                </h2>
                <p className="text-xs text-muted">
                  {reportSummary || 'Görüntülemek için bir rapor seçin'}
                </p>
              </div>
            </div>
            
            {selectedDate && (
              <GlassButton
                onClick={() => setShowExportModal(true)}
                size="sm"
              >
                <span className="flex items-center gap-2">
                  <FileOutput size={16} />
                  Aktar
                </span>
              </GlassButton>
            )}
          </div>
          
          {/* Content */}
          <div className="flex-1 overflow-auto p-6 min-h-[400px] lg:min-h-0">
            {isLoadingReport ? (
              <div className="h-full flex items-center justify-center">
                <Loader2 size={32} className="animate-spin text-accent" />
              </div>
            ) : selectedReport ? (
              <ReportViewer report={selectedReport} />
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-muted">
                <FileText size={48} className="mb-4 opacity-50" />
                <p>Görüntülemek için bir rapor seçin</p>
                <p className="text-xs mt-1">veya yeni rapor oluşturun</p>
              </div>
            )}
          </div>
        </GlassCard>
      </div>

      {/* Confirm Generate Modal */}
      <GlassModal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="📊 Rapor Oluştur"
      >
        <div className="p-4">
          <div className="flex items-start gap-3 mb-6">
            <div className="stat-icon">
              <AlertCircle size={20} />
            </div>
            <div>
              <p className="text-primary font-medium">
                Bugün için rapor oluşturulsun mu?
              </p>
              <p className="text-sm text-muted mt-1">
                {new Date().toLocaleDateString('tr-TR', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
          </div>
          
          <div className="flex justify-end gap-3">
            <GlassButton
              onClick={() => setShowConfirmModal(false)}
              size="sm"
            >
              İptal
            </GlassButton>
            <GlassButton onClick={handleConfirmGenerate} size="sm">
              <span className="flex items-center gap-2">
                <FileText size={14} />
                Raporla
              </span>
            </GlassButton>
          </div>
        </div>
      </GlassModal>

      {/* Export Modal */}
      <GlassModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        title="📤 Obsidian'a Aktar"
      >
        <div className="p-4">
          <p className="text-secondary mb-4">
            Rapor belirtilen dizine Markdown dosyası olarak kaydedilecek.
          </p>
          
          <div className="glass-input-wrap w-full">
            <div className="glass-input">
              <span className="glass-input-text-area"></span>
              <input
                type="text"
                value={exportPath}
                onChange={(e) => setExportPath(e.target.value)}
                className="relative z-10 h-full w-full bg-transparent text-primary placeholder:text-primary/50 focus:outline-none py-3 px-4"
                placeholder="/home/user/Obsidian/Vault/Raporlar/"
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-3 mt-6">
            <GlassButton
              onClick={() => setShowExportModal(false)}
              size="sm"
            >
              İptal
            </GlassButton>
            <GlassButton onClick={handleExport} size="sm">
              <span className="flex items-center gap-2">
                <Download size={14} />
                Aktar
              </span>
            </GlassButton>
          </div>
        </div>
      </GlassModal>
    </div>
    </PageTransition>
  );
}
