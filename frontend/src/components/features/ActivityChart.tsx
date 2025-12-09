/**
 * Activity Chart Component
 * ------------------------
 * Aktivite grafiği.
 */

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { useActivityStats } from '../../hooks/useApi';

// Mock data - gerçek API'den gelecek
const mockData = [
  { time: '00:00', count: 0 },
  { time: '06:00', count: 2 },
  { time: '09:00', count: 8 },
  { time: '12:00', count: 5 },
  { time: '15:00', count: 12 },
  { time: '18:00', count: 7 },
  { time: '21:00', count: 3 },
  { time: '23:00', count: 1 },
];

export function ActivityChart() {
  const { data: stats } = useActivityStats();

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={mockData}>
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
