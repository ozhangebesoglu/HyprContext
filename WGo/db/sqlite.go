// HyprContext - SQLite Veritabanı Modülü
package db

import (
	"database/sql"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

// Database yapısı
type Database struct {
	conn *sql.DB
}

// MemoryRecord - Hafıza kaydı
type MemoryRecord struct {
	ID        int64     `json:"id"`
	Timestamp time.Time `json:"timestamp"`
	Date      string    `json:"date"`
	Time      string    `json:"time"`
	Summary   string    `json:"summary"`
	Tags      string    `json:"tags"`
}

// Stats - İstatistikler
type Stats struct {
	TotalRecords int64  `json:"total_records"`
	TodayRecords int64  `json:"today_records"`
	OldestDate   string `json:"oldest_date"`
	NewestDate   string `json:"newest_date"`
}

// New - Yeni veritabanı bağlantısı
func New(path string) (*Database, error) {
	conn, err := sql.Open("sqlite3", path+"?mode=ro")
	if err != nil {
		return nil, err
	}

	// Bağlantıyı test et
	if err := conn.Ping(); err != nil {
		return nil, err
	}

	return &Database{conn: conn}, nil
}

// Close - Bağlantıyı kapat
func (d *Database) Close() error {
	return d.conn.Close()
}

// GetStats - İstatistikleri getir
func (d *Database) GetStats() (*Stats, error) {
	stats := &Stats{}

	// Toplam kayıt
	err := d.conn.QueryRow("SELECT COUNT(*) FROM memories").Scan(&stats.TotalRecords)
	if err != nil {
		return nil, err
	}

	// Bugünün kayıtları
	today := time.Now().Format("2006-01-02")
	err = d.conn.QueryRow("SELECT COUNT(*) FROM memories WHERE date = ?", today).Scan(&stats.TodayRecords)
	if err != nil {
		stats.TodayRecords = 0
	}

	// En eski tarih
	d.conn.QueryRow("SELECT MIN(date) FROM memories").Scan(&stats.OldestDate)

	// En yeni tarih
	d.conn.QueryRow("SELECT MAX(date) FROM memories").Scan(&stats.NewestDate)

	return stats, nil
}

// GetRecent - Son N kaydı getir
func (d *Database) GetRecent(limit int) ([]MemoryRecord, error) {
	rows, err := d.conn.Query(`
		SELECT id, timestamp, date, time, summary, tags 
		FROM memories 
		ORDER BY id DESC 
		LIMIT ?
	`, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var records []MemoryRecord
	for rows.Next() {
		var r MemoryRecord
		var ts string
		
		if err := rows.Scan(&r.ID, &ts, &r.Date, &r.Time, &r.Summary, &r.Tags); err != nil {
			continue
		}
		
		r.Timestamp, _ = time.Parse(time.RFC3339, ts)
		records = append(records, r)
	}

	return records, nil
}

// GetByDate - Belirli tarihin kayıtlarını getir
func (d *Database) GetByDate(date string) ([]MemoryRecord, error) {
	rows, err := d.conn.Query(`
		SELECT id, timestamp, date, time, summary, tags 
		FROM memories 
		WHERE date = ?
		ORDER BY time ASC
	`, date)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var records []MemoryRecord
	for rows.Next() {
		var r MemoryRecord
		var ts string
		
		if err := rows.Scan(&r.ID, &ts, &r.Date, &r.Time, &r.Summary, &r.Tags); err != nil {
			continue
		}
		
		r.Timestamp, _ = time.Parse(time.RFC3339, ts)
		records = append(records, r)
	}

	return records, nil
}

// GetHourlyStats - Saatlik istatistikler
func (d *Database) GetHourlyStats(date string) (map[int]int, error) {
	rows, err := d.conn.Query(`
		SELECT CAST(substr(time, 1, 2) AS INTEGER) as hour, COUNT(*) as count
		FROM memories 
		WHERE date = ?
		GROUP BY hour
		ORDER BY hour
	`, date)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	stats := make(map[int]int)
	for rows.Next() {
		var hour, count int
		if err := rows.Scan(&hour, &count); err != nil {
			continue
		}
		stats[hour] = count
	}

	return stats, nil
}

// GetTagStats - Etiket istatistikleri
func (d *Database) GetTagStats(limit int) (map[string]int, error) {
	rows, err := d.conn.Query(`
		SELECT tags, COUNT(*) as count
		FROM memories 
		GROUP BY tags
		ORDER BY count DESC
		LIMIT ?
	`, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	stats := make(map[string]int)
	for rows.Next() {
		var tag string
		var count int
		if err := rows.Scan(&tag, &count); err != nil {
			continue
		}
		stats[tag] = count
	}

	return stats, nil
}

// Search - Metin araması
func (d *Database) Search(query string, limit int) ([]MemoryRecord, error) {
	// SQLite LIKE ile basit arama
	searchPattern := "%" + query + "%"
	
	rows, err := d.conn.Query(`
		SELECT id, timestamp, date, time, summary, tags 
		FROM memories 
		WHERE summary LIKE ? OR tags LIKE ?
		ORDER BY id DESC
		LIMIT ?
	`, searchPattern, searchPattern, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var records []MemoryRecord
	for rows.Next() {
		var r MemoryRecord
		var ts string
		
		if err := rows.Scan(&r.ID, &ts, &r.Date, &r.Time, &r.Summary, &r.Tags); err != nil {
			continue
		}
		
		r.Timestamp, _ = time.Parse(time.RFC3339, ts)
		records = append(records, r)
	}

	return records, nil
}

// GetDateRange - Tarih aralığı kayıtları
func (d *Database) GetDateRange(startDate, endDate string) ([]MemoryRecord, error) {
	rows, err := d.conn.Query(`
		SELECT id, timestamp, date, time, summary, tags 
		FROM memories 
		WHERE date >= ? AND date <= ?
		ORDER BY date ASC, time ASC
	`, startDate, endDate)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var records []MemoryRecord
	for rows.Next() {
		var r MemoryRecord
		var ts string
		
		if err := rows.Scan(&r.ID, &ts, &r.Date, &r.Time, &r.Summary, &r.Tags); err != nil {
			continue
		}
		
		r.Timestamp, _ = time.Parse(time.RFC3339, ts)
		records = append(records, r)
	}

	return records, nil
}

