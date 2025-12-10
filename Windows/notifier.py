"""
HyprContext Windows - Bildirim Modülü
Windows bildirimlerini yönetir.
"""

import ctypes
import subprocess
import winsound
from enum import Enum
from typing import Optional

from loguru import logger

# Windows API sabitler
MB_OK = 0x00000000
MB_ICONWARNING = 0x00000030
MB_ICONERROR = 0x00000010
MB_ICONINFORMATION = 0x00000040


class Urgency(Enum):
    """Bildirim aciliyeti"""
    LOW = "low"
    NORMAL = "normal"
    CRITICAL = "critical"


def send_toast_notification(
    title: str,
    message: str,
    urgency: Urgency = Urgency.NORMAL,
    duration: str = "short"
) -> bool:
    """
    Windows Toast bildirimi gönder.
    win10toast veya PowerShell kullanır.
    """
    try:
        # Önce win10toast dene
        try:
            from win10toast import ToastNotifier
            
            toaster = ToastNotifier()
            toaster.show_toast(
                title=title,
                msg=message,
                duration=5 if duration == "short" else 10,
                threaded=True
            )
            logger.debug(f"Toast bildirimi gönderildi: {title}")
            return True
        except ImportError:
            pass
        
        # Fallback: PowerShell
        ps_script = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

        $template = @"
        <toast>
            <visual>
                <binding template="ToastText02">
                    <text id="1">{title}</text>
                    <text id="2">{message}</text>
                </binding>
            </visual>
        </toast>
"@

        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("HyprContext").Show($toast)
        '''
        
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        logger.debug(f"PowerShell bildirimi gönderildi: {title}")
        return True
        
    except Exception as e:
        logger.warning(f"Bildirim gönderilemedi: {e}")
        # Son çare: MessageBox
        return show_message_box(title, message, urgency)


def show_message_box(
    title: str,
    message: str,
    urgency: Urgency = Urgency.NORMAL
) -> bool:
    """Windows MessageBox göster"""
    try:
        icon = {
            Urgency.LOW: MB_ICONINFORMATION,
            Urgency.NORMAL: MB_ICONWARNING,
            Urgency.CRITICAL: MB_ICONERROR
        }.get(urgency, MB_ICONINFORMATION)
        
        ctypes.windll.user32.MessageBoxW(0, message, title, MB_OK | icon)
        return True
    except Exception as e:
        logger.error(f"MessageBox gösterilemedi: {e}")
        return False


def play_sound(sound_type: str = "info") -> None:
    """
    Sistem sesi çal.
    sound_type: "info", "warning", "error", "beep"
    """
    try:
        sounds = {
            "info": winsound.MB_ICONASTERISK,
            "warning": winsound.MB_ICONEXCLAMATION,
            "error": winsound.MB_ICONHAND,
            "beep": winsound.MB_OK
        }
        
        sound = sounds.get(sound_type, winsound.MB_OK)
        winsound.MessageBeep(sound)
    except Exception as e:
        logger.warning(f"Ses çalınamadı: {e}")


def speak_text(text: str) -> bool:
    """
    Windows TTS ile metin oku.
    """
    try:
        ps_script = f'''
        Add-Type -AssemblyName System.Speech
        $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $synth.Rate = 1
        $synth.Speak("{text}")
        '''
        
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True
    except Exception as e:
        logger.warning(f"TTS başarısız: {e}")
        return False


# Önceden tanımlı bildirim fonksiyonları

def send_focus_warning(keyword: str) -> None:
    """Dikkat dağıtıcı uyarısı"""
    send_toast_notification(
        title="🔔 Dikkat Dağıtıcı Tespit Edildi",
        message=f"'{keyword}' tespit edildi. Odaklanmaya devam!",
        urgency=Urgency.LOW
    )
    play_sound("info")


def send_time_warning(remaining: str) -> None:
    """Süre uyarısı"""
    send_toast_notification(
        title="⚠️ Süre Uyarısı",
        message=f"Dikkat dağıtıcı limitinize yaklaşıyorsunuz. Kalan: {remaining}",
        urgency=Urgency.NORMAL
    )
    play_sound("warning")


def send_limit_warning() -> None:
    """Limit aşım uyarısı"""
    send_toast_notification(
        title="⛔ Limit Doldu",
        message="Günlük dikkat dağıtıcı limitiniz doldu!",
        urgency=Urgency.CRITICAL,
        duration="long"
    )
    play_sound("error")
    # Sesli uyarı
    speak_text("Dikkat! Günlük limitiniz doldu.")


def send_startup_notification() -> None:
    """Başlangıç bildirimi"""
    send_toast_notification(
        title="🚀 HyprContext Aktif",
        message="Ekran aktivitesi izleniyor...",
        urgency=Urgency.LOW
    )


def send_analysis_notification(summary: str) -> None:
    """Analiz bildirimi"""
    # Çok uzunsa kısalt
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    send_toast_notification(
        title="📝 Aktivite Kaydedildi",
        message=summary,
        urgency=Urgency.LOW
    )


def handle_focus_warning(warning) -> None:
    """FocusWarning nesnesini işle"""
    from focus import FocusWarning
    
    if not isinstance(warning, FocusWarning):
        return
    
    if warning.warning_type == "limit":
        send_limit_warning()
    elif warning.warning_type == "time":
        send_time_warning(warning.message.split("Kalan: ")[-1] if "Kalan: " in warning.message else "az")
    elif warning.warning_type == "distraction":
        if warning.keyword:
            send_focus_warning(warning.keyword)


if __name__ == "__main__":
    # Test
    print("=== Bildirim Testi ===")
    
    print("\n1. Toast bildirimi...")
    send_toast_notification(
        title="Test Bildirimi",
        message="Bu bir test mesajıdır.",
        urgency=Urgency.NORMAL
    )
    
    print("\n2. Ses çalma...")
    play_sound("info")
    
    print("\n3. Başlangıç bildirimi...")
    send_startup_notification()
    
    print("\n✓ Test tamamlandı!")



