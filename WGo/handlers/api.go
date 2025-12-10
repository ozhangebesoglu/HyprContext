// HyprContext - API Handlers
package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"
	"strings"
	"time"

	"hyprcontext-dashboard/db"
	"hyprcontext-dashboard/ollama"
)

// APIHandler - API handler yapısı
type APIHandler struct {
	DB     *db.Database
	Ollama *ollama.Client
	Model  string
}

// Response helper
func jsonResponse(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}

func errorResponse(w http.ResponseWriter, message string, code int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(map[string]string{"error": message})
}

// Stats - Genel istatistikler
func (h *APIHandler) Stats(w http.ResponseWriter, r *http.Request) {
	if h.DB == nil {
		errorResponse(w, "Veritabanı bağlı değil", http.StatusServiceUnavailable)
		return
	}

	stats, err := h.DB.GetStats()
	if err != nil {
		errorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	jsonResponse(w, stats)
}

// Recent - Son kayıtlar
func (h *APIHandler) Recent(w http.ResponseWriter, r *http.Request) {
	if h.DB == nil {
		jsonResponse(w, []interface{}{})
		return
	}

	// Limit parametresi
	limit := 50
	if l := r.URL.Query().Get("limit"); l != "" {
		if parsed, err := strconv.Atoi(l); err == nil && parsed > 0 && parsed <= 500 {
			limit = parsed
		}
	}

	records, err := h.DB.GetRecent(limit)
	if err != nil {
		errorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	jsonResponse(w, records)
}

// ByDate - Belirli tarihin kayıtları
func (h *APIHandler) ByDate(w http.ResponseWriter, r *http.Request) {
	if h.DB == nil {
		jsonResponse(w, []interface{}{})
		return
	}

	date := r.URL.Query().Get("date")
	if date == "" {
		date = time.Now().Format("2006-01-02")
	}

	records, err := h.DB.GetByDate(date)
	if err != nil {
		errorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	jsonResponse(w, records)
}

// HourlyStats - Saatlik istatistikler
func (h *APIHandler) HourlyStats(w http.ResponseWriter, r *http.Request) {
	if h.DB == nil {
		jsonResponse(w, map[string]int{})
		return
	}

	date := r.URL.Query().Get("date")
	if date == "" {
		date = time.Now().Format("2006-01-02")
	}

	stats, err := h.DB.GetHourlyStats(date)
	if err != nil {
		errorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// 0-23 arası tüm saatler için
	fullStats := make(map[string]int)
	for i := 0; i < 24; i++ {
		key := strconv.Itoa(i)
		if count, ok := stats[i]; ok {
			fullStats[key] = count
		} else {
			fullStats[key] = 0
		}
	}

	jsonResponse(w, fullStats)
}

// TagStats - Etiket istatistikleri
func (h *APIHandler) TagStats(w http.ResponseWriter, r *http.Request) {
	if h.DB == nil {
		jsonResponse(w, map[string]int{})
		return
	}

	limit := 20
	if l := r.URL.Query().Get("limit"); l != "" {
		if parsed, err := strconv.Atoi(l); err == nil && parsed > 0 {
			limit = parsed
		}
	}

	stats, err := h.DB.GetTagStats(limit)
	if err != nil {
		errorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	jsonResponse(w, stats)
}

// Search - Arama
func (h *APIHandler) Search(w http.ResponseWriter, r *http.Request) {
	if h.DB == nil {
		jsonResponse(w, []interface{}{})
		return
	}

	query := r.URL.Query().Get("q")
	if query == "" {
		errorResponse(w, "Arama sorgusu gerekli (?q=...)", http.StatusBadRequest)
		return
	}

	limit := 50
	if l := r.URL.Query().Get("limit"); l != "" {
		if parsed, err := strconv.Atoi(l); err == nil && parsed > 0 {
			limit = parsed
		}
	}

	records, err := h.DB.Search(query, limit)
	if err != nil {
		errorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	jsonResponse(w, records)
}

// GeneratePlan - Günlük plan oluştur
func (h *APIHandler) GeneratePlan(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		errorResponse(w, "POST metodu gerekli", http.StatusMethodNotAllowed)
		return
	}

	if h.Ollama == nil {
		errorResponse(w, "Ollama bağlantısı yok", http.StatusServiceUnavailable)
		return
	}

	// Request body
	var req struct {
		Note    string `json:"note"`
		Profile string `json:"profile"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		// Boş body kabul et
		req.Note = ""
		req.Profile = ""
	}

	// Son 7 günün loglarını al
	history := ""
	if h.DB != nil {
		records, _ := h.DB.GetRecent(100)
		var lines []string
		for _, r := range records {
			lines = append(lines, "- ["+r.Date+" "+r.Time+"] "+r.Summary)
		}
		history = strings.Join(lines, "\n")
	}

	// Plan oluştur
	plan, err := h.Ollama.GeneratePlan(h.Model, req.Profile, history, req.Note)
	if err != nil {
		errorResponse(w, "Plan oluşturulamadı: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// Markdown başlığından itibaren al
	if idx := strings.Index(plan, "# 🎯"); idx > 0 {
		plan = plan[idx:]
	}

	jsonResponse(w, map[string]string{
		"plan": plan,
		"date": time.Now().Format("2006-01-02"),
	})
}

// GenerateReport - Günlük rapor oluştur
func (h *APIHandler) GenerateReport(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		errorResponse(w, "POST metodu gerekli", http.StatusMethodNotAllowed)
		return
	}

	if h.Ollama == nil {
		errorResponse(w, "Ollama bağlantısı yok", http.StatusServiceUnavailable)
		return
	}

	// Tarih parametresi
	date := r.URL.Query().Get("date")
	if date == "" {
		date = time.Now().Format("2006-01-02")
	}

	// O günün loglarını al
	if h.DB == nil {
		errorResponse(w, "Veritabanı bağlı değil", http.StatusServiceUnavailable)
		return
	}

	records, err := h.DB.GetByDate(date)
	if err != nil {
		errorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if len(records) == 0 {
		errorResponse(w, "Bu tarih için kayıt bulunamadı", http.StatusNotFound)
		return
	}

	// Logları formatla
	var lines []string
	for _, r := range records {
		lines = append(lines, "- ["+r.Time+"] "+r.Summary)
	}
	logs := strings.Join(lines, "\n")

	// Rapor oluştur
	report, err := h.Ollama.GenerateReport(h.Model, date, logs)
	if err != nil {
		errorResponse(w, "Rapor oluşturulamadı: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// Markdown başlığından itibaren al
	if idx := strings.Index(report, "# 📅"); idx > 0 {
		report = report[idx:]
	}

	jsonResponse(w, map[string]interface{}{
		"report":       report,
		"date":         date,
		"record_count": len(records),
	})
}

// AskMemory - Hafıza sorgusu
func (h *APIHandler) AskMemory(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		errorResponse(w, "POST metodu gerekli", http.StatusMethodNotAllowed)
		return
	}

	if h.Ollama == nil {
		errorResponse(w, "Ollama bağlantısı yok", http.StatusServiceUnavailable)
		return
	}

	var req struct {
		Question string `json:"question"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Question == "" {
		errorResponse(w, "Soru gerekli", http.StatusBadRequest)
		return
	}

	// İlgili kayıtları bul
	context := ""
	if h.DB != nil {
		records, _ := h.DB.Search(req.Question, 20)
		var lines []string
		for _, r := range records {
			lines = append(lines, "- ["+r.Date+" "+r.Time+"] "+r.Summary)
		}
		context = strings.Join(lines, "\n")
	}

	if context == "" {
		context = "Kayıt bulunamadı."
	}

	// AI'ya sor
	answer, err := h.Ollama.AskMemory(h.Model, req.Question, context)
	if err != nil {
		errorResponse(w, "Yanıt oluşturulamadı: "+err.Error(), http.StatusInternalServerError)
		return
	}

	jsonResponse(w, map[string]string{
		"question": req.Question,
		"answer":   answer,
	})
}

// Health - Sağlık kontrolü
func (h *APIHandler) Health(w http.ResponseWriter, r *http.Request) {
	status := map[string]interface{}{
		"status":    "ok",
		"timestamp": time.Now().Format(time.RFC3339),
		"database":  h.DB != nil,
		"ollama":    h.Ollama != nil,
	}

	jsonResponse(w, status)
}






