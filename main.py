"""
HyprContext - Ana İzleme Servisi
Ekran görüntüsü alır, AI ile analiz eder, hafızaya kaydeder.
"""

import os
import re
import time
import subprocess
import logging
from datetime import datetime
from collections import deque

import ollama

from config import (
    CAPTURE_INTERVAL, MIN_COOLDOWN, RAM_SIZE,
    YASAKLI_KELIMELER, DISTRACTION_THRESHOLD,
    MODEL_VISION
)
from database import save_memory
from window_utils import get_active_window_info, get_all_workspaces_info

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === KISA SÜRELİ HAFIZA ===
short_term_memory: deque = deque(maxlen=RAM_SIZE)

# === ODAK BEKÇİSİ ===
distraction_count = 0

# === PROMPT ŞABLONLARI ===
SYSTEM_PROMPT = """Sen bir ekran görüntüsü analistisin. Türkçe yaz.
FORMAT: Tek cümle özet + [Etiket1, Etiket2, Etiket3]
ETİKET ZORUNLU: Her cevabın sonunda mutlaka köşeli parantez içinde 2-4 etiket olmalı."""

USER_PROMPT_TEMPLATE = """EKRANI ANALİZ ET.

Aktif: {active_win}

FORMAT KURALI:
Cevabın MUTLAKA şu formatta olmalı: "Açıklama cümlesi. [Etiket1, Etiket2]"

ETİKET ÖRNEKLERİ:
- Kod yazıyorsa: [Python, Geliştirme] veya [JavaScript, React]
- Video izliyorsa: [YouTube, Video, Eğlence]
- Araştırma yapıyorsa: [Araştırma, Web, Öğrenme]
- Terminal kullanıyorsa: [Terminal, Komut, Sistem]
- Dokümantasyon okuyorsa: [Dokümantasyon, Öğrenme]

ÖRNEKLER:
✅ "VS Code'da main.py dosyası açık, analyze_image fonksiyonu düzenleniyor. [Python, AI, Geliştirme]"
✅ "YouTube'da 'React Tutorial' videosu izleniyor. [YouTube, React, Öğrenme]"
✅ "Terminal'de pip install komutu çalıştırılıyor. [Terminal, Python, Kurulum]"

YASAK:
❌ Sadece uygulama listesi yapma
❌ "Genel" etiketi kullanma
❌ Etiket koymayı unutma

ŞİMDİ EKRANA BAK VE YAZ:"""


def take_screenshot() -> str | None:
    """Ekran görüntüsü alır, dosya yolunu döndürür."""
    temp_path = "/tmp/hypr_context_snap.png"
    
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except OSError as e:
            logger.warning(f"Eski screenshot silinemedi: {e}")
    
    try:
        subprocess.run(
            ["grim", temp_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if os.path.exists(temp_path):
            return temp_path
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Screenshot hatası: {e}")
        return None
    except FileNotFoundError:
        logger.error("grim bulunamadı. 'sudo pacman -S grim' ile kur.")
        return None


def check_distraction(analysis: str) -> None:
    """Yasaklı kelimeleri kontrol eder ve bildirim atar."""
    global distraction_count
    
    summary_lower = analysis.lower()
    
    if any(keyword in summary_lower for keyword in YASAKLI_KELIMELER):
        distraction_count += 1
        logger.warning(f"Dikkat dağınıklığı tespit edildi ({distraction_count}/{DISTRACTION_THRESHOLD})")
    else:
        if distraction_count > 0:
            distraction_count -= 1

    if distraction_count >= DISTRACTION_THRESHOLD:
        try:
            subprocess.run([
                "notify-send", "-u", "critical", "-t", "7000",
                "🛑 ODAK UYARISI",
                f"{DISTRACTION_THRESHOLD} döngüdür iş dışı aktivite tespit edildi. Koduna dön!"
            ])
            distraction_count = 0
        except FileNotFoundError:
            logger.warning("notify-send bulunamadı")


def clean_output(raw_text: str) -> str:
    """Model çıktısını temizler ve formatlar.
    
    Temizlenen şeyler:
    - İngilizce giriş cümleleri (Okay, Here's, Let's, etc.)
    - Markdown başlıkları (**Analysis:**, ## Output, etc.)
    - Boş satırlar ve fazla boşluklar
    - Sadece son [etiketler] kısmını korur
    """
    text = raw_text.strip()
    
    # İngilizce giriş cümlelerini temizle
    english_patterns = [
        r"^Okay[,.]?\s*",
        r"^Here'?s?\s*(the|an|my)?\s*(analysis|output)?[:.]*\s*",
        r"^Let'?s\s+analyze[:.]*\s*",
        r"^Based on\s+.*?[,:]\s*",
        r"^Looking at\s+.*?[,:]\s*",
        r"^\*\*Analysis:?\*\*\s*",
        r"^\*\*Output:?\*\*\s*",
        r"^##?\s*(Analysis|Output|Summary)[:.]*\s*",
    ]
    
    for pattern in english_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Satırları ayır ve temizle
    lines = text.strip().split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Boş veya sadece işaret içeren satırları atla
        if not line or line in ['-', '*', '•', '—']:
            continue
        # Markdown bullet'larını temizle
        line = re.sub(r'^[-*•]\s*', '', line)
        # **bold** işaretlerini temizle
        line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
        cleaned_lines.append(line)
    
    # Türkçe içeren satırı bul (öncelik)
    turkish_chars = set('çğıöşüÇĞİÖŞÜ')
    result = None
    
    for line in cleaned_lines:
        # Etiket içeren satırı tercih et
        if '[' in line and ']' in line:
            result = line
            break
    
    # Etiket yoksa ilk Türkçe satırı al
    if not result:
        for line in cleaned_lines:
            if any(c in line for c in turkish_chars):
                result = line
                break
    
    # Hala yoksa ilk satırı al
    if not result and cleaned_lines:
        result = cleaned_lines[0]
    
    if not result:
        return raw_text.strip()
    
    # Etiket formatını düzelt: [Etiket1, Etiket2] olmalı
    tag_match = re.search(r'\[([^\]]+)\]\s*$', result)
    
    if tag_match:
        tags = tag_match.group(1)
        summary = result[:tag_match.start()].strip()
        # Virgüllerden sonra boşluk ekle
        tags = re.sub(r',\s*', ', ', tags)
        
        # "Genel" etiketini akıllı etiketle değiştir
        if tags.strip().lower() == "genel":
            tags = infer_tags(summary)
        
        result = f"{summary} [{tags}]"
    else:
        # Etiket yok, içerikten çıkar
        tags = infer_tags(result)
        result = f"{result} [{tags}]"
    
    return result


def infer_tags(text: str) -> str:
    """Metinden otomatik etiket çıkarır."""
    text_lower = text.lower()
    tags = []
    
    # Uygulama/Araç etiketleri
    app_tags = {
        "vscode": "VSCode", "vs code": "VSCode", "code": "VSCode",
        "terminal": "Terminal", "kitty": "Terminal", "konsole": "Terminal",
        "chrome": "Chrome", "firefox": "Firefox", "zen": "Tarayıcı",
        "obsidian": "Obsidian", "notion": "Notion",
        "youtube": "YouTube", "spotify": "Spotify", "netflix": "Netflix",
        "discord": "Discord", "slack": "Slack", "telegram": "Telegram",
        "cursor": "Cursor",
    }
    
    for key, tag in app_tags.items():
        if key in text_lower and tag not in tags:
            tags.append(tag)
            break  # Sadece bir uygulama etiketi
    
    # Aktivite etiketleri
    if any(x in text_lower for x in ["python", ".py", "def ", "import "]):
        tags.append("Python")
    if any(x in text_lower for x in ["javascript", ".js", "react", "node"]):
        tags.append("JavaScript")
    if any(x in text_lower for x in ["git", "commit", "push", "pull"]):
        tags.append("Git")
    if any(x in text_lower for x in ["video", "izle", "oynat"]):
        tags.append("Video")
    if any(x in text_lower for x in ["ara", "search", "google"]):
        tags.append("Araştırma")
    if any(x in text_lower for x in ["kod", "fonksiyon", "class", "düzenl"]):
        tags.append("Geliştirme")
    if any(x in text_lower for x in ["dokümantasyon", "docs", "readme"]):
        tags.append("Dokümantasyon")
    if any(x in text_lower for x in ["pip", "npm", "install", "kur"]):
        tags.append("Kurulum")
    
    # En az 2 etiket olsun
    if len(tags) < 2:
        if "Geliştirme" not in tags:
            tags.append("Geliştirme")
    
    return ", ".join(tags[:4]) if tags else "Aktivite"


def analyze_image(image_path: str) -> str | None:
    """Ekran görüntüsünü AI ile analiz eder."""
    logger.info(f"AI ({MODEL_VISION}) analiz ediyor...")
    start_time = time.time()
    
    try:
        # Bağlam verilerini topla
        active_win = get_active_window_info()
        background_apps = get_all_workspaces_info()
        
        # Kısa süreli hafızayı formatla
        if short_term_memory:
            history_str = " → ".join(list(short_term_memory)[-3:])
        else:
            history_str = "Yeni oturum"
        
        # Prompt'u oluştur
        user_prompt = USER_PROMPT_TEMPLATE.format(
            active_win=active_win,
            background_apps=background_apps,
            history=history_str
        )
        
        response = ollama.chat(
            model=MODEL_VISION,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_prompt, 'images': [image_path]}
            ],
            keep_alive='5m',
            options={
                'temperature': 0.1,  # Daha tutarlı çıktı için düşürüldü
                'num_predict': 150   # Kısa çıktı zorla
            }
        )
        
        elapsed = time.time() - start_time
        raw_content = response['message']['content']
        
        # Çıktıyı temizle
        cleaned_content = clean_output(raw_content)
        
        logger.info(f"Analiz tamamlandı ({elapsed:.2f}s)")
        logger.debug(f"Ham: {raw_content[:100]}...")
        logger.debug(f"Temiz: {cleaned_content}")
        
        return cleaned_content
        
    except Exception as e:
        logger.error(f"Analiz hatası: {e}")
        return None


def extract_summary(text: str) -> str:
    """Etiketleri çıkararak sadece özet kısmını döndürür."""
    # Son [...] kısmını bul ve çıkar
    match = re.search(r'^(.*?)\s*\[[^\]]+\]\s*$', text)
    if match:
        return match.group(1).strip()
    return text.strip()


def main():
    """Ana döngü."""
    logger.info("HyprContext başlatıldı")
    
    while True:
        loop_start = time.time()
        
        screenshot_path = take_screenshot()
        
        if screenshot_path:
            analysis = analyze_image(screenshot_path)
            
            if analysis:
                timestamp = datetime.now().isoformat()
                save_memory(analysis, timestamp)
                check_distraction(analysis)
                
                # Kısa süreli hafızaya sadece özeti ekle
                clean_summary = extract_summary(analysis)
                short_term_memory.append(clean_summary)
                
                # Debug için son çıktıyı göster
                logger.info(f"📝 {analysis}")
            
            try:
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
            except OSError:
                pass
        
        elapsed = time.time() - loop_start
        sleep_time = max(MIN_COOLDOWN, CAPTURE_INTERVAL - elapsed)
        logger.debug(f"Bekleniyor: {sleep_time:.1f}s")
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
