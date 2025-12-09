/**
 * Recent Activities Component
 * ---------------------------
 * Son aktiviteler listesi.
 */

import { GlassCard } from '../glass/GlassCard';
import { useActivities } from '../../hooks/useApi';
import { useActivityStore } from '../../stores/activityStore';
import { Clock, Tag } from 'lucide-react';
import { clsx } from 'clsx';

interface RecentActivitiesProps {
  limit?: number;
}

export function RecentActivities({ limit = 10 }: RecentActivitiesProps) {
  const { data: apiActivities, isLoading } = useActivities(undefined, limit);
  const storeActivities = useActivityStore((state) => state.activities);
  
  // WebSocket'ten gelenler önce, sonra API'den gelenler
  const activities = storeActivities.length > 0 ? storeActivities : (apiActivities || []);

  return (
    <GlassCard className="p-4">
      <h3 className="text-lg font-semibold text-primary mb-4">
        🕐 Son Aktiviteler
      </h3>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-16 bg-white/10 rounded-lg" />
            </div>
          ))}
        </div>
      ) : activities.length === 0 ? (
        <p className="text-muted text-center py-8">
          Henüz aktivite kaydedilmedi
        </p>
      ) : (
        <div className="space-y-2 max-h-96 overflow-auto">
          {activities.map((activity: any, index: number) => (
            <ActivityItem
              key={activity.id || index}
              activity={activity}
              isNew={index === 0 && storeActivities.length > 0}
            />
          ))}
        </div>
      )}
    </GlassCard>
  );
}

interface ActivityItemProps {
  activity: {
    id?: string;
    timestamp: string;
    summary: string;
    tags: string[];
  };
  isNew?: boolean;
}

function ActivityItem({ activity, isNew }: ActivityItemProps) {
  const time = new Date(activity.timestamp).toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div
      className={clsx(
        'p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors',
        isNew && 'animate-slide-up ring-1 ring-accent/50'
      )}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 p-2 rounded-lg bg-white/10">
          <Clock size={16} className="text-accent" />
        </div>
        
        <div className="flex-1 min-w-0">
          <p className="text-sm text-primary truncate">{activity.summary}</p>
          
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-muted">{time}</span>
            
            {activity.tags.length > 0 && (
              <div className="flex items-center gap-1 flex-wrap">
                {activity.tags.slice(0, 3).map((tag: string, i: number) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 text-xs rounded-full bg-accent/20 text-accent"
                  >
                    {tag}
                  </span>
                ))}
                {activity.tags.length > 3 && (
                  <span className="text-xs text-muted">
                    +{activity.tags.length - 3}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
