"""
Core
~~~~

Yapılandırma ve bağımlılık enjeksiyonu.
"""

from .config import Settings, get_settings
from .dependencies import get_ai_client, get_database, get_notification

__all__ = [
    "Settings",
    "get_settings",
    "get_ai_client",
    "get_database",
    "get_notification",
]
