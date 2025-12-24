"""
Windows Window Adapter
~~~~~~~~~~~~~~~~~~~~~~

Windows için ctypes + Windows API ile pencere bilgisi alma.
"""

import logging
from typing import Optional, List

from ..interfaces.capture import IWindowCapture, WindowInfo

logger = logging.getLogger(__name__)

# Conditional imports for Windows
try:
    import ctypes
    from ctypes import wintypes
    import psutil
    WINDOWS_API_AVAILABLE = True

    # Windows API
    user32 = ctypes.windll.user32
    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
except (ImportError, AttributeError, OSError):
    WINDOWS_API_AVAILABLE = False
    ctypes = None
    wintypes = None
    psutil = None
    user32 = None
    EnumWindowsProc = None


class WindowsWindowAdapter(IWindowCapture):
    """Windows API ile pencere bilgisi alma."""

    def _get_window_text(self, hwnd: int) -> str:
        """Pencere başlığını al."""
        if not WINDOWS_API_AVAILABLE:
            return ""
        try:
            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return ""
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            return buffer.value
        except Exception:
            return ""

    def _get_class_name(self, hwnd: int) -> str:
        """Pencere sınıf adını al."""
        if not WINDOWS_API_AVAILABLE:
            return ""
        try:
            buffer = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, buffer, 256)
            return buffer.value
        except Exception:
            return ""

    def _get_process_name(self, hwnd: int) -> str:
        """Pencere işlem adını al."""
        if not WINDOWS_API_AVAILABLE or psutil is None:
            return "unknown"
        try:
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            process = psutil.Process(pid.value)
            return process.name().replace(".exe", "")
        except Exception:
            return "unknown"

    def _is_window_visible(self, hwnd: int) -> bool:
        """Pencere görünür mü?"""
        if not WINDOWS_API_AVAILABLE:
            return False
        try:
            return bool(user32.IsWindowVisible(hwnd))
        except Exception:
            return False

    def get_active_window(self) -> Optional[WindowInfo]:
        """Aktif pencere bilgisini al.

        Returns:
            WindowInfo veya None (hata durumunda)
        """
        if not WINDOWS_API_AVAILABLE:
            logger.error("Windows API kullanılamıyor (Linux'ta mısınız?)")
            return None

        try:
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return None

            title = self._get_window_text(hwnd)
            process_name = self._get_process_name(hwnd)

            return WindowInfo(
                app_class=process_name,
                title=title,
                workspace_id=0  # Windows'ta workspace yok
            )

        except Exception as e:
            logger.error(f"Aktif pencere hatası: {e}")
            return None

    def get_all_windows(self) -> List[WindowInfo]:
        """Tüm pencerelerin bilgisini al.

        Returns:
            WindowInfo listesi
        """
        if not WINDOWS_API_AVAILABLE:
            logger.error("Windows API kullanılamıyor (Linux'ta mısınız?)")
            return []

        windows: List[WindowInfo] = []
        seen_processes = set()

        def enum_callback(hwnd: int, _: int) -> bool:
            try:
                if self._is_window_visible(hwnd):
                    title = self._get_window_text(hwnd)
                    # Boş başlıklı veya sistem pencerelerini atla
                    if title and not title.startswith("MSCTFIME"):
                        class_name = self._get_class_name(hwnd)
                        # Sistem pencerelerini filtrele
                        skip_classes = ["Shell_TrayWnd", "Progman", "WorkerW", "Button"]
                        if class_name not in skip_classes:
                            process_name = self._get_process_name(hwnd)
                            # Benzersiz process'leri al
                            if process_name not in seen_processes:
                                seen_processes.add(process_name)
                                windows.append(WindowInfo(
                                    app_class=process_name,
                                    title=title[:50],  # Kısalt
                                    workspace_id=0
                                ))
            except Exception:
                pass
            return True

        try:
            callback = EnumWindowsProc(enum_callback)
            user32.EnumWindows(callback, 0)
        except Exception as e:
            logger.error(f"Pencere listesi hatası: {e}")

        return windows[:10]  # Max 10 pencere

    def format_windows(self, windows: List[WindowInfo]) -> str:
        """Pencere listesini metin formatına çevir."""
        if not windows:
            return "Arka plan boş."

        apps = [f"{w.app_class}: {w.title}" for w in windows]
        return " | ".join(apps)
