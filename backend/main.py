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
    chat_router
)
from .api.websocket.handlers import websocket_endpoint, broadcast_activity, broadcast_focus_update
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


async def capture_loop():
    """Ekran görüntüsü yakalama döngüsü."""
    screenshot_capture = get_screenshot_capture()
    window_capture = get_window_capture()
    analyzer = get_analyzer_service()
    activity_repo = get_activity_repository()
    
    logger.info(f"Capture loop başlatıldı (interval: {settings.screenshot_interval}s)")
    
    while True:
        try:
            # Screenshot al
            result = screenshot_capture.capture()
            
            if result.success:
                # Pencere bilgilerini al
                active_window = window_capture.get_active_window()
                all_windows = window_capture.get_all_windows()
                
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
                        active_window=active_window.app_class if active_window else None
                    )
                    
                    activity_repo.save(activity)
                    
                    # WebSocket ile broadcast et
                    await broadcast_activity(activity.to_dict())
                    
                    logger.info(f"Aktivite kaydedildi: {activity.summary[:50]}...")
                else:
                    logger.warning(f"Analiz başarısız: {analysis.error_message}")
            else:
                logger.warning(f"Screenshot başarısız: {result.error_message}")
                
        except Exception as e:
            logger.error(f"Capture loop hatası: {e}")
        
        await asyncio.sleep(settings.screenshot_interval)


async def focus_loop():
    """Odak takip döngüsü."""
    focus_service = get_focus_service()
    
    logger.info("Focus loop başlatıldı")
    
    while True:
        try:
            # Dikkat dağınıklığı kontrolü
            is_distracted, keyword = focus_service.check_distraction()
            
            if is_distracted:
                # Süreyi artır
                data = focus_service.increment_distraction(seconds=1)
                
                # Uyarı kontrolü
                focus_service.check_and_warn(data)
                
                # WebSocket ile broadcast et
                stats = focus_service.get_stats()
                await broadcast_focus_update({
                    "is_distracted": True,
                    "keyword": keyword,
                    "used_seconds": stats.used_seconds,
                    "remaining_seconds": stats.remaining_seconds,
                    "percentage": stats.percentage
                })
                
        except Exception as e:
            logger.error(f"Focus loop hatası: {e}")
        
        await asyncio.sleep(1)  # Her saniye kontrol


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü."""
    global _capture_task, _focus_task
    
    # Startup
    logger.info("HyprContext Backend başlatılıyor...")
    
    yield  # Sunucu hazır
    
    # Shutdown
    logger.info("HyprContext Backend kapatılıyor...")
    
    if _capture_task:
        _capture_task.cancel()
    if _focus_task:
        _focus_task.cancel()


# FastAPI uygulaması
app = FastAPI(
    title=settings.app_name,
    description="Aktivite takip ve odak yönetim sistemi",
    version="0.1.0",
    lifespan=lifespan
)


# Startup event - background task'ları başlat
@app.on_event("startup")
async def start_background_tasks():
    """Background task'ları sunucu hazır olduktan sonra başlat."""
    global _capture_task, _focus_task
    
    # Biraz bekle
    await asyncio.sleep(1)
    
    # Task'ları başlat (şimdilik devre dışı - test için)
    # _capture_task = asyncio.create_task(capture_loop())
    # _focus_task = asyncio.create_task(focus_loop())
    logger.info("Background tasks hazır (devre dışı)")


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
