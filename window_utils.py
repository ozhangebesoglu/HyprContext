"""
HyprContext - Hyprland Pencere Yardımcıları
Aktif pencere ve workspace bilgilerini toplar.
"""

import subprocess
import json
import logging

logger = logging.getLogger(__name__)


def get_active_window_info() -> str:
    """Aktif pencere bilgisini döndürür."""
    try:
        result = subprocess.run(
            ["hyprctl", "activewindow", "-j"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            logger.warning(f"hyprctl hata kodu: {result.returncode}")
            return "Aktif pencere bilgisi alınamadı."
        
        data = json.loads(result.stdout)
        app_class = data.get('class', 'Bilinmiyor')
        title = data.get('title', 'Bilinmiyor')
        
        return f"{app_class} | {title}"
        
    except subprocess.TimeoutExpired:
        logger.error("hyprctl timeout")
        return "Pencere bilgisi alınamadı (timeout)."
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse hatası: {e}")
        return "Pencere bilgisi alınamadı (parse hatası)."
    except FileNotFoundError:
        logger.error("hyprctl bulunamadı. Hyprland kurulu mu?")
        return "hyprctl bulunamadı."
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        return "Pencere bilgisi alınamadı."


def get_all_workspaces_info() -> str:
    """Tüm workspace'lerdeki pencerelerin listesini döndürür."""
    try:
        result = subprocess.run(
            ["hyprctl", "clients", "-j"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            logger.warning(f"hyprctl hata kodu: {result.returncode}")
            return "Arka plan bilgisi alınamadı."
        
        clients = json.loads(result.stdout)
        
        if not clients:
            return "Arka plan boş."
        
        workspace_map: dict[int, list[str]] = {}
        
        for client in clients:
            ws_id = client.get('workspace', {}).get('id', 0)
            if ws_id > 0:
                app = client.get('class', 'Bilinmiyor')
                title = client.get('title', '')
                
                # Başlığı kısalt
                if len(title) > 25:
                    title = title[:25] + "..."
                
                if ws_id not in workspace_map:
                    workspace_map[ws_id] = []
                workspace_map[ws_id].append(f"{app}: {title}")
        
        if not workspace_map:
            return "Arka plan boş."
        
        # Formatla
        lines = []
        for ws in sorted(workspace_map.keys()):
            apps = " | ".join(workspace_map[ws])
            lines.append(f"WS{ws}: {apps}")
        
        return "\n".join(lines)
        
    except subprocess.TimeoutExpired:
        logger.error("hyprctl timeout")
        return "Arka plan bilgisi alınamadı (timeout)."
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse hatası: {e}")
        return "Arka plan bilgisi alınamadı (parse hatası)."
    except FileNotFoundError:
        logger.error("hyprctl bulunamadı")
        return "hyprctl bulunamadı."
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        return "Arka plan bilgisi alınamadı."
