"""
Services
~~~~~~~~

İş mantığı servisleri.
Single Responsibility: Her servis tek bir iş yapar.
"""

from .screenshot_service import ScreenshotService
from .window_service import WindowService
from .analyzer_service import AnalyzerService
from .focus_service import FocusService
from .plan_service import PlanService
from .report_service import ReportService
from .course_detector import CourseDetectorService

__all__ = [
    "ScreenshotService",
    "WindowService",
    "AnalyzerService",
    "FocusService",
    "PlanService",
    "ReportService",
    "CourseDetectorService",
]
