/**
 * Timeline Chart Component
 * ------------------------
 * Haftalık aktivite zaman çizelgesi grafiği.
 */

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { useActivityStats } from '@/hooks/useApi';
import type { DayData } from '@/types/api';

export function TimelineChart() {
  const { data: stats, isLoading } = useActivityStats();
  
  // API'den gelen veri veya boş dizi
  const data: DayData[] = stats?.by_day ?? [];
  
  if (isLoading) {
    return (
      <div className="h-48 flex items-center justify-center">
        <div className="text-muted-foreground">Yükleniyor...</div>
      </div>
    );
  }
  
  if (data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center">
        <div className="text-muted-foreground">Veri bulunamadı</div>
      </div>
    );
  }

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <XAxis
            dataKey="day"
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
          
          <Bar dataKey="activities" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={`rgba(164, 100, 59, ${Math.min(0.4 + entry.activities / 100, 1)})`}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
