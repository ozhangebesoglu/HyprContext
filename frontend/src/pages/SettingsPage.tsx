/**
 * Settings Page
 * -------------
 * Uygulama ayarları ve profil yönetimi.
 */

import { useState, useEffect } from 'react';
import { GlassCard } from '../components/glass/GlassCard';
import { GlassButton } from '../components/glass/GlassButton';
import { 
  Settings, User, Bell, Shield, Database, 
  Save, Loader2, Plus, X, Clock, BookOpen
} from 'lucide-react';

interface Profile {
  user: {
    name: string;
    profession: string;
  };
  daily_limits: {
    distraction_minutes: number;
  };
  banned_keywords: string[];
  courses: Array<{ name: string; platform: string; progress: number }>;
}

export function SettingsPage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newKeyword, setNewKeyword] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/profile');
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      }
    } catch (error) {
      console.error('Profile fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveProfile = async () => {
    if (!profile) return;
    
    setSaving(true);
    try {
      await fetch('http://localhost:8000/api/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile),
      });
    } catch (error) {
      console.error('Profile save error:', error);
    } finally {
      setSaving(false);
    }
  };

  const addBannedKeyword = () => {
    if (!newKeyword.trim() || !profile) return;
    
    setProfile({
      ...profile,
      banned_keywords: [...profile.banned_keywords, newKeyword.trim()],
    });
    setNewKeyword('');
  };

  const removeBannedKeyword = (keyword: string) => {
    if (!profile) return;
    
    setProfile({
      ...profile,
      banned_keywords: profile.banned_keywords.filter(k => k !== keyword),
    });
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 size={32} className="animate-spin text-accent" />
      </div>
    );
  }

  return (
    <div className="settings-page h-full overflow-auto animate-fade-in">
      {/* Header */}
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-primary flex items-center gap-3">
            <div className="stat-icon">
              <Settings size={24} />
            </div>
            Ayarlar
          </h1>
          <p className="text-secondary mt-1">Uygulama ve profil ayarları</p>
        </div>
        
        <GlassButton onClick={saveProfile} disabled={saving}>
          {saving ? (
            <Loader2 size={18} className="animate-spin mr-2" />
          ) : (
            <Save size={18} className="mr-2" />
          )}
          Kaydet
        </GlassButton>
      </header>

      <div className="grid grid-cols-12 gap-6">
        {/* Profile Section */}
        <div className="col-span-12 lg:col-span-6">
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="stat-icon">
                <User size={18} />
              </div>
              <h3 className="text-lg font-semibold text-primary">Profil</h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-muted block mb-2">İsim</label>
                <input
                  type="text"
                  value={profile?.user?.name || ''}
                  onChange={(e) => setProfile(profile ? {
                    ...profile,
                    user: { ...profile.user, name: e.target.value }
                  } : null)}
                  className="w-full p-3 rounded-xl bg-white/10 border border-white/20 text-primary focus:outline-none focus:border-accent/50 transition-colors"
                />
              </div>
              
              <div>
                <label className="text-sm text-muted block mb-2">Meslek</label>
                <input
                  type="text"
                  value={profile?.user?.profession || ''}
                  onChange={(e) => setProfile(profile ? {
                    ...profile,
                    user: { ...profile.user, profession: e.target.value }
                  } : null)}
                  className="w-full p-3 rounded-xl bg-white/10 border border-white/20 text-primary focus:outline-none focus:border-accent/50 transition-colors"
                />
              </div>
            </div>
          </GlassCard>
        </div>

        {/* Focus Settings */}
        <div className="col-span-12 lg:col-span-6">
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="stat-icon">
                <Clock size={18} />
              </div>
              <h3 className="text-lg font-semibold text-primary">Odak Ayarları</h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-muted block mb-2">
                  Günlük Dikkat Dağınıklığı Limiti (dakika)
                </label>
                <input
                  type="number"
                  value={profile?.daily_limits?.distraction_minutes || 120}
                  onChange={(e) => setProfile(profile ? {
                    ...profile,
                    daily_limits: { 
                      ...profile.daily_limits, 
                      distraction_minutes: parseInt(e.target.value) || 120 
                    }
                  } : null)}
                  className="w-full p-3 rounded-xl bg-white/10 border border-white/20 text-primary focus:outline-none focus:border-accent/50 transition-colors"
                />
              </div>
              
              <p className="text-xs text-muted">
                Yasaklı uygulamalarda bu süreyi aştığınızda uyarı alırsınız.
              </p>
            </div>
          </GlassCard>
        </div>

        {/* Banned Keywords */}
        <div className="col-span-12 lg:col-span-6">
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="stat-icon">
                <Shield size={18} />
              </div>
              <h3 className="text-lg font-semibold text-primary">Yasaklı Kelimeler</h3>
            </div>

            <div className="space-y-4">
              {/* Add new keyword */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newKeyword}
                  onChange={(e) => setNewKeyword(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addBannedKeyword()}
                  placeholder="Yeni kelime ekle..."
                  className="flex-1 p-3 rounded-xl bg-white/10 border border-white/20 text-primary placeholder-muted focus:outline-none focus:border-accent/50 transition-colors"
                />
                <GlassButton onClick={addBannedKeyword}>
                  <Plus size={18} />
                </GlassButton>
              </div>
              
              {/* Keywords list */}
              <div className="flex flex-wrap gap-2 max-h-48 overflow-auto">
                {profile?.banned_keywords?.map((keyword) => (
                  <span
                    key={keyword}
                    className="tag flex items-center gap-2 group"
                  >
                    {keyword}
                    <button
                      onClick={() => removeBannedKeyword(keyword)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X size={12} />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </GlassCard>
        </div>

        {/* Courses */}
        <div className="col-span-12 lg:col-span-6">
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="stat-icon">
                <BookOpen size={18} />
              </div>
              <h3 className="text-lg font-semibold text-primary">Kurslar</h3>
            </div>

            <div className="space-y-3 max-h-48 overflow-auto">
              {profile?.courses?.length ? (
                profile.courses.map((course, index) => (
                  <div
                    key={index}
                    className="activity-item"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-primary font-medium">
                        {course.name}
                      </span>
                      <span className="text-xs text-muted">
                        {course.progress}%
                      </span>
                    </div>
                    <span className="text-xs text-muted">{course.platform}</span>
                    
                    {/* Progress bar */}
                    <div className="progress-bar h-1.5 mt-2">
                      <div
                        className="progress-fill h-full"
                        style={{ width: `${course.progress}%` }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted text-center py-4">
                  Henüz kurs eklenmedi
                </p>
              )}
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
