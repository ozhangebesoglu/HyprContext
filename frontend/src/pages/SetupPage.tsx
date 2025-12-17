/**
 * Setup Page - Liquid Glass Theme
 * --------------------------------
 * İlk çalıştırma kurulum ekranı.
 * Modern glassmorphism tasarım.
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FolderOpen, CheckCircle, Sparkles, ArrowRight, Folder, Database, FileText, Image, Bot, ChevronLeft } from 'lucide-react';
import { GlassCard } from '../components/glass/GlassCard';

interface SetupPageProps {
  onComplete: () => void;
}

export default function SetupPage({ onComplete }: SetupPageProps) {
  const [step, setStep] = useState(1);
  const [dataPath, setDataPath] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Varsayılan path'i al
    if (window.electronAPI) {
      window.electronAPI.getDataPath().then((path: string) => {
        setDataPath(path);
      });
    }
  }, []);

  const handleSelectFolder = async () => {
    if (!window.electronAPI) return;
    
    const selectedPath = await window.electronAPI.selectDataFolder();
    if (selectedPath) {
      setDataPath(selectedPath);
    }
  };

  const handleComplete = async () => {
    if (!window.electronAPI || !dataPath) return;
    
    setIsLoading(true);
    setError('');
    
    try {
      const result = await window.electronAPI.completeSetup(dataPath);
      if (result.success) {
        setStep(3);
        // 2 saniye sonra ana uygulamaya geç
        setTimeout(() => {
          onComplete();
        }, 2500);
      } else {
        setError(result.error || 'Kurulum tamamlanamadı');
      }
    } catch (err) {
      setError('Bir hata oluştu');
    } finally {
      setIsLoading(false);
    }
  };

  const folders = [
    { name: 'screenshots/', icon: Image, desc: 'Ekran görüntüleri', color: 'from-purple-500 to-indigo-500' },
    { name: 'planlar/', icon: FileText, desc: 'Günlük planlarınız', color: 'from-blue-500 to-cyan-500' },
    { name: 'raporlar/', icon: FileText, desc: 'Aktivite raporları', color: 'from-emerald-500 to-teal-500' },
    { name: 'hafiza_db/', icon: Database, desc: 'AI hafıza veritabanı', color: 'from-amber-500 to-orange-500' },
    { name: 'profile.yaml', icon: Bot, desc: 'Kullanıcı profili', color: 'from-pink-500 to-rose-500' },
  ];

  return (
    <div className="min-h-screen w-full relative overflow-hidden bg-[var(--color-bg-primary)]">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Gradient Orbs */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
            y: [0, -30, 0],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-gradient-to-br from-purple-500/30 to-indigo-500/20 blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            x: [0, -40, 0],
            y: [0, 40, 0],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          className="absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full bg-gradient-to-br from-blue-500/25 to-cyan-500/15 blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            x: [0, 30, 0],
            y: [0, 50, 0],
          }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut", delay: 5 }}
          className="absolute top-1/2 left-1/4 w-72 h-72 rounded-full bg-gradient-to-br from-emerald-500/20 to-teal-500/10 blur-3xl"
        />

        {/* Subtle Grid Pattern */}
        <div 
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="max-w-xl w-full"
        >
          {/* Logo ve Başlık */}
          <div className="text-center mb-10">
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ type: 'spring', delay: 0.2, stiffness: 200 }}
              className="inline-flex items-center justify-center w-20 h-20 rounded-3xl glass mb-6 relative"
            >
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-purple-500/20 to-indigo-500/20" />
              <Sparkles className="w-9 h-9 text-[var(--color-accent)]" />
            </motion.div>
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-3xl font-bold text-[var(--color-text-primary)] mb-3"
            >
              HyprContext'e Hoş Geldiniz
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-[var(--color-text-secondary)]"
            >
              Yapay zeka destekli aktivite takip asistanınız
            </motion.p>
          </div>

          {/* Adım Göstergesi */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="flex justify-center mb-8"
          >
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center">
                <motion.div
                  animate={{
                    scale: step === s ? 1.1 : 1,
                  }}
                  className={`w-10 h-10 rounded-xl flex items-center justify-center text-sm font-semibold transition-all duration-300 ${
                    step > s
                      ? 'glass bg-gradient-to-br from-emerald-500/20 to-teal-500/20 text-emerald-400'
                      : step === s
                      ? 'glass bg-gradient-to-br from-purple-500/20 to-indigo-500/20 text-[var(--color-accent)]'
                      : 'glass-subtle text-[var(--color-text-muted)]'
                  }`}
                >
                  {step > s ? <CheckCircle className="w-5 h-5" /> : s}
                </motion.div>
                {s < 3 && (
                  <div
                    className={`w-12 h-0.5 mx-2 rounded-full transition-all duration-500 ${
                      step > s 
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-500' 
                        : 'bg-[var(--glass-border)]'
                    }`}
                  />
                )}
              </div>
            ))}
          </motion.div>

          {/* Ana İçerik Kartı */}
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 30, scale: 0.98 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: -30, scale: 0.98 }}
              transition={{ duration: 0.3 }}
            >
              <GlassCard className="p-8">
                {step === 1 && (
                  <>
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500/20 to-indigo-500/20 flex items-center justify-center">
                        <FolderOpen className="w-5 h-5 text-purple-400" />
                      </div>
                      <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
                        Veri Klasörünü Seçin
                      </h2>
                    </div>
                    <p className="text-[var(--color-text-secondary)] mb-6 leading-relaxed">
                      HyprContext tüm verilerinizi (ekran görüntüleri, planlar, raporlar) 
                      bu klasörde saklayacak. İstediğiniz zaman bu klasöre erişebilirsiniz.
                    </p>
                    
                    {/* Path Display */}
                    <div className="glass-subtle rounded-xl p-4 mb-5">
                      <div className="flex items-center gap-3">
                        <Folder className="w-5 h-5 text-[var(--color-accent)] flex-shrink-0" />
                        <span className="text-[var(--color-text-primary)] font-mono text-sm flex-1 truncate">
                          {dataPath || 'Klasör seçilmedi'}
                        </span>
                      </div>
                    </div>

                    {/* Buttons */}
                    <button
                      onClick={handleSelectFolder}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3.5 glass glass-interactive text-[var(--color-text-primary)] rounded-xl transition-all mb-4 hover:scale-[1.02]"
                    >
                      <FolderOpen className="w-5 h-5" />
                      Farklı Klasör Seç
                    </button>

                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setStep(2)}
                      disabled={!dataPath}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3.5 bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-500/25"
                    >
                      Devam Et
                      <ArrowRight className="w-5 h-5" />
                    </motion.button>
                  </>
                )}

                {step === 2 && (
                  <>
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center">
                        <Database className="w-5 h-5 text-emerald-400" />
                      </div>
                      <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
                        Kurulumu Tamamla
                      </h2>
                    </div>
                    <p className="text-[var(--color-text-secondary)] mb-6">
                      Aşağıdaki klasörler ve dosyalar oluşturulacak:
                    </p>

                    {/* Folder List */}
                    <div className="space-y-2.5 mb-6">
                      {folders.map((item, index) => (
                        <motion.div
                          key={item.name}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.08 }}
                          className="flex items-center gap-3 px-4 py-3 glass-subtle rounded-xl"
                        >
                          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${item.color} flex items-center justify-center flex-shrink-0`}>
                            <item.icon className="w-4 h-4 text-white" />
                          </div>
                          <span className="text-[var(--color-text-primary)] font-mono text-sm">{item.name}</span>
                          <span className="text-[var(--color-text-muted)] text-sm ml-auto">{item.desc}</span>
                        </motion.div>
                      ))}
                    </div>

                    {/* Error Message */}
                    {error && (
                      <motion.div 
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="glass rounded-xl p-4 mb-4 border-red-500/30"
                        style={{ background: 'rgba(239, 68, 68, 0.1)' }}
                      >
                        <p className="text-red-400 text-sm">{error}</p>
                      </motion.div>
                    )}

                    {/* Buttons */}
                    <div className="flex gap-3">
                      <button
                        onClick={() => setStep(1)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-3.5 glass glass-interactive text-[var(--color-text-primary)] rounded-xl transition-all"
                      >
                        <ChevronLeft className="w-5 h-5" />
                        Geri
                      </button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleComplete}
                        disabled={isLoading}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white rounded-xl font-medium transition-all disabled:opacity-50 shadow-lg shadow-emerald-500/25"
                      >
                        {isLoading ? (
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                          <>
                            <CheckCircle className="w-5 h-5" />
                            Kurulumu Tamamla
                          </>
                        )}
                      </motion.button>
                    </div>
                  </>
                )}

                {step === 3 && (
                  <div className="text-center py-8">
                    <motion.div
                      initial={{ scale: 0, rotate: -180 }}
                      animate={{ scale: 1, rotate: 0 }}
                      transition={{ type: 'spring', stiffness: 200 }}
                      className="inline-flex items-center justify-center w-20 h-20 rounded-2xl glass mb-6 relative"
                    >
                      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20" />
                      <CheckCircle className="w-10 h-10 text-emerald-400" />
                    </motion.div>
                    <motion.h2 
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                      className="text-2xl font-semibold text-[var(--color-text-primary)] mb-3"
                    >
                      Kurulum Tamamlandı!
                    </motion.h2>
                    <motion.p 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.4 }}
                      className="text-[var(--color-text-secondary)]"
                    >
                      HyprContext kullanıma hazır. Yönlendiriliyorsunuz...
                    </motion.p>
                    
                    {/* Loading Dots */}
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.6 }}
                      className="flex justify-center gap-2 mt-6"
                    >
                      {[0, 1, 2].map((i) => (
                        <motion.div
                          key={i}
                          animate={{
                            scale: [1, 1.5, 1],
                            opacity: [0.5, 1, 0.5],
                          }}
                          transition={{
                            duration: 1,
                            repeat: Infinity,
                            delay: i * 0.2,
                          }}
                          className="w-2 h-2 rounded-full bg-emerald-400"
                        />
                      ))}
                    </motion.div>
                  </div>
                )}
              </GlassCard>
            </motion.div>
          </AnimatePresence>

          {/* Alt Bilgi */}
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-center text-[var(--color-text-muted)] text-sm mt-8"
          >
            Veri klasörünü daha sonra Ayarlar'dan değiştirebilirsiniz
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
}
