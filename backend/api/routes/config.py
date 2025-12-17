"""
Config Routes
~~~~~~~~~~~~~

Uygulama ayarları API endpoint'leri.
"""

from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from ...core.config import get_settings, reload_settings

router = APIRouter(prefix="/config", tags=["config"])


class DataPathRequest(BaseModel):
    """Veri klasörü yolu isteği."""
    data_path: str


class DataPathResponse(BaseModel):
    """Veri klasörü yolu yanıtı."""
    data_path: str
    screenshots_dir: str
    plans_dir: str
    reports_dir: str
    profile_path: str
    history_jsonl_path: str
    chroma_db_path: str


@router.get("/data-path", response_model=DataPathResponse)
async def get_data_path():
    """Mevcut veri klasörü yollarını döndür."""
    settings = get_settings()
    
    return DataPathResponse(
        data_path=settings.data_path,
        screenshots_dir=settings.screenshots_dir,
        plans_dir=settings.plans_dir,
        reports_dir=settings.reports_dir,
        profile_path=settings.profile_path,
        history_jsonl_path=settings.history_jsonl_path,
        chroma_db_path=settings.chroma_db_path,
    )


@router.post("/data-path", response_model=DataPathResponse)
async def set_data_path(request: DataPathRequest):
    """Veri klasörü yolunu güncelle ve klasörleri oluştur."""
    settings = get_settings()
    
    # Yeni path'i ayarla
    settings.update_data_path(request.data_path)
    
    # Screenshots klasörünü de oluştur
    screenshots_path = Path(settings.screenshots_dir)
    screenshots_path.mkdir(parents=True, exist_ok=True)
    
    return DataPathResponse(
        data_path=settings.data_path,
        screenshots_dir=settings.screenshots_dir,
        plans_dir=settings.plans_dir,
        reports_dir=settings.reports_dir,
        profile_path=settings.profile_path,
        history_jsonl_path=settings.history_jsonl_path,
        chroma_db_path=settings.chroma_db_path,
    )


@router.get("/info")
async def get_config_info():
    """Tüm ayarları döndür (debug için)."""
    settings = get_settings()
    
    return {
        "app_name": settings.app_name,
        "data_path": settings.data_path,
        "screenshots_dir": settings.screenshots_dir,
        "plans_dir": settings.plans_dir,
        "reports_dir": settings.reports_dir,
        "profile_path": settings.profile_path,
        "chroma_db_path": settings.chroma_db_path,
        "ollama_model": settings.ollama_model,
        "screenshot_interval": settings.screenshot_interval,
    }
