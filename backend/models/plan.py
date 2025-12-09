"""
Plan Model
~~~~~~~~~~

Günlük plan veri modeli.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class PlanTask:
    """Plan içindeki bir görev."""
    time: str  # "09:00"
    description: str
    completed: bool = False


@dataclass
class Plan:
    """Bir günlük plan."""
    
    date: date
    mission: str  # Günün misyonu
    content: str  # Markdown içerik
    tasks: list[PlanTask] = field(default_factory=list)
    
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Metadata
    weather: Optional[str] = None
    active_course: Optional[str] = None
    user_note: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Dict'e dönüştür."""
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "mission": self.mission,
            "content": self.content,
            "tasks": [
                {"time": t.time, "description": t.description, "completed": t.completed}
                for t in self.tasks
            ],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "weather": self.weather,
            "active_course": self.active_course,
            "user_note": self.user_note,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Plan":
        """Dict'ten oluştur."""
        tasks = [
            PlanTask(time=t["time"], description=t["description"], completed=t.get("completed", False))
            for t in data.get("tasks", [])
        ]
        
        return cls(
            id=data.get("id"),
            date=date.fromisoformat(data["date"]),
            mission=data["mission"],
            content=data["content"],
            tasks=tasks,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            weather=data.get("weather"),
            active_course=data.get("active_course"),
            user_note=data.get("user_note"),
        )
    
    def get_completion_rate(self) -> float:
        """Tamamlanma oranını hesapla."""
        if not self.tasks:
            return 0.0
        completed = sum(1 for t in self.tasks if t.completed)
        return completed / len(self.tasks)
