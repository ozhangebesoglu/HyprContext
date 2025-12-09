/**
 * Tag Cloud Component
 * -------------------
 * Etiket bulutu.
 */

import { useActivityStats } from '../../hooks/useApi';
import { clsx } from 'clsx';

// Mock data - gerçek API'den gelecek
const mockTags = [
  { tag: 'VS Code', count: 45 },
  { tag: 'Python', count: 32 },
  { tag: 'Chrome', count: 28 },
  { tag: 'Terminal', count: 22 },
  { tag: 'Geliştirme', count: 18 },
  { tag: 'Araştırma', count: 15 },
  { tag: 'React', count: 12 },
  { tag: 'Obsidian', count: 8 },
];

export function TagCloud() {
  const { data: stats } = useActivityStats();
  const tags = stats?.top_tags || mockTags;

  const maxCount = Math.max(...tags.map((t: any) => t.count || t[1] || 0));

  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((item: any, index: number) => {
        const tag = item.tag || item[0];
        const count = item.count || item[1];
        const ratio = count / maxCount;
        
        return (
          <span
            key={index}
            className={clsx(
              'px-3 py-1 rounded-full cursor-pointer transition-all duration-200',
              'hover:scale-105 hover:bg-white/20',
              ratio > 0.7 ? 'bg-accent text-white' :
              ratio > 0.4 ? 'bg-accent/50 text-primary' :
              'bg-white/10 text-secondary'
            )}
            style={{
              fontSize: `${0.75 + ratio * 0.5}rem`,
            }}
            title={`${count} aktivite`}
          >
            {tag}
          </span>
        );
      })}
    </div>
  );
}
