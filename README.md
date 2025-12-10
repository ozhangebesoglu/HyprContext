# HyprContext - Windows Edition

Windows için ekran aktivite izleme ve AI analiz aracı.

## 🚀 Özellikler

- **Ekran Görüntüsü Alma:** Windows API ile otomatik screenshot
- **Pencere Takibi:** Aktif ve arka plan pencerelerini izleme
- **AI Analiz:** Ollama ile akıllı aktivite yorumlama
- **Odak Takibi:** Dikkat dağınıklığı uyarıları
- **Veritabanı:** SQLite ile yerel kayıt
- **Bildirimler:** Windows toast bildirimleri ve sesli uyarı

## 📋 Gereksinimler

- Windows 10/11
- Python 3.10+
- [Ollama](https://ollama.ai/) (AI modeli için)

## 🛠️ Kurulum

### 1. Ollama Kurulumu
```powershell
# Ollama'yı https://ollama.ai adresinden indirin
# Kurulumdan sonra model indirin:
ollama pull gemma3:4b
```

### 2. Proje Kurulumu
```powershell
# Repo'yu klonlayın
git clone -b windows https://github.com/KULLANICI_ADI/HyprContext.git
cd HyprContext

# Kurulum scriptini çalıştırın
install.bat
```

### 3. Konfigürasyon
```powershell
# .env dosyası oluşturun
copy config.example.env .env

# .env dosyasını düzenleyin (opsiyonel)
notepad .env
```

## 🎯 Kullanım

### Daemon Başlatma (Ana Mod)
```powershell
# Aktivasyon ve çalıştırma
run.bat

# Veya manuel:
venv\Scripts\activate
python main.py run
```

### CLI Komutları
```powershell
# Tek seferlik ekran yakalama
python main.py capture

# İstatistikleri görüntüle
python main.py stats

# Son aktiviteleri listele
python main.py recent --limit 10

# Aktivitelerde arama
python main.py search "Visual Studio"

# Odak durumunu göster
python main.py focus
```

## 📁 Dosya Yapısı

```
Windows/
├── main.py           # Ana giriş noktası ve CLI
├── config.py         # Konfigürasyon yönetimi
├── capture.py        # Ekran görüntüsü alma
├── window.py         # Windows API pencere bilgisi
├── analyzer.py       # Ollama AI analizi
├── database.py       # SQLite veritabanı
├── focus.py          # Odak takibi
├── notifier.py       # Windows bildirimleri
├── requirements.txt  # Python bağımlılıkları
├── config.example.env # Örnek konfigürasyon
├── install.bat       # Kurulum scripti
└── run.bat          # Çalıştırma scripti
```

## ⚙️ Konfigürasyon Seçenekleri

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API adresi |
| `MODEL_VISION` | `gemma3:4b` | Görüntü analiz modeli |
| `CAPTURE_INTERVAL` | `20` | Screenshot aralığı (saniye) |
| `FOCUS_DISTRACTION_THRESHOLD` | `300` | Dikkat dağınıklığı eşiği (saniye) |
| `DATA_DIR` | `./data` | Veri dizini |

## 🔔 Bildirim Sistemi

- **Toast Bildirimi:** Windows 10/11 bildirim merkezi
- **Sesli Uyarı:** Text-to-Speech ile sesli bildirim
- **Dikkat Uyarısı:** 5 dakika+ dikkat dağınıklığında uyarı

## 🗄️ Veritabanı

SQLite veritabanı `data/memories.db` konumunda oluşturulur:

```sql
-- Aktivite kayıtları
memories (
    id, timestamp, screenshot_path,
    active_window, all_windows, 
    analysis, tags
)

-- Odak istatistikleri
focus_stats (
    id, date, total_time, 
    distracted_time, productive_apps
)
```

## 🐛 Sorun Giderme

### Ollama bağlantı hatası
```powershell
# Ollama'nın çalıştığından emin olun
ollama serve
```

### Ekran görüntüsü alınamıyor
- Yönetici olarak çalıştırın
- Antivirüs yazılımını kontrol edin

### Pencere bilgisi alınamıyor
- `pywin32` paketinin kurulu olduğundan emin olun

## 📄 Lisans

MIT License - Detaylar için `LICENSE` dosyasına bakın.

## 🔗 Diğer Versiyonlar

- **Linux (Hyprland):** `main` branch
- **Rust Core:** `WRust/` klasörü
- **Go Dashboard:** `WGo/` klasörü
