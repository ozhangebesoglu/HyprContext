"""
Activity Repository
~~~~~~~~~~~~~~~~~~~

Aktivite verisi repository implementasyonu.
"""

import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from ..interfaces.repository import IActivityRepository
from ..interfaces.database import IDatabase
from ..interfaces.ai_client import IAIClient
from ..models.activity import Activity

logger = logging.getLogger(__name__)


class ActivityRepository(IActivityRepository):
    """Aktivite repository (JSONL + ChromaDB)."""
    
    def __init__(
        self,
        jsonl_path: str,
        vector_db: IDatabase,
        ai_client: IAIClient
    ):
        """
        Args:
            jsonl_path: JSONL dosya yolu
            vector_db: Vektör veritabanı (ChromaDB)
            ai_client: AI client (embedding için)
        """
        self.jsonl_path = Path(jsonl_path)
        self.vector_db = vector_db
        self.ai_client = ai_client
        
        # JSONL yoksa oluştur
        if not self.jsonl_path.exists():
            self.jsonl_path.touch()
    
    def save(self, activity: Activity) -> str:
        """Aktivite kaydet (JSONL + ChromaDB)."""
        from datetime import datetime
        
        # ID oluştur
        if not activity.id:
            activity.id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # JSONL'e kaydet
        self._save_to_jsonl(activity)
        
        # ChromaDB'ye kaydet (embedding ile)
        self._save_to_vector_db(activity)
        
        return activity.id
    
    def get_by_id(self, activity_id: str) -> Optional[Activity]:
        """ID ile aktivite getir."""
        for activity in self._read_all_jsonl():
            if activity.id == activity_id:
                return activity
        return None
    
    def get_by_date(self, target_date: date) -> list[Activity]:
        """Tarihe göre aktiviteleri getir."""
        target_str = target_date.isoformat()
        return [
            act for act in self._read_all_jsonl()
            if act.get_date() == target_str
        ]
    
    def get_recent(self, limit: int = 50) -> list[Activity]:
        """Son aktiviteleri getir."""
        activities = self._read_all_jsonl()
        return activities[-limit:] if len(activities) > limit else activities
    
    def search(self, query: str, limit: int = 10) -> list[Activity]:
        """Semantik arama yap."""
        try:
            # Sorgu için embedding oluştur
            query_embedding = self.ai_client.embed(query)
            
            # ChromaDB'de ara
            results = self.vector_db.semantic_search(query_embedding, n_results=limit)
            
            # Sonuçları Activity'ye dönüştür
            activities = []
            for result in results:
                metadata = result.get("metadata", {})
                if "timestamp" in metadata:
                    # timestamp string ise datetime'a çevir
                    ts = metadata["timestamp"]
                    if isinstance(ts, str):
                        ts = datetime.fromisoformat(ts)
                    
                    activities.append(Activity(
                        id=metadata.get("id"),
                        timestamp=ts,
                        summary=result.get("document", ""),
                        tags=metadata.get("tags", [])
                    ))
            
            return activities
            
        except Exception as e:
            logger.error(f"Semantik arama hatası: {e}")
            return []
    
    def get_stats(self) -> dict:
        """İstatistikleri getir."""
        from datetime import date as date_type, timedelta
        
        activities = self._read_all_jsonl()
        today = date_type.today()
        
        # Tarihe göre grupla
        date_counts = {}
        tag_counts = {}
        hour_counts = {}  # Bugünün saatlik dağılımı
        daily_counts = {}  # Son 7 günün günlük dağılımı
        today_count = 0
        
        # Son 7 gün için boş sayaçlar oluştur
        day_names = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
        for i in range(7):
            d = today - timedelta(days=6-i)
            day_name = day_names[d.weekday()]
            daily_counts[d.isoformat()] = {"day": day_name, "activities": 0}
        
        for act in activities:
            # Tarih sayısı
            act_date = act.get_date()
            date_counts[act_date] = date_counts.get(act_date, 0) + 1
            
            # Bugünün aktiviteleri
            if act_date == today.isoformat():
                today_count += 1
                # Saatlik dağılım
                hour = act.timestamp.hour
                hour_key = f"{hour:02d}"
                hour_counts[hour_key] = hour_counts.get(hour_key, 0) + 1
            
            # Son 7 gün
            if act_date in daily_counts:
                daily_counts[act_date]["activities"] += 1
            
            # Etiket sayısı
            for tag in act.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            "total_activities": len(activities),
            "total_days": len(date_counts),
            "today_count": today_count,
            "top_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "activities_per_day": sum(date_counts.values()) / max(len(date_counts), 1),
            "by_hour": hour_counts,
            "by_day": list(daily_counts.values())
        }
    
    def _save_to_jsonl(self, activity: Activity) -> None:
        """JSONL'e kaydet."""
        try:
            with open(self.jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(activity.to_dict(), ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"JSONL kaydetme hatası: {e}")
            raise
    
    def _save_to_vector_db(self, activity: Activity) -> None:
        """ChromaDB'ye kaydet."""
        try:
            # Embedding oluştur
            embedding = self.ai_client.embed(activity.summary)
            
            # Kaydet
            self.vector_db.save(
                collection="hypr_logs",
                data={
                    "document": activity.summary,
                    "embedding": embedding,
                    "metadata": {
                        "id": activity.id,
                        "timestamp": activity.timestamp.isoformat(),
                        "tags": ",".join(activity.tags)
                    }
                },
                doc_id=activity.id
            )
        except Exception as e:
            logger.error(f"ChromaDB kaydetme hatası: {e}")
            # Vector DB hatası kritik değil, devam et
    
    def _read_all_jsonl(self) -> list[Activity]:
        """Tüm JSONL kayıtlarını oku."""
        activities = []
        
        if not self.jsonl_path.exists():
            return activities
        
        try:
            with open(self.jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            activities.append(Activity.from_dict(data))
                        except json.JSONDecodeError:
                            logger.warning(f"JSON parse hatası: {line[:50]}...")
        except Exception as e:
            logger.error(f"JSONL okuma hatası: {e}")
        
        return activities
