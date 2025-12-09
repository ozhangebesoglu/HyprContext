"""
Screenshot Service
~~~~~~~~~~~~~~~~~~

Ekran görüntüsü alma servisi.
Single Responsibility: Sadece screenshot alma.
"""

import base64
import subprocess
import logging
from pathlib import Path
from typing import Optional

from ..interfaces.capture import IScreenshotCapture, CaptureResult

logger = logging.getLogger(__name__)


class ScreenshotService(IScreenshotCapture):
    """Grim ile ekran görüntüsü alma servisi."""
    
    def __init__(self, temp_path: str = "/tmp/hyprcontext_screenshot.png"):
        self.temp_path = Path(temp_path)
    
    def capture(self) -> CaptureResult:
        """Ekran görüntüsü al.
        
        Returns:
            CaptureResult: Screenshot verisi (base64) veya hata
        """
        try:
            # grim ile screenshot al
            result = subprocess.run(
                ["grim", str(self.temp_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return CaptureResult(
                    success=False,
                    error_message=f"grim komutu başarısız. Exit code: {result.returncode}. Stderr: {result.stderr}",
                    error_type="GRIM_ERROR"
                )
            
            if not self.temp_path.exists():
                return CaptureResult(
                    success=False,
                    error_message=f"grim çalıştı ama dosya oluşmadı. Yol: {self.temp_path}",
                    error_type="FILE_NOT_CREATED"
                )
            
            # Dosya boyutu kontrolü
            file_size = self.temp_path.stat().st_size
            if file_size < 1000:
                return CaptureResult(
                    success=False,
                    error_message=f"Dosya boyutu çok küçük ({file_size} bytes)",
                    error_type="INVALID_SCREENSHOT"
                )
            
            # Base64'e çevir
            with open(self.temp_path, "rb") as f:
                screenshot_data = base64.b64encode(f.read())
            
            return CaptureResult(
                success=True,
                data=screenshot_data
            )
            
        except FileNotFoundError:
            return CaptureResult(
                success=False,
                error_message="grim bulunamadı. Kurulum: 'sudo pacman -S grim'",
                error_type="GRIM_NOT_FOUND"
            )
        except subprocess.TimeoutExpired:
            return CaptureResult(
                success=False,
                error_message="grim 5 saniye içinde yanıt vermedi",
                error_type="TIMEOUT"
            )
        except Exception as e:
            logger.error(f"Screenshot hatası: {e}")
            return CaptureResult(
                success=False,
                error_message=f"Beklenmeyen hata: {str(e)}",
                error_type="UNKNOWN"
            )
