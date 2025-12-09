/**
 * Report List Component
 * ---------------------
 * Rapor listesi.
 */

import { clsx } from 'clsx';
import { FileText, Loader2 } from 'lucide-react';

interface Report {
  id: string;
  date: string;
  summary: string;
  activity_count: number;
}

interface ReportListProps {
  reports: Report[];
  selectedDate: string | null;
  onSelect: (date: string) => void;
  isLoading: boolean;
}

export function ReportList({
  reports,
  selectedDate,
  onSelect,
  isLoading,
}: ReportListProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 size={24} className="animate-spin text-accent" />
      </div>
    );
  }

  if (reports.length === 0) {
    return (
      <div className="text-center py-8">
        <FileText size={32} className="mx-auto mb-2 text-muted" />
        <p className="text-sm text-muted">Henüz rapor yok</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-96 overflow-auto">
      {reports.map((report) => (
        <div
          key={report.date}
          onClick={() => onSelect(report.date)}
          className={clsx(
            'p-3 rounded-xl cursor-pointer transition-all duration-200',
            'hover:bg-white/10',
            selectedDate === report.date && 'bg-white/20 ring-1 ring-accent/50'
          )}
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-primary">
              {formatDate(report.date)}
            </span>
            <span className="text-xs text-muted">
              {report.activity_count} aktivite
            </span>
          </div>
          
          <p className="text-xs text-muted truncate mt-1">
            {report.summary || 'Özet yok'}
          </p>
        </div>
      ))}
    </div>
  );
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}
