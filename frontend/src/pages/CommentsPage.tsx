/**
 * Comments Page
 * -------------
 * Canlı aktivite yorumları.
 */

import { GlassCard } from '../components/glass/GlassCard';
import { ActivityFeed } from '../components/features/ActivityFeed';
import { ChatWidget } from '../components/features/ChatWidget';

export function CommentsPage() {
  return (
    <div className="comments-page h-full flex gap-4">
      {/* Main Feed */}
      <div className="flex-1 overflow-hidden">
        <GlassCard className="h-full flex flex-col">
          <div className="p-4 border-b border-white/10">
            <h2 className="text-xl font-semibold text-primary">
              💬 Canlı Aktivite Yorumları
            </h2>
            <p className="text-sm text-muted">
              AI tarafından oluşturulan gerçek zamanlı aktivite açıklamaları
            </p>
          </div>
          
          <div className="flex-1 overflow-auto p-4">
            <ActivityFeed />
          </div>
        </GlassCard>
      </div>

      {/* Chat Sidebar */}
      <div className="w-96 hidden xl:block">
        <ChatWidget />
      </div>
    </div>
  );
}
