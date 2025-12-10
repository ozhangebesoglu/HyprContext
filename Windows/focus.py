"""
HyprContext Windows - Odak Takip Modülü
Dikkat dağıtıcı süreleri ve odak durumunu takip eder.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import Optional

from loguru import logger


@dataclass
class FocusData:
    """Odak takip verileri"""
    date: str
    distraction_seconds: int = 0
    distraction_count: int = 0
    focus_sessions: int = 0
    last_distraction: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "distraction_seconds": self.distraction_seconds,
            "distraction_count": self.distraction_count,
            "focus_sessions": self.focus_sessions,
            "last_distraction": self.last_distraction
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FocusData":
        return cls(
            date=data.get("date", ""),
            distraction_seconds=data.get("distraction_seconds", 0),
            distraction_count=data.get("distraction_count", 0),
            focus_sessions=data.get("focus_sessions", 0),
            last_distraction=data.get("last_distraction")
        )


@dataclass
class FocusWarning:
    """Odak uyarı bilgisi"""
    warning_type: str  # "distraction", "time", "limit"
    message: str
    urgency: str = "normal"  # "low", "normal", "critical"
    keyword: Optional[str] = None


class FocusTracker:
    """Odak takip yöneticisi"""
    
    def __init__(
        self, 
        data_path: Path,
        daily_limit_seconds: int = 1800,
        distraction_threshold: int = 3
    ):
        self.data_path = data_path
        self.daily_limit = daily_limit_seconds
        self.threshold = distraction_threshold
        self.data = self._load_or_create()
    
    def _load_or_create(self) -> FocusData:
        """Verileri yükle veya yeni oluştur"""
        today = date.today().isoformat()
        
        if self.data_path.exists():
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                # Bugünün verisi mi kontrol et
                if data.get("date") == today:
                    return FocusData.from_dict(data)
                else:
                    # Yeni gün, sıfırla
                    logger.info("Yeni gün, odak verileri sıfırlandı")
                    return FocusData(date=today)
                    
            except Exception as e:
                logger.warning(f"Odak verileri yüklenemedi: {e}")
        
        return FocusData(date=today)
    
    def _save(self) -> None:
        """Verileri kaydet"""
        try:
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(self.data.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Odak verileri kaydedilemedi: {e}")
    
    def add_distraction(self, seconds: int, keyword: Optional[str] = None) -> Optional[FocusWarning]:
        """Dikkat dağıtıcı süre ekle"""
        # Bugünün verisi mi kontrol et
        today = date.today().isoformat()
        if self.data.date != today:
            self.data = FocusData(date=today)
        
        self.data.distraction_seconds += seconds
        self.data.distraction_count += 1
        self.data.last_distraction = keyword
        
        self._save()
        
        # Uyarı kontrolü
        return self._check_warnings()
    
    def _check_warnings(self) -> Optional[FocusWarning]:
        """Uyarı gerekip gerekmediğini kontrol et"""
        used = self.data.distraction_seconds
        remaining = self.daily_limit - used
        
        # Limit aşıldı
        if remaining <= 0:
            return FocusWarning(
                warning_type="limit",
                message=f"⛔ Günlük dikkat dağıtıcı limitiniz doldu! ({self.format_duration(used)})",
                urgency="critical",
                keyword=self.data.last_distraction
            )
        
        # %80 üzeri kullanıldı
        if used / self.daily_limit > 0.8:
            return FocusWarning(
                warning_type="time",
                message=f"⚠️ Dikkat! Kalan süre: {self.format_duration(remaining)}",
                urgency="normal",
                keyword=self.data.last_distraction
            )
        
        # Eşik aşıldı (ardışık dikkat dağıtıcı)
        if self.data.distraction_count >= self.threshold:
            return FocusWarning(
                warning_type="distraction",
                message=f"🔔 Odaklan! {self.data.distraction_count} kez dikkat dağıtıcı tespit edildi.",
                urgency="low",
                keyword=self.data.last_distraction
            )
        
        return None
    
    def start_focus_session(self) -> None:
        """Yeni odak oturumu başlat"""
        self.data.focus_sessions += 1
        self.data.distraction_count = 0  # Sayacı sıfırla
        self._save()
        logger.info(f"Odak oturumu #{self.data.focus_sessions} başladı")
    
    def get_stats(self) -> dict:
        """Günlük istatistikler"""
        used = self.data.distraction_seconds
        remaining = max(0, self.daily_limit - used)
        percentage = min(100, (used / self.daily_limit) * 100) if self.daily_limit > 0 else 0
        
        return {
            "date": self.data.date,
            "used_seconds": used,
            "used_formatted": self.format_duration(used),
            "remaining_seconds": remaining,
            "remaining_formatted": self.format_duration(remaining),
            "percentage": round(percentage, 1),
            "distraction_count": self.data.distraction_count,
            "focus_sessions": self.data.focus_sessions,
            "limit_reached": remaining <= 0
        }
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Saniyeyi okunabilir formata çevir"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}dk {secs}s" if secs else f"{minutes}dk"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}sa {minutes}dk" if minutes else f"{hours}sa"
    
    def reset_daily(self) -> None:
        """Günlük verileri sıfırla"""
        today = date.today().isoformat()
        self.data = FocusData(date=today)
        self._save()
        logger.info("Günlük odak verileri sıfırlandı")


# Singleton instance
_tracker: Optional[FocusTracker] = None


def get_focus_tracker(
    data_path: Path,
    daily_limit: int = 1800,
    threshold: int = 3
) -> FocusTracker:
    """Singleton tracker instance döndür"""
    global _tracker
    if _tracker is None:
        _tracker = FocusTracker(data_path, daily_limit, threshold)
    return _tracker


if __name__ == "__main__":
    # Test
    from pathlib import Path
    
    test_path = Path("test_focus.json")
    
    print("=== Odak Takip Testi ===")
    
    tracker = FocusTracker(
        data_path=test_path,
        daily_limit_seconds=300,  # 5 dakika test için
        distraction_threshold=2
    )
    
    # Dikkat dağıtıcı ekle
    print("\n1. İlk dikkat dağıtıcı (60s):")
    warning = tracker.add_distraction(60, "youtube")
    print(f"   Uyarı: {warning.message if warning else 'Yok'}")
    
    print("\n2. İkinci dikkat dağıtıcı (60s):")
    warning = tracker.add_distraction(60, "twitter")
    print(f"   Uyarı: {warning.message if warning else 'Yok'}")
    
    print("\n3. Üçüncü dikkat dağıtıcı (120s):")
    warning = tracker.add_distraction(120, "netflix")
    print(f"   Uyarı: {warning.message if warning else 'Yok'}")
    
    # İstatistikler
    print("\n📊 İstatistikler:")
    stats = tracker.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Temizle
    test_path.unlink(missing_ok=True)
    print("\n✓ Test tamamlandı!")



