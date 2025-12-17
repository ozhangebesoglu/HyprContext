/**
 * Setup Page
 * ----------
 * İlk çalıştırma kurulum ekranı.
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FolderOpen, CheckCircle, Sparkles, ArrowRight, Folder } from 'lucide-react';

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
        }, 2000);
      } else {
        setError(result.error || 'Kurulum tamamlanamadı');
      }
    } catch (err) {
      setError('Bir hata oluştu');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-xl w-full"
      >
        {/* Logo ve Başlık */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', delay: 0.2 }}
            className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 mb-4"
          >
            <Sparkles className="w-10 h-10 text-white" />
          </motion.div>
          <h1 className="text-3xl font-bold text-white mb-2">HyprContext'e Hoş Geldiniz</h1>
          <p className="text-gray-400">Yapay zeka destekli aktivite takip asistanınız</p>
        </div>

        {/* Adımlar */}
        <div className="flex justify-center mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                  step >= s
                    ? 'bg-purple-500 text-white'
                    : 'bg-gray-700 text-gray-400'
                }`}
              >
                {step > s ? <CheckCircle className="w-5 h-5" /> : s}
              </div>
              {s < 3 && (
                <div
                  className={`w-16 h-1 mx-2 rounded transition-all ${
                    step > s ? 'bg-purple-500' : 'bg-gray-700'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* İçerik */}
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-white/10 p-6"
        >
          {step === 1 && (
            <>
              <h2 className="text-xl font-semibold text-white mb-4">
                Veri Klasörünü Seçin
              </h2>
              <p className="text-gray-400 mb-6">
                HyprContext tüm verilerinizi (ekran görüntüleri, planlar, raporlar) 
                bu klasörde saklayacak. İstediğiniz zaman bu klasöre erişebilirsiniz.
              </p>
              
              <div className="bg-slate-900/50 rounded-xl p-4 mb-4">
                <div className="flex items-center gap-3">
                  <Folder className="w-5 h-5 text-purple-400" />
                  <span className="text-white font-mono text-sm flex-1 truncate">
                    {dataPath || 'Klasör seçilmedi'}
                  </span>
                </div>
              </div>

              <button
                onClick={handleSelectFolder}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-xl transition-colors mb-4"
              >
                <FolderOpen className="w-5 h-5" />
                Farklı Klasör Seç
              </button>

              <button
                onClick={() => setStep(2)}
                disabled={!dataPath}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Devam Et
                <ArrowRight className="w-5 h-5" />
              </button>
            </>
          )}

          {step === 2 && (
            <>
              <h2 className="text-xl font-semibold text-white mb-4">
                Kurulumu Tamamla
              </h2>
              <p className="text-gray-400 mb-6">
                Aşağıdaki klasörler oluşturulacak:
              </p>

              <div className="space-y-2 mb-6">
                {[
                  { name: 'screenshots', desc: 'Ekran görüntüleri' },
                  { name: 'planlar', desc: 'Günlük planlarınız' },
                  { name: 'raporlar', desc: 'Aktivite raporları' },
                  { name: 'hafiza_db', desc: 'AI hafıza veritabanı' },
                  { name: 'profile.yaml', desc: 'Kullanıcı profili' },
                  { name: 'history.jsonl', desc: 'Aktivite geçmişi' },
                ].map((item) => (
                  <div
                    key={item.name}
                    className="flex items-center gap-3 px-4 py-2 bg-slate-900/50 rounded-lg"
                  >
                    <Folder className="w-4 h-4 text-purple-400" />
                    <span className="text-white font-mono text-sm">{item.name}</span>
                    <span className="text-gray-500 text-sm">— {item.desc}</span>
                  </div>
                ))}
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4">
                  <p className="text-red-400 text-sm">{error}</p>
                </div>
              )}

              <div className="flex gap-3">
                <button
                  onClick={() => setStep(1)}
                  className="flex-1 px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-xl transition-colors"
                >
                  Geri
                </button>
                <button
                  onClick={handleComplete}
                  disabled={isLoading}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-xl font-medium transition-all disabled:opacity-50"
                >
                  {isLoading ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <CheckCircle className="w-5 h-5" />
                      Kurulumu Tamamla
                    </>
                  )}
                </button>
              </div>
            </>
          )}

          {step === 3 && (
            <div className="text-center py-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring' }}
                className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/20 mb-4"
              >
                <CheckCircle className="w-8 h-8 text-green-400" />
              </motion.div>
              <h2 className="text-xl font-semibold text-white mb-2">
                Kurulum Tamamlandı!
              </h2>
              <p className="text-gray-400">
                HyprContext kullanıma hazır. Yönlendiriliyorsunuz...
              </p>
            </div>
          )}
        </motion.div>

        {/* Alt Bilgi */}
        <p className="text-center text-gray-500 text-sm mt-6">
          Veri klasörünü daha sonra Ayarlar'dan değiştirebilirsiniz
        </p>
      </motion.div>
    </div>
  );
}
