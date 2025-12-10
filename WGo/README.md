# 🐹 HyprContext Go Dashboard

**Hızlı ve şık web dashboard** - Rust daemon'ın verilerini görselleştirir.

## 🚀 Özellikler

- ⚡ **Tek Binary**: CGO ile SQLite embedded
- 🎨 **Modern UI**: Tailwind CSS + Koyu tema
- 📊 **Canlı İstatistikler**: 30 saniyede bir otomatik yenileme
- 🎯 **Odak Takibi**: Günlük limit ve kalan süre görsel

## 📦 Kurulum

### Gereksinimler

```bash
# Go 1.21+
go version

# CGO için (SQLite)
sudo pacman -S gcc
```

### Derleme

```bash
cd WGo

# Normal build
go build -o hyprcontext-dashboard .

# Optimize build
go build -ldflags="-s -w" -o hyprcontext-dashboard .
```

## 🎮 Kullanım

```bash
# Varsayılan port (8080)
./hyprcontext-dashboard

# Farklı port
PORT=3000 ./hyprcontext-dashboard

# Farklı DB yolu
DB_PATH=/path/to/hyprcontext.db ./hyprcontext-dashboard
```

Sonra tarayıcıda: **http://localhost:8080**

## ⚙️ Konfigürasyon

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `PORT` | 8080 | HTTP port |
| `DB_PATH` | ../WRust/hyprcontext.db | SQLite dosyası |
| `FOCUS_FILE` | ../WRust/focus_data.json | Odak takip dosyası |

## 📁 Dosya Yapısı

```
WGo/
├── main.go              # HTTP server + handlers
├── db/
│   └── sqlite.go        # Veritabanı işlemleri
├── templates/
│   └── dashboard.html   # Ana sayfa template
└── static/              # CSS/JS dosyaları
```

## 🔗 API Endpoints

### Veri Okuma

| Endpoint | Parametreler | Açıklama |
|----------|--------------|----------|
| `GET /` | - | Dashboard ana sayfa |
| `GET /api/health` | - | Sağlık kontrolü |
| `GET /api/stats` | - | Genel istatistikler |
| `GET /api/recent` | `?limit=N` | Son N kayıt (varsayılan: 50) |
| `GET /api/by-date` | `?date=YYYY-MM-DD` | Tarihe göre kayıtlar |
| `GET /api/hourly` | `?date=YYYY-MM-DD` | Saatlik aktivite dağılımı |
| `GET /api/tags` | `?limit=N` | En çok kullanılan etiketler |
| `GET /api/search` | `?q=sorgu` | Metin araması |
| `GET /api/focus` | - | Odak takip verisi |

### AI İşlemleri (POST)

| Endpoint | Body | Açıklama |
|----------|------|----------|
| `POST /api/plan` | `{"note": "...", "profile": "..."}` | Günlük plan oluştur |
| `POST /api/report` | `?date=YYYY-MM-DD` | Günlük rapor oluştur |
| `POST /api/ask` | `{"question": "..."}` | Hafızaya soru sor |

### Örnek Kullanım

```bash
# Sağlık kontrolü
curl http://localhost:8080/api/health

# Son 10 kayıt
curl "http://localhost:8080/api/recent?limit=10"

# Arama
curl "http://localhost:8080/api/search?q=python"

# Günlük plan oluştur
curl -X POST http://localhost:8080/api/plan \
  -H "Content-Type: application/json" \
  -d '{"note": "Bugün React öğreneceğim"}'

# Hafızaya soru sor
curl -X POST http://localhost:8080/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Dün ne yaptım?"}'
```

## 📊 Ekran Görüntüsü

```
┌─────────────────────────────────────────────────────────────┐
│  🧠 HyprContext                                    🔄 Yenile │
│  Kişisel AI Hafıza Ajanı                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────┐  ┌─────────┐  ┌────────────────────────────┐  │
│  │  1,234  │  │   42    │  │ Odak: 45dk / 2s kaldı      │  │
│  │  Toplam │  │  Bugün  │  │ ████████░░░░░░░░ 37.5%     │  │
│  └─────────┘  └─────────┘  └────────────────────────────┘  │
│                                                              │
│  📋 Son Aktiviteler                    ℹ️ Bilgiler          │
│  ├─ 14:30 [Python, VSCode]             İlk: 2025-11-20     │
│  │  VSCode'da main.py düzenleniyor     Son: 2025-11-29     │
│  ├─ 14:25 [Terminal, Git]                                   │
│  │  Git commit işlemi yapılıyor        🚫 Yasaklı          │
│  └─ ...                                youtube, netflix... │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Geliştirme

```bash
# Hot reload (air kullanarak)
go install github.com/air-verse/air@latest
air

# Testler
go test ./...
```

## 📄 Lisans

MIT License

