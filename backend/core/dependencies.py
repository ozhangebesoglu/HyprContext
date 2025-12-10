"""
Dependencies
~~~~~~~~~~~~

Bağımlılık enjeksiyonu (FastAPI için).
Dependency Inversion Principle uygulaması.
"""

from functools import lru_cache
from typing import Generator

from .config import Settings, get_settings

# Interface imports
from ..interfaces.ai_client import IAIClient
from ..interfaces.database import IDatabase
from ..interfaces.notification import INotification
from ..interfaces.capture import IScreenshotCapture, IWindowCapture

# Adapter imports
from ..adapters.ollama_adapter import OllamaAdapter
from ..adapters.chromadb_adapter import ChromaDBAdapter
from ..adapters.notification_adapter import DesktopNotification, CompositeNotification, TTSNotification


@lru_cache()
def get_ai_client() -> IAIClient:
    """AI client bağımlılığı.
    
    DIP: IAIClient döndürür, somut implementasyon değil.
    """
    settings = get_settings()
    return OllamaAdapter(
        model_name=settings.ollama_model,
        embed_model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url
    )


@lru_cache()
def get_database() -> IDatabase:
    """Database bağımlılığı.
    
    DIP: IDatabase döndürür, somut implementasyon değil.
    """
    settings = get_settings()
    return ChromaDBAdapter(
        db_path=settings.chroma_db_path,
        collection_name="hypr_logs"
    )


@lru_cache()
def get_notification() -> INotification:
    """Notification bağımlılığı.
    
    Composite pattern: Hem masaüstü hem TTS bildirimi.
    """
    desktop = DesktopNotification()
    tts = TTSNotification()
    
    return CompositeNotification([desktop, tts])


@lru_cache()
def get_screenshot_capture() -> IScreenshotCapture:
    """Screenshot capture bağımlılığı."""
    from ..services.screenshot_service import ScreenshotService
    settings = get_settings()
    return ScreenshotService(temp_path=settings.screenshot_temp_path)


@lru_cache()
def get_window_capture() -> IWindowCapture:
    """Window capture bağımlılığı."""
    from ..services.window_service import WindowService
    return WindowService()


# Service dependencies (tam service'ler için)
def get_analyzer_service():
    """Analyzer service bağımlılığı."""
    from ..services.analyzer_service import AnalyzerService
    return AnalyzerService(ai_client=get_ai_client())


def get_focus_service():
    """Focus service bağımlılığı."""
    from ..services.focus_service import FocusService
    from pathlib import Path
    
    settings = get_settings()
    return FocusService(
        window_capture=get_window_capture(),
        notification=get_notification(),
        banned_keywords=settings.banned_keywords,
        daily_limit_seconds=settings.daily_distraction_limit_seconds,
        data_file=Path(settings.focus_data_path)
    )


def get_activity_repository():
    """Activity repository bağımlılığı."""
    from ..repositories.activity_repository import ActivityRepository
    settings = get_settings()
    
    return ActivityRepository(
        jsonl_path=settings.history_jsonl_path,
        vector_db=get_database(),
        ai_client=get_ai_client()
    )


def get_plan_repository():
    """Plan repository bağımlılığı."""
    from ..repositories.plan_repository import PlanRepository
    settings = get_settings()
    return PlanRepository(plans_dir=settings.plans_dir)


def get_report_repository():
    """Report repository bağımlılığı."""
    from ..repositories.report_repository import ReportRepository
    settings = get_settings()
    return ReportRepository(reports_dir=settings.reports_dir)


def get_weather_service():
    """Weather service bağımlılığı."""
    from ..services.weather_service import WeatherService
    settings = get_settings()
    
    # Profile'dan şehir al
    profile = settings.get_profile()
    location = profile.get("sehir", "Istanbul")
    
    return WeatherService(location=location)


def get_plan_service():
    """Plan service bağımlılığı."""
    from ..services.plan_service import PlanService
    settings = get_settings()
    
    return PlanService(
        ai_client=get_ai_client(),
        plan_repository=get_plan_repository(),
        activity_repository=get_activity_repository(),
        profile=settings.get_profile(),
        weather_service=get_weather_service()
    )


def get_report_service():
    """Report service bağımlılığı."""
    from ..services.report_service import ReportService
    
    return ReportService(
        ai_client=get_ai_client(),
        report_repository=get_report_repository(),
        activity_repository=get_activity_repository()
    )


def get_course_detector():
    """Course detector bağımlılığı."""
    from ..services.course_detector import CourseDetectorService
    
    return CourseDetectorService(
        window_capture=get_window_capture(),
        notification=get_notification()
    )
