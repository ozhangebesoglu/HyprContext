"""
Window Service
~~~~~~~~~~~~~~

Pencere bilgisi alma servisi.
Single Responsibility: Sadece pencere bilgisi alma.
"""

import json
import subprocess
import logging
from typing import Optional

from ..interfaces.capture import IWindowCapture, WindowInfo

logger = logging.getLogger(__name__)


class WindowService(IWindowCapture):
    """Hyprland ile pencere bilgisi alma servisi."""
    
    def get_active_window(self) -> Optional[WindowInfo]:
        """Aktif pencere bilgisini al.
        
        Returns:
            WindowInfo veya None (hata durumunda)
        """
        try:
            result = subprocess.run(
                ["hyprctl", "activewindow", "-j"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.warning(f"hyprctl hata kodu: {result.returncode}")
                return None
            
            if not result.stdout.strip():
                logger.warning("hyprctl boş yanıt döndü")
                return None
            
            data = json.loads(result.stdout)
            
            return WindowInfo(
                app_class=data.get("class", "Bilinmiyor"),
                title=data.get("title", "Bilinmiyor"),
                workspace_id=data.get("workspace", {}).get("id", 0)
            )
            
        except FileNotFoundError:
            logger.error("hyprctl bulunamadı")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse hatası: {e}")
            return None
        except subprocess.TimeoutExpired:
            logger.error("hyprctl timeout")
            return None
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return None
    
    def get_all_windows(self) -> list[WindowInfo]:
        """Tüm pencerelerin bilgisini al.
        
        Returns:
            WindowInfo listesi
        """
        try:
            result = subprocess.run(
                ["hyprctl", "clients", "-j"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.warning(f"hyprctl hata kodu: {result.returncode}")
                return []
            
            clients = json.loads(result.stdout)
            windows = []
            
            for client in clients:
                ws_id = client.get("workspace", {}).get("id", 0)
                if ws_id > 0:
                    windows.append(WindowInfo(
                        app_class=client.get("class", "Bilinmiyor"),
                        title=client.get("title", "")[:50],  # Kısalt
                        workspace_id=ws_id
                    ))
            
            return windows
            
        except Exception as e:
            logger.error(f"Pencere listesi hatası: {e}")
            return []
    
    def format_windows(self, windows: list[WindowInfo]) -> str:
        """Pencere listesini metin formatına çevir."""
        if not windows:
            return "Arka plan boş."
        
        # Workspace'e göre grupla
        workspace_map: dict[int, list[str]] = {}
        
        for window in windows:
            if window.workspace_id not in workspace_map:
                workspace_map[window.workspace_id] = []
            workspace_map[window.workspace_id].append(
                f"{window.app_class}: {window.title}"
            )
        
        # Formatla
        lines = []
        for ws in sorted(workspace_map.keys()):
            apps = " | ".join(workspace_map[ws])
            lines.append(f"WS{ws}: {apps}")
        
        return "\n".join(lines)
