# 🧠 HyprContext Algoritmaları

## 1. Ana Yakalama Algoritması

### Başlatma
```
BAŞLA
    config dosyasını yükle
    veritabanı bağlantısını aç
    WebSocket sunucusunu başlat
    capture_running = false
```

### Ana Döngü
```
FONKSIYON ana_dongu():
    WHILE capture_running == true:
        
        // 1. Veri Toplama
        screenshot_sonuc = grim_ile_ekran_yakala()
        
        EĞER screenshot_sonuc.hata:
            log_error(screenshot_sonuc.hata_mesaji)
            bekle(CAPTURE_INTERVAL)
            DEVAM ET
        
        screenshot = screenshot_sonuc.veri
        
        pencere_sonuc = hyprctl_aktif_pencere()
        
        EĞER pencere_sonuc.hata:
            log_error(pencere_sonuc.hata_mesaji)
            bekle(CAPTURE_INTERVAL)
            DEVAM ET
        
        aktif_pencere = pencere_sonuc.veri
        tum_pencereler = hyprctl_tum_pencereler()
        
        // 2. Prompt Hazırlama
        prompt_sonuc = olustur_prompt(screenshot, aktif_pencere, tum_pencereler)
        
        EĞER prompt_sonuc.hata:
            log_error(prompt_sonuc.hata_mesaji)
            bekle(CAPTURE_INTERVAL)
            DEVAM ET
        
        // 3. AI Analizi
        analiz_sonuc = ollama_analiz(prompt_sonuc.veri, screenshot)
        
        EĞER analiz_sonuc.hata:
            log_error(analiz_sonuc.hata_mesaji)
            bekle(CAPTURE_INTERVAL)
            DEVAM ET
        
        // 4. Sonuç Ayrıştırma
        ozet = ayristir_ozet(analiz_sonuc.veri)
        etiketler = ayristir_etiketler(analiz_sonuc.veri)
        
        // 5. Kurs Tespiti (Otomatik)
        kurs_tespit = tespit_et_kurs(aktif_pencere, screenshot)
        EĞER kurs_tespit.bulundu:
            bildirim_kurs_onerisi(kurs_tespit)
        
        // 6. Kaydetme
        timestamp = simdi()
        jsonl_kaydet(timestamp, ozet)
        chromadb_kaydet(timestamp, ozet, etiketler)
        
        // 7. Bildirme
        websocket_broadcast({
            timestamp: timestamp,
            summary: ozet,
            tags: etiketler
        })
        
        // 8. Bekleme
        bekle(CAPTURE_INTERVAL)  // varsayılan 20 saniye
    
    DÖNGÜ SONU
```

### Ekran Yakalama
```
FONKSIYON grim_ile_ekran_yakala():
    dosya_yolu = "/tmp/hyprcontext_screenshot.png"
    
    DENE:
        sonuc = calistir("grim", dosya_yolu, timeout=5)
        
        EĞER sonuc.exit_code != 0:
            DÖNDÜR {
                hata: true,
                hata_mesaji: "SCREENSHOT_FAILED: grim komutu başarısız. Exit code: {sonuc.exit_code}. Stderr: {sonuc.stderr}",
                hata_tipi: "GRIM_ERROR"
            }
        
        EĞER dosya_var(dosya_yolu) == false:
            DÖNDÜR {
                hata: true,
                hata_mesaji: "SCREENSHOT_FILE_NOT_FOUND: grim çalıştı ama dosya oluşmadı. Yol: {dosya_yolu}. Disk dolu olabilir veya yazma izni yok.",
                hata_tipi: "FILE_NOT_CREATED"
            }
        
        dosya_boyut = dosya_boyutu(dosya_yolu)
        EĞER dosya_boyut < 1000:  // 1KB'dan küçükse
            DÖNDÜR {
                hata: true,
                hata_mesaji: "SCREENSHOT_TOO_SMALL: Dosya boyutu çok küçük ({dosya_boyut} bytes). Ekran boş olabilir veya grim düzgün çalışmamış.",
                hata_tipi: "INVALID_SCREENSHOT"
            }
        
        base64_veri = dosya_oku_base64(dosya_yolu)
        
        DÖNDÜR {
            hata: false,
            veri: base64_veri
        }
    
    HATA DURUMUNDA FileNotFoundError:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "GRIM_NOT_INSTALLED: grim komutu bulunamadı. Kurulum: 'sudo pacman -S grim' (Arch) veya 'sudo apt install grim' (Debian)",
            hata_tipi: "GRIM_NOT_FOUND"
        }
    
    HATA DURUMUNDA TimeoutError:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "GRIM_TIMEOUT: grim 5 saniye içinde yanıt vermedi. Wayland compositor sorunlu olabilir.",
            hata_tipi: "TIMEOUT"
        }
    
    HATA DURUMUNDA Exception as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "SCREENSHOT_UNKNOWN_ERROR: Beklenmeyen hata: {str(e)}",
            hata_tipi: "UNKNOWN"
        }
```

### Pencere Bilgisi Alma
```
FONKSIYON hyprctl_aktif_pencere():
    
    DENE:
        sonuc = calistir("hyprctl activewindow -j", timeout=5)
        
        EĞER sonuc.exit_code != 0:
            DÖNDÜR {
                hata: true,
                hata_mesaji: "HYPRCTL_FAILED: hyprctl komutu başarısız. Exit code: {sonuc.exit_code}. Hyprland çalışıyor mu?",
                hata_tipi: "HYPRCTL_ERROR"
            }
        
        EĞER sonuc.stdout.strip() == "":
            DÖNDÜR {
                hata: true,
                hata_mesaji: "HYPRCTL_EMPTY: hyprctl boş yanıt döndü. Aktif pencere yok olabilir.",
                hata_tipi: "EMPTY_RESPONSE"
            }
        
        json = parse_json(sonuc.stdout)
        
        DÖNDÜR {
            hata: false,
            veri: {
                class: json.class veya "Bilinmiyor",
                title: json.title veya "Bilinmiyor"
            }
        }
    
    HATA DURUMUNDA FileNotFoundError:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "HYPRCTL_NOT_FOUND: hyprctl komutu bulunamadı. Hyprland kurulu mu? HYPRLAND_INSTANCE_SIGNATURE ortam değişkeni tanımlı mı?",
            hata_tipi: "HYPRCTL_NOT_FOUND"
        }
    
    HATA DURUMUNDA JSONDecodeError as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "HYPRCTL_JSON_ERROR: JSON parse hatası. Ham veri: {sonuc.stdout[:100]}. Hata: {str(e)}",
            hata_tipi: "JSON_ERROR"
        }
    
    HATA DURUMUNDA Exception as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "HYPRCTL_UNKNOWN_ERROR: Beklenmeyen hata: {str(e)}",
            hata_tipi: "UNKNOWN"
        }

FONKSIYON hyprctl_tum_pencereler():
    sonuc = calistir("hyprctl clients -j")
    
    EĞER sonuc.hata:
        DÖNDÜR {}  // Boş map, kritik değil
    
    clients = parse_json(sonuc.stdout)
    
    workspace_map = {}
    
    HER client İÇİN clients:
        ws_id = client.workspace.id
        
        EĞER ws_id > 0:
            EĞER ws_id workspace_map'te YOK:
                workspace_map[ws_id] = []
            
            workspace_map[ws_id].ekle({
                app: client.class,
                title: client.title[0:25]
            })
    
    DÖNDÜR workspace_map
```

---

## 2. AI Analiz Algoritması

### Prompt Oluşturma
```
FONKSIYON olustur_prompt(screenshot, aktif, tum):
    
    // Girdi doğrulama
    EĞER screenshot == null VEYA screenshot == "":
        DÖNDÜR {
            hata: true,
            hata_mesaji: "PROMPT_NO_SCREENSHOT: Screenshot verisi boş. Ekran yakalama başarısız olmuş.",
            hata_tipi: "INVALID_INPUT"
        }
    
    EĞER aktif == null:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "PROMPT_NO_WINDOW: Aktif pencere bilgisi yok. Hyprland bağlantısı kontrol edilmeli.",
            hata_tipi: "INVALID_INPUT"
        }
    
    pencere_metni = formatla_pencereler(aktif, tum)
    
    EĞER pencere_metni.uzunluk > 5000:
        pencere_metni = pencere_metni[0:5000] + "... (kısaltıldı)"
        log_warning("Pencere metni çok uzun, kısaltıldı.")
    
    prompt = """
    Ekran görüntüsünü ve pencere bilgilerini analiz et.
    
    PENCERELER:
    {pencere_metni}
    
    GÖREV:
    1. Kullanıcının ne yaptığını tek cümle ile özetle
    2. İlgili etiketleri belirle (en az 2, en fazla 5 etiket)
    
    ETİKET KURALLARI:
    - Uygulama adı (VS Code, Chrome, Terminal, vb.)
    - Aktivite türü (Kodlama, Araştırma, Video, Oyun, vb.)
    - Teknoloji/Dil (Python, JavaScript, React, vb.)
    - Durum (Geliştirme, Öğrenme, Eğlence, Boşta, vb.)
    
    FORMAT (Bu formatı kesinlikle kullan):
    [özet cümlesi] [Etiket1, Etiket2, Etiket3]
    
    ÖRNEK:
    VS Code'da Python projesi geliştiriyor. [VS Code, Python, Geliştirme, Kodlama]
    """
    
    DÖNDÜR {
        hata: false,
        veri: prompt
    }
```

### Ollama İletişimi
```
FONKSIYON ollama_analiz(prompt, screenshot):
    
    istek = {
        model: MODEL_VISION,  // "gemma3"
        prompt: prompt,
        images: [screenshot],
        stream: false
    }
    
    DENE:
        // Bağlantı testi
        health_check = http_get("http://localhost:11434/api/tags", timeout=3)
        
        EĞER health_check.status != 200:
            DÖNDÜR {
                hata: true,
                hata_mesaji: "OLLAMA_NOT_RUNNING: Ollama servisi çalışmıyor. Başlatmak için: 'ollama serve' veya 'systemctl start ollama'",
                hata_tipi: "SERVICE_DOWN",
                cozum_onerileri: [
                    "1. Terminal'de 'ollama serve' çalıştırın",
                    "2. Veya 'systemctl --user start ollama'",
                    "3. Ollama kurulu değilse: https://ollama.ai adresinden indirin"
                ]
            }
        
        // Model kontrolü
        modeller = health_check.json().models
        model_var = MODEL_VISION modeller İÇİNDE
        
        EĞER model_var == false:
            DÖNDÜR {
                hata: true,
                hata_mesaji: "OLLAMA_MODEL_NOT_FOUND: '{MODEL_VISION}' modeli yüklü değil. Mevcut modeller: {modeller}",
                hata_tipi: "MODEL_MISSING",
                cozum_onerileri: [
                    "1. Modeli indirin: 'ollama pull {MODEL_VISION}'",
                    "2. Veya config'den farklı bir model seçin"
                ]
            }
        
        // Ana istek
        yanit = http_post("http://localhost:11434/api/generate", istek, timeout=60)
        
        EĞER yanit.status != 200:
            DÖNDÜR {
                hata: true,
                hata_mesaji: "OLLAMA_REQUEST_FAILED: API isteği başarısız. Status: {yanit.status}. Body: {yanit.body[:200]}",
                hata_tipi: "API_ERROR"
            }
        
        EĞER yanit.json().response == null VEYA yanit.json().response == "":
            DÖNDÜR {
                hata: true,
                hata_mesaji: "OLLAMA_EMPTY_RESPONSE: Model boş yanıt döndü. Screenshot çok karmaşık olabilir veya model context window aşılmış.",
                hata_tipi: "EMPTY_RESPONSE"
            }
        
        DÖNDÜR {
            hata: false,
            veri: yanit.json().response
        }
    
    HATA DURUMUNDA ConnectionError:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "OLLAMA_CONNECTION_ERROR: localhost:11434 adresine bağlanılamadı. Ollama servisi kapalı.",
            hata_tipi: "CONNECTION_REFUSED",
            cozum_onerileri: [
                "1. Ollama'nın çalıştığını kontrol edin: 'pgrep ollama'",
                "2. Servisi başlatın: 'ollama serve'",
                "3. Port'un açık olduğunu kontrol edin: 'ss -tlnp | grep 11434'"
            ]
        }
    
    HATA DURUMUNDA TimeoutError:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "OLLAMA_TIMEOUT: Model 60 saniye içinde yanıt vermedi. Model çok yavaş veya sistem kaynakları yetersiz.",
            hata_tipi: "TIMEOUT",
            cozum_onerileri: [
                "1. Daha küçük bir model deneyin (gemma2:2b)",
                "2. GPU kullanımını kontrol edin: 'nvidia-smi' veya 'rocm-smi'",
                "3. RAM kullanımını kontrol edin: 'free -h'"
            ]
        }
    
    HATA DURUMUNDA Exception as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "OLLAMA_UNKNOWN_ERROR: Beklenmeyen hata: {type(e).__name__}: {str(e)}",
            hata_tipi: "UNKNOWN"
        }
```

### Embedding Oluşturma
```
FONKSIYON ollama_embed(metin):
    
    EĞER metin == null VEYA metin.strip() == "":
        DÖNDÜR {
            hata: true,
            hata_mesaji: "EMBED_EMPTY_TEXT: Embedding için metin boş. Analiz sonucu alınamamış olabilir.",
            hata_tipi: "INVALID_INPUT"
        }
    
    istek = {
        model: MODEL_EMBED,  // "mxbai-embed-large"
        prompt: metin
    }
    
    DENE:
        yanit = http_post("http://localhost:11434/api/embeddings", istek, timeout=30)
        
        EĞER yanit.status != 200:
            DÖNDÜR {
                hata: true,
                hata_mesaji: "EMBED_REQUEST_FAILED: Embedding isteği başarısız. Status: {yanit.status}",
                hata_tipi: "API_ERROR",
                cozum_onerileri: [
                    "1. Embedding modelini kontrol edin: 'ollama list'",
                    "2. Model yoksa indirin: 'ollama pull {MODEL_EMBED}'"
                ]
            }
        
        embedding = yanit.json().embedding
        
        EĞER embedding == null VEYA embedding.uzunluk == 0:
            DÖNDÜR {
                hata: true,
                hata_mesaji: "EMBED_EMPTY_RESULT: Model embedding döndürmedi. Model bozuk olabilir.",
                hata_tipi: "EMPTY_RESPONSE"
            }
        
        DÖNDÜR {
            hata: false,
            veri: embedding
        }
    
    HATA DURUMUNDA ConnectionError:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "EMBED_CONNECTION_ERROR: Ollama'ya bağlanılamadı. Servis kapalı olabilir.",
            hata_tipi: "CONNECTION_REFUSED"
        }
    
    HATA DURUMUNDA TimeoutError:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "EMBED_TIMEOUT: Embedding 30 saniye içinde tamamlanmadı. Metin çok uzun olabilir.",
            hata_tipi: "TIMEOUT"
        }
    
    HATA DURUMUNDA Exception as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "EMBED_UNKNOWN_ERROR: Beklenmeyen hata: {type(e).__name__}: {str(e)}",
            hata_tipi: "UNKNOWN"
        }
```

### Sonuç Ayrıştırma
```
FONKSIYON ayristir_ozet(analiz):
    // "[" karakterinden önceki kısım özet
    EĞER "[" analiz İÇİNDE:
        DÖNDÜR analiz.split("[")[0].trim()
    DEĞİLSE:
        DÖNDÜR analiz.trim()

FONKSIYON ayristir_etiketler(analiz):
    // [...] içindeki kısım etiketler
    regex = /\[([^\]]+)\]$/
    eslesme = regex.bul(analiz)
    
    EĞER eslesme:
        etiket_str = eslesme[1]
        etiketler = etiket_str.split(",").map(e => e.trim())
        
        // Boş etiketleri filtrele
        etiketler = etiketler.filter(e => e.uzunluk > 0)
        
        EĞER etiketler.uzunluk > 0:
            DÖNDÜR etiketler
    
    // Etiket bulunamadı - akıllı tahmin yap
    DÖNDÜR tahmin_et_etiketler(analiz)

FONKSIYON tahmin_et_etiketler(analiz):
    """
    AI etiket döndürmediyse, metinden akıllı tahmin yap.
    Bu fonksiyon "Genel" yerine daha anlamlı etiketler üretir.
    """
    
    analiz_kucuk = analiz.kucuk_harf()
    bulunan_etiketler = []
    
    // Uygulama tespiti
    uygulama_eslestirme = {
        "code": "VS Code",
        "vscode": "VS Code",
        "cursor": "Cursor",
        "chrome": "Chrome",
        "firefox": "Firefox",
        "zen": "Zen Browser",
        "terminal": "Terminal",
        "kitty": "Terminal",
        "obsidian": "Obsidian",
        "spotify": "Spotify",
        "discord": "Discord",
        "slack": "Slack"
    }
    
    HER (anahtar, deger) İÇİN uygulama_eslestirme:
        EĞER anahtar analiz_kucuk İÇİNDE:
            bulunan_etiketler.ekle(deger)
            BREAK  // İlk eşleşme yeterli
    
    // Aktivite tespiti
    aktivite_eslestirme = {
        "yazıyor": "Kodlama",
        "geliştir": "Geliştirme",
        "izliyor": "Video",
        "okuyor": "Okuma",
        "araştır": "Araştırma",
        "dinliyor": "Müzik",
        "oyun": "Oyun",
        "sohbet": "İletişim",
        "mail": "E-posta",
        "not": "Not Alma"
    }
    
    HER (anahtar, deger) İÇİN aktivite_eslestirme:
        EĞER anahtar analiz_kucuk İÇİNDE:
            bulunan_etiketler.ekle(deger)
            BREAK
    
    // Teknoloji tespiti
    teknoloji_eslestirme = {
        "python": "Python",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "react": "React",
        "node": "Node.js",
        "rust": "Rust",
        "go": "Go",
        "java": "Java",
        "html": "HTML",
        "css": "CSS"
    }
    
    HER (anahtar, deger) İÇİN teknoloji_eslestirme:
        EĞER anahtar analiz_kucuk İÇİNDE:
            bulunan_etiketler.ekle(deger)
    
    // En az 1 etiket garanti
    EĞER bulunan_etiketler.uzunluk == 0:
        // Son çare: zaman bazlı etiket
        saat = simdi().saat
        EĞER saat >= 9 VE saat < 12:
            bulunan_etiketler.ekle("Sabah Aktivitesi")
        DEĞİLSE EĞER saat >= 12 VE saat < 18:
            bulunan_etiketler.ekle("Gündüz Aktivitesi")
        DEĞİLSE:
            bulunan_etiketler.ekle("Akşam Aktivitesi")
        
        bulunan_etiketler.ekle("Sınıflandırılamadı")
        
        log_warning("ETİKET_TAHMİN_BAŞARISIZ: AI etiket döndürmedi ve otomatik tahmin yapılamadı. Analiz: {analiz[:100]}")
    
    DÖNDÜR bulunan_etiketler
```

---

## 3. Veritabanı Kayıt Algoritması

### JSONL Kayıt
```
FONKSIYON jsonl_kaydet(timestamp, ozet):
    kayit = {
        timestamp: timestamp.isoformat(),
        summary: ozet
    }
    
    DENE:
        satir = json_stringify(kayit)
        dosya_ekle(HISTORY_FILE, satir + "\n")
        
        DÖNDÜR {hata: false}
    
    HATA DURUMUNDA IOError as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "JSONL_WRITE_ERROR: Dosyaya yazılamadı. Disk dolu veya izin yok. Hata: {str(e)}",
            hata_tipi: "IO_ERROR"
        }
```

### ChromaDB Kayıt
```
FONKSIYON chromadb_kaydet(timestamp, ozet, etiketler):
    
    // 1. Embedding oluştur
    embed_sonuc = ollama_embed(ozet)
    
    EĞER embed_sonuc.hata:
        log_error(embed_sonuc.hata_mesaji)
        DÖNDÜR {hata: true, hata_mesaji: embed_sonuc.hata_mesaji}
    
    embedding = embed_sonuc.veri
    
    // 2. Benzersiz ID üret
    doc_id = timestamp.format("YYYYMMDD_HHmmss_ffffff")
    
    // 3. Metadata hazırla
    metadata = {
        timestamp: timestamp.isoformat(),
        date: timestamp.format("YYYY-MM-DD"),
        time: timestamp.format("HH:mm"),
        tags: etiketler.join(",")
    }
    
    // 4. Koleksiyona ekle
    DENE:
        collection.add(
            documents: [ozet],
            embeddings: [embedding],
            metadatas: [metadata],
            ids: [doc_id]
        )
        DÖNDÜR {hata: false}
    
    HATA DURUMUNDA Exception as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "CHROMADB_INSERT_ERROR: Vektör veritabanına eklenemedi. Hata: {str(e)}",
            hata_tipi: "DB_ERROR"
        }
```

---

## 4. Odak Takip Algoritması

### Ana Döngü
```
FONKSIYON odak_takip_dongusu():
    
    bugun = bugunun_tarihi()
    gunluk_veri = yukle_veya_olustur(bugun)
    son_uyari_esigi = 0
    
    WHILE true:
        
        // Gün değişimi kontrolü
        EĞER bugunun_tarihi() != bugun:
            bugun = bugunun_tarihi()
            gunluk_veri = yukle_veya_olustur(bugun)
            son_uyari_esigi = 0
            log_info("Yeni gün başladı, sayaç sıfırlandı.")
        
        // Yasaklı uygulama kontrolü
        (dikkat_dagıldı, bulunan_kelime) = kontrol_yasak()
        
        EĞER dikkat_dagıldı:
            gunluk_veri.distraction_seconds += 1
            
            // Log (her 30 saniyede)
            EĞER gunluk_veri.distraction_seconds % 30 == 0:
                log_info("Yasaklı uygulama açık: '{bulunan_kelime}' - Toplam: {formatla_sure(gunluk_veri.distraction_seconds)}")
            
            // Kaydet (her 60 saniyede)
            EĞER gunluk_veri.distraction_seconds % 60 == 0:
                kaydet_veri(gunluk_veri)
            
            // Uyarı kontrolü
            kontrol_uyari(gunluk_veri, son_uyari_esigi)
        
        bekle(1)  // 1 saniye - hafif yük, arka planda çalışır
```

### Yasaklı Uygulama Kontrolü
```
FONKSIYON kontrol_yasak():
    
    // Aktif pencereyi kontrol et
    aktif = hyprctl_aktif_pencere()
    
    EĞER aktif.hata == false:
        aktif_metin = (aktif.veri.class + " " + aktif.veri.title).kucuk_harf()
        
        HER kelime İÇİN YASAKLI_KELIMELER:
            EĞER kelime aktif_metin İÇİNDE:
                DÖNDÜR (true, kelime)
    
    // Tüm workspace'leri kontrol et
    tum = hyprctl_tum_pencereler()
    tum_metin = formatla_pencereler_metin(tum).kucuk_harf()
    
    HER kelime İÇİN YASAKLI_KELIMELER:
        EĞER kelime tum_metin İÇİNDE:
            DÖNDÜR (true, kelime)
    
    DÖNDÜR (false, null)
```

### Uyarı Sistemi
```
// Uyarı eşikleri: 15, 30, 60, 90, 120 dakika
// Sesli uyarı: 60 ve 120 dakikada
SABIT UYARI_ESIKLERI = [
    {saniye: 900,  etiket: "15 dakika",  sesli: false},  // 15 dk
    {saniye: 1800, etiket: "30 dakika",  sesli: false},  // 30 dk
    {saniye: 3600, etiket: "1 saat",     sesli: true},   // 60 dk - SESLİ
    {saniye: 5400, etiket: "1.5 saat",   sesli: false},  // 90 dk
    {saniye: 7200, etiket: "2 saat",     sesli: true}    // 120 dk - SESLİ + LİMİT
]

SABIT GUNLUK_LIMIT = 7200  // 2 saat

FONKSIYON kontrol_uyari(veri, son_esik):
    kullanilan = veri.distraction_seconds
    kalan = GUNLUK_LIMIT - kullanilan
    
    HER esik_obj İÇİN UYARI_ESIKLERI:
        esik = esik_obj.saniye
        etiket = esik_obj.etiket
        sesli = esik_obj.sesli
        
        EĞER kullanilan >= esik VE esik > son_esik:
            son_esik = esik
            veri.warnings_sent.ekle(esik)
            
            EĞER esik >= GUNLUK_LIMIT:
                // Kritik uyarı - LİMİT DOLDU
                veri.limit_reached = true
                
                bildirim_gonder(
                    baslik: "🛑 GÜNLÜK LİMİT DOLDU!",
                    mesaj: "Yasaklı uygulamalarda {etiket} geçirdin!\nBugünlük yeter, işine dön!",
                    oncelik: "critical"
                )
                
                // Sesli uyarı
                sesli_uyari("Dikkat! Günlük limit doldu. Lütfen işine dön!")
                
                log_warning("ODAK_LIMIT_DOLDU: Kullanıcı günlük limiti aştı. Toplam: {etiket}")
            
            DEĞİLSE:
                // Normal uyarı
                bildirim_gonder(
                    baslik: "⏰ Dikkat Dağınıklığı Uyarısı",
                    mesaj: "Yasaklı uygulamalarda {etiket} geçirdin.\nKalan süre: {formatla_sure(kalan)}",
                    oncelik: "normal"
                )
                
                // 60 dakikada sesli uyarı
                EĞER sesli:
                    sesli_uyari("Dikkat! {etiket} boyunca dikkatini dağıttın. Kalan süren {formatla_sure(kalan)}.")
                
                log_info("ODAK_UYARI: {etiket} eşiği aşıldı. Kalan: {formatla_sure(kalan)}")
            
            kaydet_veri(veri)
    
    // Limit aşıldıysa her 5 dakikada bir uyar
    EĞER veri.limit_reached VE kullanilan % 300 == 0 VE kullanilan > GUNLUK_LIMIT:
        bildirim_gonder(
            baslik: "🛑 LİMİT AŞILDI!",
            mesaj: "Bugün toplam {formatla_sure(kullanilan)} harcadın.\nHemen işine dön!",
            oncelik: "critical"
        )
        
        sesli_uyari("Limit aşıldı! İşine dön!")
```

---

## 5. Plan Oluşturma Algoritması

### Kurs Tespiti (Otomatik)
```
FONKSIYON tespit_et_kurs(aktif_pencere, screenshot):
    """
    Kullanıcının ekranında eğitim platformu varsa kursu tespit et.
    Desteklenen platformlar: Udemy, Coursera, Scrimba, YouTube (eğitim)
    """
    
    pencere_metin = (aktif_pencere.class + " " + aktif_pencere.title).kucuk_harf()
    
    // Platform tespiti
    platform = null
    
    EĞER "udemy" pencere_metin İÇİNDE:
        platform = "Udemy"
    DEĞİLSE EĞER "coursera" pencere_metin İÇİNDE:
        platform = "Coursera"
    DEĞİLSE EĞER "scrimba" pencere_metin İÇİNDE:
        platform = "Scrimba"
    DEĞİLSE EĞER "youtube" pencere_metin İÇİNDE VE ("tutorial" pencere_metin İÇİNDE VEYA "course" pencere_metin İÇİNDE VEYA "learn" pencere_metin İÇİNDE):
        platform = "YouTube"
    DEĞİLSE:
        DÖNDÜR {bulundu: false}
    
    // Kurs adını pencere başlığından çıkar
    kurs_adi = aktif_pencere.title
    
    // Platform adını temizle
    kurs_adi = kurs_adi.replace("- Udemy", "")
    kurs_adi = kurs_adi.replace("| Coursera", "")
    kurs_adi = kurs_adi.replace("- Scrimba", "")
    kurs_adi = kurs_adi.replace("- YouTube", "")
    kurs_adi = kurs_adi.trim()
    
    // Çok uzunsa kısalt
    EĞER kurs_adi.uzunluk > 50:
        kurs_adi = kurs_adi[0:50] + "..."
    
    DÖNDÜR {
        bulundu: true,
        platform: platform,
        kurs_adi: kurs_adi
    }

FONKSIYON bildirim_kurs_onerisi(kurs_tespit):
    """
    Kullanıcıya kurs ekleme önerisi gönder.
    """
    
    // Daha önce bu kurs önerildi mi kontrol et
    profil = yukle_yaml(PROFILE_PATH)
    mevcut_kurslar = profil.egitim_programi.durum veya []
    
    // Kurs zaten profilde mi?
    HER kurs İÇİN mevcut_kurslar:
        EĞER kurs.isim.kucuk_harf() == kurs_tespit.kurs_adi.kucuk_harf():
            DÖNDÜR  // Zaten var, bildirim gönderme
    
    // Son 1 saatte bu kurs için bildirim gönderildi mi?
    son_bildirim = cache_oku("kurs_bildirim_" + kurs_tespit.kurs_adi)
    EĞER son_bildirim VE (simdi() - son_bildirim) < 3600:
        DÖNDÜR  // 1 saat içinde tekrar sorma
    
    // Bildirim gönder
    bildirim_gonder_interaktif(
        baslik: "📚 Yeni Kurs Tespit Edildi!",
        mesaj: "{kurs_tespit.platform}'de '{kurs_tespit.kurs_adi}' kursunu izliyorsun.\n\nBu kursu profiline eklemek ister misin?",
        butonlar: [
            {id: "evet", metin: "✅ Evet, Ekle"},
            {id: "hayir", metin: "❌ Hayır"}
        ],
        callback: kurs_ekleme_yaniti
    )
    
    // Cache'e kaydet
    cache_yaz("kurs_bildirim_" + kurs_tespit.kurs_adi, simdi())

FONKSIYON kurs_ekleme_yaniti(buton_id, kurs_tespit):
    EĞER buton_id == "evet":
        // Profile ekle
        profil = yukle_yaml(PROFILE_PATH)
        
        yeni_kurs = {
            isim: kurs_tespit.kurs_adi,
            platform: kurs_tespit.platform,
            durum: "Sırada (Aktif)",
            ekleme_tarihi: bugunun_tarihi()
        }
        
        profil.egitim_programi.durum.ekle(yeni_kurs)
        kaydet_yaml(PROFILE_PATH, profil)
        
        bildirim_gonder(
            baslik: "✅ Kurs Eklendi!",
            mesaj: "'{kurs_tespit.kurs_adi}' profiline eklendi.",
            oncelik: "normal"
        )
        
        log_info("KURS_EKLENDI: {kurs_tespit.kurs_adi} ({kurs_tespit.platform})")
    DEĞİLSE:
        log_info("KURS_REDDEDILDI: Kullanıcı '{kurs_tespit.kurs_adi}' kursunu eklemedi.")
```

### Plan Oluşturma
```
FONKSIYON gunluk_plan_olustur(kullanici_notu, manuel_kurs):
    """
    Günlük plan oluştur.
    
    Parametreler:
    - kullanici_notu: Opsiyonel kullanıcı notu
    - manuel_kurs: Opsiyonel manuel kurs adı (otomatik tespit edilenin üzerine yazar)
    """
    
    // 1. Profili yükle
    DENE:
        profil = yukle_yaml(PROFILE_PATH)
    HATA DURUMUNDA FileNotFoundError:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "PLAN_PROFILE_NOT_FOUND: profile.yaml dosyası bulunamadı. Önce profil oluşturun.",
            hata_tipi: "PROFILE_MISSING"
        }
    HATA DURUMUNDA YAMLError as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "PLAN_PROFILE_INVALID: profile.yaml geçersiz YAML formatı. Hata: {str(e)}",
            hata_tipi: "PROFILE_INVALID"
        }
    
    // 2. Verileri topla
    hava = hava_durumu_al()  // Hata olursa "Bilinmiyor" döner
    
    // 3. Aktif kurs belirle
    EĞER manuel_kurs != null VE manuel_kurs != "":
        aktif_kurs = manuel_kurs
    DEĞİLSE:
        aktif_kurs = bul_aktif_kurs(profil)
    
    // 4. Logları al
    loglar_sonuc = son_n_gun_loglar(MEMORY_DAYS)
    
    EĞER loglar_sonuc.uzunluk == 0:
        log_warning("PLAN_NO_LOGS: Son {MEMORY_DAYS} günde log bulunamadı. Plan genel olacak.")
        log_metni = "Geçmiş aktivite verisi yok."
    DEĞİLSE:
        log_metni = formatla_loglar(loglar_sonuc)
    
    // 5. System prompt
    system_prompt = """
    Sen bir günlük planlama asistanısın.
    Sadece verilen şablonu doldur, ekstra açıklama yapma.
    Dil: Türkçe.
    
    KULLANICI PROFİLİ:
    {yaml_dump(profil)}
    """
    
    // 6. User prompt
    user_prompt = """
    Bugünün planını oluştur.
    
    VERİLER:
    - Tarih: {bugunun_tarihi()}
    - Hava: {hava}
    - Kullanıcı Notu: {kullanici_notu veya "Yok"}
    - Aktif Eğitim/Odak: {aktif_kurs}
    - Geçmiş Aktiviteler:
    {log_metni}
    
    KURAL: "{aktif_kurs}" konusuna odaklan. Tüm bloklar bu konuyla ilgili olsun.
    
    ŞABLON:
    # 🎯 Günün Misyonu: [Tek cümle hedef]
    > **Hava:** {hava}
    > **Odak:** {aktif_kurs}
    
    ## 🌅 Sabah (09:00 - 12:00)
    * [Saat]: [Görev] ({aktif_kurs})
    
    ## ☀️ Öğle (13:00 - 17:00)
    * [Saat]: [Görev] ({aktif_kurs})
    
    ## 🌙 Akşam (18:00 - 22:00)
    * [Saat]: [Görev] ({aktif_kurs})
    
    ## ⚠️ Asistan Notu
    [Kısa motivasyon notu]
    """
    
    // 7. AI'dan plan al
    DENE:
        plan_sonuc = ollama_chat(system_prompt, user_prompt, {
            temperature: 0.1,
            num_predict: 1024
        })
        
        EĞER plan_sonuc.hata:
            DÖNDÜR {
                hata: true,
                hata_mesaji: "PLAN_AI_ERROR: AI plan oluşturamadı. {plan_sonuc.hata_mesaji}",
                hata_tipi: "AI_ERROR"
            }
        
        plan = plan_sonuc.veri
    
    HATA DURUMUNDA Exception as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "PLAN_GENERATION_ERROR: Plan oluşturma sırasında hata: {str(e)}",
            hata_tipi: "UNKNOWN"
        }
    
    // 8. Temizle
    EĞER "# 🎯" plan İÇİNDE:
        plan = plan.substring(plan.indexOf("# 🎯"))
    
    // 9. Kaydet
    DENE:
        dosya_yolu = OBSIDIAN_DIR / "Plan_{bugunun_tarihi()}.md"
        dosya_yaz(dosya_yolu, plan)
        log_info("PLAN_CREATED: Plan kaydedildi: {dosya_yolu}")
    
    HATA DURUMUNDA IOError as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "PLAN_SAVE_ERROR: Plan dosyası kaydedilemedi. Hata: {str(e)}",
            hata_tipi: "IO_ERROR"
        }
    
    DÖNDÜR {
        hata: false,
        veri: plan,
        dosya_yolu: dosya_yolu
    }
```

---

## 6. Rapor Oluşturma Algoritması

```
FONKSIYON gunluk_rapor_olustur(tarih):
    """
    Belirtilen tarih için günlük rapor oluştur.
    
    Parametreler:
    - tarih: Opsiyonel. Varsayılan: bugün
    """
    
    EĞER tarih == null:
        tarih = bugunun_tarihi()
    
    // 1. Logları al
    DENE:
        loglar = tarih_bazli_loglar(tarih)
    HATA DURUMUNDA Exception as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "RAPOR_LOG_ERROR: Loglar alınamadı. Hata: {str(e)}",
            hata_tipi: "DB_ERROR"
        }
    
    // 2. Log kontrolü
    EĞER loglar == null VEYA loglar.uzunluk == 0:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "RAPOR_NO_LOGS: {tarih} tarihi için hiç aktivite kaydı bulunamadı. Capture servisi çalışıyor mu?",
            hata_tipi: "NO_DATA",
            oneriler: [
                "1. Capture servisinin çalıştığından emin olun",
                "2. Farklı bir tarih deneyin",
                "3. history.jsonl dosyasını kontrol edin"
            ]
        }
    
    log_info("RAPOR_BASLATILDI: {tarih} için {loglar.uzunluk} aktivite bulundu.")
    
    // 3. Logları formatla
    log_metni = ""
    HER log İÇİN loglar:
        log_metni += "- [{log.time}] {log.content}\n"
    
    // 4. System prompt
    system_prompt = """
    Sen bir veri analistisin.
    Logları analiz et ve Markdown rapor oluştur.
    Yorum yapma, sadece raporu yaz.
    Dil: Türkçe.
    """
    
    // 5. User prompt
    user_prompt = """
    LOGLAR ({loglar.uzunluk} kayıt):
    {log_metni}
    
    ŞABLON:
    # 📅 Günlük Rapor: {tarih}
    
    ## 🎯 Günün Özeti
    (Ana aktiviteler, 2-3 cümle)
    
    ## 🛠️ Kullanılan Teknolojiler
    (Tespit edilen araçlar, diller - liste halinde)
    
    ## ⏱️ Zaman Çizelgesi
    (Sabah ne yapıldı, öğle ne yapıldı, akşam ne yapıldı)
    
    ## 💡 Verimlilik Notları
    (Odaklanma seviyesi, dikkat dağınıklığı varsa belirt)
    """
    
    // 6. AI'dan rapor al
    DENE:
        rapor_sonuc = ollama_chat(system_prompt, user_prompt, {
            temperature: 0.2,
            num_predict: 2048
        })
        
        EĞER rapor_sonuc.hata:
            DÖNDÜR {
                hata: true,
                hata_mesaji: "RAPOR_AI_ERROR: AI rapor oluşturamadı. {rapor_sonuc.hata_mesaji}",
                hata_tipi: "AI_ERROR"
            }
        
        rapor = rapor_sonuc.veri
    
    HATA DURUMUNDA Exception as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "RAPOR_GENERATION_ERROR: Rapor oluşturma sırasında hata: {str(e)}",
            hata_tipi: "UNKNOWN"
        }
    
    // 7. Ham logları ekle
    rapor += "\n\n---\n\n## 📋 Ham Loglar\n" + log_metni
    
    // 8. Kaydet
    DENE:
        dosya_yolu = OBSIDIAN_DIR / "{tarih}.md"
        dosya_yaz(dosya_yolu, rapor)
        log_info("RAPOR_CREATED: Rapor kaydedildi: {dosya_yolu}")
    
    HATA DURUMUNDA IOError as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "RAPOR_SAVE_ERROR: Rapor dosyası kaydedilemedi. Hata: {str(e)}",
            hata_tipi: "IO_ERROR"
        }
    
    DÖNDÜR {
        hata: false,
        veri: rapor,
        dosya_yolu: dosya_yolu,
        log_sayisi: loglar.uzunluk
    }
```

---

## 7. Semantik Arama Algoritması

```
FONKSIYON semantik_ara(sorgu, sonuc_sayisi):
    
    EĞER sorgu == null VEYA sorgu.trim() == "":
        DÖNDÜR {
            hata: true,
            hata_mesaji: "ARAMA_EMPTY_QUERY: Arama sorgusu boş olamaz.",
            hata_tipi: "INVALID_INPUT"
        }
    
    // 1. Sorgu embedding'i oluştur
    embed_sonuc = ollama_embed(sorgu)
    
    EĞER embed_sonuc.hata:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "ARAMA_EMBED_ERROR: Sorgu embedding'i oluşturulamadı. {embed_sonuc.hata_mesaji}",
            hata_tipi: "EMBED_ERROR"
        }
    
    // 2. ChromaDB'de ara
    DENE:
        sonuclar = collection.query(
            query_embeddings: [embed_sonuc.veri],
            n_results: sonuc_sayisi
        )
    HATA DURUMUNDA Exception as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "ARAMA_DB_ERROR: Veritabanı sorgusu başarısız. Hata: {str(e)}",
            hata_tipi: "DB_ERROR"
        }
    
    // 3. Sonuçları formatla
    EĞER sonuclar.documents[0].uzunluk == 0:
        DÖNDÜR {
            hata: false,
            veri: [],
            mesaj: "Aramanızla eşleşen sonuç bulunamadı."
        }
    
    formatli = []
    
    HER i İÇİN sonuclar.documents[0]:
        meta = sonuclar.metadatas[0][i]
        formatli.ekle({
            date: meta.date,
            time: meta.time,
            content: sonuclar.documents[0][i]
        })
    
    DÖNDÜR {
        hata: false,
        veri: formatli
    }
```

---

## 8. Chat Algoritması

```
FONKSIYON sohbet_yaniti(soru):
    
    EĞER soru == null VEYA soru.trim() == "":
        DÖNDÜR {
            hata: true,
            hata_mesaji: "CHAT_EMPTY_QUESTION: Soru boş olamaz.",
            hata_tipi: "INVALID_INPUT"
        }
    
    // 1. Semantik arama
    arama_sonuc = semantik_ara(soru, 10)
    
    EĞER arama_sonuc.hata:
        DÖNDÜR arama_sonuc
    
    ilgili_kayitlar = arama_sonuc.veri
    
    EĞER ilgili_kayitlar.uzunluk == 0:
        DÖNDÜR {
            hata: false,
            veri: "Hafızada bu soruyla ilgili yeterli veri bulunamadı. Daha fazla aktivite kaydedildikten sonra tekrar deneyin."
        }
    
    // 2. Bağlam oluştur
    baglam = ""
    HER kayit İÇİN ilgili_kayitlar:
        baglam += "- [{kayit.date} {kayit.time}] {kayit.content}\n"
    
    // 3. Prompt
    prompt = """
    Sen kişisel bir asistansın.
    Kullanıcının geçmiş aktivitelerine erişimin var.
    
    GEÇMİŞ KAYITLAR:
    {baglam}
    
    SORU: {soru}
    
    KURALLAR:
    - Sadece kayıtlara dayanarak cevap ver
    - Türkçe ve samimi bir dil kullan
    - Kayıtlarda yoksa "Bu konuda kayıt bulamadım" de
    """
    
    // 4. AI yanıtı
    DENE:
        yanit_sonuc = ollama_chat_stream(prompt)
        
        EĞER yanit_sonuc.hata:
            DÖNDÜR {
                hata: true,
                hata_mesaji: "CHAT_AI_ERROR: AI yanıt veremedi. {yanit_sonuc.hata_mesaji}",
                hata_tipi: "AI_ERROR"
            }
        
        DÖNDÜR {
            hata: false,
            veri: yanit_sonuc.veri
        }
    
    HATA DURUMUNDA Exception as e:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "CHAT_ERROR: Sohbet sırasında hata: {str(e)}",
            hata_tipi: "UNKNOWN"
        }
```

---

## 9. API Kontrol Algoritması

### Başlatma
```
FONKSIYON api_baslat():
    GLOBAL capture_task
    GLOBAL focus_task
    GLOBAL capture_running
    
    EĞER capture_running == true:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "SERVICE_ALREADY_RUNNING: Servis zaten çalışıyor.",
            hata_tipi: "ALREADY_RUNNING"
        }
    
    DENE:
        capture_running = true
        capture_task = arka_plan_gorevi(ana_dongu)
        focus_task = arka_plan_gorevi(odak_takip_dongusu)
        
        log_info("SERVICE_STARTED: Capture ve Focus servisleri başlatıldı.")
        
        DÖNDÜR {
            hata: false,
            veri: {status: "started"}
        }
    
    HATA DURUMUNDA Exception as e:
        capture_running = false
        DÖNDÜR {
            hata: true,
            hata_mesaji: "SERVICE_START_ERROR: Servis başlatılamadı. Hata: {str(e)}",
            hata_tipi: "START_ERROR"
        }
```

### Durdurma
```
FONKSIYON api_durdur():
    GLOBAL capture_running
    GLOBAL capture_task
    GLOBAL focus_task
    
    EĞER capture_running == false:
        DÖNDÜR {
            hata: true,
            hata_mesaji: "SERVICE_NOT_RUNNING: Servis zaten durmuş.",
            hata_tipi: "NOT_RUNNING"
        }
    
    capture_running = false
    
    EĞER capture_task != null:
        capture_task.iptal()
        capture_task = null
    
    EĞER focus_task != null:
        focus_task.iptal()
        focus_task = null
    
    log_info("SERVICE_STOPPED: Servisler durduruldu.")
    
    DÖNDÜR {
        hata: false,
        veri: {status: "stopped"}
    }
```

### Durum Sorgulama
```
FONKSIYON api_durum():
    DÖNDÜR {
        hata: false,
        veri: {
            running: capture_running,
            uptime: capture_task?.calisma_suresi veya 0,
            today_count: bugun_kayit_sayisi(),
            last_activity: son_aktivite_zamani(),
            focus_data: bugunun_odak_verisi()
        }
    }
```

---

## 📋 Sabitler

```
// Zaman (saniye)
CAPTURE_INTERVAL = 20
FOCUS_CHECK_INTERVAL = 1
GUNLUK_LIMIT = 7200  // 2 saat

// Dosya yolları
HISTORY_FILE = "history.jsonl"
DB_PATH = "hafiza_db/"
PROFILE_PATH = "profile.yaml"

// Modeller
MODEL_VISION = "gemma3"
MODEL_EMBED = "mxbai-embed-large"
MODEL_CHAT = "gemma3"

// Yasaklı kelimeler
YASAKLI_KELIMELER = [
    "youtube", "instagram", "twitter", 
    "reddit", "netflix", "tiktok", 
    "oyun", "video", "game"
]

// Uyarı eşikleri (saniye, etiket, sesli mi)
UYARI_ESIKLERI = [
    {saniye: 900,  etiket: "15 dakika",  sesli: false},
    {saniye: 1800, etiket: "30 dakika",  sesli: false},
    {saniye: 3600, etiket: "1 saat",     sesli: true},
    {saniye: 5400, etiket: "1.5 saat",   sesli: false},
    {saniye: 7200, etiket: "2 saat",     sesli: true}
]

// Desteklenen eğitim platformları
EGITIM_PLATFORMLARI = [
    "udemy", "coursera", "scrimba", 
    "pluralsight", "linkedin learning",
    "edx", "skillshare"
]
```

---

## 🔧 Hata Kodları Özeti

| Kod | Açıklama |
|-----|----------|
| GRIM_NOT_INSTALLED | grim kurulu değil |
| GRIM_ERROR | grim çalışma hatası |
| GRIM_TIMEOUT | grim yanıt vermedi |
| HYPRCTL_NOT_FOUND | hyprctl kurulu değil |
| HYPRCTL_ERROR | hyprctl çalışma hatası |
| OLLAMA_NOT_RUNNING | Ollama servisi kapalı |
| OLLAMA_MODEL_NOT_FOUND | Model yüklü değil |
| OLLAMA_TIMEOUT | Model yanıt vermedi |
| OLLAMA_CONNECTION_ERROR | Bağlantı hatası |
| EMBED_ERROR | Embedding oluşturulamadı |
| CHROMADB_ERROR | Veritabanı hatası |
| PROFILE_MISSING | profile.yaml yok |
| NO_LOGS | Log bulunamadı |
| IO_ERROR | Dosya okuma/yazma hatası |

---

*Son güncelleme: 2025-12-09*
