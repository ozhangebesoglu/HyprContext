/**
 * Settings Page
 * -------------
 * Uygulama ayarları ve profil yönetimi.
 */

import { useState, useEffect } from 'react';
import { GlassCard } from '../components/glass/GlassCard';
import { GlassButton } from '../components/ui/glass-button';
import { GlassInput } from '../components/ui/glass-input';
import { PageTransition } from '../components/layout/PageTransition';
import {
  Settings, User, Shield,
  Save, Loader2, Plus, X, Clock, BookOpen, FolderOpen, RotateCcw, Trash2
} from 'lucide-react';
import {
  useAddCourse, useDeleteCourse, useFocusReset, useFocusStats
} from '../hooks/useApi';

// Backend'den gelen profil yapısı
interface Profile {
  isim: string;
  meslek: string;
  ulke: string;
  sehir: string;
  gun_baslangici: string;
  gun_bitisi: string;
  egitim_programi?: {
    durum: Array<{ isim: string; durum: string; sure?: string; platform?: string }>;
  };
  yasak_kelimeler: string[];
  obsidian_vault?: string;
}

interface Course {
  isim: string;
  durum: string;
  sure?: string;
  platform?: string;
}

export function SettingsPage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newKeyword, setNewKeyword] = useState('');
  const [newCourse, setNewCourse] = useState({ isim: '', platform: '', durum: 'Aktif' });
  const [showCourseForm, setShowCourseForm] = useState(false);

  // API Hooks
  const addCourseMutation = useAddCourse();
  const deleteCourseMutation = useDeleteCourse();
  const focusResetMutation = useFocusReset();
  const { data: focusStats } = useFocusStats();

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/profile/');
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
      await fetch('http://localhost:8000/api/profile/', {
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
      yasak_kelimeler: [...(profile.yasak_kelimeler || []), newKeyword.trim()],
    });
    setNewKeyword('');
  };

  const removeBannedKeyword = (keyword: string) => {
    if (!profile) return;

    setProfile({
      ...profile,
      yasak_kelimeler: (profile.yasak_kelimeler || []).filter((k: string) => k !== keyword),
    });
  };

  const addCourse = async () => {
    if (!newCourse.isim.trim() || !newCourse.platform.trim()) return;

    try {
      await addCourseMutation.mutateAsync(newCourse);
      setNewCourse({ isim: '', platform: '', durum: 'Aktif' });
      setShowCourseForm(false);
      fetchProfile();
    } catch (error) {
      console.error('Kurs eklenirken hata:', error);
    }
  };

  const deleteCourse = async (courseName: string) => {
    try {
      await deleteCourseMutation.mutateAsync(courseName);
      fetchProfile();
    } catch (error) {
      console.error('Kurs silinirken hata:', error);
    }
  };

  const resetFocusStats = async () => {
    try {
      await focusResetMutation.mutateAsync();
    } catch (error) {
      console.error('Focus sıfırlanırken hata:', error);
    }
  };

  // Kursları al
  const courses: Course[] = profile?.egitim_programi?.durum || [];

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 size={32} className="animate-spin text-accent" />
      </div>
    );
  }

  return (
    <PageTransition>
    <div className="settings-page h-full overflow-auto">
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

        <GlassButton onClick={saveProfile} disabled={saving} size="sm">
          <span className="flex items-center gap-2">
            {saving ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Save size={16} />
            )}
            Kaydet
          </span>
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

            <div className="space-y-5">
              <GlassInput
                label="İsim"
                icon={<User size={18} />}
                value={profile?.isim || ''}
                onChange={(e) => setProfile(profile ? {
                  ...profile,
                  isim: e.target.value
                } : null)}
                placeholder="İsminizi girin..."
              />

              <GlassInput
                label="Meslek"
                value={profile?.meslek || ''}
                onChange={(e) => setProfile(profile ? {
                  ...profile,
                  meslek: e.target.value
                } : null)}
                placeholder="Mesleğinizi girin..."
              />

              <GlassInput
                label="Şehir"
                value={profile?.sehir || ''}
                onChange={(e) => setProfile(profile ? {
                  ...profile,
                  sehir: e.target.value
                } : null)}
                placeholder="Şehrinizi girin..."
              />
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
              <h3 className="text-lg font-semibold text-primary">Odak Durumu</h3>
            </div>

            <div className="space-y-4">
              {/* Güncel Odak Durumu */}
              {focusStats && (
                <div className="p-4 rounded-lg bg-white/5 border border-white/10 space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-secondary">Bugün Kullanılan:</span>
                    <span className="text-sm font-medium text-primary">
                      {focusStats.formatted_used || '0dk'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-secondary">Kalan:</span>
                    <span className={`text-sm font-medium ${focusStats.limit_reached ? 'text-red-400' : 'text-green-400'}`}>
                      {focusStats.formatted_remaining || '2s 0dk'}
                    </span>
                  </div>
                  <div className="progress-bar h-2">
                    <div
                      className={`progress-fill h-full ${focusStats.percentage > 80 ? 'bg-red-500' : ''}`}
                      style={{ width: `${Math.min(focusStats.percentage || 0, 100)}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Reset Butonu */}
              <GlassButton
                onClick={resetFocusStats}
                disabled={focusResetMutation.isPending}
                className="w-full"
              >
                <span className="flex items-center gap-2 justify-center">
                  {focusResetMutation.isPending ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <RotateCcw size={16} />
                  )}
                  Günlük Sayacı Sıfırla
                </span>
              </GlassButton>

              <p className="text-xs text-muted pl-3">
                Bu işlem bugünkü dikkat dağınıklığı süresini ve uyarıları sıfırlar.
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
              <div className="flex gap-3 items-end">
                <GlassInput
                  value={newKeyword}
                  onChange={(e) => setNewKeyword(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addBannedKeyword()}
                  placeholder="Yeni kelime ekle..."
                />
                <GlassButton onClick={addBannedKeyword} size="icon">
                  <Plus size={18} />
                </GlassButton>
              </div>

              {/* Keywords list */}
              <div className="flex flex-wrap gap-2 max-h-48 overflow-auto">
                {(profile?.yasak_kelimeler || []).map((keyword: string) => (
                  <span
                    key={keyword}
                    className="tag flex items-center gap-2 group"
                  >
                    {keyword}
                    <button
                      onClick={() => removeBannedKeyword(keyword)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity hover:text-red-500"
                    >
                      <X size={12} />
                    </button>
                  </span>
                ))}
              </div>

              <p className="text-xs text-muted">
                Bu kelimeleri içeren uygulamalar "dikkat dağınıklığı" olarak sayılır.
              </p>
            </div>
          </GlassCard>
        </div>

        {/* Courses */}
        <div className="col-span-12 lg:col-span-6">
          <GlassCard className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="stat-icon">
                  <BookOpen size={18} />
                </div>
                <h3 className="text-lg font-semibold text-primary">Kurslar</h3>
              </div>
              <GlassButton
                size="icon"
                onClick={() => setShowCourseForm(!showCourseForm)}
              >
                {showCourseForm ? <X size={16} /> : <Plus size={16} />}
              </GlassButton>
            </div>

            {/* Kurs Ekleme Formu */}
            {showCourseForm && (
              <div className="space-y-3 mb-4 p-4 rounded-lg bg-white/5 border border-white/10">
                <GlassInput
                  label="Kurs Adı"
                  value={newCourse.isim}
                  onChange={(e) => setNewCourse({ ...newCourse, isim: e.target.value })}
                  placeholder="Örn: React Masterclass"
                />
                <GlassInput
                  label="Platform"
                  value={newCourse.platform}
                  onChange={(e) => setNewCourse({ ...newCourse, platform: e.target.value })}
                  placeholder="Örn: Udemy, Coursera"
                />
                <GlassButton
                  onClick={addCourse}
                  disabled={addCourseMutation.isPending}
                  className="w-full"
                >
                  {addCourseMutation.isPending ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <span className="flex items-center gap-2">
                      <Plus size={16} />
                      Kurs Ekle
                    </span>
                  )}
                </GlassButton>
              </div>
            )}

            <div className="space-y-3 max-h-48 overflow-auto">
              {courses.length > 0 ? (
                courses.map((course: Course, index: number) => (
                  <div
                    key={index}
                    className="activity-item group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-primary font-medium">
                        {course.isim}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          course.durum?.includes('Tamamlandı') ? 'bg-green-500/20 text-green-400' :
                          course.durum?.includes('Aktif') ? 'bg-blue-500/20 text-blue-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {course.durum}
                        </span>
                        <button
                          onClick={() => deleteCourse(course.isim)}
                          disabled={deleteCourseMutation.isPending}
                          className="opacity-0 group-hover:opacity-100 transition-opacity text-red-400 hover:text-red-500"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                    {course.sure && (
                      <span className="text-xs text-muted">{course.sure}</span>
                    )}
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

        {/* Obsidian Settings */}
        <div className="col-span-12 lg:col-span-6">
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="stat-icon">
                <FolderOpen size={18} />
              </div>
              <h3 className="text-lg font-semibold text-primary">Obsidian Entegrasyonu</h3>
            </div>

            <div className="space-y-4">
              <GlassInput
                label="Obsidian Vault Dizini"
                icon={<FolderOpen size={18} />}
                value={profile?.obsidian_vault || ''}
                onChange={(e) => setProfile(profile ? {
                  ...profile,
                  obsidian_vault: e.target.value
                } : null)}
                placeholder="~/SecondBrain veya tam dizin yolu..."
              />

              <p className="text-xs text-muted pl-3">
                Plan ve raporları bu dizine .md dosyası olarak aktarabilirsiniz.
                Örnek: ~/SecondBrain, ~/Documents/Obsidian
              </p>
            </div>
          </GlassCard>
        </div>

        {/* Data Folder */}
        <div className="col-span-12 lg:col-span-6">
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="stat-icon">
                <FolderOpen size={18} />
              </div>
              <h3 className="text-lg font-semibold text-primary">Veri Klasörü</h3>
            </div>

            <div className="space-y-4">
              <p className="text-sm text-secondary">
                Ekran görüntüleri, planlar, raporlar ve diğer verileriniz bu klasörde saklanır.
              </p>

              <GlassButton
                onClick={() => {
                  if (window.electronAPI) {
                    window.electronAPI.openDataFolder();
                  }
                }}
                className="w-full"
              >
                <span className="flex items-center gap-2">
                  <FolderOpen size={16} />
                  Veri Klasörünü Aç
                </span>
              </GlassButton>

              <p className="text-xs text-muted">
                İpucu: Bu klasörü yedeklemek verilerinizi korur.
              </p>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
    </PageTransition>
  );
}
