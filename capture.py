"""
HyprContext Windows - Ekran Görüntüsü Modülü
mss kullanarak hızlı ekran görüntüsü alır.
"""

import base64
from io import BytesIO
from pathlib import Path
from typing import Optional

import mss
from PIL import Image
from loguru import logger


class ScreenCapture:
    """Ekran görüntüsü yöneticisi"""
    
    def __init__(self):
        self.sct = mss.mss()
    
    def capture_primary(self) -> Optional[Image.Image]:
        """Ana monitörden görüntü al"""
        try:
            # Ana monitör (index 1, 0 tüm ekranlar)
            monitor = self.sct.monitors[1]
            screenshot = self.sct.grab(monitor)
            
            # PIL Image'e dönüştür
            img = Image.frombytes(
                "RGB",
                screenshot.size,
                screenshot.bgra,
                "raw",
                "BGRX"
            )
            
            return img
        except Exception as e:
            logger.error(f"Ekran görüntüsü alınamadı: {e}")
            return None
    
    def capture_all_monitors(self) -> Optional[Image.Image]:
        """Tüm monitörlerden görüntü al"""
        try:
            # Tüm monitörler (index 0)
            screenshot = self.sct.grab(self.sct.monitors[0])
            
            img = Image.frombytes(
                "RGB",
                screenshot.size,
                screenshot.bgra,
                "raw",
                "BGRX"
            )
            
            return img
        except Exception as e:
            logger.error(f"Ekran görüntüsü alınamadı: {e}")
            return None
    
    def save_screenshot(self, path: Path, quality: int = 85) -> bool:
        """Ekran görüntüsünü dosyaya kaydet"""
        try:
            img = self.capture_primary()
            if img is None:
                return False
            
            # JPEG olarak kaydet (daha küçük boyut)
            if path.suffix.lower() in [".jpg", ".jpeg"]:
                img.save(str(path), "JPEG", quality=quality, optimize=True)
            else:
                img.save(str(path), "PNG", optimize=True)
            
            logger.debug(f"Screenshot kaydedildi: {path}")
            return True
        except Exception as e:
            logger.error(f"Screenshot kaydedilemedi: {e}")
            return False
    
    def to_base64(self, format: str = "JPEG", quality: int = 85) -> Optional[str]:
        """Ekran görüntüsünü base64 string olarak döndür"""
        try:
            img = self.capture_primary()
            if img is None:
                return None
            
            # BytesIO'ya kaydet
            buffer = BytesIO()
            if format.upper() == "JPEG":
                img.save(buffer, format="JPEG", quality=quality, optimize=True)
            else:
                img.save(buffer, format="PNG", optimize=True)
            
            # Base64'e dönüştür
            buffer.seek(0)
            b64_str = base64.b64encode(buffer.read()).decode("utf-8")
            
            logger.debug(f"Screenshot base64 boyutu: {len(b64_str)} karakter")
            return b64_str
        except Exception as e:
            logger.error(f"Base64 dönüşümü başarısız: {e}")
            return None
    
    def close(self):
        """Kaynakları serbest bırak"""
        self.sct.close()


# Singleton instance
_capture: Optional[ScreenCapture] = None


def get_capture() -> ScreenCapture:
    """Singleton capture instance döndür"""
    global _capture
    if _capture is None:
        _capture = ScreenCapture()
    return _capture


def take_screenshot(path: Path) -> bool:
    """Ekran görüntüsü al ve dosyaya kaydet"""
    return get_capture().save_screenshot(path)


def take_screenshot_base64(quality: int = 85) -> Optional[str]:
    """Ekran görüntüsü al ve base64 döndür"""
    return get_capture().to_base64(format="JPEG", quality=quality)


def cleanup_screenshot(path: Path) -> None:
    """Geçici screenshot dosyasını sil"""
    try:
        if path.exists():
            path.unlink()
            logger.debug(f"Screenshot silindi: {path}")
    except Exception as e:
        logger.warning(f"Screenshot silinemedi: {e}")


def read_as_base64(path: Path) -> Optional[str]:
    """Dosyadan resmi oku ve base64 döndür"""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"Dosya okunamadı: {e}")
        return None


if __name__ == "__main__":
    # Test
    from pathlib import Path
    
    capture = get_capture()
    
    print("=== Ekran Görüntüsü Testi ===")
    
    # Dosyaya kaydet
    test_path = Path("test_screenshot.png")
    if capture.save_screenshot(test_path):
        print(f"✓ Screenshot kaydedildi: {test_path}")
        print(f"  Boyut: {test_path.stat().st_size / 1024:.1f} KB")
        test_path.unlink()  # Temizle
    
    # Base64
    b64 = capture.to_base64()
    if b64:
        print(f"✓ Base64 uzunluk: {len(b64)} karakter")
        print(f"  Yaklaşık boyut: {len(b64) * 3 / 4 / 1024:.1f} KB")
    
    capture.close()
    print("\n✓ Test tamamlandı!")


