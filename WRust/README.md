# 🦀 HyprContext Rust Core

**Yüksek performanslı AI hafıza ajanı daemon'ı** - Minimal bellek kullanımı, maksimum verimlilik.

## 🚀 Özellikler

- ⚡ **Düşük Kaynak Kullanımı**: ~10MB RAM, %0.1 CPU (idle)
- 🔒 **Tip Güvenliği**: Rust'ın derleme zamanı garantileri
- 🎯 **Odak Takibi**: Yasaklı uygulamalarda geçirilen süreyi izler
- 📊 **SQLite Veritabanı**: Hafif ve güvenilir veri saklama
- 🔔 **Sistem Bildirimleri**: Anlık uyarılar

## 📦 Kurulum

### Gereksinimler

```bash
# Arch Linux
sudo pacman -S grim libnotify rustup

# Rust toolchain
rustup default stable
```

### Derleme

```bash
cd WRust

# Development build
cargo build

# Release build (optimize)
cargo build --release
```

## 🎮 Kullanım

### Ana Daemon

```bash
# Geliştirme modunda
cargo run

# veya release binary
./target/release/hyprcontext_core run

# Verbose logging ile
./target/release/hyprcontext_core -v run
```

### Komutlar

```bash
# Odak istatistikleri
./target/release/hyprcontext_core stats

# Veritabanı istatistikleri
./target/release/hyprcontext_core db-stats

# Son 20 kayıt
./target/release/hyprcontext_core recent --limit 20
```

## ⚙️ Konfigürasyon

`.env` dosyası oluşturun:

```bash
cp .env.example .env
nano .env
```

### Değişkenler

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `HYPR_CAPTURE_INTERVAL` | 20 | Screenshot aralığı (saniye) |
| `HYPR_MODEL_VISION` | gemma3 | Ollama vision modeli |
| `HYPR_BANNED_KEYWORDS` | youtube,... | Yasaklı kelimeler |
| `HYPR_DAILY_DISTRACTION_LIMIT` | 7200 | Günlük limit (saniye) |
| `HYPR_DB_PATH` | hyprcontext.db | Veritabanı yolu |

## 🏗️ Modül Yapısı

```
src/
├── main.rs       # CLI ve daemon döngüsü
├── config.rs     # Konfigürasyon yönetimi
├── capture.rs    # Screenshot (grim)
├── window.rs     # Hyprland entegrasyonu
├── analyzer.rs   # Ollama AI analizi
├── database.rs   # SQLite işlemleri
├── focus.rs      # Odak takipçisi
└── notifier.rs   # Sistem bildirimleri
```

## 🔄 Python ile Entegrasyon

Rust daemon veritabanını Python tarafından da okuyabilirsiniz:

```python
import sqlite3

conn = sqlite3.connect('hyprcontext.db')
cursor = conn.execute('SELECT * FROM memories ORDER BY id DESC LIMIT 10')

for row in cursor:
    print(row)
```

## 📊 Performans Karşılaştırması

| Metrik | Python | Rust |
|--------|--------|------|
| RAM (idle) | ~80MB | ~10MB |
| CPU (idle) | %1-2 | %0.1 |
| Startup | ~500ms | ~5ms |
| Binary | N/A | ~8MB |

## 🛠️ Geliştirme

```bash
# Test
cargo test

# Lint
cargo clippy

# Format
cargo fmt

# Watch mode
cargo watch -x run
```

## 📄 Lisans

MIT License






