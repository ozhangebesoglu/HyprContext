"""
HyprContext - Odak Takipçisi
Yasaklı uygulamalarda geçirilen süreyi takip eder.
Günlük limit aşılırsa uyarı verir.
"""

import json
import subprocess
import time
import logging
from datetime import datetime, date
from pathlib import Path

from config import BASE_DIR, YASAKLI_KELIMELER, DAILY_DISTRACTION_LIMIT_SECONDS
from window_utils import get_active_window_info, get_all_workspaces_info

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === AYARLAR ===
DAILY_LIMIT_SECONDS = DAILY_DISTRACTION_LIMIT_SECONDS
CHECK_INTERVAL = 1  # Her 1 saniyede bir kontrol (hassas takip)
TRACKER_FILE = BASE_DIR / "focus_data.json"

# Uyarı eşikleri (saniye)
WARNING_THRESHOLDS = [
    (30 * 60, "30 dakika"),      # 30 dk
    (60 * 60, "1 saat"),         # 1 saat
    (90 * 60, "1.5 saat"),       # 1.5 saat
    (110 * 60, "1 saat 50 dk"),  # Son 10 dk uyarısı
    (DAILY_LIMIT_SECONDS, "2 saat - LİMİT DOLDU!")
]


def load_tracker_data() -> dict:
    """Takip verisini yükler."""
    if not TRACKER_FILE.exists():
        return {}
    
    try:
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_tracker_data(data: dict) -> None:
    """Takip verisini kaydeder."""
    try:
        with open(TRACKER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Veri kaydetme hatası: {e}")


def get_today_key() -> str:
    """Bugünün tarihini anahtar olarak döndürür."""
    return date.today().isoformat()


def is_distraction(window_info: str) -> bool:
    """Pencere bilgisinde yasaklı kelime var mı kontrol eder."""
    window_lower = window_info.lower()
    return any(keyword in window_lower for keyword in YASAKLI_KELIMELER)


def check_all_workspaces() -> tuple[bool, str | None]:
    """Tüm workspace'lerde yasaklı uygulama var mı kontrol eder.
    
    Returns:
        (is_distraction, found_keyword): Yasaklı var mı ve hangi kelime bulundu
    """
    # Önce aktif pencereyi kontrol et
    active_window = get_active_window_info()
    if is_distraction(active_window):
        for keyword in YASAKLI_KELIMELER:
            if keyword in active_window.lower():
                return True, keyword
    
    # Tüm workspace'leri kontrol et
    all_windows = get_all_workspaces_info()
    all_windows_lower = all_windows.lower()
    
    for keyword in YASAKLI_KELIMELER:
        if keyword in all_windows_lower:
            return True, keyword
    
    return False, None


def format_time(seconds: int) -> str:
    """Saniyeyi okunabilir formata çevirir."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}s {minutes}dk"
    elif minutes > 0:
        return f"{minutes}dk {secs}sn"
    else:
        return f"{secs}sn"


def play_sound(sound_type: str = "warning") -> None:
    """Ses çalar.
    
    Args:
        sound_type: "warning", "critical", "speak"
    """
    try:
        if sound_type == "critical":
            # Kritik uyarı - alarm sesi
            subprocess.Popen(
                ["paplay", "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif sound_type == "speak":
            # Sesli uyarı - Edge TTS ile doğal Türkçe ses
            speak_warning()
        else:
            # Normal uyarı
            subprocess.Popen(
                ["paplay", "/usr/share/sounds/freedesktop/stereo/message.oga"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except FileNotFoundError:
        pass  # Ses aracı yoksa sessizce geç


def speak_warning(message: str = "Dikkat! Yasaklı uygulama açık. Lütfen işine dön!") -> None:
    """Edge TTS ile doğal Türkçe sesli uyarı."""
    try:
        # Arka planda çalıştır
        subprocess.Popen(
            f'cd {BASE_DIR} && source venv/bin/activate && '
            f'edge-tts --voice tr-TR-AhmetNeural --text "{message}" --write-media /tmp/warning.mp3 && '
            f'mpv --no-video --really-quiet /tmp/warning.mp3',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logger.debug(f"TTS hatası: {e}")


def send_notification(title: str, message: str, urgency: str = "normal", sound: bool = True) -> None:
    """Bildirim gönderir (opsiyonel sesli)."""
    try:
        subprocess.run([
            "notify-send",
            "-u", urgency,
            "-t", "5000",
            title,
            message
        ], check=False)
        
        # Sesli uyarı
        if sound:
            if urgency == "critical":
                play_sound("critical")
            else:
                play_sound("warning")
                
    except FileNotFoundError:
        logger.warning("notify-send bulunamadı")


def get_remaining_time(used_seconds: int) -> int:
    """Kalan süreyi hesaplar."""
    return max(0, DAILY_LIMIT_SECONDS - used_seconds)


def run_tracker():
    """Ana takip döngüsü."""
    logger.info("🎯 Odak Takipçisi başlatıldı")
    logger.info(f"Günlük limit: {format_time(DAILY_LIMIT_SECONDS)}")
    logger.info(f"Yasaklı kelimeler: {', '.join(YASAKLI_KELIMELER)}")
    
    # Takip verisi
    data = load_tracker_data()
    today = get_today_key()
    
    # Bugünün verisini başlat
    if today not in data:
        data[today] = {
            "distraction_seconds": 0,
            "warnings_sent": [],
            "limit_reached": False
        }
        save_tracker_data(data)
    
    today_data = data[today]
    last_warning_threshold = 0
    
    # Önceki uyarıları yükle
    for threshold, _ in WARNING_THRESHOLDS:
        if threshold in today_data.get("warnings_sent", []):
            last_warning_threshold = max(last_warning_threshold, threshold)
    
    logger.info(f"Bugün kullanılan: {format_time(today_data['distraction_seconds'])}")
    logger.info(f"Kalan: {format_time(get_remaining_time(today_data['distraction_seconds']))}")
    
    while True:
        try:
            # Gün değişti mi?
            current_day = get_today_key()
            if current_day != today:
                logger.info("🌅 Yeni gün başladı, sayaç sıfırlandı")
                today = current_day
                if today not in data:
                    data[today] = {
                        "distraction_seconds": 0,
                        "warnings_sent": [],
                        "limit_reached": False
                    }
                today_data = data[today]
                last_warning_threshold = 0
                save_tracker_data(data)
            
            # Tüm workspace'leri kontrol et
            is_distracted, found_keyword = check_all_workspaces()
            
            if is_distracted:
                # Yasaklı uygulama açık - süreyi artır
                today_data["distraction_seconds"] += CHECK_INTERVAL
                used = today_data["distraction_seconds"]
                
                remaining = get_remaining_time(used)
                
                # Log (her 30 saniyede bir)
                if used % 30 == 0:
                    logger.info(f"🚨 '{found_keyword}' - Kullanılan: {format_time(used)} | Kalan: {format_time(remaining)}")
                
                # Periyodik kaydet (her 60 saniyede bir)
                if used % 60 == 0:
                    save_tracker_data(data)
                
                # Uyarı kontrolü
                for threshold, label in WARNING_THRESHOLDS:
                    if used >= threshold and threshold > last_warning_threshold:
                        last_warning_threshold = threshold
                        today_data["warnings_sent"].append(threshold)
                        
                        if threshold >= DAILY_LIMIT_SECONDS:
                            # Limit doldu!
                            today_data["limit_reached"] = True
                            send_notification(
                                "🛑 GÜNLÜK LİMİT DOLDU!",
                                f"Yasaklı uygulamalarda {label} geçirdin!\nBugünlük yeter, işine dön!",
                                "critical"
                            )
                            # Sesli uyarı (TTS)
                            play_sound("speak")
                            logger.warning(f"🛑 LİMİT DOLDU! {label}")
                        else:
                            send_notification(
                                "⏰ Süre Uyarısı",
                                f"Yasaklı uygulamalarda {label} geçirdin.\nKalan: {format_time(remaining)}",
                                "normal"
                            )
                            logger.info(f"⏰ Uyarı: {label} - Kalan: {format_time(remaining)}")
                        
                        save_tracker_data(data)
                
                # Limit aşıldıysa her dakika uyar
                if today_data.get("limit_reached") and used % 60 == 0:
                    send_notification(
                        "🛑 LİMİT AŞILDI!",
                        f"Bugün {format_time(used)} harcadın. İşine dön!",
                        "critical"
                    )
                    # Her 5 dakikada bir sesli uyarı
                    if used % 300 == 0:
                        play_sound("speak")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Takipçi durduruldu")
            save_tracker_data(data)
            break
        except Exception as e:
            logger.error(f"Hata: {e}")
            time.sleep(CHECK_INTERVAL)


def show_stats():
    """Bugünün istatistiklerini gösterir."""
    data = load_tracker_data()
    today = get_today_key()
    
    if today not in data:
        print("Bugün için veri yok.")
        return
    
    today_data = data[today]
    used = today_data["distraction_seconds"]
    remaining = get_remaining_time(used)
    
    print("\n" + "=" * 40)
    print("📊 Bugünün Odak İstatistikleri")
    print("=" * 40)
    print(f"📅 Tarih: {today}")
    print(f"⏱️  Kullanılan: {format_time(used)}")
    print(f"⏳ Kalan: {format_time(remaining)}")
    print(f"📈 Yüzde: {(used / DAILY_LIMIT_SECONDS) * 100:.1f}%")
    
    if today_data.get("limit_reached"):
        print("🛑 Durum: LİMİT AŞILDI!")
    elif used > DAILY_LIMIT_SECONDS * 0.75:
        print("⚠️  Durum: Kritik seviye!")
    elif used > DAILY_LIMIT_SECONDS * 0.5:
        print("🟡 Durum: Dikkatli ol")
    else:
        print("🟢 Durum: İyi gidiyorsun!")
    
    print("=" * 40 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        show_stats()
    else:
        run_tracker()

