<p align="center">
  <img src="../docs/screenshots/App_Photos/anasayfa.png" alt="HyprContext Windows" width="500">
</p>

<h1 align="center">HyprContext - Windows Edition</h1>

<p align="center">
  <strong>Screen Activity Monitoring and AI Analysis Tool for Windows</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-blue?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.10+-green?style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/AI-Ollama-purple?style=for-the-badge" alt="Ollama">
  <img src="https://img.shields.io/badge/status-In%20Development-orange?style=for-the-badge" alt="Status">
</p>

<p align="center">
  <a href="#english">English</a> | <a href="#türkçe">Türkçe</a>
</p>

---

# English

## Features

| Feature | Description |
|---------|-------------|
| **Screen Capture** | Automatic screenshot using Windows API (mss) |
| **Window Tracking** | Monitor active and background windows |
| **AI Analysis** | Smart activity interpretation with Ollama |
| **Focus Tracking** | Distraction warnings and time limits |
| **Database** | Local SQLite storage |
| **Notifications** | Windows toast notifications and audio alerts |

## Screenshots

<details>
<summary><strong>Show Screenshots</strong></summary>

| Home Page | Graphs |
|-----------|--------|
| ![Home](../docs/screenshots/App_Photos/anasayfa.png) | ![Graphs](../docs/screenshots/App_Photos/grafikler.png) |

| Plans | Reports |
|-------|---------|
| ![Plans](../docs/screenshots/App_Photos/planlar.png) | ![Reports](../docs/screenshots/App_Photos/raporlar.png) |

| Live Activity | Settings |
|---------------|----------|
| ![Live](../docs/screenshots/App_Photos/canliaktivite.png) | ![Settings](../docs/screenshots/App_Photos/ayarlar.png) |

</details>

---

## Requirements

| Requirement | Version |
|-------------|---------|
| Windows | 10 / 11 |
| Python | 3.10+ |
| Ollama | Latest |

---

## Installation

### 1. Install Ollama

```powershell
# Download Ollama from https://ollama.ai
# After installation, pull the model:
ollama pull gemma3
ollama pull mxbai-embed-large
```

### 2. Project Setup

```powershell
# Clone repository
git clone https://github.com/ozhangebesoglu/HyprContext.git
cd HyprContext
git checkout windows
cd Windows

# Run install script
install.bat
```

### 3. Configuration

```powershell
# Create .env file
copy config.example.env .env

# Edit .env file (optional)
notepad .env
```

---

## Usage

### Start Daemon (Main Mode)

```powershell
# Activate and run
run.bat

# Or manually:
venv\Scripts\activate
python main.py run
```

### CLI Commands

```powershell
# Single capture
python main.py capture

# View stats
python main.py stats

# List recent activities
python main.py recent --count 10

# Search activities
python main.py search "Visual Studio"

# Show focus status
python main.py focus

# Show version
python main.py version
```

---

## Project Structure

```
Windows/
├── main.py           # Entry point and CLI (Typer)
├── config.py         # Configuration management (Pydantic)
├── capture.py        # Screen capture (mss + PIL)
├── window.py         # Windows API window info
├── analyzer.py       # Ollama AI analysis
├── database.py       # SQLite database
├── focus.py          # Focus tracking
├── notifier.py       # Windows notifications
├── requirements.txt  # Python dependencies
├── install.bat       # Installation script
└── run.bat           # Run script
```

---

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API address |
| `MODEL_VISION` | `gemma3` | Vision analysis model |
| `MODEL_EMBED` | `mxbai-embed-large` | Embedding model |
| `CAPTURE_INTERVAL` | `20` | Screenshot interval (seconds) |
| `DISTRACTION_THRESHOLD` | `3` | Distraction warning threshold |
| `DAILY_DISTRACTION_LIMIT` | `1800` | Daily distraction limit (seconds) |

---

## Architecture Comparison

| Component | Linux (Main) | Windows |
|-----------|--------------|---------|
| Backend | FastAPI + REST API | CLI (Typer) |
| Database | ChromaDB (Vector) | SQLite |
| Screenshots | grim (Wayland) | mss (Windows API) |
| Notifications | libnotify | win10toast |
| UI | Electron + React | CLI only (GUI planned) |

---

## Notification System

| Type | Description |
|------|-------------|
| **Toast Notification** | Windows 10/11 notification center |
| **Audio Alert** | Text-to-Speech voice notification |
| **Distraction Warning** | Alert after 5+ minutes of distraction |

---

## Troubleshooting

### Ollama connection error

```powershell
# Make sure Ollama is running
ollama serve
```

### Screenshot not working

- Run as Administrator
- Check antivirus software

### Window info not available

```powershell
# Make sure pywin32 is installed
pip install pywin32
```

---

## Other Platforms

| Platform | Status | Link |
|----------|--------|------|
| Linux (Hyprland) | Full Support | [Main README](../README.md) |
| Rust Core | Experimental | [WRust/](../WRust/README.md) |
| Go Dashboard | Experimental | [WGo/](../WGo/README.md) |

---

# Türkçe

## Özellikler

| Özellik | Açıklama |
|---------|----------|
| **Ekran Görüntüsü** | Windows API ile otomatik screenshot (mss) |
| **Pencere Takibi** | Aktif ve arka plan pencerelerini izleme |
| **AI Analiz** | Ollama ile akıllı aktivite yorumlama |
| **Odak Takibi** | Dikkat dağınıklığı uyarıları ve zaman limitleri |
| **Veritabanı** | SQLite ile yerel kayıt |
| **Bildirimler** | Windows toast bildirimleri ve sesli uyarı |

## Ekran Görüntüleri

<details>
<summary><strong>Görüntüleri Göster</strong></summary>

| Ana Sayfa | Grafikler |
|-----------|-----------|
| ![Ana Sayfa](../docs/screenshots/App_Photos/anasayfa.png) | ![Grafikler](../docs/screenshots/App_Photos/grafikler.png) |

| Planlar | Raporlar |
|---------|----------|
| ![Planlar](../docs/screenshots/App_Photos/planlar.png) | ![Raporlar](../docs/screenshots/App_Photos/raporlar.png) |

| Canlı Aktivite | Ayarlar |
|----------------|---------|
| ![Canlı](../docs/screenshots/App_Photos/canliaktivite.png) | ![Ayarlar](../docs/screenshots/App_Photos/ayarlar.png) |

</details>

---

## Gereksinimler

| Gereksinim | Versiyon |
|------------|----------|
| Windows | 10 / 11 |
| Python | 3.10+ |
| Ollama | En son |

---

## Kurulum

### 1. Ollama Kurulumu

```powershell
# Ollama'yı https://ollama.ai adresinden indirin
# Kurulumdan sonra modeli indirin:
ollama pull gemma3
ollama pull mxbai-embed-large
```

### 2. Proje Kurulumu

```powershell
# Repo'yu klonlayın
git clone https://github.com/ozhangebesoglu/HyprContext.git
cd HyprContext
git checkout windows
cd Windows

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

---

## Kullanım

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
python main.py recent --count 10

# Aktivitelerde arama
python main.py search "Visual Studio"

# Odak durumunu göster
python main.py focus

# Versiyon bilgisi
python main.py version
```

---

## Dosya Yapısı

```
Windows/
├── main.py           # Ana giriş noktası ve CLI (Typer)
├── config.py         # Konfigürasyon yönetimi (Pydantic)
├── capture.py        # Ekran görüntüsü alma (mss + PIL)
├── window.py         # Windows API pencere bilgisi
├── analyzer.py       # Ollama AI analizi
├── database.py       # SQLite veritabanı
├── focus.py          # Odak takibi
├── notifier.py       # Windows bildirimleri
├── requirements.txt  # Python bağımlılıkları
├── install.bat       # Kurulum scripti
└── run.bat           # Çalıştırma scripti
```

---

## Konfigürasyon Seçenekleri

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API adresi |
| `MODEL_VISION` | `gemma3` | Görüntü analiz modeli |
| `MODEL_EMBED` | `mxbai-embed-large` | Embedding modeli |
| `CAPTURE_INTERVAL` | `20` | Screenshot aralığı (saniye) |
| `DISTRACTION_THRESHOLD` | `3` | Dikkat dağınıklığı eşiği |
| `DAILY_DISTRACTION_LIMIT` | `1800` | Günlük dikkat dağıtıcı limiti (saniye) |

---

## Mimari Karşılaştırması

| Bileşen | Linux (Ana) | Windows |
|---------|-------------|---------|
| Backend | FastAPI + REST API | CLI (Typer) |
| Veritabanı | ChromaDB (Vektör) | SQLite |
| Ekran Görüntüsü | grim (Wayland) | mss (Windows API) |
| Bildirimler | libnotify | win10toast |
| UI | Electron + React | Sadece CLI (GUI planlanıyor) |

---

## Bildirim Sistemi

| Tür | Açıklama |
|-----|----------|
| **Toast Bildirimi** | Windows 10/11 bildirim merkezi |
| **Sesli Uyarı** | Text-to-Speech ile sesli bildirim |
| **Dikkat Uyarısı** | 5+ dakika dikkat dağınıklığında uyarı |

---

## Sorun Giderme

### Ollama bağlantı hatası

```powershell
# Ollama'nın çalıştığından emin olun
ollama serve
```

### Ekran görüntüsü alınamıyor

- Yönetici olarak çalıştırın
- Antivirüs yazılımını kontrol edin

### Pencere bilgisi alınamıyor

```powershell
# pywin32 paketinin kurulu olduğundan emin olun
pip install pywin32
```

---

## Diğer Platformlar

| Platform | Durum | Link |
|----------|-------|------|
| Linux (Hyprland) | Tam Destek | [Ana README](../README.md) |
| Rust Core | Deneysel | [WRust/](../WRust/README.md) |
| Go Dashboard | Deneysel | [WGo/](../WGo/README.md) |

---

## Roadmap / Yol Haritası

- [ ] FastAPI backend integration / FastAPI backend entegrasyonu
- [ ] Electron + React GUI / Electron + React arayüzü
- [ ] ChromaDB vector database / ChromaDB vektör veritabanı
- [ ] WebSocket real-time updates / WebSocket gerçek zamanlı güncellemeler
- [ ] System tray integration / Sistem tepsisi entegrasyonu

---

## License / Lisans

MIT License - See [LICENSE](../LICENSE) file for details.

---

<p align="center">
  <sub>Windows port - HyprContext project</sub>
</p>
