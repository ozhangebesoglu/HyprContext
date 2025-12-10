//! HyprContext - Veritabanı Modülü
//! SQLite ile kayıt saklama.

use anyhow::{Context, Result};
use chrono::{DateTime, Local, NaiveDate};
use rusqlite::{params, Connection};
use std::path::Path;
use tracing::{debug, info};

/// Veritabanı yapısı
pub struct Database {
    conn: Connection,
}

/// Hafıza kaydı
#[derive(Debug, Clone)]
pub struct MemoryRecord {
    pub id: i64,
    pub timestamp: DateTime<Local>,
    pub summary: String,
    pub tags: String,
}

impl Database {
    /// Yeni veritabanı bağlantısı oluşturur
    pub fn new(path: &Path) -> Result<Self> {
        let conn = Connection::open(path)
            .context("Veritabanı açılamadı")?;
        
        // Tabloyu oluştur
        conn.execute(
            "CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                summary TEXT NOT NULL,
                tags TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )",
            [],
        )?;

        // Index oluştur
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_date ON memories(date)",
            [],
        )?;

        info!("Veritabanı hazır: {:?}", path);
        Ok(Self { conn })
    }

    /// Yeni kayıt ekler
    pub fn save(&self, summary: &str, tags: &str) -> Result<i64> {
        let now = Local::now();
        let date = now.format("%Y-%m-%d").to_string();
        let time = now.format("%H:%M").to_string();
        let timestamp = now.to_rfc3339();

        self.conn.execute(
            "INSERT INTO memories (timestamp, date, time, summary, tags) VALUES (?1, ?2, ?3, ?4, ?5)",
            params![timestamp, date, time, summary, tags],
        )?;

        let id = self.conn.last_insert_rowid();
        debug!("Kayıt eklendi: id={}, tags={}", id, tags);
        Ok(id)
    }

    /// Belirli bir tarihin kayıtlarını getirir
    pub fn get_by_date(&self, date: &str) -> Result<Vec<MemoryRecord>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, timestamp, summary, tags FROM memories 
             WHERE date = ?1 ORDER BY time ASC"
        )?;

        let records = stmt.query_map([date], |row| {
            Ok(MemoryRecord {
                id: row.get(0)?,
                timestamp: DateTime::parse_from_rfc3339(&row.get::<_, String>(1)?)
                    .map(|dt| dt.with_timezone(&Local))
                    .unwrap_or_else(|_| Local::now()),
                summary: row.get(2)?,
                tags: row.get(3)?,
            })
        })?
        .filter_map(|r| r.ok())
        .collect();

        Ok(records)
    }

    /// Son N günün kayıtlarını getirir
    pub fn get_last_n_days(&self, days: u32) -> Result<Vec<MemoryRecord>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, timestamp, summary, tags FROM memories 
             WHERE date >= date('now', ?1) 
             ORDER BY date DESC, time DESC"
        )?;

        let offset = format!("-{} days", days);
        let records = stmt.query_map([offset], |row| {
            Ok(MemoryRecord {
                id: row.get(0)?,
                timestamp: DateTime::parse_from_rfc3339(&row.get::<_, String>(1)?)
                    .map(|dt| dt.with_timezone(&Local))
                    .unwrap_or_else(|_| Local::now()),
                summary: row.get(2)?,
                tags: row.get(3)?,
            })
        })?
        .filter_map(|r| r.ok())
        .collect();

        Ok(records)
    }

    /// Son N kaydı getirir
    pub fn get_recent(&self, limit: u32) -> Result<Vec<MemoryRecord>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, timestamp, summary, tags FROM memories 
             ORDER BY id DESC LIMIT ?1"
        )?;

        let records = stmt.query_map([limit], |row| {
            Ok(MemoryRecord {
                id: row.get(0)?,
                timestamp: DateTime::parse_from_rfc3339(&row.get::<_, String>(1)?)
                    .map(|dt| dt.with_timezone(&Local))
                    .unwrap_or_else(|_| Local::now()),
                summary: row.get(2)?,
                tags: row.get(3)?,
            })
        })?
        .filter_map(|r| r.ok())
        .collect();

        Ok(records)
    }

    /// Toplam kayıt sayısını döndürür
    pub fn count(&self) -> Result<u64> {
        let count: u64 = self.conn.query_row(
            "SELECT COUNT(*) FROM memories",
            [],
            |row| row.get(0),
        )?;
        Ok(count)
    }

    /// İstatistikleri döndürür
    pub fn stats(&self) -> Result<DatabaseStats> {
        let total = self.count()?;
        
        let oldest: Option<String> = self.conn.query_row(
            "SELECT MIN(date) FROM memories",
            [],
            |row| row.get(0),
        ).ok();

        let newest: Option<String> = self.conn.query_row(
            "SELECT MAX(date) FROM memories",
            [],
            |row| row.get(0),
        ).ok();

        Ok(DatabaseStats {
            total_records: total,
            oldest_date: oldest,
            newest_date: newest,
        })
    }
}

#[derive(Debug)]
pub struct DatabaseStats {
    pub total_records: u64,
    pub oldest_date: Option<String>,
    pub newest_date: Option<String>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_database_operations() {
        let path = PathBuf::from(":memory:");
        let db = Database::new(&path).unwrap();
        
        // Kayıt ekle
        let id = db.save("Test özet", "Test, Etiket").unwrap();
        assert!(id > 0);
        
        // Sayı kontrol
        assert_eq!(db.count().unwrap(), 1);
        
        // Son kayıtları al
        let records = db.get_recent(10).unwrap();
        assert_eq!(records.len(), 1);
        assert_eq!(records[0].summary, "Test özet");
    }
}






