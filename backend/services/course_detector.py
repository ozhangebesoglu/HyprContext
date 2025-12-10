"""
Course Detector Service
~~~~~~~~~~~~~~~~~~~~~~~

Otomatik kurs/eğitim tespiti.
Pencere başlığından Udemy, Coursera vb. platformları algılar.
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta

from ..interfaces.capture import IWindowCapture, WindowInfo
from ..interfaces.notification import INotification, NotificationMessage, NotificationPriority

logger = logging.getLogger(__name__)


@dataclass
class DetectedCourse:
    """Tespit edilen kurs bilgisi."""
    name: str
    platform: str
    window_title: str
    detected_at: datetime


class CourseDetectorService:
    """Kurs tespit servisi."""
    
    # Platform tanımlayıcıları
    PLATFORMS = {
        "udemy": {
            "patterns": [r"udemy", r"udemy\.com"],
            "title_extract": r"(.+?)\s*[-|]\s*Udemy",
            "name": "Udemy"
        },
        "coursera": {
            "patterns": [r"coursera", r"coursera\.org"],
            "title_extract": r"(.+?)\s*[-|]\s*Coursera",
            "name": "Coursera"
        },
        "scrimba": {
            "patterns": [r"scrimba", r"scrimba\.com"],
            "title_extract": r"(.+?)\s*[-|]\s*Scrimba",
            "name": "Scrimba"
        },
        "youtube_learning": {
            "patterns": [r"youtube.*tutorial", r"youtube.*course", r"youtube.*learn"],
            "title_extract": r"(.+?)\s*[-|]\s*YouTube",
            "name": "YouTube"
        },
        "pluralsight": {
            "patterns": [r"pluralsight"],
            "title_extract": r"(.+?)\s*[-|]\s*Pluralsight",
            "name": "Pluralsight"
        },
        "codecademy": {
            "patterns": [r"codecademy"],
            "title_extract": r"(.+?)\s*[-|]\s*Codecademy",
            "name": "Codecademy"
        },
        "freecodecamp": {
            "patterns": [r"freecodecamp", r"fcc"],
            "title_extract": r"(.+?)\s*[-|]\s*freeCodeCamp",
            "name": "freeCodeCamp"
        },
        "linkedin_learning": {
            "patterns": [r"linkedin.*learning", r"linkedin\.com/learning"],
            "title_extract": r"(.+?)\s*[-|]\s*LinkedIn",
            "name": "LinkedIn Learning"
        }
    }
    
    # Son bildirilen kurslar (tekrar bildirimi önlemek için)
    _notified_courses: dict[str, datetime] = {}
    NOTIFICATION_COOLDOWN = timedelta(hours=1)
    
    def __init__(
        self,
        window_capture: IWindowCapture,
        notification: Optional[INotification] = None
    ):
        """
        Args:
            window_capture: Pencere bilgisi servisi
            notification: Bildirim servisi (opsiyonel)
        """
        self.window_capture = window_capture
        self.notification = notification
    
    def detect_course(self) -> Optional[DetectedCourse]:
        """Aktif pencereden kurs tespit et.
        
        Returns:
            DetectedCourse veya None
        """
        # Aktif pencereyi al
        active_window = self.window_capture.get_active_window()
        if not active_window:
            return None
        
        return self._detect_from_window(active_window)
    
    def detect_course_from_all_windows(self) -> list[DetectedCourse]:
        """Tüm pencerelerden kurs tespit et.
        
        Returns:
            Tespit edilen kurslar listesi
        """
        windows = self.window_capture.get_all_windows()
        courses = []
        
        for window in windows:
            course = self._detect_from_window(window)
            if course:
                courses.append(course)
        
        return courses
    
    def _detect_from_window(self, window: WindowInfo) -> Optional[DetectedCourse]:
        """Pencere bilgisinden kurs tespit et."""
        text = f"{window.app_class} {window.title}".lower()
        
        for platform_id, config in self.PLATFORMS.items():
            # Pattern eşleşmesi kontrol et
            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    # Kurs adını çıkar
                    course_name = self._extract_course_name(
                        window.title, 
                        config["title_extract"]
                    )
                    
                    if course_name:
                        return DetectedCourse(
                            name=course_name,
                            platform=config["name"],
                            window_title=window.title,
                            detected_at=datetime.now()
                        )
        
        return None
    
    def _extract_course_name(self, title: str, pattern: str) -> Optional[str]:
        """Başlıktan kurs adını çıkar."""
        match = re.search(pattern, title, re.IGNORECASE)
        
        if match:
            name = match.group(1).strip()
            # Çok kısa veya çok uzun isimleri filtrele
            if 3 <= len(name) <= 100:
                return name
        
        # Pattern eşleşmezse başlığı temizleyerek döndür
        # "-" veya "|" ile ayrılmış ilk kısmı al
        parts = re.split(r'\s*[-|]\s*', title)
        if parts and 3 <= len(parts[0]) <= 100:
            return parts[0].strip()
        
        return None
    
    def should_notify(self, course: DetectedCourse) -> bool:
        """Bu kurs için bildirim gönderilmeli mi?
        
        Aynı kurs için kısa sürede tekrar bildirim göndermez.
        """
        course_key = f"{course.platform}:{course.name}"
        
        if course_key in self._notified_courses:
            last_notified = self._notified_courses[course_key]
            if datetime.now() - last_notified < self.NOTIFICATION_COOLDOWN:
                return False
        
        return True
    
    def send_course_notification(self, course: DetectedCourse) -> bool:
        """Kurs tespit bildirimi gönder.
        
        Args:
            course: Tespit edilen kurs
            
        Returns:
            Bildirim gönderildi mi
        """
        if not self.notification:
            return False
        
        if not self.should_notify(course):
            logger.debug(f"Kurs bildirimi atlandı (cooldown): {course.name}")
            return False
        
        message = NotificationMessage(
            title="📚 Kurs Tespit Edildi",
            body=f"'{course.name}' kursunu ({course.platform}) profilinize eklemek ister misiniz?",
            priority=NotificationPriority.NORMAL,
            sound=False
        )
        
        success = self.notification.send(message)
        
        if success:
            course_key = f"{course.platform}:{course.name}"
            self._notified_courses[course_key] = datetime.now()
            logger.info(f"Kurs bildirimi gönderildi: {course.name} ({course.platform})")
        
        return success
    
    def clear_notification_cache(self) -> None:
        """Bildirim önbelleğini temizle."""
        self._notified_courses.clear()
