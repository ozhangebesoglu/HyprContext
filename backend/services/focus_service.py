"""
Focus Service
~~~~~~~~~~~~~

Odak takip servisi.
Single Responsibility: Sadece odak takibi.
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional

from ..interfaces.capture import IWindowCapture
from ..interfaces.notification import INotification, NotificationMessage, NotificationPriority
from ..models.focus import FocusData, FocusStats

logger = logging.getLogger(__name__)


class FocusService:
    """Odak takip servisi."""
    
    # Uyarı eşikleri (saniye, etiket, sesli mi)
    WARNING_THRESHOLDS = [
        (900, "15 dakika", False),    # 15 dk
        (1800, "30 dakika", False),   # 30 dk
        (3600, "1 saat", True),       # 60 dk - SESLİ
        (5400, "1.5 saat", False),    # 90 dk
        (7200, "2 saat", True),       # 120 dk - SESLİ + LİMİT
    ]
    
    def __init__(
        self,
        window_capture: IWindowCapture,
        notification: INotification,
        banned_keywords: list[str],
        daily_limit_seconds: int = 7200,
        data_file: Optional[Path] = None
    ):
        """
        Args:
            window_capture: Pencere bilgisi servisi (DIP)
            notification: Bildirim servisi (DIP)
            banned_keywords: Yasaklı kelimeler listesi
            daily_limit_seconds: Günlük limit (saniye)
            data_file: Veri dosyası yolu
        """
        self.window_capture = window_capture
        self.notification = notification
        self.banned_keywords = [k.lower() for k in banned_keywords]
        self.daily_limit_seconds = daily_limit_seconds
        self.data_file = data_file or Path("focus_data.json")
        
        self._last_warning_threshold = 0
    
    def check_distraction(self) -> tuple[bool, Optional[str]]:
        """Yasaklı uygulama kontrolü yap.
        
        Returns:
            (is_distracted, found_keyword): Dikkat dağıldı mı ve hangi kelime
        """
        # Aktif pencereyi kontrol et
        active = self.window_capture.get_active_window()
        if active:
            text = f"{active.app_class} {active.title}".lower()
            for keyword in self.banned_keywords:
                if keyword in text:
                    return True, keyword
        
        # Tüm pencereleri kontrol et
        all_windows = self.window_capture.get_all_windows()
        for window in all_windows:
            text = f"{window.app_class} {window.title}".lower()
            for keyword in self.banned_keywords:
                if keyword in text:
                    return True, keyword
        
        return False, None
    
    def get_today_data(self) -> FocusData:
        """Bugünün odak verisini al."""
        today = date.today()
        all_data = self._load_data()
        
        today_key = today.isoformat()
        if today_key in all_data:
            return FocusData.from_dict({"date": today, **all_data[today_key]})
        
        return FocusData(date=today)
    
    def get_stats(self) -> FocusStats:
        """Odak istatistiklerini al."""
        return FocusStats(
            today=self.get_today_data(),
            daily_limit_seconds=self.daily_limit_seconds
        )
    
    def increment_distraction(self, seconds: int = 1) -> FocusData:
        """Dikkat dağınıklığı süresini artır.
        
        Args:
            seconds: Eklenecek saniye
            
        Returns:
            Güncellenmiş FocusData
        """
        data = self.get_today_data()
        data.distraction_seconds += seconds
        self._save_today(data)
        return data
    
    # Limit aşıldıktan sonra tekrar uyarı aralığı (saniye)
    OVERTIME_WARNING_INTERVAL = 300  # 5 dakika
    
    def check_and_warn(self, data: FocusData) -> bool:
        """Eşik kontrolü yap ve gerekirse uyarı gönder.
        
        Args:
            data: Güncel odak verisi
            
        Returns:
            Uyarı gönderildi mi
        """
        used = data.distraction_seconds
        remaining = max(0, self.daily_limit_seconds - used)
        
        # Eşik bazlı uyarılar
        for threshold, label, is_voice in self.WARNING_THRESHOLDS:
            if used >= threshold and threshold > self._last_warning_threshold:
                self._last_warning_threshold = threshold
                data.warnings_sent.append(threshold)
                
                if threshold >= self.daily_limit_seconds:
                    # Limit doldu
                    data.limit_reached = True
                    self._send_warning(
                        title="🛑 GÜNLÜK LİMİT DOLDU!",
                        body=f"Yasaklı uygulamalarda {label} geçirdin!\nBugünlük yeter, işine dön!",
                        priority=NotificationPriority.CRITICAL
                    )
                else:
                    # Normal uyarı
                    self._send_warning(
                        title="⏰ Dikkat Dağınıklığı Uyarısı",
                        body=f"Yasaklı uygulamalarda {label} geçirdin.\nKalan: {self._format_duration(remaining)}",
                        priority=NotificationPriority.HIGH if is_voice else NotificationPriority.NORMAL
                    )
                
                self._save_today(data)
                return True
        
        # Limit aşıldıktan sonra her 5 dakikada bir uyar
        if data.limit_reached and used > self.daily_limit_seconds:
            overtime = used - self.daily_limit_seconds
            if overtime > 0 and overtime % self.OVERTIME_WARNING_INTERVAL == 0:
                overtime_minutes = overtime // 60
                self._send_warning(
                    title="🛑 LİMİT AŞILDI!",
                    body=f"Bugün toplam {self._format_duration(used)} harcadın.\nLimiti {overtime_minutes} dakika aştın!\nHemen işine dön!",
                    priority=NotificationPriority.CRITICAL
                )
                logger.warning(f"Limit aşım uyarısı: +{overtime_minutes} dakika")
                return True
        
        return False
    
    def reset_daily_warnings(self) -> None:
        """Günlük uyarı sayacını sıfırla."""
        self._last_warning_threshold = 0
    
    def _send_warning(self, title: str, body: str, priority: NotificationPriority) -> None:
        """Uyarı gönder."""
        message = NotificationMessage(
            title=title,
            body=body,
            priority=priority,
            sound=True
        )
        self.notification.send(message)
    
    def _load_data(self) -> dict:
        """Tüm veriyi yükle."""
        if not self.data_file.exists():
            return {}
        
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_today(self, data: FocusData) -> None:
        """Bugünün verisini kaydet."""
        all_data = self._load_data()
        all_data[data.date.isoformat()] = {
            "distraction_seconds": data.distraction_seconds,
            "warnings_sent": data.warnings_sent,
            "limit_reached": data.limit_reached
        }
        
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Veri kaydetme hatası: {e}")
    
    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Süreyi formatla."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}s {minutes}dk"
        return f"{minutes}dk"
