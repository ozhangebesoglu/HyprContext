"""
Windows Notification Adapter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Windows için toast bildirimleri ve sesli uyarılar.
"""

import logging
import subprocess
from typing import Optional

from ..interfaces.notification import INotification, NotificationMessage, NotificationPriority

logger = logging.getLogger(__name__)

# Conditional imports for Windows
try:
    import ctypes
    CTYPES_AVAILABLE = True
except ImportError:
    CTYPES_AVAILABLE = False
    ctypes = None

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False
    winsound = None

try:
    from win10toast import ToastNotifier
    WIN10TOAST_AVAILABLE = True
except ImportError:
    WIN10TOAST_AVAILABLE = False
    ToastNotifier = None


class WindowsNotification(INotification):
    """Windows toast bildirimi ve sesli uyarı."""

    def __init__(self):
        self._toaster = None
        if WIN10TOAST_AVAILABLE and ToastNotifier:
            try:
                self._toaster = ToastNotifier()
            except Exception as e:
                logger.warning(f"win10toast başlatılamadı: {e}")

    def send(self, message: NotificationMessage) -> bool:
        """Windows bildirimi gönder.

        Args:
            message: Bildirim mesajı

        Returns:
            bool: Başarılı mı
        """
        success = False

        # Önceliğe göre ses çal
        if message.priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL]:
            self._play_sound(message.priority)

        # Toast bildirimi gönder
        if self._toaster:
            success = self._send_toast(message)
        else:
            success = self._send_powershell_toast(message)

        # Kritik uyarılarda TTS kullan
        if message.priority == NotificationPriority.CRITICAL:
            self._speak(message.body)

        return success

    def is_available(self) -> bool:
        """Bildirim sistemi kullanılabilir mi?"""
        return True  # Windows'ta her zaman en az bir yöntem var

    def _send_toast(self, message: NotificationMessage) -> bool:
        """win10toast ile bildirim gönder."""
        if not self._toaster:
            return False
        try:
            self._toaster.show_toast(
                title=message.title,
                msg=message.body,
                duration=5,
                threaded=True
            )
            return True
        except Exception as e:
            logger.warning(f"Toast hatası: {e}")
            return False

    def _send_powershell_toast(self, message: NotificationMessage) -> bool:
        """PowerShell ile toast bildirimi gönder."""
        try:
            # PowerShell script
            ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$template = @"
<toast><visual><binding template="ToastText02">
<text id="1">{message.title}</text>
<text id="2">{message.body}</text>
</binding></visual></toast>
"@
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("HyprContext").Show($toast)
'''
            # subprocess için Windows-specific flags
            creationflags = 0
            try:
                creationflags = subprocess.CREATE_NO_WINDOW
            except AttributeError:
                pass

            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                creationflags=creationflags,
                timeout=10
            )
            return True
        except Exception as e:
            logger.warning(f"PowerShell toast hatası: {e}")
            return self._show_message_box(message)

    def _show_message_box(self, message: NotificationMessage) -> bool:
        """Windows MessageBox göster (fallback)."""
        if not CTYPES_AVAILABLE:
            return False
        try:
            MB_OK = 0x00000000
            MB_ICONWARNING = 0x00000030
            MB_ICONERROR = 0x00000010

            icon = MB_ICONWARNING
            if message.priority == NotificationPriority.CRITICAL:
                icon = MB_ICONERROR

            ctypes.windll.user32.MessageBoxW(
                0,
                message.body,
                message.title,
                MB_OK | icon
            )
            return True
        except Exception as e:
            logger.error(f"MessageBox hatası: {e}")
            return False

    def _play_sound(self, priority: NotificationPriority) -> None:
        """Windows sistem sesi çal."""
        if not WINSOUND_AVAILABLE:
            return
        try:
            if priority == NotificationPriority.CRITICAL:
                winsound.MessageBeep(winsound.MB_ICONHAND)
            else:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

    def _speak(self, text: str) -> None:
        """Windows TTS ile sesli okuma."""
        try:
            # PowerShell TTS
            ps_script = f'''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = 2
$synth.Speak("{text[:100]}")
'''
            creationflags = 0
            try:
                creationflags = subprocess.CREATE_NO_WINDOW
            except AttributeError:
                pass

            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                creationflags=creationflags,
                timeout=15
            )
        except Exception as e:
            logger.warning(f"TTS hatası: {e}")
