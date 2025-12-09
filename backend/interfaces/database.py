"""
Database Interface
~~~~~~~~~~~~~~~~~~

Veritabanı işlemleri için soyut temel sınıf.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class IDatabase(ABC):
    """Veritabanı işlemleri için soyut interface."""
    
    @abstractmethod
    def save(self, collection: str, data: dict, doc_id: Optional[str] = None) -> str:
        """Veri kaydet.
        
        Args:
            collection: Koleksiyon/tablo adı
            data: Kaydedilecek veri
            doc_id: Opsiyonel döküman ID
            
        Returns:
            Kaydedilen dökümanın ID'si
        """
        pass
    
    @abstractmethod
    def get(self, collection: str, doc_id: str) -> Optional[dict]:
        """ID ile veri getir.
        
        Args:
            collection: Koleksiyon/tablo adı
            doc_id: Döküman ID
            
        Returns:
            Bulunan veri veya None
        """
        pass
    
    @abstractmethod
    def query(self, collection: str, filters: dict) -> list[dict]:
        """Filtreye göre veri sorgula.
        
        Args:
            collection: Koleksiyon/tablo adı
            filters: Sorgu filtreleri
            
        Returns:
            Eşleşen dökümanlar listesi
        """
        pass
    
    @abstractmethod
    def delete(self, collection: str, doc_id: str) -> bool:
        """Veri sil.
        
        Args:
            collection: Koleksiyon/tablo adı
            doc_id: Döküman ID
            
        Returns:
            Silme başarılı mı
        """
        pass
    
    @abstractmethod
    def update(self, collection: str, doc_id: str, data: dict) -> bool:
        """Veri güncelle.
        
        Args:
            collection: Koleksiyon/tablo adı
            doc_id: Döküman ID
            data: Güncellenecek alanlar
            
        Returns:
            Güncelleme başarılı mı
        """
        pass
