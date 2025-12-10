"""
HyprContext Windows - Veritabanı Modülü
SQLite ile aktivite kayıtlarını yönetir.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from loguru import logger


@dataclass
class MemoryRecord:
    """Aktivite kaydı"""
    id: int
    timestamp: datetime
    summary: str
    tags: str
    
    def __str__(self) -> str:
        return f"[{self.timestamp.strftime('%H:%M')}] {self.summary}"


class Database:
    """SQLite veritabanı yöneticisi"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(
            str(db_path),
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        logger.info(f"Veritabanı hazır: {db_path}")
    
    def _init_tables(self):
        """Tabloları oluştur"""
        cursor = self.conn.cursor()
        
        # Ana aktivite tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                summary TEXT NOT NULL,
                tags TEXT DEFAULT ''
            )
        """)
        
        # Kısa süreli bellek tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS short_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # İndeksler
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activities_timestamp 
            ON activities(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activities_tags 
            ON activities(tags)
        """)
        
        self.conn.commit()
    
    def save(self, summary: str, tags: str = "") -> int:
        """Yeni aktivite kaydet"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO activities (summary, tags) VALUES (?, ?)",
            (summary, tags)
        )
        self.conn.commit()
        
        record_id = cursor.lastrowid
        logger.debug(f"Aktivite kaydedildi (ID: {record_id})")
        return record_id
    
    def get_recent(self, limit: int = 10) -> List[MemoryRecord]:
        """Son aktiviteleri getir"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, timestamp, summary, tags 
            FROM activities 
            ORDER BY timestamp DESC 
            LIMIT ?
            """,
            (limit,)
        )
        
        return [
            MemoryRecord(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]) if isinstance(row["timestamp"], str) else row["timestamp"],
                summary=row["summary"],
                tags=row["tags"]
            )
            for row in cursor.fetchall()
        ]
    
    def get_by_date(self, date_str: str) -> List[MemoryRecord]:
        """Belirli bir tarihin aktivitelerini getir (YYYY-MM-DD)"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, timestamp, summary, tags 
            FROM activities 
            WHERE date(timestamp) = date(?)
            ORDER BY timestamp DESC
            """,
            (date_str,)
        )
        
        return [
            MemoryRecord(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]) if isinstance(row["timestamp"], str) else row["timestamp"],
                summary=row["summary"],
                tags=row["tags"]
            )
            for row in cursor.fetchall()
        ]
    
    def get_today(self) -> List[MemoryRecord]:
        """Bugünün aktivitelerini getir"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_by_date(today)
    
    def get_last_n_days(self, days: int) -> List[MemoryRecord]:
        """Son N günün aktivitelerini getir"""
        cursor = self.conn.cursor()
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        cursor.execute(
            """
            SELECT id, timestamp, summary, tags 
            FROM activities 
            WHERE date(timestamp) >= date(?)
            ORDER BY timestamp DESC
            """,
            (start_date,)
        )
        
        return [
            MemoryRecord(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]) if isinstance(row["timestamp"], str) else row["timestamp"],
                summary=row["summary"],
                tags=row["tags"]
            )
            for row in cursor.fetchall()
        ]
    
    def search(self, query: str, limit: int = 50) -> List[MemoryRecord]:
        """Aktivitelerde arama yap"""
        cursor = self.conn.cursor()
        search_pattern = f"%{query}%"
        
        cursor.execute(
            """
            SELECT id, timestamp, summary, tags 
            FROM activities 
            WHERE summary LIKE ? OR tags LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (search_pattern, search_pattern, limit)
        )
        
        return [
            MemoryRecord(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]) if isinstance(row["timestamp"], str) else row["timestamp"],
                summary=row["summary"],
                tags=row["tags"]
            )
            for row in cursor.fetchall()
        ]
    
    def get_stats(self) -> dict:
        """Veritabanı istatistikleri"""
        cursor = self.conn.cursor()
        
        # Toplam kayıt
        cursor.execute("SELECT COUNT(*) FROM activities")
        total = cursor.fetchone()[0]
        
        # Bugünkü kayıt
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT COUNT(*) FROM activities WHERE date(timestamp) = date(?)",
            (today,)
        )
        today_count = cursor.fetchone()[0]
        
        # Son 7 gün
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT COUNT(*) FROM activities WHERE date(timestamp) >= date(?)",
            (week_ago,)
        )
        week_count = cursor.fetchone()[0]
        
        # En sık kullanılan etiketler
        cursor.execute("""
            SELECT tags, COUNT(*) as count 
            FROM activities 
            WHERE tags != ''
            GROUP BY tags 
            ORDER BY count DESC 
            LIMIT 10
        """)
        top_tags = [(row["tags"], row["count"]) for row in cursor.fetchall()]
        
        return {
            "total": total,
            "today": today_count,
            "week": week_count,
            "top_tags": top_tags
        }
    
    # Kısa süreli bellek metodları
    def add_to_short_term_memory(self, content: str) -> None:
        """Kısa süreli belleğe ekle"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO short_term_memory (content) VALUES (?)",
            (content,)
        )
        self.conn.commit()
    
    def get_short_term_memory(self, limit: int = 5) -> str:
        """Kısa süreli belleği al"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT content 
            FROM short_term_memory 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            (limit,)
        )
        
        memories = [row["content"] for row in cursor.fetchall()]
        
        if not memories:
            return "Yeni oturum"
        
        # Ters çevir (eski → yeni)
        memories.reverse()
        return " → ".join(memories)
    
    def clear_short_term_memory(self) -> None:
        """Kısa süreli belleği temizle"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM short_term_memory")
        self.conn.commit()
    
    def cleanup_old_memory(self, keep_count: int = 10) -> None:
        """Eski kısa süreli bellek kayıtlarını temizle"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            DELETE FROM short_term_memory 
            WHERE id NOT IN (
                SELECT id FROM short_term_memory 
                ORDER BY created_at DESC 
                LIMIT ?
            )
            """,
            (keep_count,)
        )
        self.conn.commit()
    
    def cleanup_old_activities(self, days: int) -> int:
        """Eski aktiviteleri temizle"""
        cursor = self.conn.cursor()
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        cursor.execute(
            "DELETE FROM activities WHERE date(timestamp) < date(?)",
            (cutoff,)
        )
        deleted = cursor.rowcount
        self.conn.commit()
        
        if deleted > 0:
            logger.info(f"{deleted} eski aktivite silindi")
        
        return deleted
    
    def close(self):
        """Bağlantıyı kapat"""
        self.conn.close()


# Singleton instance
_db: Optional[Database] = None


def get_database(db_path: Path) -> Database:
    """Singleton database instance döndür"""
    global _db
    if _db is None:
        _db = Database(db_path)
    return _db


if __name__ == "__main__":
    # Test
    from pathlib import Path
    
    test_db = Path("test_hyprcontext.db")
    
    print("=== Veritabanı Testi ===")
    
    db = Database(test_db)
    
    # Kaydet
    db.save("VS Code'da Python projesi üzerinde çalışıyor.", "Python, VS Code, Geliştirme")
    db.save("Chrome'da GitHub'a göz atıyor.", "Chrome, GitHub, Araştırma")
    db.save("Terminal'de pip install çalıştırıyor.", "Terminal, Python, Kurulum")
    
    print("\n✓ 3 test kaydı eklendi")
    
    # Son kayıtlar
    print("\n📋 Son kayıtlar:")
    for record in db.get_recent(3):
        print(f"  [{record.timestamp.strftime('%H:%M')}] {record.summary}")
    
    # İstatistikler
    print("\n📊 İstatistikler:")
    stats = db.get_stats()
    print(f"  Toplam: {stats['total']}")
    print(f"  Bugün: {stats['today']}")
    
    # Kısa süreli bellek
    db.add_to_short_term_memory("Python geliştirme")
    db.add_to_short_term_memory("GitHub araştırma")
    print(f"\n🧠 Kısa süreli bellek: {db.get_short_term_memory()}")
    
    # Temizle
    db.close()
    test_db.unlink()
    print("\n✓ Test tamamlandı!")



