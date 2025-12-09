/**
 * Timeline Chart Component
 * ------------------------
 * Zaman çizelgesi grafiği.
 */

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

// Mock data - gerçek API'den gelecek
const mockData = [
  { day: 'Pzt', activities: 24, focus: 85 },
  { day: 'Sal', activities: 18, focus: 72 },
  { day: 'Çar', activities: 32, focus: 90 },
  { day: 'Per', activities: 28, focus: 78 },
  { day: 'Cum', activities: 20, focus: 65 },
  { day: 'Cmt', activities: 12, focus: 45 },
  { day: 'Paz', activities: 8, focus: 40 },
];

export function TimelineChart() {
  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={mockData}>
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
            {mockData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={`rgba(164, 100, 59, ${0.4 + entry.focus / 200})`}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
