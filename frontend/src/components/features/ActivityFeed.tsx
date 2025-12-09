/**
 * Activity Feed Component
 * -----------------------
 * Canlı aktivite akışı.
 */

import { useActivityStore } from '../../stores/activityStore';
import { useActivities } from '../../hooks/useApi';
import { Clock, Tag, Zap } from 'lucide-react';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';
import { tr } from 'date-fns/locale';

export function ActivityFeed() {
  const { data: apiActivities } = useActivities(undefined, 50);
  const storeActivities = useActivityStore((state) => state.activities);
  
  const activities = storeActivities.length > 0 ? storeActivities : (apiActivities || []);

  if (activities.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Zap size={48} className="text-muted mx-auto mb-4" />
          <p className="text-muted">Henüz aktivite yok</p>
          <p className="text-sm text-muted">Aktiviteler burada görünecek</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {activities.map((activity: any, index: number) => (
        <ActivityCard
          key={activity.id || index}
          activity={activity}
          isNew={index === 0 && storeActivities.length > 0}
        />
      ))}
    </div>
  );
}

interface ActivityCardProps {
  activity: {
    id?: string;
    timestamp: string;
    summary: string;
    tags: string[];
  };
  isNew?: boolean;
}

function ActivityCard({ activity, isNew }: ActivityCardProps) {
  const time = formatDistanceToNow(new Date(activity.timestamp), {
    addSuffix: true,
    locale: tr,
  });

  return (
    <div
      className={clsx(
        'p-4 rounded-xl bg-white/5 border border-white/10',
        'hover:bg-white/10 transition-all duration-200',
        isNew && 'animate-slide-up ring-2 ring-accent/30'
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <Clock size={14} className="text-muted" />
        <span className="text-sm text-muted">{time}</span>
        {isNew && (
          <span className="px-2 py-0.5 text-xs rounded-full bg-accent text-white">
            Yeni
          </span>
        )}
      </div>

      {/* Summary */}
      <p className="text-primary mb-3">{activity.summary}</p>

      {/* Tags */}
      {activity.tags.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          <Tag size={14} className="text-muted" />
          {activity.tags.map((tag: string, i: number) => (
            <span
              key={i}
              className="px-2 py-0.5 text-xs rounded-full bg-accent/20 text-accent"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
