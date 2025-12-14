/**
 * Home Page
 * ---------
 * Genel bakış sayfası - Liquid Glass style.
 */

import { GlassCard } from '../components/glass/GlassCard';
import { FocusWidget } from '../components/features/FocusWidget';
import { RecentActivities } from '../components/features/RecentActivities';
import { TodayPlan } from '../components/features/TodayPlan';
import { CaptureControl } from '../components/features/CaptureControl';
import { useActivityStats, useFocusStats } from '../hooks/useApi';
import { Clock, Activity, Target, Sparkles } from 'lucide-react';

export function HomePage() {
  const now = new Date();
  const greeting = getGreeting(now.getHours());
  const emoji = getEmoji(now.getHours());

  return (
    <div className="home-page h-full overflow-auto pr-2">
      {/* Header */}
      <header className="mb-8 animate-slide-down">
        <div className="flex items-center gap-4 mb-2">
          <span className="text-4xl">{emoji}</span>
          <h1 className="font-handwriting text-5xl font-semibold text-primary tracking-wide">
            {greeting}
          </h1>
        </div>
        <p className="text-secondary ml-14 font-medium">
          {now.toLocaleDateString('tr-TR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </p>
      </header>

      {/* Grid Layout */}
      <div className="grid grid-cols-12 gap-5">
        {/* Capture Control - Sol üst */}
        <div className="col-span-12 lg:col-span-4 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <CaptureControl />
        </div>

        {/* Focus Widget - Orta üst */}
        <div className="col-span-12 lg:col-span-4 animate-slide-up" style={{ animationDelay: '0.15s' }}>
          <FocusWidget />
        </div>

        {/* Quick Stats - Sağ üst */}
        <div className="col-span-12 lg:col-span-4 animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <QuickStats />
        </div>

        {/* Today's Plan - Sol alt */}
        <div className="col-span-12 lg:col-span-5 animate-slide-up" style={{ animationDelay: '0.3s' }}>
          <TodayPlan />
        </div>

        {/* Recent Activities - Sağ alt */}
        <div className="col-span-12 lg:col-span-7 animate-slide-up" style={{ animationDelay: '0.4s' }}>
          <RecentActivities limit={10} />
        </div>
      </div>
    </div>
  );
}

function QuickStats() {
  const { data: activityStats, isLoading: loadingActivity } = useActivityStats();
  const { data: focusStats, isLoading: loadingFocus } = useFocusStats();

  const totalCount = activityStats?.total_activities ?? 0;
  const avgPerDay = activityStats?.activities_per_day ?? 0;
  const focusScore = focusStats 
    ? Math.round(100 - focusStats.percentage) 
    : 0;

  return (
    <GlassCard className="p-5 h-full">
      <h3 className="text-lg font-semibold text-primary mb-5 flex items-center gap-2">
        <div className="stat-icon">
          <Sparkles size={20} />
        </div>
        <span>Hızlı Bakış</span>
      </h3>
      
      <div className="grid grid-cols-3 gap-5">
        <StatItem
          icon={<Clock size={22} />}
          label="Toplam"
          value={loadingActivity ? "--" : String(totalCount)}
          subtext="aktivite"
        />
        <StatItem
          icon={<Activity size={22} />}
          label="Günlük Ort."
          value={loadingActivity ? "--" : String(Math.round(avgPerDay))}
          subtext="aktivite"
        />
        <StatItem
          icon={<Target size={22} />}
          label="Odak"
          value={loadingFocus ? "--%"  : `${focusScore}%`}
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
    <div className="activity-item flex items-center gap-4 group cursor-pointer">
      <div className="stat-icon group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <div>
        <p className="text-xs text-muted mb-0.5">{label}</p>
        <p className="text-2xl font-bold text-primary">{value}</p>
        <p className="text-xs text-muted opacity-70">{subtext}</p>
      </div>
    </div>
  );
}

function getGreeting(hour: number): string {
  if (hour < 6) return 'İyi Geceler';
  if (hour < 12) return 'Günaydın';
  if (hour < 18) return 'İyi Günler';
  return 'İyi Akşamlar';
}

function getEmoji(hour: number): string {
  if (hour < 6) return '🌙';
  if (hour < 12) return '🌅';
  if (hour < 18) return '☀️';
  return '🌆';
}
