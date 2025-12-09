# 🖥️ HyprContext Frontend Planı

## 🎨 Tema: Liquid Glass + Cashmere

Tüm uygulama **Liquid Glass** (macOS Sequoia tarzı cam efekti) teması kullanacak. Kartlar, butonlar, modallar, sidebar'lar ve dock hepsi bu efekti kullanacak.

### Renk Paleti: Cashmere

#### Light Mode
| İsim | HEX | Kullanım |
|------|-----|----------|
| Buff | `#D9B596` | Arka plan (gradient/resim) |
| Cocoa | `#824830` | Metin |
| Sienna | `#A4643B` | Accent |
| Glass Tint | `rgba(255, 255, 255, 0.5)` | Cam rengi |
| Glass Border | `rgba(255, 255, 255, 0.3)` | Cam kenar |

#### Dark Mode
| İsim | HEX | Kullanım |
|------|-----|----------|
| Charcoal | `#1a1612` | Arka plan |
| Cream | `#E8DDD0` | Metin |
| Sienna | `#A4643B` | Accent (aynı) |
| Glass Tint | `rgba(26, 22, 18, 0.6)` | Cam rengi |
| Glass Border | `rgba(255, 255, 255, 0.1)` | Cam kenar |

### CSS Değişkenleri
```css
:root {
  /* Light Mode */
  --bg-primary: #D9B596;
  --text-primary: #824830;
  --text-secondary: #AE9D8A;
  --accent: #A4643B;
  
  /* Liquid Glass */
  --glass-tint: rgba(255, 255, 255, 0.5);
  --glass-border: rgba(255, 255, 255, 0.3);
  --glass-shine: rgba(255, 255, 255, 0.5);
  --glass-shadow: rgba(0, 0, 0, 0.2);
  --glass-blur: 20px;
}

[data-theme="dark"] {
  /* Dark Mode */
  --bg-primary: #1a1612;
  --text-primary: #E8DDD0;
  --text-secondary: #8B7B6B;
  --accent: #A4643B;
  
  /* Liquid Glass - Dark */
  --glass-tint: rgba(26, 22, 18, 0.6);
  --glass-border: rgba(255, 255, 255, 0.1);
  --glass-shine: rgba(255, 255, 255, 0.15);
  --glass-shadow: rgba(0, 0, 0, 0.4);
  --glass-blur: 20px;
}
```

---

## 💎 Liquid Glass Tasarım Sistemi

### Temel Prensip
Uygulama arka planında bir **gradient veya resim** olacak. Tüm UI elementleri bu arka planın üzerinde **yarı saydam cam** gibi görünecek.

### Arka Plan
```css
/* Light Mode - Gradient */
body {
  background: linear-gradient(135deg, #D9B596 0%, #E8DDD0 50%, #D9B596 100%);
  /* Veya pattern/resim */
  background-image: url('/assets/cashmere-pattern.png');
  background-size: cover;
}

/* Dark Mode */
[data-theme="dark"] body {
  background: linear-gradient(135deg, #1a1612 0%, #2d2420 50%, #1a1612 100%);
}
```

### Glass Component Yapısı
Her cam element 4 katmandan oluşur:

```
┌─────────────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  ← 1. Effect (blur + distortion)
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  ← 2. Tint (renk katmanı)
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  ← 3. Shine (ışık yansıması)
│ ░░░░░░░  İÇERİK  ░░░░░░░░░░░░░░░░░ │  ← 4. Content (gerçek içerik)
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────────────┘
```

### Glass Variants

| Variant | Kullanım | Blur | Tint Opaklık |
|---------|----------|------|--------------|
| `glass-solid` | Kartlar, Sidebar | 20px | 0.5 |
| `glass-light` | Butonlar, Tags | 10px | 0.3 |
| `glass-heavy` | Modal, Dock | 30px | 0.6 |
| `glass-subtle` | Hover states | 5px | 0.2 |

---

## 💎 Liquid Glass CSS Sistemi

### Base Glass Component
```css
/* Base Liquid Glass */
.glass {
  position: relative;
  overflow: hidden;
  border-radius: 1rem;
  box-shadow: 
    0 8px 32px var(--glass-shadow),
    inset 0 0 0 1px var(--glass-border);
}

.glass::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
}

.glass::after {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
  background: var(--glass-tint);
  box-shadow: 
    inset 2px 2px 4px 0 var(--glass-shine),
    inset -1px -1px 2px 0 var(--glass-shine);
}

.glass > * {
  position: relative;
  z-index: 2;
}
```

### Glass Variants
```css
/* Solid - Kartlar, Paneller */
.glass-solid {
  --glass-blur: 20px;
  --glass-tint: rgba(255, 255, 255, 0.5);
}
[data-theme="dark"] .glass-solid {
  --glass-tint: rgba(26, 22, 18, 0.6);
}

/* Light - Butonlar, Tags */
.glass-light {
  --glass-blur: 10px;
  --glass-tint: rgba(255, 255, 255, 0.3);
  border-radius: 0.5rem;
}
[data-theme="dark"] .glass-light {
  --glass-tint: rgba(26, 22, 18, 0.4);
}

/* Heavy - Modal, Dock */
.glass-heavy {
  --glass-blur: 30px;
  --glass-tint: rgba(255, 255, 255, 0.6);
}
[data-theme="dark"] .glass-heavy {
  --glass-tint: rgba(26, 22, 18, 0.7);
}

/* Subtle - Hover */
.glass-subtle {
  --glass-blur: 5px;
  --glass-tint: rgba(255, 255, 255, 0.2);
}
```

### Glass Components

```css
/* Card */
.glass-card {
  @apply glass glass-solid;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 12px 40px var(--glass-shadow),
    inset 0 0 0 1px var(--glass-border);
}

/* Button */
.glass-button {
  @apply glass glass-light;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-primary);
  font-weight: 500;
}

.glass-button:hover {
  --glass-tint: rgba(255, 255, 255, 0.5);
  transform: scale(1.02);
}

.glass-button:active {
  transform: scale(0.98);
}

/* Button Primary (Accent) */
.glass-button-primary {
  @apply glass-button;
  background: var(--accent);
  color: white;
}

/* Sidebar */
.glass-sidebar {
  @apply glass glass-solid;
  height: 100%;
  border-radius: 0 1rem 1rem 0;
}

/* Modal */
.glass-modal {
  @apply glass glass-heavy;
  max-width: 500px;
  padding: 2rem;
}

/* Input */
.glass-input {
  @apply glass glass-light;
  padding: 0.75rem 1rem;
  border: none;
  outline: none;
  background: transparent;
  color: var(--text-primary);
}

.glass-input:focus {
  box-shadow: 
    0 0 0 2px var(--accent),
    inset 0 0 0 1px var(--glass-border);
}

/* Tag */
.glass-tag {
  @apply glass glass-light;
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  border-radius: 9999px;
}

/* Dock */
.glass-dock {
  @apply glass glass-heavy;
  padding: 0.75rem;
  border-radius: 2rem;
}
```

### SVG Distortion Filter (Opsiyonel - Ekstra Efekt)
```html
<svg style="display: none">
  <filter id="glass-distortion" x="0%" y="0%" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.01" numOctaves="1" seed="5" result="noise" />
    <feDisplacementMap in="SourceGraphic" in2="noise" scale="10" xChannelSelector="R" yChannelSelector="G" />
  </filter>
</svg>

/* Kullanım */
.glass-distorted::before {
  filter: url(#glass-distortion);
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
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  ░░                                                         ░░ │
│  ░░                    HyprContext                          ░░ │
│  ░░                  ─────────────────                      ░░ │
│  ░░                                                         ░░ │
│  ░░           ╭─────────────────────────────╮               ░░ │
│  ░░           │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░ │               ░░ │
│  ░░           │ ░░░                     ░░░ │               ░░ │
│  ░░           │ ░░░    ▶️  BAŞLAT       ░░░ │  glass-button ░░ │
│  ░░           │ ░░░                     ░░░ │               ░░ │
│  ░░           │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░ │               ░░ │
│  ░░           ╰─────────────────────────────╯               ░░ │
│  ░░                                                         ░░ │
│  ░░                ☐ Sistem ile otomatik başlat             ░░ │
│  ░░                                                         ░░ │
│  ░░     ╭───────────────────────────────────────────╮       ░░ │
│  ░░     │ ░░░░░░░░ 📊 Bugünün Özeti ░░░░░░░░░░░░░░░ │       ░░ │
│  ░░     │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │       ░░ │
│  ░░     │ ░░  Kayıt      Süre       Odak       ░░░░ │       ░░ │
│  ░░     │ ░░   142       4s 32dk     %78       ░░░░ │ glass ░░ │
│  ░░     │ ░░                                   ░░░░ │ card  ░░ │
│  ░░     │ ░░  Son aktivite: 2 dk önce          ░░░░ │       ░░ │
│  ░░     │ ░░  "VS Code'da Python yazıyor"      ░░░░ │       ░░ │
│  ░░     │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │       ░░ │
│  ░░     ╰───────────────────────────────────────────╯       ░░ │
│  ░░                                                         ░░ │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
├─────────────────────────────────────────────────────────────────┤
│  ╭──────────────────────────────────────────────────────────╮  │
│  │ ░░░ [🏠]    [📝]    [📊]    [📅]    [📄]    [⚙️] ░░░░░ │  │
│  ╰──────────────────────────────────────────────────────────╯  │
│                          glass-dock                             │
└─────────────────────────────────────────────────────────────────┘

Arka plan: Gradient veya pattern
Tüm elementler: Liquid Glass efekti
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
│   ├── glass/                    # 💎 Liquid Glass Primitives
│   │   ├── GlassCard.tsx         # Temel cam kart
│   │   ├── GlassButton.tsx       # Cam buton
│   │   ├── GlassInput.tsx        # Cam input
│   │   ├── GlassModal.tsx        # Cam modal
│   │   ├── GlassTag.tsx          # Cam etiket
│   │   ├── GlassSidebar.tsx      # Cam sidebar
│   │   ├── GlassDock.tsx         # Cam dock
│   │   └── GlassFilter.tsx       # SVG distortion filter
│   │
│   ├── layout/
│   │   ├── AppLayout.tsx         # Ana layout (arka plan + dock)
│   │   ├── PageContainer.tsx     # Sayfa wrapper
│   │   └── SidebarLayout.tsx     # Sidebar'lı sayfa layout
│   │
│   ├── common/
│   │   ├── Slider.tsx
│   │   ├── Dropdown.tsx
│   │   ├── Checkbox.tsx
│   │   ├── Calendar.tsx
│   │   ├── Toast.tsx
│   │   └── LoadingSpinner.tsx
│   │
│   ├── features/
│   │   ├── ActivityCard.tsx      # glass-card kullanan
│   │   ├── PlanViewer.tsx
│   │   ├── PlanEditor.tsx        # Markdown editör
│   │   ├── ReportViewer.tsx
│   │   ├── ConfirmModal.tsx      # Onay modalı
│   │   ├── StatusIndicator.tsx
│   │   ├── StatCard.tsx
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
│
├── styles/
│   ├── globals.css               # Temel stiller
│   ├── glass.css                 # Liquid Glass sistemi
│   └── themes.css                # Light/Dark tema
```

### Glass Component Örneği

```tsx
// components/glass/GlassCard.tsx
import { ReactNode } from 'react';
import clsx from 'clsx';

interface GlassCardProps {
  children: ReactNode;
  variant?: 'solid' | 'light' | 'heavy' | 'subtle';
  className?: string;
  hover?: boolean;
}

export const GlassCard = ({ 
  children, 
  variant = 'solid', 
  className,
  hover = true 
}: GlassCardProps) => {
  return (
    <div 
      className={clsx(
        'glass',
        `glass-${variant}`,
        hover && 'glass-hover',
        className
      )}
    >
      {children}
    </div>
  );
};

// Kullanım
<GlassCard variant="solid" className="p-6">
  <h2>Bugünün Özeti</h2>
  <p>142 kayıt</p>
</GlassCard>
```

### App Layout (Arka Plan + Glass)

```tsx
// components/layout/AppLayout.tsx
import { Outlet } from 'react-router-dom';
import { GlassDock } from '../glass/GlassDock';
import { GlassFilter } from '../glass/GlassFilter';

export const AppLayout = () => {
  return (
    <div className="app-layout">
      {/* SVG Filter (gizli) */}
      <GlassFilter />
      
      {/* Arka plan */}
      <div className="app-background" />
      
      {/* Sayfa içeriği */}
      <main className="app-content">
        <Outlet />
      </main>
      
      {/* Dock */}
      <GlassDock />
    </div>
  );
};

// CSS
.app-layout {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.app-background {
  position: fixed;
  inset: 0;
  z-index: -1;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  /* Veya pattern */
}

.app-content {
  padding: 2rem;
  padding-bottom: 100px; /* Dock için alan */
}
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

### Faz 1: Temel Yapı + Glass System (4-5 gün)
- [ ] Electron + Vite + React kurulumu
- [ ] Tailwind + CSS değişkenleri
- [ ] **Liquid Glass Tasarım Sistemi:**
  - [ ] glass.css (base styles)
  - [ ] GlassCard.tsx
  - [ ] GlassButton.tsx
  - [ ] GlassInput.tsx
  - [ ] GlassModal.tsx
  - [ ] GlassTag.tsx
  - [ ] GlassSidebar.tsx
  - [ ] GlassDock.tsx
  - [ ] GlassFilter.tsx (SVG)
- [ ] AppLayout (arka plan + dock)
- [ ] Tema toggle (Light/Dark)
- [ ] Ana sayfa (glass componentlerle)

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
| **Ana Tema** | **Liquid Glass** (tüm uygulama) |
| Renk Paleti | Cashmere (Light + Dark) |
| Navigasyon | Dock (alt, glass-heavy) |
| Kartlar | glass-solid |
| Butonlar | glass-light |
| Modallar | glass-heavy |
| Sidebar | glass-solid |
| Plan düzenleme | Markdown editör |
| Rapor oluşturma | Onay modalı (glass-modal) |
| Kapatma davranışı | Tray'e minimize |

### Liquid Glass Hierarchy

```
Yoğunluk (Blur + Opacity)
─────────────────────────────────────────►
subtle (5px)  light (10px)  solid (20px)  heavy (30px)
   │              │             │             │
   ▼              ▼             ▼             ▼
  Hover        Butonlar      Kartlar       Modal
  States       Tags          Sidebar       Dock
               Inputs        Paneller
```

---

*Son güncelleme: 2025-12-09*
