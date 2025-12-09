"""
Activity Model
~~~~~~~~~~~~~~

Aktivite kaydı veri modeli.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Activity:
    """Bir aktivite kaydı."""
    
    timestamp: datetime
    summary: str
    tags: list[str] = field(default_factory=list)
    id: Optional[str] = None
    
    # Ek metadata
    active_window: Optional[str] = None
    screenshot_path: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Dict'e dönüştür."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "summary": self.summary,
            "tags": self.tags,
            "active_window": self.active_window,
            "screenshot_path": self.screenshot_path,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Activity":
        """Dict'ten oluştur."""
        return cls(
            id=data.get("id"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            summary=data["summary"],
            tags=data.get("tags", []),
            active_window=data.get("active_window"),
            screenshot_path=data.get("screenshot_path"),
        )
    
    def get_date(self) -> str:
        """Tarihi YYYY-MM-DD formatında döndür."""
        return self.timestamp.strftime("%Y-%m-%d")
    
    def get_time(self) -> str:
        """Saati HH:MM formatında döndür."""
        return self.timestamp.strftime("%H:%M")
