"""
Repository Interfaces
~~~~~~~~~~~~~~~~~~~~~

Veri erişim katmanı için soyut sınıflar.
Interface Segregation: Her entity için ayrı repository.
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import date


class IActivityRepository(ABC):
    """Aktivite verileri için repository interface'i."""
    
    @abstractmethod
    def save(self, activity: "Activity") -> str:
        """Aktivite kaydet."""
        pass
    
    @abstractmethod
    def get_by_id(self, activity_id: str) -> Optional["Activity"]:
        """ID ile aktivite getir."""
        pass
    
    @abstractmethod
    def get_by_date(self, target_date: date) -> list["Activity"]:
        """Tarihe göre aktiviteleri getir."""
        pass
    
    @abstractmethod
    def get_recent(self, limit: int = 50) -> list["Activity"]:
        """Son aktiviteleri getir."""
        pass
    
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list["Activity"]:
        """Semantik arama yap."""
        pass
    
    @abstractmethod
    def get_stats(self) -> dict:
        """İstatistikleri getir."""
        pass


class IPlanRepository(ABC):
    """Plan verileri için repository interface'i."""
    
    @abstractmethod
    def save(self, plan: "Plan") -> str:
        """Plan kaydet."""
        pass
    
    @abstractmethod
    def get_by_date(self, target_date: date) -> Optional["Plan"]:
        """Tarihe göre plan getir."""
        pass
    
    @abstractmethod
    def get_all(self) -> list["Plan"]:
        """Tüm planları getir."""
        pass
    
    @abstractmethod
    def update(self, plan: "Plan") -> bool:
        """Plan güncelle."""
        pass
    
    @abstractmethod
    def delete(self, target_date: date) -> bool:
        """Plan sil."""
        pass


class IReportRepository(ABC):
    """Rapor verileri için repository interface'i."""
    
    @abstractmethod
    def save(self, report: "Report") -> str:
        """Rapor kaydet."""
        pass
    
    @abstractmethod
    def get_by_date(self, target_date: date) -> Optional["Report"]:
        """Tarihe göre rapor getir."""
        pass
    
    @abstractmethod
    def get_all(self) -> list["Report"]:
        """Tüm raporları getir."""
        pass
    
    @abstractmethod
    def export_to_markdown(self, report: "Report", path: str) -> bool:
        """Raporu Markdown olarak dışa aktar."""
        pass
