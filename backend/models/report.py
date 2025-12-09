"""
Report Model
~~~~~~~~~~~~

Günlük rapor veri modeli.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Report:
    """Bir günlük rapor."""
    
    date: date
    summary: str  # Günün özeti
    content: str  # Markdown içerik
    
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    # Analiz verileri
    technologies: list[str] = field(default_factory=list)
    activity_count: int = 0
    focus_percentage: Optional[float] = None
    distraction_minutes: int = 0
    
    # Ham loglar
    raw_logs: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Dict'e dönüştür."""
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "summary": self.summary,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "technologies": self.technologies,
            "activity_count": self.activity_count,
            "focus_percentage": self.focus_percentage,
            "distraction_minutes": self.distraction_minutes,
            "raw_logs": self.raw_logs,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Report":
        """Dict'ten oluştur."""
        return cls(
            id=data.get("id"),
            date=date.fromisoformat(data["date"]),
            summary=data["summary"],
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            technologies=data.get("technologies", []),
            activity_count=data.get("activity_count", 0),
            focus_percentage=data.get("focus_percentage"),
            distraction_minutes=data.get("distraction_minutes", 0),
            raw_logs=data.get("raw_logs"),
        )
    
    def to_markdown(self) -> str:
        """Markdown formatına dönüştür."""
        return self.content
