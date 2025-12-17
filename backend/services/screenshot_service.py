"""
Screenshot Service
~~~~~~~~~~~~~~~~~~

Ekran görüntüsü alma servisi.
Single Responsibility: Sadece screenshot alma.
"""

import base64
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..interfaces.capture import IScreenshotCapture, CaptureResult
from ..core.config import get_settings

logger = logging.getLogger(__name__)


class ScreenshotService(IScreenshotCapture):
    """Grim ile ekran görüntüsü alma servisi."""
    
    def __init__(self, screenshots_dir: Optional[str] = None):
        settings = get_settings()
        self.screenshots_dir = Path(screenshots_dir or settings.screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_screenshot_path(self) -> Path:
        """Timestamp'li screenshot dosya yolu oluştur."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.screenshots_dir / f"screenshot_{timestamp}.png"
    
    def capture(self) -> CaptureResult:
        """Ekran görüntüsü al.
        
        Returns:
            CaptureResult: Screenshot verisi (base64) veya hata
        """
        screenshot_path = self._get_screenshot_path()
        
        try:
            # grim ile screenshot al
            result = subprocess.run(
                ["grim", str(screenshot_path)],
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
            
            if not screenshot_path.exists():
                return CaptureResult(
                    success=False,
                    error_message=f"grim çalıştı ama dosya oluşmadı. Yol: {screenshot_path}",
                    error_type="FILE_NOT_CREATED"
                )
            
            # Dosya boyutu kontrolü
            file_size = screenshot_path.stat().st_size
            if file_size < 1000:
                return CaptureResult(
                    success=False,
                    error_message=f"Dosya boyutu çok küçük ({file_size} bytes)",
                    error_type="INVALID_SCREENSHOT"
                )
            
            # Base64'e çevir
            with open(screenshot_path, "rb") as f:
                screenshot_data = base64.b64encode(f.read())
            
            return CaptureResult(
                success=True,
                data=screenshot_data,
                screenshot_path=str(screenshot_path)
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
