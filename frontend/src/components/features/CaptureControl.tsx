/**
 * Capture Control Component
 * -------------------------
 * Ekran yakalama başlat/durdur kontrolü.
 */

import { Play, Square, Loader2, Camera } from 'lucide-react';
import { GlassCard } from '../glass/GlassCard';
import { useControlStatus, useStartCapture, useStopCapture } from '@/hooks/useApi';

export function CaptureControl() {
  const { data: status, isLoading: statusLoading } = useControlStatus();
  const startCapture = useStartCapture();
  const stopCapture = useStopCapture();

  const isRunning = status?.running ?? false;
  const isLoading = startCapture.isPending || stopCapture.isPending || statusLoading;

  const handleToggle = () => {
    if (isRunning) {
      stopCapture.mutate();
    } else {
      startCapture.mutate();
    }
  };

  return (
    <GlassCard className="p-5 h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-primary flex items-center gap-2">
          <div className="stat-icon">
            <Camera size={20} />
          </div>
          <span>Capture Kontrolü</span>
        </h3>
        
        {/* Status Indicator */}
        <div className="flex items-center gap-2">
          <div 
            className={`w-2.5 h-2.5 rounded-full transition-colors ${
              isRunning 
                ? 'bg-green-500 animate-pulse' 
                : 'bg-gray-400'
            }`} 
          />
          <span className="text-sm text-muted">
            {isRunning ? 'Çalışıyor' : 'Durdu'}
          </span>
        </div>
      </div>

      <div className="flex flex-col items-center gap-4">
        {/* Main Control Button */}
        <button
          onClick={handleToggle}
          disabled={isLoading}
          className={`
            w-24 h-24 rounded-full flex items-center justify-center
            transition-all duration-300 transform
            ${isRunning 
              ? 'bg-red-500/20 hover:bg-red-500/30 text-red-500 hover:scale-105' 
              : 'bg-green-500/20 hover:bg-green-500/30 text-green-500 hover:scale-105'
            }
            ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            border-2 ${isRunning ? 'border-red-500/40' : 'border-green-500/40'}
            shadow-lg
          `}
        >
          {isLoading ? (
            <Loader2 size={36} className="animate-spin" />
          ) : isRunning ? (
            <Square size={36} className="fill-current" />
          ) : (
            <Play size={36} className="fill-current ml-1" />
          )}
        </button>

        {/* Action Text */}
        <p className="text-sm font-medium text-secondary">
          {isLoading 
            ? 'İşleniyor...' 
            : isRunning 
              ? 'Durdurmak için tıkla' 
              : 'Başlatmak için tıkla'
          }
        </p>

        {/* Status Details */}
        {status && (
          <div className="flex gap-4 text-xs text-muted mt-2">
            <span>
              Capture: {status.capture_active ? '✓' : '✗'}
            </span>
            <span>
              Focus: {status.focus_active ? '✓' : '✗'}
            </span>
            {status.today_count !== undefined && (
              <span>
                Bugün: {status.today_count}
              </span>
            )}
          </div>
        )}
      </div>
    </GlassCard>
  );
}
