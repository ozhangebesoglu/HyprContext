# 📥 Kurulum Rehberi

HyprContext'i sisteminize kurmak için bu rehberi takip edin.

---

## 📋 Sistem Gereksinimleri

| Gereksinim | Açıklama |
|------------|----------|
| **İşletim Sistemi** | Linux (Arch, Fedora, Ubuntu, vb.) |
| **Masaüstü** | Wayland (Hyprland, Sway, KDE Plasma, GNOME) |
| **RAM** | Minimum 4GB (8GB önerilir) |
| **Disk** | 500MB uygulama + AI modelleri için ~5GB |

---

## 🔧 Bağımlılıklar

### 1. Ollama (Zorunlu)

Yerel AI için Ollama gereklidir:

```bash
# Kurulum
curl -fsSL https://ollama.ai/install.sh | sh

# Servisi başlat
systemctl --user enable --now ollama

# Modelleri indir
ollama pull gemma3              # Ana analiz modeli (~2GB)
ollama pull mxbai-embed-large   # Embedding modeli (~600MB)
```

### 2. grim (Zorunlu - Wayland)

Ekran görüntüsü almak için:

```bash
# Arch Linux
sudo pacman -S grim

# Fedora
sudo dnf install grim

# Ubuntu/Debian
sudo apt install grim
```

### 3. hyprctl (Opsiyonel)

Hyprland kullanıyorsanız zaten yüklüdür. Diğer WM'ler için pencere bilgisi sınırlı olabilir.

---

## 📦 Uygulama Kurulumu

### Yöntem 1: AppImage (Önerilen)

```bash
# İndir
wget https://github.com/ozhangebesoglu/HyprContext/releases/latest/download/HyprContext-0.4.0-x86_64.AppImage

# Çalıştırılabilir yap
chmod +x HyprContext-*.AppImage

# Çalıştır
./HyprContext-*.AppImage
```

### Yöntem 2: Kaynak Koddan

```bash
# Repo'yu klonla
git clone https://github.com/ozhangebesoglu/HyprContext.git
cd HyprContext

# Backend bağımlılıkları
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Frontend bağımlılıkları
cd frontend
npm install

# Geliştirme modunda çalıştır
npm run dev  # Terminal 1
cd .. && uvicorn backend.main:app --reload  # Terminal 2
```

---

## 🚀 İlk Çalıştırma

### Adım 1: Kurulum Sihirbazı

İlk açılışta kurulum ekranı görünür:

1. **"Devam Et"** butonuna tıklayın
2. **Veri klasörünü seçin** veya varsayılanı kabul edin
3. **"Kurulumu Tamamla"** butonuna tıklayın

### Adım 2: Oluşturulan Klasör Yapısı

```
~/Documents/HyprContext/
├── screenshots/      # Ekran görüntüleri
├── planlar/          # Günlük planlar (.json, .md)
├── raporlar/         # Aktivite raporları
├── hafiza_db/        # AI hafıza veritabanı
├── profile.yaml      # Kullanıcı profili
└── history.jsonl     # Aktivite geçmişi
```

### Adım 3: Takibi Başlat

- **Tray ikonuna sağ tıklayın**
- **"▶️ Başlat"** seçeneğini tıklayın
- Artık 30 saniyede bir aktiviteleriniz kaydediliyor!

---

## ⚙️ Yapılandırma

### Profil Ayarları

`profile.yaml` dosyasını düzenleyin:

```yaml
user:
  name: "Adınız"
  profession: "Mesleğiniz"

daily_limits:
  distraction_minutes: 120  # 2 saat

banned_keywords:
  - youtube
  - twitter
  - reddit

courses:
  - name: "Python Kursu"
    platform: "Udemy"
    progress: 65
```

### Environment Variables

```bash
export HYPRCONTEXT_DATA_PATH="~/MyData/HyprContext"
export HYPRCONTEXT_SCREENSHOT_INTERVAL=60  # saniye
```

---

## 🔍 Sorun Giderme

### Ollama bağlanmıyor

```bash
# Servis durumunu kontrol et
systemctl --user status ollama

# Yeniden başlat
systemctl --user restart ollama
```

### grim çalışmıyor

```bash
# Test et
grim /tmp/test.png

# Wayland ortam değişkenlerini kontrol et
echo $WAYLAND_DISPLAY
echo $XDG_RUNTIME_DIR
```

### Backend başlamıyor

```bash
# Port kullanımda mı?
lsof -i :8000

# Manuel başlat
cd /path/to/HyprContext
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## ⬆️ Güncelleme

```bash
# Yeni AppImage'ı indir
wget https://github.com/ozhangebesoglu/HyprContext/releases/latest/download/HyprContext-*.AppImage

# Eskisini sil, yenisini çalıştır
chmod +x HyprContext-*.AppImage
./HyprContext-*.AppImage
```

> 💡 Verileriniz korunur çünkü ayrı bir klasörde saklanır.

---

[[← Ana Sayfa|Home]] | [[Kullanım Kılavuzu →]]
