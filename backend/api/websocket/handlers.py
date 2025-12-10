"""
WebSocket Handlers
~~~~~~~~~~~~~~~~~~

Gerçek zamanlı event handler'ları.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Set

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket bağlantı yöneticisi."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Yeni bağlantı kabul et."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket bağlantısı: {len(self.active_connections)} aktif")
    
    def disconnect(self, websocket: WebSocket):
        """Bağlantıyı kaldır."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket ayrıldı: {len(self.active_connections)} aktif")
    
    async def broadcast(self, message: dict):
        """Tüm bağlı istemcilere mesaj gönder."""
        if not self.active_connections:
            return
        
        data = json.dumps(message, ensure_ascii=False)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.append(connection)
        
        # Kopan bağlantıları temizle
        for conn in disconnected:
            self.active_connections.discard(conn)
    
    async def send_to(self, websocket: WebSocket, message: dict):
        """Belirli bir istemciye mesaj gönder."""
        try:
            data = json.dumps(message, ensure_ascii=False)
            await websocket.send_text(data)
        except Exception as e:
            logger.error(f"Mesaj gönderme hatası: {e}")


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """Ana WebSocket endpoint'i.
    
    Event türleri:
    - activity: Yeni aktivite
    - focus_update: Odak durumu güncellemesi
    - distraction_warning: Dikkat dağınıklığı uyarısı
    - plan_update: Plan güncellemesi
    - ping/pong: Bağlantı kontrolü
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # İstemciden mesaj bekle
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                event_type = message.get("type", "")
                
                # Event işle
                if event_type == "ping":
                    await manager.send_to(websocket, {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
                elif event_type == "subscribe":
                    # Belirli event'lere abone ol
                    channels = message.get("channels", [])
                    await manager.send_to(websocket, {
                        "type": "subscribed",
                        "channels": channels
                    })
                
                else:
                    # Bilinmeyen event
                    await manager.send_to(websocket, {
                        "type": "error",
                        "message": f"Bilinmeyen event türü: {event_type}"
                    })
                    
            except json.JSONDecodeError:
                await manager.send_to(websocket, {
                    "type": "error",
                    "message": "Geçersiz JSON"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket hatası: {e}")
        manager.disconnect(websocket)


# Event broadcast fonksiyonları
async def broadcast_activity(activity: dict):
    """Yeni aktivite broadcast et."""
    await manager.broadcast({
        "type": "activity",
        "data": activity,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_focus_update(stats: dict):
    """Odak durumu güncellemesi broadcast et."""
    await manager.broadcast({
        "type": "focus_update",
        "data": stats,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_distraction_warning(warning: dict):
    """Dikkat dağınıklığı uyarısı broadcast et."""
    await manager.broadcast({
        "type": "distraction_warning",
        "data": warning,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_plan_update(plan: dict):
    """Plan güncellemesi broadcast et."""
    await manager.broadcast({
        "type": "plan_update",
        "data": plan,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_system_stats(stats: dict):
    """Sistem istatistiklerini broadcast et."""
    await manager.broadcast({
        "type": "system_stats",
        "data": stats,
        "timestamp": datetime.now().isoformat()
    })
