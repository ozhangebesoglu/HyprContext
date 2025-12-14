/**
 * Activity Chart Component
 * ------------------------
 * Aktivite grafiği.
 */

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { useActivityStats } from '../../hooks/useApi';
import { useMemo } from 'react';

export function ActivityChart() {
  const { data: stats, isLoading } = useActivityStats();

  // API'den gelen by_hour verisini chart formatına çevir
  const chartData = useMemo(() => {
    // 24 saat için veri oluştur
    const hourData = Array.from({ length: 24 }, (_, i) => ({
      time: `${String(i).padStart(2, '0')}:00`,
      count: 0,
    }));

    // API'den gelen verileri ekle
    if (stats?.by_hour) {
      Object.entries(stats.by_hour).forEach(([hour, count]) => {
        const hourIndex = parseInt(hour);
        if (hourIndex >= 0 && hourIndex < 24) {
          hourData[hourIndex].count = count as number;
        }
      });
    }

    return hourData;
  }, [stats?.by_hour]);

  if (isLoading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="animate-pulse text-muted">Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="rgb(64.4% 39.4% 23.2%)" stopOpacity={0.3} />
              <stop offset="95%" stopColor="rgb(64.4% 39.4% 23.2%)" stopOpacity={0} />
            </linearGradient>
          </defs>
          
          <XAxis
            dataKey="time"
            stroke="rgb(68.4% 61.7% 54.3%)"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          
          <YAxis
            stroke="rgb(68.4% 61.7% 54.3%)"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '12px',
              color: 'rgb(51.2% 28.2% 18.9%)',
            }}
            labelStyle={{ color: 'rgb(51.2% 28.2% 18.9%)' }}
          />
          
          <Area
            type="monotone"
            dataKey="count"
            stroke="rgb(64.4% 39.4% 23.2%)"
            fillOpacity={1}
            fill="url(#colorCount)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
