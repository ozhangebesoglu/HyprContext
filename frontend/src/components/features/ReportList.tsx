/**
 * Report List Component
 * ---------------------
 * FileTree kullanarak rapor listesi.
 */

import { useMemo } from 'react';
import { FileTree } from '../ui/file-tree';
import { FileText, Loader2 } from 'lucide-react';

interface Report {
  id: string;
  date: string;
  summary: string;
  activity_count: number;
}

interface FileNode {
  name: string;
  type: "file" | "folder";
  children?: FileNode[];
  extension?: string;
  path?: string;
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
  // Reports'u FileTree formatına dönüştür
  const fileTreeData = useMemo(() => {
    if (!reports || reports.length === 0) return [];

    // Ay bazlı grupla
    const grouped: Record<string, FileNode[]> = {};
    
    reports.forEach((report) => {
      const date = new Date(report.date);
      const monthKey = date.toLocaleDateString('tr-TR', { month: 'long', year: 'numeric' });
      
      if (!grouped[monthKey]) {
        grouped[monthKey] = [];
      }
      
      grouped[monthKey].push({
        name: `${report.date}.md`,
        type: "file" as const,
        extension: "md",
        path: report.date,
      });
    });

    // FileTree formatına çevir
    return Object.entries(grouped).map(([month, files]) => ({
      name: month,
      type: "folder" as const,
      children: files,
    }));
  }, [reports]);

  const handleFileSelect = (file: FileNode) => {
    if (file.path) {
      onSelect(file.path);
    }
  };

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
        <p className="text-xs text-muted mt-1">
          Rapor oluşturmak için 📊 butonuna tıklayın
        </p>
      </div>
    );
  }

  return (
    <FileTree
      data={fileTreeData}
      selectedFile={selectedDate || undefined}
      onFileSelect={handleFileSelect}
      title="📄 Raporlar"
    />
  );
}
