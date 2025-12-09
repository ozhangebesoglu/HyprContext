# 🔄 HyprContext Veri Akışı

## 📊 Genel Bakış

HyprContext, kullanıcının bilgisayar aktivitelerini izleyen, analiz eden ve raporlayan bir sistemdir. Veri akışı 5 ana katmandan oluşur.

---

## 1️⃣ Veri Toplama Katmanı

### Girdiler
- **Ekran Görüntüsü:** `grim` aracı ile Wayland ekran görüntüsü alınır
- **Pencere Bilgisi:** `hyprctl` komutu ile Hyprland'dan aktif pencere ve tüm workspace'lerdeki pencereler alınır

### Toplanan Veriler
- Screenshot (PNG formatında)
- Aktif pencere: Uygulama adı ve pencere başlığı
- Arka plan pencereleri: Tüm workspace'lerdeki açık uygulamaların adı

### Tetikleyici
- Her **20 saniyede** bir otomatik olarak çalışır
- Manuel tetikleme de yapılabilir

---

## 2️⃣ Analiz Katmanı

### Kullanılan Teknoloji
- **Ollama** üzerinde çalışan **gemma3** modeli
- Vision (görüntü) desteği ile screenshot analizi

### Analiz Süreci
1. Screenshot ve pencere bilgisi Ollama'ya gönderilir
2. AI, görüntüyü ve metni birlikte değerlendirir
3. Kullanıcının ne yaptığını özetleyen bir metin üretir
4. İlgili etiketler (tags) çıkarır

### Örnek Çıktı
```
Girdi: VS Code ekran görüntüsü + "code | main.py - HyprContext"
Çıktı: "VS Code'da Python projesi geliştiriyor. [Python, Geliştirme, Kodlama]" (Etiketlemesinin sebebi: Kategorileştirme)
```

---

## 3️⃣ Depolama Katmanı

### İki Katmanlı Depolama

#### JSONL (history.jsonl)
- **Format:** Her satır bir JSON objesi
- **Amaç:** Düz metin log, kolay okuma, backup
- **İçerik:** Timestamp + özet metin

#### ChromaDB (hafiza_db/)
- **Format:** Vektör embedding'ler
- **Amaç:** Semantik arama, benzerlik sorguları
- **İçerik:** Metin + embedding + metadata

### Neden İki Katman?
- JSONL: Hızlı erişim, debug, dışa aktarma
- ChromaDB: "Dün ne yaptım?" gibi doğal dil sorgular

---

## 4️⃣ API Katmanı

### Teknoloji
- **FastAPI** sunucusu
- **localhost:8000** portunda çalışır

### REST API Endpoints

#### Aktiviteler
| Endpoint | Açıklama |
|----------|----------|
| `GET /activities` | Son aktiviteleri listele |
| `GET /activities/today` | Bugünün aktiviteleri |
| `GET /activities/search?q=python` | Semantik arama |
| `GET /activities/stats` | İstatistikler |

#### Planlar
| Endpoint | Açıklama |
|----------|----------|
| `GET /plans` | Tüm planları listele |
| `GET /plans/2025-12-09` | Belirli tarihin planı |
| `POST /plans/generate` | Yeni plan oluştur |

#### Raporlar
| Endpoint | Açıklama |
|----------|----------|
| `GET /reports` | Tüm raporları listele |
| `GET /reports/2025-12-09` | Belirli tarihin raporu |
| `POST /reports/generate` | Rapor oluştur |

#### Kontrol
| Endpoint | Açıklama |
|----------|----------|
| `POST /control/start` | Yakalamayı başlat |
| `POST /control/stop` | Yakalamayı durdur |
| `GET /control/status` | Durum sorgula |

### WebSocket Streams
| Endpoint | Açıklama |
|----------|----------|
| `WS /ws/activities` | Canlı aktivite akışı |
| `WS /ws/system` | CPU/RAM/GPU anlık değerler |
| `WS /ws/focus` | Odak uyarıları |

---

## 5️⃣ Kullanıcı Arayüzü Katmanı

### Teknoloji
- **Electron** masaüstü uygulaması
- **React** + **TypeScript** frontend
- **TailwindCSS** stil

### Sayfalar

#### 🏠 Ana Sayfa
- Başlat/Durdur kontrolü
- Sistem ile başlat seçeneği
- Bugünün özet istatistikleri

#### 📝 Anlık Yorumlar
- WebSocket ile canlı aktivite akışı
- Etiket bazlı filtreleme
- Zaman bazlı liste

#### 📊 Grafikler
- CPU, RAM, GPU, Disk kullanımı
- Saatlik aktivite dağılımı
- En çok kullanılan uygulamalar

#### 📅 Planlar
- Tarih bazlı plan listesi
- Yeni plan oluşturma
- Görev checkbox'ları

#### 📄 Raporlar
- Günlük rapor görüntüleme
- Geçmiş raporlar
- Dışa aktarma

#### ⚙️ Ayarlar
- AI model seçimi
- Yakalama aralığı
- Yasaklı uygulamalar
- Dizin ayarları

---

## 🔁 Ana Döngü (Her 20 Saniye)

1. **Screenshot al** → grim ile ekran görüntüsü
2. **Pencere bilgisi al** → hyprctl ile aktif ve arka plan pencereleri
3. **AI'a gönder** → Ollama gemma3 modeline görüntü + metin
4. **Analiz al** → Özet metin ve etiketler
5. **JSONL'e kaydet** → history.jsonl dosyasına ekle
6. **ChromaDB'ye kaydet** → Vektör embedding oluştur ve kaydet
7. **WebSocket ile bildir** → Bağlı tüm client'lara yeni aktiviteyi gönder
8. **Bekle** → 20 saniye sonra tekrarla

---

## 🎯 Odak Takibi Döngüsü (Her 1 Saniye)

1. **Pencere kontrol et** → Aktif ve arka plan pencereleri
2. **Yasaklı kelime ara** → youtube, instagram, twitter, reddit, vb.
3. **Eğer yasaklı varsa:**
   - Sayacı 1 saniye artır
   - Günlük toplam süreyi güncelle
4. **Eşik kontrolü:**
   - 30 dakika → Normal uyarı
   - 1 saat → Normal uyarı
   - 1.5 saat → Normal uyarı
   - 2 saat → Kritik uyarı (limit doldu)
5. **Uyarı gönder:**
   - Masaüstü bildirimi (notify-send)
   - Ses uyarısı (paplay)
   - Sesli uyarı (edge-tts ile Türkçe)

---

## 📤 Çıktı Türleri

### Plan Oluşturma
- **Girdi:** Son 7 günün aktiviteleri + kullanıcı profili + hava durumu
- **İşlem:** Ollama AI plan şablonunu doldurur
- **Çıktı:** `Plan_2025-12-09.md` dosyası Obsidian'a kaydedilir

### Rapor Oluşturma
- **Girdi:** Bugünün tüm aktiviteleri
- **İşlem:** Ollama AI rapor şablonunu doldurur
- **Çıktı:** `2025-12-09.md` dosyası Obsidian'a kaydedilir

### Sohbet (Chat)
- **Girdi:** Kullanıcı sorusu
- **İşlem:** Semantik arama ile ilgili kayıtlar bulunur, AI'a gönderilir
- **Çıktı:** Kayıtlara dayalı Türkçe yanıt

---

## 🔗 Modül İlişkileri

### config.py (Merkez)
Tüm modüller config.py'den ayarları okur:
- Dosya yolları
- Model isimleri
- Zaman aralıkları
- Yasaklı kelimeler

### database.py
- JSONL okuma/yazma
- ChromaDB bağlantısı
- Semantik arama
- Tarih bazlı sorgular

### window_utils.py
- Hyprland ile iletişim
- Aktif pencere bilgisi
- Tüm workspace bilgisi

### Servisler
- **Capture Service:** Screenshot + analiz + kayıt
- **Focus Service:** Pencere takibi + uyarılar
- **System Service:** CPU/RAM/GPU izleme

### API Katmanı
- FastAPI routes
- WebSocket handlers
- Background tasks

---

## 📋 Teknoloji Özeti

| Katman | Teknoloji | Görevi |
|--------|-----------|--------|
| Ekran Yakalama | grim | Wayland screenshot |
| Pencere Bilgisi | hyprctl | Hyprland API |
| AI Analiz | Ollama + gemma3 | Görüntü ve metin analizi |
| Embedding | mxbai-embed-large | Vektör oluşturma |
| Vektör DB | ChromaDB | Semantik arama |
| Log Depolama | JSONL | Düz metin kayıt |
| API Sunucu | FastAPI | REST + WebSocket |
| Masaüstü App | Electron | Uygulama çerçevesi |
| Frontend | React + TypeScript | Kullanıcı arayüzü |
| Stil | TailwindCSS | UI tasarım |

---

*Son güncelleme: 2025-12-09*
