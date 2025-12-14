/**
 * Graphs Page
 * -----------
 * Aktivite grafikleri ve istatistikler.
 */

import { GlassCard } from '../components/glass/GlassCard';
import { ActivityChart } from '../components/features/ActivityChart';
import { TagCloud } from '../components/features/TagCloud';
import { TimelineChart } from '../components/features/TimelineChart';
import { PageTransition } from '../components/layout/PageTransition';
import { useFocusStats, useActivityStats } from '../hooks/useApi';
import { BarChart3, Target, Clock, Zap, TrendingUp, Activity } from 'lucide-react';

export function GraphsPage() {
  const { data: focusStats } = useFocusStats();
  const { data: activityStats } = useActivityStats();

  return (
    <PageTransition>
    <div className="graphs-page h-full overflow-auto">
      {/* Header */}
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-primary flex items-center gap-3">
            <div className="stat-icon">
              <BarChart3 size={24} />
            </div>
            Grafikler & Analitik
          </h1>
          <p className="text-secondary mt-1">Aktivite analizi ve performans metrikleri</p>
        </div>
      </header>

      {/* Quick Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <QuickStat
          icon={<Activity size={20} />}
          label="Bugünkü Aktivite"
          value={activityStats?.today_count || 0}
          trend="+12%"
        />
        <QuickStat
          icon={<Target size={20} />}
          label="Odak Skoru"
          value={focusStats ? `${Math.round((1 - focusStats.percentage / 100) * 100)}%` : '--'}
          trend={focusStats?.percentage && focusStats.percentage < 50 ? '+' : '-'}
        />
        <QuickStat
          icon={<Clock size={20} />}
          label="Toplam Gün"
          value={activityStats?.total_days ?? '--'}
          trend=""
        />
        <QuickStat
          icon={<Zap size={20} />}
          label="Günlük Ort."
          value={activityStats?.activities_per_day ? Math.round(activityStats.activities_per_day) : '--'}
          trend=""
        />
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Activity Timeline - Main Chart */}
        <div className="col-span-12 lg:col-span-8">
          <GlassCard className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="stat-icon">
                  <TrendingUp size={18} />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-primary">Günlük Aktivite</h3>
                  <p className="text-xs text-muted">Son 24 saat</p>
                </div>
              </div>
              <div className="flex gap-2">
                <span className="tag">Bugün</span>
              </div>
            </div>
            <ActivityChart />
          </GlassCard>
        </div>

        {/* Tag Cloud */}
        <div className="col-span-12 lg:col-span-4">
          <GlassCard className="p-6 h-full">
            <div className="flex items-center gap-3 mb-6">
              <div className="stat-icon">
                <Zap size={18} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-primary">Popüler Etiketler</h3>
                <p className="text-xs text-muted">En çok kullanılanlar</p>
              </div>
            </div>
            <TagCloud />
          </GlassCard>
        </div>

        {/* Weekly Timeline */}
        <div className="col-span-12">
          <GlassCard className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="stat-icon">
                  <BarChart3 size={18} />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-primary">Haftalık Özet</h3>
                  <p className="text-xs text-muted">Son 7 gün</p>
                </div>
              </div>
              <div className="flex gap-2">
                <span className="tag">Bu Hafta</span>
              </div>
            </div>
            <TimelineChart />
          </GlassCard>
        </div>
      </div>
    </div>
    </PageTransition>
  );
}

interface QuickStatProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  trend?: string;
}

function QuickStat({ icon, label, value, trend }: QuickStatProps) {
  const isPositive = trend?.startsWith('+');
  
  return (
    <GlassCard className="p-4">
      <div className="flex items-start justify-between">
        <div className="stat-icon">{icon}</div>
        {trend && (
          <span className={`text-xs ${isPositive ? 'text-green-500' : 'text-red-400'}`}>
            {trend}
          </span>
        )}
      </div>
      <div className="mt-3">
        <p className="text-2xl font-bold text-primary">{value}</p>
        <p className="text-xs text-muted mt-1">{label}</p>
      </div>
    </GlassCard>
  );
}
