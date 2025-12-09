/**
 * Plan Editor Component
 * ---------------------
 * Markdown plan editörü.
 */

import { useState, useEffect } from 'react';
import MDEditor from '@uiw/react-md-editor';
import { GlassButton } from '../glass/GlassButton';
import { useUpdatePlan } from '../../hooks/useApi';
import { Save, Loader2 } from 'lucide-react';

interface PlanEditorProps {
  date: string;
  initialContent: string;
}

export function PlanEditor({ date, initialContent }: PlanEditorProps) {
  const [content, setContent] = useState(initialContent);
  const [hasChanges, setHasChanges] = useState(false);
  const updatePlan = useUpdatePlan();

  useEffect(() => {
    setContent(initialContent);
    setHasChanges(false);
  }, [initialContent, date]);

  const handleChange = (value?: string) => {
    setContent(value || '');
    setHasChanges(value !== initialContent);
  };

  const handleSave = async () => {
    await updatePlan.mutateAsync({
      date,
      content,
    });
    setHasChanges(false);
  };

  return (
    <div className="h-full flex flex-col" data-color-mode="light">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-2 border-b border-white/10">
        <span className="text-sm text-muted">
          {hasChanges ? '● Kaydedilmemiş değişiklikler' : '✓ Kaydedildi'}
        </span>
        
        <GlassButton
          size="sm"
          onClick={handleSave}
          disabled={!hasChanges || updatePlan.isPending}
        >
          {updatePlan.isPending ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Save size={16} />
          )}
          <span className="ml-1">Kaydet</span>
        </GlassButton>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        <MDEditor
          value={content}
          onChange={handleChange}
          height="100%"
          preview="edit"
          hideToolbar={false}
          style={{
            backgroundColor: 'transparent',
          }}
        />
      </div>
    </div>
  );
}
