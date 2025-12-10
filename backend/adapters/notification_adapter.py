"""
Notification Adapters
~~~~~~~~~~~~~~~~~~~~~

Bildirim sistemi implementasyonları.
Liskov Substitution: Tüm bildirim türleri INotification'ı implement eder.
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass

from ..interfaces.notification import INotification, NotificationMessage, NotificationPriority

logger = logging.getLogger(__name__)


@dataclass
class InteractiveNotification:
    """İnteraktif bildirim (action butonları ile)."""
    title: str
    body: str
    actions: list[tuple[str, str]]  # [(action_id, label), ...]
    callback: Optional[Callable[[str], None]] = None


class DesktopNotification(INotification):
    """Linux masaüstü bildirimi (notify-send / dunstify)."""
    
    def __init__(self):
        self._has_dunst = self._check_dunst()
    
    def send(self, message: NotificationMessage) -> bool:
        """Masaüstü bildirimi gönder."""
        try:
            # Önceliğe göre urgency belirle
            urgency_map = {
                NotificationPriority.LOW: "low",
                NotificationPriority.NORMAL: "normal",
                NotificationPriority.HIGH: "normal",
                NotificationPriority.CRITICAL: "critical"
            }
            urgency = urgency_map.get(message.priority, "normal")
            
            cmd = [
                "notify-send",
                "-u", urgency,
                "-t", "5000",  # 5 saniye
                message.title,
                message.body
            ]
            
            if message.icon:
                cmd.extend(["-i", message.icon])
            
            subprocess.run(cmd, check=False)
            
            # Ses çal
            if message.sound:
                self._play_sound(message.priority)
            
            return True
            
        except FileNotFoundError:
            logger.warning("notify-send bulunamadı")
            return False
        except Exception as e:
            logger.error(f"Bildirim hatası: {e}")
            return False
    
    def send_interactive(
        self, 
        notification: InteractiveNotification,
        timeout: int = 30000  # 30 saniye
    ) -> Optional[str]:
        """İnteraktif bildirim gönder ve yanıtı al.
        
        Args:
            notification: İnteraktif bildirim
            timeout: Bekleme süresi (ms)
            
        Returns:
            Tıklanan action_id veya None (timeout/kapatıldı)
        """
        if self._has_dunst:
            return self._send_dunst_interactive(notification, timeout)
        else:
            # Dunst yoksa normal bildirim gönder
            self.send(NotificationMessage(
                title=notification.title,
                body=notification.body,
                priority=NotificationPriority.NORMAL
            ))
            return None
    
    def _send_dunst_interactive(
        self, 
        notification: InteractiveNotification,
        timeout: int
    ) -> Optional[str]:
        """Dunstify ile interaktif bildirim gönder."""
        try:
            cmd = [
                "dunstify",
                "-t", str(timeout),
                "-u", "normal",
            ]
            
            # Action'ları ekle
            for action_id, label in notification.actions:
                cmd.extend(["-A", f"{action_id},{label}"])
            
            cmd.extend([notification.title, notification.body])
            
            # Senkron çalıştır ve yanıtı al
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout // 1000 + 5  # Saniyeye çevir + buffer
            )
            
            action = result.stdout.strip()
            
            if action and notification.callback:
                notification.callback(action)
            
            return action if action else None
            
        except subprocess.TimeoutExpired:
            logger.debug("İnteraktif bildirim timeout")
            return None
        except Exception as e:
            logger.error(f"Dunstify hatası: {e}")
            return None
    
    def is_available(self) -> bool:
        """notify-send mevcut mu?"""
        try:
            subprocess.run(
                ["which", "notify-send"],
                capture_output=True,
                check=True
            )
            return True
        except Exception:
            return False
    
    def _check_dunst(self) -> bool:
        """dunstify mevcut mu?"""
        try:
            subprocess.run(
                ["which", "dunstify"],
                capture_output=True,
                check=True
            )
            return True
        except Exception:
            return False
    
    def _play_sound(self, priority: NotificationPriority) -> None:
        """Bildirim sesi çal."""
        try:
            if priority == NotificationPriority.CRITICAL:
                sound_file = "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"
            else:
                sound_file = "/usr/share/sounds/freedesktop/stereo/message.oga"
            
            subprocess.Popen(
                ["paplay", sound_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass  # Ses yoksa sessizce geç


class TTSNotification(INotification):
    """Sesli uyarı (Text-to-Speech)."""
    
    def __init__(self, voice: str = "tr-TR-AhmetNeural"):
        """
        Args:
            voice: Edge TTS ses adı
        """
        self.voice = voice
    
    def send(self, message: NotificationMessage) -> bool:
        """Sesli uyarı gönder."""
        try:
            # edge-tts ile ses oluştur ve çal
            text = message.body
            
            subprocess.Popen(
                f'edge-tts --voice {self.voice} --text "{text}" --write-media /tmp/tts_warning.mp3 && '
                f'mpv --no-video --really-quiet /tmp/tts_warning.mp3',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            return True
            
        except Exception as e:
            logger.error(f"TTS hatası: {e}")
            return False
    
    def is_available(self) -> bool:
        """edge-tts ve mpv mevcut mu?"""
        try:
            subprocess.run(["which", "edge-tts"], capture_output=True, check=True)
            subprocess.run(["which", "mpv"], capture_output=True, check=True)
            return True
        except Exception:
            return False


class CompositeNotification(INotification):
    """Birden fazla bildirim türünü birleştir.
    
    Örnek: Hem masaüstü bildirimi hem sesli uyarı gönder.
    """
    
    def __init__(self, notifications: list[INotification]):
        """
        Args:
            notifications: Bildirim servisleri listesi
        """
        self.notifications = notifications
    
    def send(self, message: NotificationMessage) -> bool:
        """Tüm bildirim servislerine gönder."""
        results = []
        for notification in self.notifications:
            try:
                results.append(notification.send(message))
            except Exception as e:
                logger.error(f"Bildirim hatası: {e}")
                results.append(False)
        
        return any(results)  # En az biri başarılı olduysa True
    
    def is_available(self) -> bool:
        """En az bir servis mevcut mu?"""
        return any(n.is_available() for n in self.notifications)
