/**
 * Recent Activities Component
 * ---------------------------
 * Son aktiviteler listesi - Liquid Glass style.
 */

import { GlassCard } from '../glass/GlassCard';
import { useActivities } from '../../hooks/useApi';
import { useActivityStore } from '../../stores/activityStore';
import { Clock, Zap } from 'lucide-react';
import { clsx } from 'clsx';

interface RecentActivitiesProps {
  limit?: number;
}

export function RecentActivities({ limit = 10 }: RecentActivitiesProps) {
  const { data: apiActivities, isLoading } = useActivities(undefined, limit);
  const storeActivities = useActivityStore((state) => state.activities);
  
  const activities = storeActivities.length > 0 ? storeActivities : (apiActivities || []);

  return (
    <GlassCard className="p-5">
      <h3 className="text-lg font-semibold text-primary mb-4 flex items-center gap-2">
        <div className="stat-icon">
          <Zap size={20} />
        </div>
        <span>Son Aktiviteler</span>
      </h3>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="activity-item animate-pulse">
              <div className="h-4 bg-white/20 rounded w-3/4 mb-2 shimmer" />
              <div className="h-3 bg-white/10 rounded w-1/4 shimmer" />
            </div>
          ))}
        </div>
      ) : activities.length === 0 ? (
        <div className="text-center py-12">
          <div className="stat-icon inline-block mb-4">
            <Clock size={32} />
          </div>
          <p className="text-muted">Henüz aktivite kaydedilmedi</p>
          <p className="text-sm text-muted mt-1 opacity-70">
            Aktiviteler burada görünecek
          </p>
        </div>
      ) : (
        <div className="space-y-3 max-h-80 overflow-auto pr-2">
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
        'activity-item',
        isNew && 'new'
      )}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-1">
          <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
        </div>
        
        <div className="flex-1 min-w-0">
          <p className="text-sm text-primary leading-relaxed line-clamp-2">
            {activity.summary}
          </p>
          
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            <span className="text-xs text-muted flex items-center gap-1">
              <Clock size={12} />
              {time}
            </span>
            
            {activity.tags.length > 0 && (
              <div className="flex items-center gap-1.5 flex-wrap">
                {activity.tags.slice(0, 3).map((tag: string, i: number) => (
                  <span key={i} className="tag">
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
