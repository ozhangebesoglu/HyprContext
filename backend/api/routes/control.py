"""
Control API
~~~~~~~~~~~

Servis kontrol endpointleri (start/stop/status).
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/control", tags=["control"])


class ServiceStatus(BaseModel):
    """Servis durum bilgisi."""
    running: bool
    capture_active: bool
    focus_active: bool
    uptime_seconds: Optional[float] = None
    last_activity: Optional[str] = None
    today_count: int = 0
    focus_data: Optional[dict] = None


class ControlResponse(BaseModel):
    """Kontrol yanıtı."""
    success: bool
    message: str
    status: Optional[ServiceStatus] = None


# Global referanslar (main.py'den erişilecek)
_start_time: Optional[datetime] = None
_is_running: bool = False


def get_task_manager():
    """Task manager referanslarını al."""
    from ...main import _capture_task, _focus_task
    return _capture_task, _focus_task


def set_running_state(running: bool):
    """Çalışma durumunu ayarla."""
    global _is_running, _start_time
    _is_running = running
    if running:
        _start_time = datetime.now()
    else:
        _start_time = None


@router.get("/status", response_model=ServiceStatus)
async def get_status():
    """Servis durumunu sorgula."""
    from ...core.dependencies import get_focus_service, get_activity_repository
    
    capture_task, focus_task = get_task_manager()
    
    # Uptime hesapla
    uptime = None
    if _start_time:
        uptime = (datetime.now() - _start_time).total_seconds()
    
    # Bugünün aktivite sayısı
    today_count = 0
    last_activity = None
    try:
        activity_repo = get_activity_repository()
        from datetime import date
        activities = activity_repo.get_by_date(date.today())
        today_count = len(activities) if activities else 0
        if activities:
            last_activity = activities[-1].timestamp.isoformat()
    except Exception:
        pass
    
    # Focus verisi
    focus_data = None
    try:
        focus_service = get_focus_service()
        stats = focus_service.get_stats()
        focus_data = {
            "used_seconds": stats.used_seconds,
            "remaining_seconds": stats.remaining_seconds,
            "percentage": stats.percentage,
            "limit_reached": stats.today.limit_reached
        }
    except Exception:
        pass
    
    return ServiceStatus(
        running=_is_running,
        capture_active=capture_task is not None and not capture_task.done(),
        focus_active=focus_task is not None and not focus_task.done(),
        uptime_seconds=uptime,
        last_activity=last_activity,
        today_count=today_count,
        focus_data=focus_data
    )


@router.post("/start", response_model=ControlResponse)
async def start_services():
    """Capture ve focus servislerini başlat."""
    global _is_running
    
    if _is_running:
        return ControlResponse(
            success=False,
            message="Servisler zaten çalışıyor",
            status=await get_status()
        )
    
    try:
        # main.py'deki task'ları başlat
        from ...main import capture_loop, focus_loop
        import backend.main as main_module
        
        main_module._capture_task = asyncio.create_task(capture_loop())
        main_module._focus_task = asyncio.create_task(focus_loop())
        
        set_running_state(True)
        logger.info("Servisler manuel olarak başlatıldı")
        
        return ControlResponse(
            success=True,
            message="Servisler başlatıldı",
            status=await get_status()
        )
        
    except Exception as e:
        logger.error(f"Servis başlatma hatası: {e}")
        raise HTTPException(500, f"Servis başlatılamadı: {str(e)}")


@router.post("/stop", response_model=ControlResponse)
async def stop_services():
    """Capture ve focus servislerini durdur."""
    global _is_running
    
    if not _is_running:
        return ControlResponse(
            success=False,
            message="Servisler zaten durmuş",
            status=await get_status()
        )
    
    try:
        import backend.main as main_module
        
        # Task'ları iptal et ve tamamlanmasını bekle
        tasks_to_cancel = []
        
        if main_module._capture_task and not main_module._capture_task.done():
            main_module._capture_task.cancel()
            tasks_to_cancel.append(main_module._capture_task)
        
        if main_module._focus_task and not main_module._focus_task.done():
            main_module._focus_task.cancel()
            tasks_to_cancel.append(main_module._focus_task)
        
        # İptal edilen task'ların bitmesini bekle
        if tasks_to_cancel:
            await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
        
        # Referansları temizle
        main_module._capture_task = None
        main_module._focus_task = None
        
        set_running_state(False)
        logger.info("Servisler manuel olarak durduruldu")
        
        return ControlResponse(
            success=True,
            message="Servisler durduruldu",
            status=await get_status()
        )
        
    except Exception as e:
        logger.error(f"Servis durdurma hatası: {e}")
        raise HTTPException(500, f"Servisler durdurulamadı: {str(e)}")


@router.post("/restart", response_model=ControlResponse)
async def restart_services():
    """Servisleri yeniden başlat."""
    # Önce durdur
    await stop_services()
    
    # Biraz bekle
    await asyncio.sleep(1)
    
    # Sonra başlat
    return await start_services()




