"""
Notification Interface
~~~~~~~~~~~~~~~~~~~~~~

Bildirim gönderme için soyut sınıf.
Liskov Substitution: Tüm bildirim türleri aynı interface'i kullanır.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class NotificationPriority(Enum):
    """Bildirim önceliği."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NotificationMessage:
    """Bildirim mesajı."""
    title: str
    body: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    sound: bool = True
    icon: Optional[str] = None


class INotification(ABC):
    """Bildirim gönderme interface'i."""
    
    @abstractmethod
    def send(self, message: NotificationMessage) -> bool:
        """Bildirim gönder.
        
        Args:
            message: Bildirim mesajı
            
        Returns:
            Gönderim başarılı mı
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Bildirim sisteminin kullanılabilir olup olmadığını kontrol et."""
        pass
