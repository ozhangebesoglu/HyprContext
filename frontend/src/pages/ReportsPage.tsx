/**
 * Reports Page
 * ------------
 * Rapor görüntüleme ve oluşturma.
 */

import { useState } from 'react';
import { GlassCard } from '../components/glass/GlassCard';
import { GlassButton } from '../components/glass/GlassButton';
import { GlassModal } from '../components/glass/GlassModal';
import { ReportList } from '../components/features/ReportList';
import { ReportViewer } from '../components/features/ReportViewer';
import { useGenerateReport, useExportReport, useReports } from '../hooks/useApi';
import { FileText, Download, Loader2, AlertCircle } from 'lucide-react';

export function ReportsPage() {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  
  const { data: reports, isLoading } = useReports();
  const generateReport = useGenerateReport();
  const exportReport = useExportReport();

  const handleGenerateClick = () => {
    setShowConfirmModal(true);
  };

  const handleConfirmGenerate = () => {
    setShowConfirmModal(false);
    generateReport.mutate(undefined);
  };

  const handleExport = (path: string) => {
    if (selectedDate) {
      exportReport.mutate({ date: selectedDate, path });
      setShowExportModal(false);
    }
  };

  const selectedReport = reports?.find((r: any) => r.date === selectedDate);

  return (
    <div className="reports-page h-full flex gap-4">
      {/* Sidebar - Report List */}
      <div className="w-72 flex flex-col gap-4">
        <GlassCard className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-primary">📄 Raporlar</h3>
            <GlassButton
              onClick={handleGenerateClick}
              disabled={generateReport.isPending}
              title="Rapor Oluştur"
            >
              {generateReport.isPending ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <FileText size={18} />
              )}
            </GlassButton>
          </div>
          
          <ReportList
            reports={reports || []}
            selectedDate={selectedDate}
            onSelect={setSelectedDate}
            isLoading={isLoading}
          />
        </GlassCard>
      </div>

      {/* Main - Report Viewer */}
      <div className="flex-1">
        <GlassCard className="h-full flex flex-col">
          <div className="p-4 border-b border-white/10 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-primary">
              {selectedDate ? `Rapor: ${selectedDate}` : 'Bir rapor seçin'}
            </h2>
            
            {selectedDate && (
              <GlassButton
                onClick={() => setShowExportModal(true)}
                title="Obsidian'a Aktar"
              >
                <Download size={18} />
                <span className="ml-2">Aktar</span>
              </GlassButton>
            )}
          </div>
          
          <div className="flex-1 overflow-auto p-4">
            {selectedReport ? (
              <ReportViewer report={selectedReport} />
            ) : (
              <div className="h-full flex items-center justify-center text-muted">
                Görüntülemek için bir rapor seçin
              </div>
            )}
          </div>
        </GlassCard>
      </div>

      {/* Confirm Generate Modal */}
      <GlassModal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="Rapor Oluştur"
      >
        <div className="p-4">
          <div className="flex items-start gap-3 mb-4">
            <AlertCircle className="text-accent flex-shrink-0" size={24} />
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
          
          <div className="flex justify-end gap-2">
            <GlassButton
              variant="subtle"
              onClick={() => setShowConfirmModal(false)}
            >
              İptal
            </GlassButton>
            <GlassButton onClick={handleConfirmGenerate}>
              Raporla
            </GlassButton>
          </div>
        </div>
      </GlassModal>

      {/* Export Modal */}
      <GlassModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        title="Obsidian'a Aktar"
      >
        <div className="p-4">
          <p className="text-secondary mb-4">
            Rapor Obsidian vault'unuza kaydedilecek.
          </p>
          
          <input
            type="text"
            className="w-full p-3 rounded-xl bg-white/10 border border-white/20 text-primary placeholder-muted"
            placeholder="/home/user/Obsidian/Vault/Raporlar/"
            id="export-path"
          />
          
          <div className="flex justify-end gap-2 mt-4">
            <GlassButton
              variant="subtle"
              onClick={() => setShowExportModal(false)}
            >
              İptal
            </GlassButton>
            <GlassButton
              onClick={() => {
                const input = document.getElementById('export-path') as HTMLInputElement;
                handleExport(input.value);
              }}
            >
              Aktar
            </GlassButton>
          </div>
        </div>
      </GlassModal>
    </div>
  );
}
