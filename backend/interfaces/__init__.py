"""
Interfaces (Soyutlamalar)
~~~~~~~~~~~~~~~~~~~~~~~~~

Dependency Inversion Principle (DIP) için soyut sınıflar.
Tüm servisler bu interface'lere bağımlı olmalı, somut sınıflara değil.
"""

from .ai_client import IAIClient
from .database import IDatabase
from .capture import IScreenshotCapture, IWindowCapture
from .notification import INotification
from .repository import IActivityRepository, IPlanRepository, IReportRepository

__all__ = [
    "IAIClient",
    "IDatabase",
    "IScreenshotCapture",
    "IWindowCapture",
    "INotification",
    "IActivityRepository",
    "IPlanRepository",
    "IReportRepository",
]
