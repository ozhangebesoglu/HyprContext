"""
HyprContext Backend - Main Entry Point
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FastAPI uygulaması ve arka plan görevleri.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .core.exceptions import (
    HyprContextException,
    hyprcontext_exception_handler,
    generic_exception_handler
)
from .core.dependencies import (
    get_screenshot_capture,
    get_window_capture,
    get_analyzer_service,
    get_focus_service,
    get_activity_repository
)
from .api.routes import (
    activities_router,
    plans_router,
    reports_router,
    focus_router,
    chat_router,
    profile_router,
    control_router
)
from .api.websocket.handlers import (
    websocket_endpoint, 
    broadcast_activity, 
    broadcast_focus_update,
    broadcast_distraction_warning,
    broadcast_system_stats
)
from .models.activity import Activity

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Settings
settings = get_settings()

# Background task referansları
_capture_task = None
_focus_task = None
_system_monitor_task = None


async def capture_loop():
    """Ekran görüntüsü yakalama döngüsü."""
    from .core.dependencies import get_course_detector
    
    screenshot_capture = get_screenshot_capture()
    window_capture = get_window_capture()
    analyzer = get_analyzer_service()
    activity_repo = get_activity_repository()
    course_detector = get_course_detector()
    
    logger.info(f"Capture loop başlatıldı (interval: {settings.screenshot_interval}s)")
    
    try:
        while True:
            try:
                # Screenshot al
                result = screenshot_capture.capture()
                
                if result.success:
                    # Pencere bilgilerini al
                    active_window = window_capture.get_active_window()
                    all_windows = window_capture.get_all_windows()
                    
                    logger.info(f"Pencere bilgisi: {active_window}")
                    
                    # Kurs tespiti yap
                    course = course_detector.detect_course()
                    if course:
                        course_detector.send_course_notification(course)
                    
                    # Analiz et
                    analysis = analyzer.analyze(
                        screenshot=result.data,
                        active_window=active_window,
                        all_windows=all_windows
                    )
                    
                    if analysis.success:
                        # Activity oluştur ve kaydet
                        from datetime import datetime
                        activity = Activity(
                            timestamp=datetime.now(),
                            summary=analysis.summary,
                            tags=analysis.tags,
                            active_window=active_window.app_class if active_window else None,
                            screenshot_path=result.screenshot_path
                        )
                        
                        activity_repo.save(activity)
                        
                        # WebSocket ile broadcast et
                        await broadcast_activity(activity.to_dict())
                        
                        logger.info(f"Aktivite kaydedildi: {activity.summary[:50]}...")
                    else:
                        logger.warning(f"Analiz başarısız: {analysis.error_message}")
                else:
                    logger.warning(f"Screenshot başarısız: {result.error_message}")
                    
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Capture loop hatası: {e}")
            
            await asyncio.sleep(settings.screenshot_interval)
    except asyncio.CancelledError:
        logger.info("Capture loop durduruldu")
        raise


async def focus_loop():
    """Odak takip döngüsü."""
    focus_service = get_focus_service()
    
    logger.info("Focus loop başlatıldı")
    
    try:
        while True:
            try:
                # Dikkat dağınıklığı kontrolü
                is_distracted, keyword = focus_service.check_distraction()
                
                if is_distracted:
                    # Süreyi artır
                    data = focus_service.increment_distraction(seconds=1)
                    
                    # İstatistikleri al
                    stats = focus_service.get_stats()
                    
                    # Uyarı kontrolü ve WebSocket broadcast
                    warning_sent = focus_service.check_and_warn(data)
                    
                    if warning_sent:
                        # Uyarı gönderildi - WebSocket'e de bildir
                        await broadcast_distraction_warning({
                            "keyword": keyword,
                            "used_seconds": stats.used_seconds,
                            "remaining_seconds": stats.remaining_seconds,
                            "percentage": stats.percentage,
                            "limit_reached": data.limit_reached,
                            "message": f"Yasaklı uygulamalarda {stats.format_used()} geçirdin!"
                        })
                    
                    # Normal durum güncellemesi
                    await broadcast_focus_update({
                        "is_distracted": True,
                        "keyword": keyword,
                        "used_seconds": stats.used_seconds,
                        "remaining_seconds": stats.remaining_seconds,
                        "percentage": stats.percentage
                    })
                    
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Focus loop hatası: {e}")
            
            await asyncio.sleep(1)  # Her saniye kontrol
    except asyncio.CancelledError:
        logger.info("Focus loop durduruldu")
        raise


async def system_monitor_loop():
    """Sistem kaynak izleme döngüsü."""
    from .services.system_monitor import SystemMonitorService
    
    monitor = SystemMonitorService()
    
    if not monitor.is_available():
        logger.warning("System monitor kullanılamıyor (psutil kurulu değil)")
        return
    
    logger.info("System monitor loop başlatıldı")
    
    while True:
        try:
            stats = monitor.get_stats()
            
            if stats:
                await broadcast_system_stats(stats.to_dict())
                
        except Exception as e:
            logger.error(f"System monitor hatası: {e}")
        
        await asyncio.sleep(2)  # Her 2 saniyede bir güncelle


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü."""
    global _capture_task, _focus_task, _system_monitor_task
    
    # Startup
    logger.info("HyprContext Backend başlatılıyor...")
    
    yield  # Sunucu hazır
    
    # Shutdown
    logger.info("HyprContext Backend kapatılıyor...")
    
    if _capture_task:
        _capture_task.cancel()
    if _focus_task:
        _focus_task.cancel()
    if _system_monitor_task:
        _system_monitor_task.cancel()


# FastAPI uygulaması
app = FastAPI(
    title=settings.app_name,
    description="Aktivite takip ve odak yönetim sistemi",
    version="0.1.0",
    lifespan=lifespan
)

# Exception handlers
app.add_exception_handler(HyprContextException, hyprcontext_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Startup event - sadece system monitor başlat, capture/focus kullanıcı tarafından başlatılacak
@app.on_event("startup")
async def start_background_tasks():
    """Background task'ları sunucu hazır olduktan sonra başlat."""
    global _system_monitor_task
    
    # Biraz bekle ki sunucu tamamen hazır olsun
    await asyncio.sleep(1)
    
    # Sadece system monitor'u başlat (capture/focus kullanıcı kontrolünde)
    _system_monitor_task = asyncio.create_task(system_monitor_loop())
    
    logger.info("System monitor başlatıldı. Capture/Focus kullanıcı tarafından başlatılacak.")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(activities_router, prefix="/api")
app.include_router(plans_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(focus_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(control_router, prefix="/api")

# WebSocket
app.websocket("/ws")(websocket_endpoint)


@app.get("/")
async def root():
    """Health check."""
    return {
        "name": settings.app_name,
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Detaylı health check."""
    from .core.dependencies import get_ai_client, get_database
    
    ai_available = False
    db_count = 0
    
    try:
        ai_client = get_ai_client()
        ai_available = ai_client.is_available()
    except Exception:
        pass
    
    try:
        db = get_database()
        db_count = db.get_count()
    except Exception:
        pass
    
    return {
        "status": "healthy",
        "ai_available": ai_available,
        "database_records": db_count
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
