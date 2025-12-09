/**
 * Graphs Page
 * -----------
 * Aktivite grafikleri ve istatistikler.
 */

import { GlassCard } from '../components/glass/GlassCard';
import { ActivityChart } from '../components/features/ActivityChart';
import { TagCloud } from '../components/features/TagCloud';
import { TimelineChart } from '../components/features/TimelineChart';

export function GraphsPage() {
  return (
    <div className="graphs-page h-full overflow-auto">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-primary">📊 Grafikler</h1>
        <p className="text-secondary">Aktivite analizi ve istatistikler</p>
      </header>

      <div className="grid grid-cols-12 gap-4">
        {/* Activity Timeline */}
        <div className="col-span-12 lg:col-span-8">
          <GlassCard className="p-4">
            <h3 className="text-lg font-semibold text-primary mb-4">
              Günlük Aktivite
            </h3>
            <ActivityChart />
          </GlassCard>
        </div>

        {/* Tag Cloud */}
        <div className="col-span-12 lg:col-span-4">
          <GlassCard className="p-4">
            <h3 className="text-lg font-semibold text-primary mb-4">
              Popüler Etiketler
            </h3>
            <TagCloud />
          </GlassCard>
        </div>

        {/* Timeline */}
        <div className="col-span-12">
          <GlassCard className="p-4">
            <h3 className="text-lg font-semibold text-primary mb-4">
              Zaman Çizelgesi
            </h3>
            <TimelineChart />
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
