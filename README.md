<p align="center">
  <img src="docs/screenshots/App_Photos/anasayfa.png" alt="HyprContext" width="600">
</p>

<h1 align="center">🌟 HyprContext</h1>

<p align="center">
  <strong>Yapay Zeka Destekli Akıllı Üretkenlik Takip Asistanı</strong>
</p>

<p align="center">
  <a href="https://github.com/ozhangebesoglu/HyprContext/releases"><img src="https://img.shields.io/github/v/release/ozhangebesoglu/HyprContext?style=for-the-badge&color=a855f7" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/platform-Linux-orange?style=for-the-badge" alt="Platform"></a>
  <a href="#"><img src="https://img.shields.io/badge/Hyprland-Ready-00ff88?style=for-the-badge" alt="Hyprland"></a>
</p>

<p align="center">
  <em>Yerel AI ile çalışan, gizlilik odaklı masaüstü aktivite takip uygulaması</em>
</p>

---

## 💎 Nedir?

HyprContext, bilgisayar aktivitelerinizi **yerel yapay zeka** ile analiz eden ve üretkenliğinizi artırmanıza yardımcı olan bir masaüstü uygulamasıdır.

> 🔒 **Gizlilik Öncelikli**: Tüm verileriniz cihazınızda kalır. Bulut yok, veri paylaşımı yok.

## ✨ Temel Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🤖 **AI Analiz** | Ollama ile yerel analiz, internet gerektirmez |
| 📸 **Akıllı Takip** | 30 saniyelik periyotlarla ekran analizi |
| 📊 **Detaylı Raporlar** | Günlük, haftalık aktivite özetleri |
| 📅 **Plan Yönetimi** | AI destekli günlük planlama |
| ⏱️ **Odak Modu** | Dikkat dağıtıcı uygulama takibi |
| 💬 **AI Sohbet** | Aktiviteleriniz hakkında soru sorun |
| 🎨 **Liquid Glass UI** | Modern, şık cam efektli arayüz |

## 📸 Ekran Görüntüleri

<details>
<summary><strong>🖼️ Görüntüleri Göster</strong></summary>

| Ana Sayfa | Grafikler |
|-----------|-----------|
| ![Ana Sayfa](docs/screenshots/App_Photos/anasayfa.png) | ![Grafikler](docs/screenshots/App_Photos/grafikler.png) |

| Planlar | Raporlar |
|---------|----------|
| ![Planlar](docs/screenshots/App_Photos/planlar.png) | ![Raporlar](docs/screenshots/App_Photos/raporlar.png) |

| Canlı Aktivite | Ayarlar |
|----------------|---------|
| ![Canlı](docs/screenshots/App_Photos/canliaktivite.png) | ![Ayarlar](docs/screenshots/App_Photos/ayarlar.png) |

| İlk Kurulum |
|-------------|
| ![Setup](docs/screenshots/App_Photos/setup1.png) |

</details>

---

## 🚀 Hızlı Başlangıç (Linux)

### Gereksinimler

- Linux (Arch, Fedora, Ubuntu)
- Hyprland veya herhangi bir Wayland WM
- [Ollama](https://ollama.ai/) (AI için)
- `grim` (screenshot için)

### Kurulum

```bash
# 1. Ollama'yı kur
curl -fsSL https://ollama.ai/install.sh | sh

# 2. AI modellerini indir
ollama pull gemma3
ollama pull mxbai-embed-large

# 3. grim kur (Arch)
sudo pacman -S grim

# 4. AppImage'ı indir ve çalıştır
chmod +x HyprContext-*.AppImage
./HyprContext-*.AppImage
```

### İlk Çalıştırma

1. **Veri klasörünü seçin** (varsayılan: `~/Documents/HyprContext`)
2. **Kurulumu tamamlayın**
3. **Tray'dan "Başlat"** ile takibi aktifleştirin

---

## 🏗️ Mimari

```
HyprContext/
├── backend/          # FastAPI Python backend
│   ├── api/          # REST API endpoints
│   ├── services/     # İş mantığı servisleri
│   ├── models/       # Veri modelleri
│   └── adapters/     # Harici servis adaptörleri (Ollama, ChromaDB)
├── frontend/         # React + TypeScript + Electron
│   ├── src/          # Uygulama kaynak kodu
│   └── electron/     # Electron ana süreç
├── docs/             # Dokümantasyon
│   └── wiki/         # Wiki sayfaları
└── Windows/          # Windows portu (ayrı branch)
```

## 📖 Dokümantasyon

| Sayfa | İçerik |
|-------|--------|
| [Wiki Ana Sayfa](docs/wiki/Home.md) | Genel bakış |
| [Kurulum Rehberi](docs/wiki/Kurulum.md) | Detaylı kurulum |
| [Kullanım Kılavuzu](docs/wiki/Kullanim-Kilavuzu.md) | Özellikler ve senaryolar |
| [Yol Haritası](docs/wiki/Yol-Haritasi.md) | Proje geçmişi ve planlar |
| [API Referansı](docs/wiki/API-Referansi.md) | Backend API docs |

---

## 🖥️ Platform Desteği

| Platform | Durum | Açıklama |
|----------|-------|----------|
| 🐧 **Linux (Hyprland)** | ✅ Tam Destek | Ana platform, AppImage mevcut |
| 🐧 **Linux (Diğer WM)** | ✅ Destekleniyor | Wayland WM'ler için çalışır |
| 🪟 **Windows** | 🔄 Geliştiriliyor | [Windows Kurulum Rehberi](Windows/README.md) |

---

## 🛠️ Geliştirme

### Gereksinimler

- Python 3.11+
- Node.js 18+
- pnpm

### Geliştirme Ortamı

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
pnpm install
pnpm dev
```

---

## 🤝 Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit'leyin (`git commit -m 'feat: amazing feature'`)
4. Push'layın (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 🔗 Bağlantılar

- 📦 [Releases](https://github.com/ozhangebesoglu/HyprContext/releases)
- 📚 [Wiki](https://github.com/ozhangebesoglu/HyprContext/wiki)
- 🐛 [Issues](https://github.com/ozhangebesoglu/HyprContext/issues)

---

<p align="center">
  <sub>Made with ❤️ for productivity enthusiasts</sub>
</p>
