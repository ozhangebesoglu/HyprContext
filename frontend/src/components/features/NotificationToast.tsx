/**
 * Notification Toast Component
 * ----------------------------
 * Uygulama içi bildirimler için toast.
 */

import { useEffect } from 'react';
import { X, AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';
import { useSystemStore } from '../../stores/systemStore';

const icons = {
  info: Info,
  warning: AlertTriangle,
  error: AlertCircle,
  success: CheckCircle,
};

const colors = {
  info: 'bg-blue-500/20 border-blue-500/30 text-blue-400',
  warning: 'bg-amber-500/20 border-amber-500/30 text-amber-400',
  error: 'bg-red-500/20 border-red-500/30 text-red-400',
  success: 'bg-green-500/20 border-green-500/30 text-green-400',
};

export function NotificationToast() {
  const notifications = useSystemStore((state) => state.notifications);
  const removeNotification = useSystemStore((state) => state.removeNotification);

  return (
    <div className="fixed bottom-24 right-4 z-50 flex flex-col-reverse gap-2 max-w-sm">
      {notifications.map((notification) => {
        const Icon = icons[notification.type];
        
        return (
          <ToastItem
            key={notification.id}
            notification={notification}
            Icon={Icon}
            onRemove={() => removeNotification(notification.id)}
          />
        );
      })}
    </div>
  );
}

interface ToastItemProps {
  notification: {
    id: string;
    type: 'info' | 'warning' | 'error' | 'success';
    title: string;
    message: string;
  };
  Icon: typeof Info;
  onRemove: () => void;
}

function ToastItem({ notification, Icon, onRemove }: ToastItemProps) {
  // Auto-dismiss after 5 seconds
  useEffect(() => {
    const timer = setTimeout(onRemove, 5000);
    return () => clearTimeout(timer);
  }, [onRemove]);

  return (
    <div
      className={`
        glass p-4 rounded-xl border animate-slide-down
        ${colors[notification.type]}
      `}
    >
      <div className="flex items-start gap-3">
        <Icon size={20} className="flex-shrink-0 mt-0.5" />
        
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-sm text-primary">
            {notification.title}
          </h4>
          <p className="text-xs text-secondary mt-1 line-clamp-2">
            {notification.message}
          </p>
        </div>
        
        <button
          onClick={onRemove}
          className="p-1 rounded-lg hover:bg-white/10 transition-colors flex-shrink-0"
        >
          <X size={14} />
        </button>
      </div>
    </div>
  );
}




