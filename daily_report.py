"""
HyprContext - Günlük Rapor Oluşturucu
Günün aktivitelerini analiz edip özet rapor üretir.
"""

import logging
from datetime import datetime

import ollama

from config import OBSIDIAN_DAILY_DIR, MODEL_REPORT, ensure_dirs
from database import get_logs_by_date

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def format_logs(logs: list[dict]) -> str:
    """Log listesini okunabilir formata çevirir."""
    return "\n".join([f"- [{log['time']}] {log['content']}" for log in logs])


def generate_report():
    """Günlük rapor oluşturur ve kaydeder."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"{today_str} raporu hazırlanıyor...")
    
    # Bugünün loglarını çek
    logs = get_logs_by_date(today_str)
    
    if not logs:
        logger.warning("Bugün için henüz kayıt yok.")
        return
    
    logger.info(f"{len(logs)} aktivite analiz ediliyor...")
    
    full_text = format_logs(logs)
    
    # === SYSTEM PROMPT ===
    system_prompt = """Sen bir veri analistisin.
Logları analiz et ve Markdown rapor oluştur.
Yorum yapma, sohbet etme. Sadece raporu yaz.
Dil: Türkçe."""

    # === USER PROMPT ===
    user_prompt = f"""LOGLAR:
{full_text}

ŞABLON:
# 📅 Günlük Rapor: {today_str}

## 🎯 Günün Özeti
(Ana odak noktası, hangi projeler üzerinde çalışıldı. 2-3 cümle.)

## 🛠️ Kullanılan Teknolojiler
(Tespit edilen araçlar, diller, kütüphaneler. Liste halinde.)

## ⏱️ Zaman Çizelgesi
(Günü bloklara böl. Sabah, öğle, akşam ne yapıldı.)

## 💡 Verimlilik Notları
(Odaklanma seviyesi, çoklu görev durumu.)"""

    print("\n" + "=" * 40)
    
    try:
        stream = ollama.chat(
            model=MODEL_REPORT,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            options={
                'temperature': 0.2,
                'num_predict': 2048
            },
            stream=True
        )
        
        summary = ""
        for chunk in stream:
            part = chunk['message']['content']
            print(part, end="", flush=True)
            summary += part
        
        print("\n" + "=" * 40)
        
        # Temizlik
        header_marker = "# 📅"
        if header_marker in summary:
            summary = summary[summary.find(header_marker):]
        
        # Ham logları da ekle
        final_content = f"{summary}\n\n## 📋 Ham Loglar\n{full_text}"
        
        # Kaydet
        ensure_dirs()
        file_path = OBSIDIAN_DAILY_DIR / f"{today_str}.md"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        logger.info(f"Rapor kaydedildi: {file_path}")
        
    except Exception as e:
        logger.error(f"Rapor oluşturma hatası: {e}")


if __name__ == "__main__":
    generate_report()
