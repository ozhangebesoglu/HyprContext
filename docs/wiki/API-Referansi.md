# 🔌 API Referansı

HyprContext Backend API dokümantasyonu.

---

## 📍 Base URL

```
http://localhost:8000/api
```

---

## 🏥 Health Check

### `GET /health`

Sistem durumunu kontrol et.

**Yanıt:**
```json
{
  "status": "healthy",
  "ai_available": true,
  "database_records": 542
}
```

---

## 📊 Aktiviteler

### `GET /activities/`

Aktivite listesini al.

**Parametreler:**
| Parametre | Tür | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `limit` | int | 50 | Maksimum kayıt |
| `offset` | int | 0 | Atlama sayısı |
| `date` | str | - | Tarih filtresi (YYYY-MM-DD) |

**Örnek:**
```bash
curl "http://localhost:8000/api/activities/?limit=10&date=2025-12-17"
```

**Yanıt:**
```json
[
  {
    "id": "20251217_122856_794713",
    "timestamp": "2025-12-17T12:28:56.794696",
    "summary": "Python ile main.py dosyasını düzenliyor",
    "tags": ["Python", "VSCode", "Backend"],
    "active_window": "code",
    "screenshot_path": "/path/to/screenshot.png"
  }
]
```

### `GET /activities/{id}`

Tek aktivite detayı.

### `GET /activities/search?q={query}`

Semantik arama yap.

---

## 📅 Planlar

### `GET /plans/`

Tüm planları listele.

### `GET /plans/{date}`

Belirli tarihin planını al.

**Örnek:**
```bash
curl "http://localhost:8000/api/plans/2025-12-17"
```

### `POST /plans/`

Yeni plan oluştur.

**Body:**
```json
{
  "date": "2025-12-18",
  "goals": ["Wiki hazırla", "Test yaz"],
  "notes": "Önemli gün"
}
```

### `PUT /plans/{date}`

Planı güncelle.

---

## 📄 Raporlar

### `GET /reports/`

Tüm raporları listele.

### `GET /reports/{date}`

Belirli tarihin raporunu al.

### `POST /reports/generate`

Günlük rapor oluştur.

**Body:**
```json
{
  "date": "2025-12-17"
}
```

---

## 💬 Chat

### `POST /chat/`

AI ile sohbet et.

**Body:**
```json
{
  "message": "Bugün en çok ne üzerinde çalıştım?"
}
```

**Yanıt:**
```json
{
  "response": "Bugün ağırlıklı olarak HyprContext projesinde çalıştınız...",
  "context_used": 15
}
```

---

## ⏱️ Focus

### `GET /focus/status`

Odak durumunu al.

**Yanıt:**
```json
{
  "used_seconds": 1800,
  "remaining_seconds": 5400,
  "percentage": 25.0,
  "limit_reached": false
}
```

### `POST /focus/reset`

Günlük sayacı sıfırla.

---

## ⚙️ Control

### `GET /control/status`

Servis durumunu al.

**Yanıt:**
```json
{
  "running": true,
  "capture_active": true,
  "focus_active": true,
  "uptime_seconds": 3600,
  "last_activity": "2025-12-17T12:28:56",
  "today_count": 42
}
```

### `POST /control/start`

Servisleri başlat.

### `POST /control/stop`

Servisleri durdur.

---

## 👤 Profile

### `GET /profile/`

Kullanıcı profilini al.

### `PUT /profile/`

Profili güncelle.

**Body:**
```json
{
  "user": {
    "name": "Özhan",
    "profession": "Developer"
  },
  "daily_limits": {
    "distraction_minutes": 120
  },
  "banned_keywords": ["youtube", "twitter"]
}
```

---

## 🔧 Config

### `GET /config/info`

Tüm yapılandırmayı al.

**Yanıt:**
```json
{
  "app_name": "HyprContext",
  "data_path": "/home/user/Documents/HyprContext",
  "screenshots_dir": "/home/user/Documents/HyprContext/screenshots",
  "plans_dir": "/home/user/Documents/HyprContext/planlar",
  "reports_dir": "/home/user/Documents/HyprContext/raporlar",
  "ollama_model": "gemma3",
  "screenshot_interval": 30
}
```

### `GET /config/data-path`

Veri yollarını al.

### `POST /config/data-path`

Veri yolunu güncelle.

**Body:**
```json
{
  "data_path": "/new/path/HyprContext"
}
```

---

## 🔌 WebSocket

### `WS /ws`

Gerçek zamanlı güncellemeler.

**Bağlantı:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data.type, data.payload);
};
```

**Event Tipleri:**

| Tip | Açıklama |
|-----|----------|
| `activity` | Yeni aktivite kaydı |
| `focus_update` | Odak durumu değişimi |
| `distraction_warning` | Dikkat dağınıklığı uyarısı |
| `system_stats` | Sistem istatistikleri |

---

## 🔐 Hata Kodları

| Kod | Anlamı |
|-----|--------|
| 200 | Başarılı |
| 201 | Oluşturuldu |
| 400 | Geçersiz istek |
| 404 | Bulunamadı |
| 500 | Sunucu hatası |

---

## 📝 Örnek Kullanımlar

### Bash ile aktivite listesi
```bash
curl -s "http://localhost:8000/api/activities/?limit=5" | jq
```

### Python ile chat
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat/",
    json={"message": "Bu hafta ne kadar çalıştım?"}
)
print(response.json()["response"])
```

### JavaScript ile WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (e) => {
  const { type, payload } = JSON.parse(e.data);
  if (type === 'activity') {
    console.log('Yeni aktivite:', payload.summary);
  }
};
```

---

[[← Ana Sayfa|Home]]
