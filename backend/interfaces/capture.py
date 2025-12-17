"""
Capture Interfaces
~~~~~~~~~~~~~~~~~~

Ekran ve pencere yakalama için soyut sınıflar.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class WindowInfo:
    """Pencere bilgisi."""
    app_class: str
    title: str
    workspace_id: int = 0


@dataclass
class CaptureResult:
    """Yakalama sonucu."""
    success: bool
    data: Optional[bytes] = None
    screenshot_path: Optional[str] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None


class IScreenshotCapture(ABC):
    """Ekran görüntüsü yakalama interface'i."""
    
    @abstractmethod
    def capture(self) -> CaptureResult:
        """Ekran görüntüsü al.
        
        Returns:
            CaptureResult: Screenshot verisi veya hata
        """
        pass


class IWindowCapture(ABC):
    """Pencere bilgisi yakalama interface'i."""
    
    @abstractmethod
    def get_active_window(self) -> Optional[WindowInfo]:
        """Aktif pencere bilgisini al.
        
        Returns:
            WindowInfo veya None
        """
        pass
    
    @abstractmethod
    def get_all_windows(self) -> list[WindowInfo]:
        """Tüm pencerelerin bilgisini al.
        
        Returns:
            WindowInfo listesi
        """
        pass
