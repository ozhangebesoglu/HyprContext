/**
 * Report Viewer Component
 * -----------------------
 * Rapor görüntüleyici.
 */

import ReactMarkdown from 'react-markdown';
import { GlassCard } from '../glass/GlassCard';
import { BarChart2, Clock, Cpu } from 'lucide-react';
import type { Report } from '../../types/api';

interface ReportViewerProps {
  report: Report;
}

export function ReportViewer({ report }: ReportViewerProps) {
  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          icon={<Clock size={20} />}
          label="Aktivite"
          value={report.activity_count || 0}
        />
        <StatCard
          icon={<BarChart2 size={20} />}
          label="Odak"
          value={report.focus_percentage ? `${Math.round(report.focus_percentage)}%` : '--'}
        />
        <StatCard
          icon={<Cpu size={20} />}
          label="Teknoloji"
          value={report.technologies?.length || 0}
        />
      </div>

      {/* Technologies */}
      {report.technologies && report.technologies.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {report.technologies.map((tech, i) => (
            <span
              key={i}
              className="px-3 py-1 text-sm rounded-full bg-accent/20 text-accent"
            >
              {tech}
            </span>
          ))}
        </div>
      )}

      {/* Content */}
      <div className="prose prose-invert max-w-none">
        <ReactMarkdown>{report.content || ''}</ReactMarkdown>
      </div>
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number | string;
}

function StatCard({ icon, label, value }: StatCardProps) {
  return (
    <GlassCard variant="subtle" className="p-3 flex items-center gap-3">
      <div className="text-accent">{icon}</div>
      <div>
        <p className="text-xs text-muted">{label}</p>
        <p className="text-lg font-bold text-primary">{value}</p>
      </div>
    </GlassCard>
  );
}
