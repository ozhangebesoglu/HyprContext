"""
HyprContext - Veritabanı Modülü
ChromaDB bağlantısı ve ortak veritabanı işlemleri.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import chromadb
import ollama

from config import DB_PATH, HISTORY_FILE, COLLECTION_NAME, MODEL_EMBED

logger = logging.getLogger(__name__)

# === SINGLETON BAĞLANTI ===
_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.Collection] = None


def get_client() -> chromadb.PersistentClient:
    """ChromaDB client'ı döndürür (singleton)."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(DB_PATH))
    return _client


def get_collection() -> chromadb.Collection:
    """Ana koleksiyonu döndürür (singleton)."""
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


def generate_unique_id() -> str:
    """Benzersiz ID üretir (timestamp + mikrosaniye)."""
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def parse_timestamp(timestamp: str) -> tuple[str, str]:
    """Timestamp'ten tarih ve saat çıkarır.
    
    Returns:
        (date: "YYYY-MM-DD", time: "HH:MM")
    """
    if "T" in timestamp:
        date_part, time_part = timestamp.split("T")
        return date_part, time_part[:5]
    return timestamp[:10], "00:00"


def save_to_jsonl(data: dict) -> bool:
    """JSONL dosyasına kayıt ekler."""
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        logger.error(f"JSONL kayıt hatası: {e}")
        return False


def save_to_vectordb(text: str, timestamp: str, doc_id: Optional[str] = None) -> bool:
    """Metni vektör veritabanına kaydeder.
    
    Metadata'da hem timestamp hem date saklanır (filtreleme için).
    """
    try:
        collection = get_collection()
        
        # Embedding oluştur
        embed_response = ollama.embeddings(model=MODEL_EMBED, prompt=text)
        
        # Benzersiz ID
        if doc_id is None:
            doc_id = generate_unique_id()
        
        # Tarih ve saat ayrıştır
        date_str, time_str = parse_timestamp(timestamp)
        
        collection.add(
            documents=[text],
            embeddings=[embed_response["embedding"]],
            metadatas=[{
                "timestamp": timestamp,
                "date": date_str,      # Filtreleme için
                "time": time_str       # Sıralama için
            }],
            ids=[doc_id]
        )
        return True
    except Exception as e:
        logger.error(f"VectorDB kayıt hatası: {e}")
        return False


def save_memory(analysis: str, timestamp: Optional[str] = None) -> bool:
    """Hem JSONL hem de VectorDB'ye kaydeder."""
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    entry = {"timestamp": timestamp, "summary": analysis}
    
    jsonl_ok = save_to_jsonl(entry)
    vector_ok = save_to_vectordb(analysis, timestamp)
    
    return jsonl_ok and vector_ok


def extract_content(text: str) -> str:
    """Etiketleri temizleyerek içeriği çıkarır."""
    # Son [...] kısmını kaldır
    if "[" in text:
        return text.split("[")[0].strip()
    return text.strip()


def get_logs_by_date(target_date: str) -> list[dict]:
    """Belirli bir tarihe ait logları getirir.
    
    ChromaDB where filtresi ile optimize edilmiş sorgu.
    
    Args:
        target_date: "YYYY-MM-DD" formatında tarih
    
    Returns:
        [{"time": "HH:MM", "content": "..."}, ...]
    """
    try:
        collection = get_collection()
        
        # Önce where filtresi ile dene (yeni kayıtlar için)
        results = collection.get(
            where={"date": target_date},
            include=["documents", "metadatas"]
        )
        
        logs = []
        
        # Yeni format (date field var)
        if results['metadatas']:
            for i, meta in enumerate(results['metadatas']):
                time_str = meta.get('time', meta['timestamp'].split("T")[1][:5])
                content = extract_content(results['documents'][i])
                logs.append({"time": time_str, "content": content})
        
        # Eski format için fallback (date field yok)
        if not logs:
            all_results = collection.get(include=["documents", "metadatas"])
            for i, meta in enumerate(all_results['metadatas']):
                if meta['timestamp'].startswith(target_date):
                    time_str = meta['timestamp'].split("T")[1][:5]
                    content = extract_content(all_results['documents'][i])
                    logs.append({"time": time_str, "content": content})
        
        # Saate göre sırala
        logs.sort(key=lambda x: x["time"])
        return logs
        
    except Exception as e:
        logger.error(f"Log çekme hatası: {e}")
        return []


def get_logs_last_n_days(days: int = 7, limit: int = 100) -> list[dict]:
    """Son N günün loglarını getirir.
    
    ChromaDB $in operatörü ile optimize edilmiş sorgu.
    
    Args:
        days: Kaç gün geriye gidilsin
        limit: Maksimum kayıt sayısı
    
    Returns:
        [{"date": "YYYY-MM-DD", "time": "HH:MM", "content": "..."}, ...]
    """
    try:
        collection = get_collection()
        
        # Geçerli tarihleri hesapla
        valid_dates = [
            (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(days + 1)
        ]
        
        # Önce where filtresi ile dene (yeni kayıtlar için)
        results = collection.get(
            where={"date": {"$in": valid_dates}},
            include=["documents", "metadatas"]
        )
        
        logs = []
        
        # Yeni format
        if results['metadatas']:
            for i, meta in enumerate(results['metadatas']):
                date_str = meta.get('date', meta['timestamp'].split("T")[0])
                time_str = meta.get('time', meta['timestamp'].split("T")[1][:5])
                content = extract_content(results['documents'][i])
                logs.append({
                    "date": date_str,
                    "time": time_str,
                    "content": content
                })
        
        # Eski format için fallback
        if not logs:
            all_results = collection.get(include=["documents", "metadatas"])
            valid_set = set(valid_dates)
            
            for i, meta in enumerate(all_results['metadatas']):
                ts_day = meta['timestamp'].split("T")[0]
                if ts_day in valid_set:
                    time_str = meta['timestamp'].split("T")[1][:5]
                    content = extract_content(all_results['documents'][i])
                    logs.append({
                        "date": ts_day,
                        "time": time_str,
                        "content": content
                    })
        
        # Tarihe göre sırala ve limitle
        logs.sort(key=lambda x: (x["date"], x["time"]))
        return logs[-limit:]
        
    except Exception as e:
        logger.error(f"Log çekme hatası: {e}")
        return []


def semantic_search(query: str, n_results: int = 10) -> list[dict]:
    """Semantik arama yapar.
    
    Args:
        query: Arama sorgusu
        n_results: Kaç sonuç dönsün
    
    Returns:
        [{"time": "HH:MM", "content": "...", "date": "YYYY-MM-DD"}, ...]
    """
    try:
        collection = get_collection()
        
        # Query embedding
        embed_response = ollama.embeddings(model=MODEL_EMBED, prompt=query)
        
        results = collection.query(
            query_embeddings=[embed_response["embedding"]],
            n_results=n_results
        )
        
        logs = []
        if results['documents'] and results['metadatas']:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                date_str, time_str = parse_timestamp(meta['timestamp'])
                logs.append({
                    "date": date_str,
                    "time": time_str,
                    "content": doc
                })
        
        return logs
        
    except Exception as e:
        logger.error(f"Semantik arama hatası: {e}")
        return []


def migrate_old_records() -> int:
    """Eski kayıtlara date/time metadata ekler.
    
    Returns:
        Güncellenen kayıt sayısı
    """
    try:
        collection = get_collection()
        results = collection.get(include=["documents", "metadatas", "embeddings"])
        
        if not results['ids']:
            logger.info("Migrate edilecek kayıt yok")
            return 0
        
        migrated = 0
        
        for i, meta in enumerate(results['metadatas']):
            # Zaten date field varsa atla
            if 'date' in meta:
                continue
            
            # Tarih ve saat çıkar
            date_str, time_str = parse_timestamp(meta['timestamp'])
            
            # Yeni metadata
            new_meta = {
                "timestamp": meta['timestamp'],
                "date": date_str,
                "time": time_str
            }
            
            # Güncelle (ChromaDB'de update = delete + add)
            doc_id = results['ids'][i]
            document = results['documents'][i]
            embedding = results['embeddings'][i]
            
            collection.delete(ids=[doc_id])
            collection.add(
                ids=[doc_id],
                documents=[document],
                embeddings=[embedding],
                metadatas=[new_meta]
            )
            
            migrated += 1
        
        logger.info(f"{migrated} kayıt migrate edildi")
        return migrated
        
    except Exception as e:
        logger.error(f"Migration hatası: {e}")
        return 0


def get_stats() -> dict:
    """Veritabanı istatistiklerini döndürür."""
    try:
        collection = get_collection()
        count = collection.count()
        
        # En eski ve en yeni kayıt
        results = collection.get(include=["metadatas"])
        
        if results['metadatas']:
            timestamps = [m['timestamp'] for m in results['metadatas']]
            timestamps.sort()
            
            return {
                "total_records": count,
                "oldest": timestamps[0] if timestamps else None,
                "newest": timestamps[-1] if timestamps else None,
                "has_date_field": any('date' in m for m in results['metadatas'])
            }
        
        return {"total_records": 0, "oldest": None, "newest": None, "has_date_field": False}
        
    except Exception as e:
        logger.error(f"Stats hatası: {e}")
        return {"error": str(e)}
