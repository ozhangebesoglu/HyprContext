"""
HyprContext - Günlük Plan Oluşturucu
Kullanıcı profiline ve geçmiş aktivitelere dayalı günlük plan üretir.
"""

import subprocess
import sys
import logging
from datetime import datetime

import yaml
import ollama

from config import (
    PROFILE_PATH, OBSIDIAN_DAILY_DIR, 
    MEMORY_DAYS, MODEL_PLAN, WEATHER_URL,
    ensure_dirs
)
from database import get_logs_last_n_days

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_profile() -> dict | None:
    """Kullanıcı profilini yükler."""
    if not PROFILE_PATH.exists():
        logger.error(f"Profil dosyası bulunamadı: {PROFILE_PATH}")
        return None
    
    try:
        with open(PROFILE_PATH, 'r', encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Profil okuma hatası: {e}")
        return None


def get_weather() -> str:
    """Hava durumunu çeker."""
    try:
        result = subprocess.run(
            ["curl", "-s", WEATHER_URL],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() or "Bilinmiyor"
    except Exception:
        return "Bilinmiyor"


def get_active_course(profile: dict) -> str:
    """Aktif eğitim modülünü bulur."""
    try:
        courses = profile.get('egitim_programi', {}).get('durum', [])
        for course in courses:
            if "Aktif" in course.get('durum', ''):
                return course['isim']
    except Exception:
        pass
    return "Genel Gelişim"


def format_history(logs: list[dict]) -> str:
    """Log listesini okunabilir formata çevirir."""
    if not logs:
        return "Belirtilen sürede kayıt yok."
    
    lines = [f"- [{log['date']} {log['time']}] {log['content']}" for log in logs]
    return "\n".join(lines)


def generate_daily_plan():
    """Günlük planı oluşturur ve kaydeder."""
    logger.info("Günlük plan oluşturuluyor...")
    
    # Profili yükle
    profile = load_profile()
    if not profile:
        return
    
    # Verileri topla
    weather = get_weather()
    active_course = get_active_course(profile)
    logs = get_logs_last_n_days(MEMORY_DAYS)
    history = format_history(logs)
    
    # Kullanıcı notu (varsa)
    user_note = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Yok"
    if user_note != "Yok":
        logger.info(f"Kullanıcı notu: {user_note}")
    
    logger.info(f"Aktif eğitim: {active_course}")
    
    # === SYSTEM PROMPT ===
    system_prompt = f"""Sen bir günlük planlama asistanısın.
Sadece verilen şablonu doldur, ekstra açıklama yapma.
Dil: Türkçe.

KULLANICI PROFİLİ:
{yaml.dump(profile, allow_unicode=True)}"""

    # === USER PROMPT ===
    user_prompt = f"""Bugünün planını oluştur.

VERİLER:
- Hava: {weather}
- Not: {user_note}
- Aktif Eğitim: {active_course}
- Geçmiş Aktiviteler:
{history}

KURAL: "{active_course}" konusuna odaklan. Tüm bloklar bu dersle ilgili olsun.

ŞABLON:
# 🎯 Günün Misyonu: [Tek cümle hedef]
> **Hava:** {weather}

## 🌅 Sabah (09:00 - 12:00)
* [Saat]: [Görev] ({active_course})

## ☀️ Öğle (13:00 - 17:00)
* [Saat]: [Görev] ({active_course})

## 🌙 Akşam (18:00 - 22:00)
* [Saat]: [Görev] ({active_course})

## ⚠️ Asistan Notu
[Kısa motivasyon notu]"""

    print("\n" + "=" * 40)
    
    try:
        stream = ollama.chat(
            model=MODEL_PLAN,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            options={
                'temperature': 0.1,
                'repeat_penalty': 1.2,
                'num_predict': 1024
            },
            stream=True
        )
        
        plan = ""
        header_marker = "# 🎯"
        header_found = False
        
        for chunk in stream:
            content = chunk['message']['content']
            plan += content
            
            # Canlı filtreleme
            if not header_found:
                if header_marker in plan:
                    header_found = True
                    clean_start = plan.find(header_marker)
                    print(plan[clean_start:], end="", flush=True)
            else:
                print(content, end="", flush=True)
        
        print("\n" + "=" * 40)
        
        # Temizlik
        if header_marker in plan:
            plan = plan[plan.find(header_marker):]
        
        # Kaydet
        ensure_dirs()
        today_str = datetime.now().strftime("%Y-%m-%d")
        file_path = OBSIDIAN_DAILY_DIR / f"Plan_{today_str}.md"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(plan)
        
        logger.info(f"Plan kaydedildi: {file_path}")
        
    except Exception as e:
        logger.error(f"Plan oluşturma hatası: {e}")


if __name__ == "__main__":
    generate_daily_plan()
