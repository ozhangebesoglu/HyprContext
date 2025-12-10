/**
 * Plan List Component
 * -------------------
 * FileTree kullanarak plan listesi.
 */

import { useMemo } from 'react';
import { usePlans } from '../../hooks/useApi';
import { FileTree } from '../ui/file-tree';
import { Calendar, Loader2 } from 'lucide-react';

interface PlanListProps {
  selectedDate: string | null;
  onSelect: (date: string) => void;
}

interface FileNode {
  name: string;
  type: "file" | "folder";
  children?: FileNode[];
  extension?: string;
  path?: string;
}

export function PlanList({ selectedDate, onSelect }: PlanListProps) {
  const { data: plans, isLoading } = usePlans();

  // Plans'ı FileTree formatına dönüştür
  const fileTreeData = useMemo(() => {
    if (!plans || plans.length === 0) return [];

    // Ay bazlı grupla
    const grouped: Record<string, FileNode[]> = {};
    
    plans.forEach((plan: any) => {
      const date = new Date(plan.date);
      const monthKey = date.toLocaleDateString('tr-TR', { month: 'long', year: 'numeric' });
      
      if (!grouped[monthKey]) {
        grouped[monthKey] = [];
      }
      
      grouped[monthKey].push({
        name: `Plan_${plan.date}.md`,
        type: "file" as const,
        extension: "md",
        path: plan.date,
      });
    });

    // FileTree formatına çevir
    return Object.entries(grouped).map(([month, files]) => ({
      name: month,
      type: "folder" as const,
      children: files,
    }));
  }, [plans]);

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

  if (!plans || plans.length === 0) {
    return (
      <div className="text-center py-8">
        <Calendar size={32} className="mx-auto mb-2 text-muted" />
        <p className="text-sm text-muted">Henüz plan yok</p>
        <p className="text-xs text-muted mt-1">
          Yeni plan oluşturmak için ✨ butonuna tıklayın
        </p>
      </div>
    );
  }

  return (
    <FileTree
      data={fileTreeData}
      selectedFile={selectedDate || undefined}
      onFileSelect={handleFileSelect}
      title="📅 Planlar"
    />
  );
}
