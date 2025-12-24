"""
Windows Screenshot Adapter
~~~~~~~~~~~~~~~~~~~~~~~~~~

Windows için mss + PIL ile ekran görüntüsü alma.
"""

import base64
import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

from ..interfaces.capture import IScreenshotCapture, CaptureResult

logger = logging.getLogger(__name__)

# Conditional imports for Windows
try:
    import mss
    from PIL import Image
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    mss = None
    Image = None


class WindowsScreenshotAdapter(IScreenshotCapture):
    """mss ile ekran görüntüsü alma (Windows)."""

    def __init__(self, screenshots_dir: str):
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self._sct = None

        if MSS_AVAILABLE:
            self._sct = mss.mss()

    def _get_screenshot_path(self) -> Path:
        """Timestamp'li screenshot dosya yolu oluştur."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.screenshots_dir / f"screenshot_{timestamp}.png"

    def capture(self) -> CaptureResult:
        """Ekran görüntüsü al.

        Returns:
            CaptureResult: Screenshot verisi (base64) veya hata
        """
        if not MSS_AVAILABLE:
            return CaptureResult(
                success=False,
                error_message="mss veya PIL kütüphanesi yüklü değil. 'pip install mss Pillow'",
                error_type="MSS_NOT_INSTALLED"
            )

        if self._sct is None:
            return CaptureResult(
                success=False,
                error_message="mss başlatılamadı",
                error_type="MSS_INIT_ERROR"
            )

        screenshot_path = self._get_screenshot_path()

        try:
            # Ana monitörden screenshot al (index 1, 0 tüm ekranlar)
            monitor = self._sct.monitors[1]
            screenshot = self._sct.grab(monitor)

            # PIL Image'e dönüştür
            img = Image.frombytes(
                "RGB",
                screenshot.size,
                screenshot.bgra,
                "raw",
                "BGRX"
            )

            # PNG olarak dosyaya kaydet
            img.save(str(screenshot_path), "PNG", optimize=True)

            # Dosya boyutu kontrolü
            file_size = screenshot_path.stat().st_size
            if file_size < 1000:
                return CaptureResult(
                    success=False,
                    error_message=f"Dosya boyutu çok küçük ({file_size} bytes)",
                    error_type="INVALID_SCREENSHOT"
                )

            # JPEG olarak base64'e çevir (daha küçük boyut)
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            buffer.seek(0)
            screenshot_data = base64.b64encode(buffer.read())

            logger.debug(f"Screenshot kaydedildi: {screenshot_path}")

            return CaptureResult(
                success=True,
                data=screenshot_data,
                screenshot_path=str(screenshot_path)
            )

        except Exception as e:
            logger.error(f"Windows screenshot hatası: {e}")
            return CaptureResult(
                success=False,
                error_message=f"Screenshot hatası: {str(e)}",
                error_type="MSS_ERROR"
            )

    def __del__(self):
        """Cleanup."""
        if self._sct is not None:
            try:
                self._sct.close()
            except Exception:
                pass
