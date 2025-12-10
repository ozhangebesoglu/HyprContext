"""
API Routes
~~~~~~~~~~

FastAPI router'ları.
"""

from .activities import router as activities_router
from .plans import router as plans_router
from .reports import router as reports_router
from .focus import router as focus_router
from .chat import router as chat_router
from .profile import router as profile_router
from .control import router as control_router

__all__ = [
    "activities_router",
    "plans_router",
    "reports_router",
    "focus_router",
    "chat_router",
    "profile_router",
    "control_router",
]
