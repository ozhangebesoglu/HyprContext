/**
 * Home Page
 * ---------
 * Genel bakış sayfası.
 */

import { GlassCard } from '../components/glass/GlassCard';
import { FocusWidget } from '../components/features/FocusWidget';
import { RecentActivities } from '../components/features/RecentActivities';
import { TodayPlan } from '../components/features/TodayPlan';
import { Clock, Activity, Target } from 'lucide-react';

export function HomePage() {
  const now = new Date();
  const greeting = getGreeting(now.getHours());

  return (
    <div className="home-page h-full overflow-auto">
      {/* Header */}
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-primary">{greeting}</h1>
        <p className="text-secondary">
          {now.toLocaleDateString('tr-TR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </p>
      </header>

      {/* Grid Layout */}
      <div className="grid grid-cols-12 gap-4">
        {/* Focus Widget - Sol üst */}
        <div className="col-span-12 lg:col-span-4">
          <FocusWidget />
        </div>

        {/* Quick Stats - Sağ üst */}
        <div className="col-span-12 lg:col-span-8">
          <QuickStats />
        </div>

        {/* Today's Plan - Sol alt */}
        <div className="col-span-12 lg:col-span-5">
          <TodayPlan />
        </div>

        {/* Recent Activities - Sağ alt */}
        <div className="col-span-12 lg:col-span-7">
          <RecentActivities limit={10} />
        </div>
      </div>
    </div>
  );
}

function QuickStats() {
  return (
    <GlassCard className="p-4">
      <h3 className="text-lg font-semibold text-primary mb-4">Hızlı Bakış</h3>
      
      <div className="grid grid-cols-3 gap-4">
        <StatItem
          icon={<Clock className="text-accent" size={24} />}
          label="Bugün"
          value="--"
          subtext="aktivite"
        />
        <StatItem
          icon={<Activity className="text-accent" size={24} />}
          label="Bu Hafta"
          value="--"
          subtext="aktivite"
        />
        <StatItem
          icon={<Target className="text-accent" size={24} />}
          label="Odak"
          value="--%"
          subtext="verimlilik"
        />
      </div>
    </GlassCard>
  );
}

interface StatItemProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  subtext: string;
}

function StatItem({ icon, label, value, subtext }: StatItemProps) {
  return (
    <div className="flex items-center gap-3">
      <div className="p-2 rounded-xl bg-white/10">{icon}</div>
      <div>
        <p className="text-sm text-muted">{label}</p>
        <p className="text-xl font-bold text-primary">{value}</p>
        <p className="text-xs text-muted">{subtext}</p>
      </div>
    </div>
  );
}

function getGreeting(hour: number): string {
  if (hour < 6) return '🌙 İyi Geceler';
  if (hour < 12) return '🌅 Günaydın';
  if (hour < 18) return '☀️ İyi Günler';
  return '🌆 İyi Akşamlar';
}
