"""
Adapters (Somut Implementasyonlar)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Interface'lerin somut implementasyonları.
Open/Closed: Yeni adapter eklemek için mevcut kodu değiştirmene gerek yok.
"""

from .ollama_adapter import OllamaAdapter
from .chromadb_adapter import ChromaDBAdapter
from .notification_adapter import DesktopNotification, TTSNotification

__all__ = [
    "OllamaAdapter",
    "ChromaDBAdapter",
    "DesktopNotification",
    "TTSNotification",
]
