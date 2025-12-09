# 🖥️ HyprContext Frontend Planı

## 🎨 Renk Paleti

### Light Mode: Cashmere in Buff

| İsim | RGB | HEX | Kullanım |
|------|-----|-----|----------|
| Buff | rgb(85% 71% 59%) | `#D9B596` | Ana arka plan |
| Cocoa | rgb(51.2% 28.2% 18.9%) | `#824830` | Metin, başlıklar |
| Sienna | rgb(64.4% 39.4% 23.2%) | `#A4643B` | Accent, butonlar |
| Taupe | rgb(68.4% 61.7% 54.3%) | `#AE9D8A` | İkincil metin, border |
| Sand | rgb(84.8% 81% 74.8%) | `#D8CEBF` | Kart arka planı |
| Cream | rgb(100% 98.7% 91.8%) | `#FFFCEA` | Vurgu, hover |

### Dark Mode: Cashmere Night

| İsim | HEX | Kullanım |
|------|-----|----------|
| Charcoal | `#1a1612` | Ana arka plan |
| Espresso | `#2d2420` | Kart arka planı |
| Mocha | `#3d322a` | Hover, border |
| Latte | `#A4643B` | Accent (aynı) |
| Cream Text | `#E8DDD0` | Ana metin |
| Muted | `#8B7B6B` | İkincil metin |

### Tema Değişkeni (CSS)
```css
:root {
  /* Light Mode */
  --bg-primary: #D9B596;
  --bg-card: #D8CEBF;
  --bg-hover: #FFFCEA;
  --accent: #A4643B;
  --text-primary: #824830;
  --text-secondary: #AE9D8A;
  --border: #AE9D8A;
}

[data-theme="dark"] {
  /* Dark Mode */
  --bg-primary: #1a1612;
  --bg-card: #2d2420;
  --bg-hover: #3d322a;
  --accent: #A4643B;
  --text-primary: #E8DDD0;
  --text-secondary: #8B7B6B;
  --border: #3d322a;
}
```

---

## 📐 Genel Düzen

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                                                                 │
│                         SAYFA İÇERİĞİ                          │
│                                                                 │
│                   (Her sayfa kendi düzenine sahip)              │
│                                                                 │
│                                                                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                           DOCK                                  │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐   │
│  │  🏠  │  │  📝  │  │  📊  │  │  📅  │  │  📄  │  │  ⚙️  │   │
│  │ Ana  │  │Anlık │  │Grafik│  │ Plan │  │Rapor │  │ Ayar │   │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📄 Sayfa Tasarımları

### 1. 🏠 Ana Sayfa

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                        HyprContext                              │
│                     ─────────────────                           │
│                                                                 │
│                  ┌─────────────────────┐                        │
│                  │                     │                        │
│                  │    ▶️  BAŞLAT       │   ← Büyük yuvarlak     │
│                  │                     │     buton              │
│                  └─────────────────────┘                        │
│                                                                 │
│                  ☐ Sistem ile otomatik başlat                   │
│                                                                 │
│           ┌─────────────────────────────────────┐               │
│           │         📊 Bugünün Özeti            │               │
│           ├─────────────────────────────────────┤               │
│           │                                     │               │
│           │  Kayıt      Süre       Odak        │               │
│           │  ━━━━━      ━━━━━      ━━━━━       │               │
│           │   142       4s 32dk     %78        │               │
│           │                                     │               │
│           │  Son aktivite: 2 dk önce           │               │
│           │  "VS Code'da Python yazıyor"       │               │
│           │                                     │               │
│           └─────────────────────────────────────┘               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [🏠]    [📝]    [📊]    [📅]    [📄]    [⚙️]                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2. 📝 Anlık Yorumlar

```
┌─────────────────────────────────────────────────────────────────┐
│  📝 Anlık Yorumlar                              🔴 Canlı        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 🔍 Ara...                              [Tümü ▼]         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 15:32:15                                                │   │
│  │ VS Code'da Python projesi geliştiriyor.                 │   │
│  │ ┌────────┐ ┌────────┐ ┌──────────┐                      │   │
│  │ │ Python │ │VS Code │ │Geliştirme│                      │   │
│  │ └────────┘ └────────┘ └──────────┘                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 15:31:45                                                │   │
│  │ Chrome'da Stack Overflow araştırması yapıyor.           │   │
│  │ ┌────────┐ ┌──────────┐                                 │   │
│  │ │ Chrome │ │Araştırma │                                 │   │
│  │ └────────┘ └──────────┘                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 15:31:20                                         ⚠️     │   │
│  │ YouTube'da video izliyor.                               │   │
│  │ ┌─────────┐ ┌───────┐                                   │   │
│  │ │ YouTube │ │ Video │                                   │   │
│  │ └─────────┘ └───────┘                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                        ↓ Daha fazla yükle                       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [🏠]    [📝]    [📊]    [📅]    [📄]    [⚙️]                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3. 📊 Grafikler

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 Grafikler                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  📈 Saatlik Aktivite Dağılımı                 [Bugün ▼]   │ │
│  │                                                           │ │
│  │      ▄▄                                                   │ │
│  │   ▄▄████▄▄      ▄▄▄▄                                     │ │
│  │  ████████████▄▄██████▄▄    ▄▄                            │ │
│  │  ──────────────────────────────────────────              │ │
│  │  09  10  11  12  13  14  15  16  17  18  19              │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────┐  ┌────────────────────────┐        │
│  │  🥧 Uygulama Dağılımı  │  │  📉 Haftalık Trend     │        │
│  │                        │  │                        │        │
│  │      ┌────┐            │  │    ╱╲    ╱╲           │        │
│  │   ┌──┤    ├──┐         │  │   ╱  ╲  ╱  ╲  ╱      │        │
│  │   │VS│Code│  │         │  │  ╱    ╲╱    ╲╱       │        │
│  │   │  ├────┤  │         │  │ ────────────────      │        │
│  │   │  │Chrm│  │         │  │ Pzt Sal Çar Per Cum   │        │
│  │   └──┴────┴──┘         │  │                        │        │
│  │                        │  │                        │        │
│  └────────────────────────┘  └────────────────────────┘        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  🏷️ En Çok Kullanılan Etiketler                           │ │
│  │                                                           │ │
│  │  Geliştirme  ████████████████████  45                    │ │
│  │  Python      ██████████████        32                    │ │
│  │  Araştırma   ████████████          28                    │ │
│  │  VS Code     ██████████            24                    │ │
│  │  Video       ██████                15                    │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [🏠]    [📝]    [📊]    [📅]    [📄]    [⚙️]                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### 4. 📅 Planlar (Sol Sidebar ile)

```
┌─────────────────────────────────────────────────────────────────┐
│  📅 Planlar                                                     │
├───────────────┬─────────────────────────────────────────────────┤
│               │                                                 │
│  📆 Aralık    │  # 🎯 Günün Misyonu: JavaScript Öğren          │
│  ───────────  │  > **Hava:** ☀️ +12°C                          │
│               │  > **Odak:** JavaScript Fundamentals            │
│  ● 09 Pzt ◀   │                                                 │
│  ○ 08 Paz     │  ## 🌅 Sabah (09:00 - 12:00)                   │
│  ○ 07 Cmt     │  ☐ 09:00 - Array methods çalış                 │
│  ○ 06 Cum     │  ☑ 10:30 - Scrimba challenge yap ✅            │
│  ○ 05 Per     │                                                 │
│               │  ## ☀️ Öğle (13:00 - 17:00)                    │
│  ◀ Kasım     │  ☐ 13:00 - DOM manipulation                    │
│               │  ☐ 15:00 - Mini proje yap                      │
│  ───────────  │                                                 │
│               │  ## 🌙 Akşam (18:00 - 22:00)                   │
│  📝 Yeni Plan │  ☐ 19:00 - Async/Await öğren                   │
│  ───────────  │                                                 │
│               │  ## ⚠️ Asistan Notu                            │
│  Not:         │  Bugün odaklan, telefonu kapat!                 │
│  ┌─────────┐  │                                                 │
│  │         │  │  ─────────────────────────────────────────     │
│  │         │  │                                                 │
│  └─────────┘  │  [✏️ Düzenle]  [📓 Obsidian'a Aktar]           │
│               │                                                 │
│  [🚀 Oluştur] │                                                 │
│               │                                                 │
├───────────────┴─────────────────────────────────────────────────┤
│  [🏠]    [📝]    [📊]    [📅]    [📄]    [⚙️]                  │
└─────────────────────────────────────────────────────────────────┘
```

**Düzenleme Modu (Markdown Editör):**
```
┌─────────────────────────────────────────────────────────────────┐
│  📅 Planlar                                        [💾 Kaydet]  │
├───────────────┬─────────────────────────────────────────────────┤
│               │                                                 │
│  📆 Aralık    │  ┌────────────────────────────────────────────┐│
│  ───────────  │  │ [B] [I] [H1] [H2] [📋] [🔗] [📷]  │ 👁️ │  ││
│               │  ├────────────────────────────────────────────┤│
│  ● 09 Pzt ◀   │  │                                            ││
│  ○ 08 Paz     │  │ # 🎯 Günün Misyonu: JavaScript Öğren      ││
│  ...          │  │ > **Hava:** ☀️ +12°C                      ││
│               │  │ > **Odak:** JavaScript Fundamentals        ││
│               │  │                                            ││
│               │  │ ## 🌅 Sabah (09:00 - 12:00)               ││
│               │  │ - [ ] 09:00 - Array methods çalış          ││
│               │  │ - [x] 10:30 - Scrimba challenge yap        ││
│               │  │                                            ││
│               │  │ ## ☀️ Öğle (13:00 - 17:00)                ││
│               │  │ - [ ] 13:00 - DOM manipulation             ││
│               │  │ ...                                        ││
│               │  │                                            ││
│               │  └────────────────────────────────────────────┘│
│               │                                                 │
│               │  [❌ İptal]  [💾 Kaydet]                        │
│               │                                                 │
├───────────────┴─────────────────────────────────────────────────┤
│  [🏠]    [📝]    [📊]    [📅]    [📄]    [⚙️]                  │
└─────────────────────────────────────────────────────────────────┘
```

### Markdown Editör Özellikleri

| Özellik | Açıklama |
|---------|----------|
| Toolbar | Bold, Italic, Heading, List, Link, Image |
| Preview | 👁️ butonu ile canlı önizleme |
| Syntax Highlight | Markdown renklendirme |
| Checkbox | `- [ ]` ve `- [x]` desteği |
| Auto-save | Her 30 saniyede otomatik kayıt (draft) |
| Keyboard Shortcuts | Ctrl+B (bold), Ctrl+I (italic), vb. |

### Önerilen Kütüphane

```tsx
// @uiw/react-md-editor veya react-markdown-editor-lite

import MDEditor from '@uiw/react-md-editor';

const PlanEditor = ({ content, onChange }) => {
  return (
    <MDEditor
      value={content}
      onChange={onChange}
      preview="edit"  // "edit" | "preview" | "live"
      height={500}
      data-color-mode={theme === 'dark' ? 'dark' : 'light'}
    />
  );
};
```

---

### 5. 📄 Raporlar (Sol Sidebar ile)

```
┌─────────────────────────────────────────────────────────────────┐
│  📄 Raporlar                                                    │
├───────────────┬─────────────────────────────────────────────────┤
│               │                                                 │
│  📆 Aralık    │  # 📅 Günlük Rapor: 2025-12-09                 │
│  ───────────  │                                                 │
│               │  ## 🎯 Günün Özeti                              │
│  ● 09 Pzt ◀   │  React ve TypeScript üzerine yoğun çalışma     │
│  ○ 08 Paz     │  yapıldı. Scrimba kursunda ilerleme kaydedildi.│
│  ○ 07 Cmt     │                                                 │
│  ○ 06 Cum     │  ## 🛠️ Kullanılan Teknolojiler                 │
│  ○ 05 Per     │  - VS Code                                      │
│               │  - Chrome (Stack Overflow)                      │
│  ◀ Kasım     │  - Terminal                                     │
│               │                                                 │
│  ───────────  │  ## ⏱️ Zaman Çizelgesi                         │
│               │  - **Sabah:** Scrimba dersleri                  │
│  📊 Raporla   │  - **Öğle:** Proje geliştirme                  │
│  ───────────  │  - **Akşam:** Dokümantasyon                    │
│               │                                                 │
│  Bugünü       │  ## 💡 Verimlilik Notları                      │
│  raporla      │  Odaklanma seviyesi yüksek. 42 dk dikkat       │
│               │  dağınıklığı tespit edildi.                     │
│  ┌─────────┐  │                                                 │
│  │   📊    │  │  ─────────────────────────────────────────     │
│  │ Raporla │  │                                                 │
│  └─────────┘  │  [📓 Obsidian'a Aktar]  [📥 PDF İndir]         │
│               │                                                 │
│  ───────────  │                                                 │
│  Obsidian'a   │                                                 │
│  ┌─────────┐  │                                                 │
│  │   📓    │  │                                                 │
│  │  Aktar  │  │                                                 │
│  └─────────┘  │                                                 │
│               │                                                 │
├───────────────┴─────────────────────────────────────────────────┤
│  [🏠]    [📝]    [📊]    [📅]    [📄]    [⚙️]                  │
└─────────────────────────────────────────────────────────────────┘
```

**Raporla Butonu Akışı:**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. Kullanıcı "📊 Raporla" butonuna tıklar                     │
│                         │                                       │
│                         ▼                                       │
│  2. Onay Modalı açılır:                                        │
│     ┌─────────────────────────────────────────┐                │
│     │         📊 Rapor Oluştur                │                │
│     ├─────────────────────────────────────────┤                │
│     │                                         │                │
│     │  Tarih: 2025-12-09                      │                │
│     │  Saat:  15:45                           │                │
│     │                                         │                │
│     │  Bugün için 142 aktivite kaydı          │                │
│     │  bulundu. Rapor oluşturulsun mu?        │                │
│     │                                         │                │
│     │     [❌ İptal]    [✅ Oluştur]          │                │
│     │                                         │                │
│     └─────────────────────────────────────────┘                │
│                         │                                       │
│                         ▼                                       │
│  3. "Oluştur" tıklanırsa:                                      │
│     - Loading göster                                            │
│     - Backend'e POST /reports/generate                         │
│     - AI rapor üretir (streaming)                              │
│                         │                                       │
│                         ▼                                       │
│  4. Rapor oluşturuldu:                                         │
│     - Uygulama içinde kaydedilir                               │
│     - Sol sidebar'da yeni rapor görünür                        │
│     - Toast: "✅ Rapor başarıyla oluşturuldu"                  │
│                         │                                       │
│                         ▼                                       │
│  5. Kullanıcı isterse:                                         │
│     - "📓 Obsidian'a Aktar" → MD dosyası oluşturur            │
│     - "📥 PDF İndir" → PDF export                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Onay Modalı Komponenti

```tsx
// ConfirmReportModal.tsx
interface Props {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  date: string;
  activityCount: number;
  isLoading: boolean;
}

const ConfirmReportModal = ({ isOpen, onClose, onConfirm, date, activityCount, isLoading }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="modal-header">
        <h2>📊 Rapor Oluştur</h2>
      </div>
      
      <div className="modal-body">
        <p><strong>Tarih:</strong> {date}</p>
        <p><strong>Saat:</strong> {new Date().toLocaleTimeString('tr-TR')}</p>
        <p className="mt-4">
          Bugün için <strong>{activityCount}</strong> aktivite kaydı bulundu.
          <br />
          Rapor oluşturulsun mu?
        </p>
      </div>
      
      <div className="modal-footer">
        <Button variant="secondary" onClick={onClose} disabled={isLoading}>
          ❌ İptal
        </Button>
        <Button variant="primary" onClick={onConfirm} loading={isLoading}>
          ✅ Oluştur
        </Button>
      </div>
    </Modal>
  );
};
```

---

### 6. ⚙️ Ayarlar

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️ Ayarlar                                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  🤖 AI Ayarları                                           │ │
│  │                                                           │ │
│  │  Model                    ┌─────────────────────────┐     │ │
│  │                           │ gemma3              ▼   │     │ │
│  │                           └─────────────────────────┘     │ │
│  │                                                           │ │
│  │  Embedding Model          ┌─────────────────────────┐     │ │
│  │                           │ mxbai-embed-large   ▼   │     │ │
│  │                           └─────────────────────────┘     │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  ⏱️ Yakalama Ayarları                                     │ │
│  │                                                           │ │
│  │  Yakalama Aralığı         20 saniye                       │ │
│  │  ○────────────●──────────○                                │ │
│  │  10s                    60s                               │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  🚫 Odak Ayarları                                         │ │
│  │                                                           │ │
│  │  Günlük Limit             2 saat                          │ │
│  │  ○────────────●──────────○                                │ │
│  │  1s                     4s                                │ │
│  │                                                           │ │
│  │  Yasaklı Kelimeler                                        │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ youtube, instagram, twitter, reddit, netflix,       │ │ │
│  │  │ tiktok, oyun, video                                 │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  [+ Ekle]                                                 │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  📁 Dizin Ayarları                                        │ │
│  │                                                           │ │
│  │  Obsidian Vault           ~/SecondBrain          [📂]     │ │
│  │  Günlük Dizini            ~/SecondBrain/Gunlukler[📂]     │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│                                      [💾 Kaydet]               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [🏠]    [📝]    [📊]    [📅]    [📄]    [⚙️]                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧭 Dock Tasarımı: Liquid Glass

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│      ╭────────────────────────────────────────────────╮        │
│      │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │        │
│      │ ░░ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ░░ │
│      │ ░░ │      │ │      │ │      │ │      │ │      │ │      │ ░░ │
│      │ ░░ │  🏠  │ │  📝  │ │  📊  │ │  📅  │ │  📄  │ │  ⚙️  │ ░░ │
│      │ ░░ │      │ │      │ │      │ │      │ │      │ │      │ ░░ │
│      │ ░░ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ ░░ │
│      │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │        │
│      ╰────────────────────────────────────────────────╯        │
│                         Liquid Glass Effect                     │
└─────────────────────────────────────────────────────────────────┘
```

### Liquid Glass CSS Yapısı

```tsx
// Dock.tsx
<div className="dock-wrapper">
  {/* SVG Filter - Gizli */}
  <svg style={{ display: 'none' }}>
    <filter id="glass-distortion" ...>
      <feTurbulence ... />
      <feDisplacementMap ... />
    </filter>
  </svg>

  {/* Liquid Glass Katmanları */}
  <div className="liquidGlass-wrapper dock">
    <div className="liquidGlass-effect" />   {/* Blur + Distortion */}
    <div className="liquidGlass-tint" />     {/* Renk tonu */}
    <div className="liquidGlass-shine" />    {/* Işık yansıması */}
    <div className="liquidGlass-content">    {/* İçerik */}
      <DockIcon icon="🏠" label="Ana" active />
      <DockIcon icon="📝" label="Anlık" />
      <DockIcon icon="📊" label="Grafik" />
      <DockIcon icon="📅" label="Plan" />
      <DockIcon icon="📄" label="Rapor" />
      <DockIcon icon="⚙️" label="Ayar" />
    </div>
  </div>
</div>
```

### Liquid Glass CSS

```css
/* Liquid Glass Wrapper */
.liquidGlass-wrapper {
  position: relative;
  display: flex;
  overflow: hidden;
  border-radius: 2rem;
  box-shadow: 
    0 6px 6px rgba(0, 0, 0, 0.2), 
    0 0 20px rgba(0, 0, 0, 0.1);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2);
}

/* Distortion + Blur Katmanı */
.liquidGlass-effect {
  position: absolute;
  z-index: 0;
  inset: 0;
  backdrop-filter: blur(3px);
  filter: url(#glass-distortion);
  overflow: hidden;
}

/* Renk Tonu - Light Mode */
.liquidGlass-tint {
  z-index: 1;
  position: absolute;
  inset: 0;
  background: rgba(217, 181, 150, 0.5); /* Buff tonu */
}

/* Renk Tonu - Dark Mode */
[data-theme="dark"] .liquidGlass-tint {
  background: rgba(26, 22, 18, 0.6); /* Charcoal tonu */
}

/* Işık Yansıması */
.liquidGlass-shine {
  position: absolute;
  inset: 0;
  z-index: 2;
  overflow: hidden;
  box-shadow: 
    inset 2px 2px 1px 0 rgba(255, 255, 255, 0.5),
    inset -1px -1px 1px 1px rgba(255, 255, 255, 0.5);
}

[data-theme="dark"] .liquidGlass-shine {
  box-shadow: 
    inset 2px 2px 1px 0 rgba(255, 255, 255, 0.15),
    inset -1px -1px 1px 1px rgba(255, 255, 255, 0.1);
}

/* İçerik */
.liquidGlass-content {
  z-index: 3;
  display: flex;
  gap: 8px;
  padding: 0.6rem;
}

/* Dock Hover */
.dock:hover {
  padding: 0.8rem;
  border-radius: 2.5rem;
}

/* Dock Icon */
.dock-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2);
  border-radius: 12px;
}

.dock-icon:hover {
  transform: scale(1.15) translateY(-5px);
  background: var(--bg-hover);
}

.dock-icon.active {
  background: var(--accent);
  color: white;
}

/* Aktif İndikatör (nokta) */
.dock-icon.active::after {
  content: '';
  position: absolute;
  bottom: -8px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
}
```

### SVG Filter (Distortion Efekti)

```html
<svg style="display: none">
  <filter id="glass-distortion" 
          x="0%" y="0%" width="100%" height="100%" 
          filterUnits="objectBoundingBox">
    
    <!-- Gürültü oluştur -->
    <feTurbulence 
      type="fractalNoise" 
      baseFrequency="0.01 0.01" 
      numOctaves="1" 
      seed="5" 
      result="turbulence" 
    />
    
    <!-- Renk eşleme -->
    <feComponentTransfer in="turbulence" result="mapped">
      <feFuncR type="gamma" amplitude="1" exponent="10" offset="0.5" />
      <feFuncG type="gamma" amplitude="0" exponent="1" offset="0" />
      <feFuncB type="gamma" amplitude="0" exponent="1" offset="0.5" />
    </feComponentTransfer>
    
    <!-- Yumuşatma -->
    <feGaussianBlur in="turbulence" stdDeviation="3" result="softMap" />
    
    <!-- Işık efekti -->
    <feSpecularLighting 
      in="softMap" 
      surfaceScale="5" 
      specularConstant="1" 
      specularExponent="100" 
      lighting-color="white" 
      result="specLight">
      <fePointLight x="-200" y="-200" z="300" />
    </feSpecularLighting>
    
    <!-- Birleştir -->
    <feComposite 
      in="specLight" 
      operator="arithmetic" 
      k1="0" k2="1" k3="1" k4="0" 
      result="litImage" 
    />
    
    <!-- Bükme efekti -->
    <feDisplacementMap 
      in="SourceGraphic" 
      in2="softMap" 
      scale="150" 
      xChannelSelector="R" 
      yChannelSelector="G" 
    />
  </filter>
</svg>
```

---

## 📦 Component Yapısı

```
src/
├── components/
│   │
│   ├── layout/
│   │   ├── Dock.tsx              # Alt navigasyon
│   │   ├── PageContainer.tsx     # Sayfa wrapper
│   │   └── Sidebar.tsx           # Planlar/Raporlar için
│   │
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Slider.tsx
│   │   ├── Dropdown.tsx
│   │   ├── Checkbox.tsx
│   │   ├── Modal.tsx
│   │   ├── Tag.tsx               # Etiket badge
│   │   └── Calendar.tsx          # Tarih seçici
│   │
│   ├── features/
│   │   ├── ActivityCard.tsx      # Aktivite kartı
│   │   ├── PlanViewer.tsx        # Plan görüntüleyici
│   │   ├── PlanEditor.tsx        # Plan düzenleyici (Markdown)
│   │   ├── ReportViewer.tsx      # Rapor görüntüleyici
│   │   ├── StatusIndicator.tsx   # Çalışıyor/Durdu
│   │   ├── StatCard.tsx          # İstatistik kartı
│   │   └── charts/
│   │       ├── ActivityChart.tsx
│   │       ├── PieChart.tsx
│   │       └── TrendChart.tsx
│   │
│   └── pages/
│       ├── Home.tsx
│       ├── Live.tsx
│       ├── Charts.tsx
│       ├── Plans.tsx
│       ├── Reports.tsx
│       └── Settings.tsx
```

---

## 🔄 Veri Akışı (Frontend)

```
┌─────────────────────────────────────────────────────────────────┐
│                         ZUSTAND STORE                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │  isRunning: boolean                                     │   │
│  │  activities: Activity[]                                 │   │
│  │  currentPlan: Plan | null                               │   │
│  │  currentReport: Report | null                           │   │
│  │  settings: Settings                                     │   │
│  │  focusData: FocusData                                   │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   React Query   │  │   WebSocket     │  │   Local         │
│   (REST API)    │  │   (Canlı veri)  │  │   Storage       │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    │   localhost:8000    │
                    └─────────────────────┘
```

---

## 📱 Responsive Davranış

```
Minimum pencere boyutu: 800x600

< 1024px:  Dock iconları küçülür
< 900px:   Sidebar collapse olur (sadece icon)
< 800px:   Desteklenmiyor (uyarı göster)
```

---

## 🎬 Animasyonlar

| Element | Animasyon | Süre |
|---------|-----------|------|
| Sayfa geçişi | Fade | 200ms |
| Dock hover | Scale (1.15x) + translateY(-5px) | 150ms |
| Kart hover | Shadow + lift | 200ms |
| Modal | Fade + scale | 250ms |
| Aktivite ekleme | Slide down | 300ms |
| Liquid Glass | cubic-bezier(0.175, 0.885, 0.32, 2.2) | 400ms |

---

## 🔔 System Tray

Uygulama kapatıldığında (X butonuna basıldığında) tamamen kapanmaz, system tray'e minimize olur.

### Tray Davranışı

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. Kullanıcı X butonuna tıklar                                │
│                         │                                       │
│                         ▼                                       │
│  2. Pencere gizlenir (hide), uygulama arka planda çalışır      │
│                         │                                       │
│                         ▼                                       │
│  3. System tray'de icon görünür:                               │
│                                                                 │
│     ┌──────────────────────────────────┐                       │
│     │  🟢 HyprContext (Çalışıyor)      │ ← Tray icon           │
│     └──────────────────────────────────┘                       │
│                                                                 │
│  4. Tray icon'a sağ tıklama:                                   │
│     ┌─────────────────────┐                                    │
│     │ 📊 Aç               │                                    │
│     │ ─────────────────── │                                    │
│     │ ▶️ Başlat           │                                    │
│     │ ⏸️ Durdur           │                                    │
│     │ ─────────────────── │                                    │
│     │ 📅 Bugünün Planı    │                                    │
│     │ 📄 Rapor Oluştur    │                                    │
│     │ ─────────────────── │                                    │
│     │ ❌ Çıkış            │                                    │
│     └─────────────────────┘                                    │
│                                                                 │
│  5. Tray icon'a çift tıklama → Pencereyi göster                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Electron Tray Kodu

```typescript
// electron/tray.ts
import { Tray, Menu, nativeImage, app } from 'electron';
import path from 'path';

let tray: Tray | null = null;

export function createTray(mainWindow: BrowserWindow) {
  const iconPath = path.join(__dirname, 'assets/tray-icon.png');
  const icon = nativeImage.createFromPath(iconPath);
  
  tray = new Tray(icon);
  tray.setToolTip('HyprContext');
  
  const contextMenu = Menu.buildFromTemplate([
    { 
      label: '📊 Aç', 
      click: () => mainWindow.show() 
    },
    { type: 'separator' },
    { 
      label: '▶️ Başlat', 
      click: () => startCapture() 
    },
    { 
      label: '⏸️ Durdur', 
      click: () => stopCapture() 
    },
    { type: 'separator' },
    { 
      label: '📅 Bugünün Planı', 
      click: () => openPlan() 
    },
    { 
      label: '📄 Rapor Oluştur', 
      click: () => generateReport() 
    },
    { type: 'separator' },
    { 
      label: '❌ Çıkış', 
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);
  
  tray.setContextMenu(contextMenu);
  
  // Çift tıklama
  tray.on('double-click', () => {
    mainWindow.show();
  });
  
  return tray;
}

// Durum ikonunu güncelle
export function updateTrayIcon(isRunning: boolean) {
  if (tray) {
    const iconName = isRunning ? 'tray-icon-active.png' : 'tray-icon.png';
    const iconPath = path.join(__dirname, `assets/${iconName}`);
    tray.setImage(nativeImage.createFromPath(iconPath));
    tray.setToolTip(`HyprContext (${isRunning ? 'Çalışıyor' : 'Durdu'})`);
  }
}
```

### Pencere Kapatma Davranışı

```typescript
// electron/main.ts
mainWindow.on('close', (event) => {
  if (!app.isQuitting) {
    event.preventDefault();
    mainWindow.hide();  // Tray'e minimize et
  }
});

// macOS için dock'tan kaldırma
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    // Windows/Linux'ta tray'de kal
  }
});
```

### Tray Icon Tasarımı

```
Normal (Durdu):     Aktif (Çalışıyor):
┌────────┐          ┌────────┐
│   ◯    │          │   ●    │
│  ╱ ╲   │          │  ╱ ╲   │
│ ╱   ╲  │          │ ╱   ╲  │
│╱     ╲ │          │╱     ╲ │
└────────┘          └────────┘
 Gri tonu            Yeşil/Accent rengi
```

---

## 📋 Geliştirme Sırası

### Faz 1: Temel Yapı (3-4 gün)
- [ ] Electron + Vite + React kurulumu
- [ ] Tailwind + renk paleti (Light & Dark mode)
- [ ] Liquid Glass CSS + SVG Filter
- [ ] Dock komponenti (Liquid Glass)
- [ ] Tema toggle (Light/Dark)
- [ ] Ana sayfa (statik)

### Faz 2: API Entegrasyonu (3-4 gün)
- [ ] API servisi (axios/fetch)
- [ ] Zustand store
- [ ] Ana sayfa (dinamik)
- [ ] Başlat/Durdur fonksiyonu
- [ ] System Tray + minimize

### Faz 3: Anlık & Grafikler (4-5 gün)
- [ ] WebSocket bağlantısı
- [ ] Anlık yorumlar sayfası
- [ ] Grafikler sayfası
- [ ] Recharts entegrasyonu

### Faz 4: Plan & Rapor (4-5 gün)
- [ ] Planlar sayfası (sol sidebar)
- [ ] Markdown editör (@uiw/react-md-editor)
- [ ] Raporlar sayfası (sol sidebar)
- [ ] Rapor onay modalı
- [ ] Obsidian export
- [ ] PDF export (opsiyonel)

### Faz 5: Ayarlar & Polish (2-3 gün)
- [ ] Ayarlar sayfası
- [ ] Animasyonlar
- [ ] Hata handling
- [ ] Toast bildirimleri
- [ ] Loading states

---

## 📦 Bağımlılıklar Özeti

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.0.0",
    "zustand": "^4.0.0",
    "@tanstack/react-query": "^5.0.0",
    "recharts": "^2.0.0",
    "lucide-react": "^0.300.0",
    "@uiw/react-md-editor": "^4.0.0",
    "socket.io-client": "^4.0.0",
    "framer-motion": "^10.0.0"
  },
  "devDependencies": {
    "electron": "^28.0.0",
    "electron-builder": "^24.0.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.0.0"
  }
}
```

---

## 🎯 Özet

| Karar | Seçim |
|-------|-------|
| Tema | Light (Cashmere) + Dark Mode |
| Navigasyon | Dock (alt, Liquid Glass) |
| Plan düzenleme | Markdown editör |
| Rapor oluşturma | Onay modalı ile |
| Kapatma davranışı | Tray'e minimize |
| Efekt | Liquid Glass (macOS Sequoia tarzı) |

---

*Son güncelleme: 2025-12-09*
