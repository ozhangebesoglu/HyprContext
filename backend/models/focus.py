"""
Focus Models
~~~~~~~~~~~~

Odak takibi veri modelleri.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class FocusData:
    """Günlük odak verisi."""
    
    date: date
    distraction_seconds: int = 0
    warnings_sent: list[int] = field(default_factory=list)
    limit_reached: bool = False
    
    def to_dict(self) -> dict:
        """Dict'e dönüştür."""
        return {
            "date": self.date.isoformat(),
            "distraction_seconds": self.distraction_seconds,
            "warnings_sent": self.warnings_sent,
            "limit_reached": self.limit_reached,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FocusData":
        """Dict'ten oluştur."""
        return cls(
            date=date.fromisoformat(data["date"]) if isinstance(data["date"], str) else data["date"],
            distraction_seconds=data.get("distraction_seconds", 0),
            warnings_sent=data.get("warnings_sent", []),
            limit_reached=data.get("limit_reached", False),
        )
    
    def get_remaining_seconds(self, daily_limit: int) -> int:
        """Kalan süreyi hesapla."""
        return max(0, daily_limit - self.distraction_seconds)
    
    def get_percentage(self, daily_limit: int) -> float:
        """Kullanım yüzdesini hesapla."""
        if daily_limit == 0:
            return 0.0
        return (self.distraction_seconds / daily_limit) * 100


@dataclass
class FocusStats:
    """Odak istatistikleri."""
    
    today: FocusData
    daily_limit_seconds: int
    
    @property
    def used_seconds(self) -> int:
        """Kullanılan süre."""
        return self.today.distraction_seconds
    
    @property
    def remaining_seconds(self) -> int:
        """Kalan süre."""
        return self.today.get_remaining_seconds(self.daily_limit_seconds)
    
    @property
    def percentage(self) -> float:
        """Kullanım yüzdesi."""
        return self.today.get_percentage(self.daily_limit_seconds)
    
    @property
    def is_limit_reached(self) -> bool:
        """Limit aşıldı mı."""
        return self.today.limit_reached
    
    def format_used(self) -> str:
        """Kullanılan süreyi formatla."""
        return self._format_duration(self.used_seconds)
    
    def format_remaining(self) -> str:
        """Kalan süreyi formatla."""
        return self._format_duration(self.remaining_seconds)
    
    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Süreyi okunabilir formata çevir."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}s {minutes}dk"
        elif minutes > 0:
            return f"{minutes}dk {secs}sn"
        else:
            return f"{secs}sn"
