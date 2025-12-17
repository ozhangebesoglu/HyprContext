# 🌟 HyprContext

<div align="center">

**Yapay Zeka Destekli Akıllı Üretkenlik Takip Asistanı**

*Hyprland kullanıcıları için tasarlanmış, yerel AI ile çalışan gizlilik odaklı masaüstü uygulaması*

[![Release](https://img.shields.io/github/v/release/ozhangebesoglu/HyprContext?style=for-the-badge&color=a855f7)](https://github.com/ozhangebesoglu/HyprContext/releases)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux-orange?style=for-the-badge)](https://github.com/ozhangebesoglu/HyprContext)

</div>

---

## 💎 Nedir?

HyprContext, bilgisayar aktivitelerinizi **yerel AI** ile analiz eden ve üretkenliğinizi artırmanıza yardımcı olan bir masaüstü uygulamasıdır.

> 🔒 **Gizlilik Öncelikli**: Tüm verileriniz cihazınızda kalır. Bulut yok, veri paylaşımı yok.

---

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

---

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler

```
✓ Linux (Arch, Fedora, Ubuntu)
✓ Hyprland veya herhangi bir Wayland WM
✓ Ollama (AI için)
✓ grim (screenshot için)
```

### 2. Kurulum

```bash
# Ollama'yı kur
curl -fsSL https://ollama.ai/install.sh | sh

# AI modelini indir
ollama pull gemma3
ollama pull mxbai-embed-large

# AppImage'ı indir ve çalıştır
chmod +x HyprContext-*.AppImage
./HyprContext-*.AppImage
```

### 3. İlk Çalıştırma

Uygulama ilk açıldığında:
1. **Veri klasörünü seçin** (varsayılan: `~/Documents/HyprContext`)
2. **Kurulumu tamamlayın**
3. **Tray'dan "Başlat"** ile takibi aktifleştirin

---

## 📖 Dokümantasyon

| Sayfa | İçerik |
|-------|--------|
| [[Kurulum]] | Detaylı kurulum rehberi |
| [[Kullanım Kılavuzu]] | Özellikler ve kullanım senaryoları |
| [[Yol Haritası]] | Proje geçmişi ve gelecek planları |
| [[API Referansı]] | Backend API dokümantasyonu |

---

## 📸 Ekran Görüntüleri

<details>
<summary>📊 Ana Panel</summary>

Aktivitelerinizi timeline görünümünde inceleyin, AI özetlerini okuyun.
</details>

<details>
<summary>📅 Planlar</summary>

Günlük hedeflerinizi belirleyin, AI önerilerinden faydalanın.
</details>

<details>
<summary>💬 AI Sohbet</summary>

"Bugün en çok ne üzerinde çalıştım?" gibi sorular sorun.
</details>

---

## 🤝 Katkıda Bulunun

Katkılarınızı bekliyoruz! 

- 🐛 Bug bildirimi: [Issues](https://github.com/ozhangebesoglu/HyprContext/issues)
- 💡 Özellik önerisi: [Discussions](https://github.com/ozhangebesoglu/HyprContext/discussions)
- 🔧 Pull Request: Fork yapın, geliştirin, PR gönderin

---

<div align="center">

**Made with 💜 for the Linux community**

</div>
