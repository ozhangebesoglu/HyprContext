"""
ChromaDB Adapter
~~~~~~~~~~~~~~~~

ChromaDB veritabanı implementasyonu.
"""

import logging
from typing import Optional, Any
from pathlib import Path

import chromadb

from ..interfaces.database import IDatabase

logger = logging.getLogger(__name__)


class ChromaDBAdapter(IDatabase):
    """ChromaDB implementasyonu."""
    
    def __init__(self, db_path: str = "./hafiza_db", collection_name: str = "hypr_logs"):
        """
        Args:
            db_path: Veritabanı dizini
            collection_name: Koleksiyon adı
        """
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection: Optional[chromadb.Collection] = None
    
    @property
    def client(self) -> chromadb.PersistentClient:
        """ChromaDB client (lazy initialization)."""
        if self._client is None:
            self._client = chromadb.PersistentClient(path=str(self.db_path))
        return self._client
    
    @property
    def collection(self) -> chromadb.Collection:
        """Ana koleksiyon (lazy initialization)."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
        return self._collection
    
    def save(self, collection: str, data: dict, doc_id: Optional[str] = None) -> str:
        """Veri kaydet.
        
        ChromaDB için embedding de gerekli, bu yüzden data içinde
        'embedding' ve 'document' alanları olmalı.
        """
        try:
            if doc_id is None:
                from datetime import datetime
                doc_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            
            coll = self.client.get_or_create_collection(name=collection)
            
            coll.add(
                ids=[doc_id],
                documents=[data.get("document", str(data))],
                embeddings=[data["embedding"]] if "embedding" in data else None,
                metadatas=[data.get("metadata", {})]
            )
            
            return doc_id
            
        except Exception as e:
            logger.error(f"ChromaDB save hatası: {e}")
            raise
    
    def get(self, collection: str, doc_id: str) -> Optional[dict]:
        """ID ile veri getir."""
        try:
            coll = self.client.get_or_create_collection(name=collection)
            result = coll.get(ids=[doc_id], include=["documents", "metadatas"])
            
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result["documents"][0] if result["documents"] else None,
                    "metadata": result["metadatas"][0] if result["metadatas"] else {}
                }
            return None
            
        except Exception as e:
            logger.error(f"ChromaDB get hatası: {e}")
            return None
    
    def query(self, collection: str, filters: dict) -> list[dict]:
        """Filtreye göre veri sorgula.
        
        ChromaDB where filtresi kullanır.
        """
        try:
            coll = self.client.get_or_create_collection(name=collection)
            
            result = coll.get(
                where=filters if filters else None,
                include=["documents", "metadatas"]
            )
            
            items = []
            for i, doc_id in enumerate(result["ids"]):
                items.append({
                    "id": doc_id,
                    "document": result["documents"][i] if result["documents"] else None,
                    "metadata": result["metadatas"][i] if result["metadatas"] else {}
                })
            
            return items
            
        except Exception as e:
            logger.error(f"ChromaDB query hatası: {e}")
            return []
    
    def delete(self, collection: str, doc_id: str) -> bool:
        """Veri sil."""
        try:
            coll = self.client.get_or_create_collection(name=collection)
            coll.delete(ids=[doc_id])
            return True
        except Exception as e:
            logger.error(f"ChromaDB delete hatası: {e}")
            return False
    
    def update(self, collection: str, doc_id: str, data: dict) -> bool:
        """Veri güncelle."""
        try:
            coll = self.client.get_or_create_collection(name=collection)
            
            coll.update(
                ids=[doc_id],
                documents=[data.get("document")] if "document" in data else None,
                metadatas=[data.get("metadata")] if "metadata" in data else None
            )
            return True
            
        except Exception as e:
            logger.error(f"ChromaDB update hatası: {e}")
            return False
    
    def semantic_search(self, query_embedding: list[float], n_results: int = 10) -> list[dict]:
        """Semantik arama yap.
        
        Args:
            query_embedding: Sorgu vektörü
            n_results: Kaç sonuç dönsün
            
        Returns:
            Benzer dökümanlar listesi
        """
        try:
            result = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            items = []
            if result["documents"] and result["documents"][0]:
                for i, doc in enumerate(result["documents"][0]):
                    items.append({
                        "document": doc,
                        "metadata": result["metadatas"][0][i] if result["metadatas"] else {}
                    })
            
            return items
            
        except Exception as e:
            logger.error(f"ChromaDB semantic search hatası: {e}")
            return []
    
    def get_count(self) -> int:
        """Toplam kayıt sayısını döndür."""
        return self.collection.count()
