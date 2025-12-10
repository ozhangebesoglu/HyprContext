/**
 * Plan Editor Component
 * ---------------------
 * Obsidian-style markdown plan editörü.
 */

import { useState, useEffect } from 'react';
import MDEditor from '@uiw/react-md-editor';
import { GlassButton } from '../ui/glass-button';
import { useUpdatePlan } from '../../hooks/useApi';
import { useTheme } from '../../hooks/useTheme';
import { Save, Loader2, Eye, Edit3 } from 'lucide-react';

interface PlanEditorProps {
  date: string;
  initialContent: string;
}

export function PlanEditor({ date, initialContent }: PlanEditorProps) {
  const [content, setContent] = useState(initialContent);
  const [hasChanges, setHasChanges] = useState(false);
  const [previewMode, setPreviewMode] = useState<'live' | 'edit' | 'preview'>('live');
  const updatePlan = useUpdatePlan();
  const { theme } = useTheme();

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
    <div className="h-full flex flex-col plan-editor" data-color-mode={theme}>
      {/* Toolbar */}
      <div className="flex items-center justify-between p-2 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted">
            {hasChanges ? '● Kaydedilmemiş değişiklikler' : '✓ Kaydedildi'}
          </span>
          
          {/* Mode Toggle */}
          <div className="flex items-center gap-1 ml-4 p-1 rounded-lg bg-white/5">
            <button
              onClick={() => setPreviewMode('edit')}
              className={`p-1.5 rounded-md transition-all ${
                previewMode === 'edit' 
                  ? 'bg-accent/20 text-accent' 
                  : 'text-muted hover:text-primary'
              }`}
              title="Düzenleme Modu"
            >
              <Edit3 size={14} />
            </button>
            <button
              onClick={() => setPreviewMode('live')}
              className={`px-2 py-1 rounded-md text-xs font-medium transition-all ${
                previewMode === 'live' 
                  ? 'bg-accent/20 text-accent' 
                  : 'text-muted hover:text-primary'
              }`}
              title="Canlı Önizleme (Obsidian Tarzı)"
            >
              Live
            </button>
            <button
              onClick={() => setPreviewMode('preview')}
              className={`p-1.5 rounded-md transition-all ${
                previewMode === 'preview' 
                  ? 'bg-accent/20 text-accent' 
                  : 'text-muted hover:text-primary'
              }`}
              title="Önizleme Modu"
            >
              <Eye size={14} />
            </button>
          </div>
        </div>
        
        <GlassButton
          size="sm"
          onClick={handleSave}
          disabled={!hasChanges || updatePlan.isPending}
        >
          <span className="flex items-center gap-1.5">
            {updatePlan.isPending ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <Save size={14} />
            )}
            Kaydet
          </span>
        </GlassButton>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden md-editor-container">
        <MDEditor
          value={content}
          onChange={handleChange}
          height="100%"
          preview={previewMode}
          hideToolbar={true}
          visibleDragbar={false}
        />
      </div>
    </div>
  );
}
