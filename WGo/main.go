// HyprContext - Go Web Dashboard & API
package main

import (
	"embed"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"hyprcontext-dashboard/db"
	"hyprcontext-dashboard/handlers"
	"hyprcontext-dashboard/ollama"
)

//go:embed templates/*
var templatesFS embed.FS

//go:embed static/*
var staticFS embed.FS

// Config yapısı
type Config struct {
	Port      string
	DBPath    string
	FocusFile string
	OllamaURL string
	Model     string
}

// Template fonksiyonları
var funcMap = template.FuncMap{
	"split": strings.Split,
	"join":  strings.Join,
}

// Her sayfa için template cache
var pageTemplates = make(map[string]*template.Template)

func loadTemplates() error {
	pages := []string{"dashboard", "activities", "analytics", "planner", "chat"}
	
	for _, page := range pages {
		// Her sayfa için base + o sayfa template'ini parse et
		tmpl, err := template.New("").Funcs(funcMap).ParseFS(templatesFS, 
			"templates/base.html", 
			fmt.Sprintf("templates/%s.html", page))
		if err != nil {
			return fmt.Errorf("%s template hatası: %w", page, err)
		}
		pageTemplates[page] = tmpl
	}
	return nil
}

func main() {
	// Config
	cfg := Config{
		Port:      getEnv("PORT", "8080"),
		DBPath:    getEnv("DB_PATH", "../WRust/hyprcontext.db"),
		FocusFile: getEnv("FOCUS_FILE", "../WRust/focus_data.json"),
		OllamaURL: getEnv("OLLAMA_URL", "http://localhost:11434"),
		Model:     getEnv("MODEL", "gemma3"),
	}

	// Template'leri yükle
	if err := loadTemplates(); err != nil {
		log.Fatalf("Template hatası: %v", err)
	}

	// Veritabanı bağlantısı
	database, err := db.New(cfg.DBPath)
	if err != nil {
		log.Printf("⚠️ Veritabanı bağlanamadı: %v", err)
	}

	// Ollama client
	ollamaClient := ollama.New(cfg.OllamaURL)

	// Dashboard handler
	dashHandler := &DashboardHandler{
		db:        database,
		focusFile: cfg.FocusFile,
	}

	// API handler
	apiHandler := &handlers.APIHandler{
		DB:     database,
		Ollama: ollamaClient,
		Model:  cfg.Model,
	}

	// Routes
	mux := http.NewServeMux()

	// Static dosyalar
	mux.Handle("/static/", http.FileServer(http.FS(staticFS)))

	// Dashboard sayfaları
	mux.HandleFunc("/", dashHandler.Dashboard)
	mux.HandleFunc("/activities", dashHandler.Activities)
	mux.HandleFunc("/analytics", dashHandler.Analytics)
	mux.HandleFunc("/planner", dashHandler.Planner)
	mux.HandleFunc("/chat", dashHandler.Chat)

	// API endpoints
	mux.HandleFunc("/api/health", apiHandler.Health)
	mux.HandleFunc("/api/stats", apiHandler.Stats)
	mux.HandleFunc("/api/recent", apiHandler.Recent)
	mux.HandleFunc("/api/by-date", apiHandler.ByDate)
	mux.HandleFunc("/api/hourly", apiHandler.HourlyStats)
	mux.HandleFunc("/api/tags", apiHandler.TagStats)
	mux.HandleFunc("/api/search", apiHandler.Search)
	mux.HandleFunc("/api/focus", dashHandler.APIFocus)
	mux.HandleFunc("/api/plan", apiHandler.GeneratePlan)
	mux.HandleFunc("/api/report", apiHandler.GenerateReport)
	mux.HandleFunc("/api/ask", apiHandler.AskMemory)

	handler := corsMiddleware(mux)

	addr := ":" + cfg.Port
	log.Printf("🚀 HyprContext Dashboard")
	log.Printf("📍 http://localhost%s", addr)
	log.Printf("📊 DB: %s", cfg.DBPath)

	if err := http.ListenAndServe(addr, handler); err != nil {
		log.Fatalf("Server hatası: %v", err)
	}
}

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}
		next.ServeHTTP(w, r)
	})
}

type DashboardHandler struct {
	db        *db.Database
	focusFile string
}

func (h *DashboardHandler) baseData(page string) map[string]interface{} {
	return map[string]interface{}{
		"Page":      page,
		"Timestamp": time.Now().Format("15:04:05"),
		"Today":     time.Now().Format("2006-01-02"),
	}
}

func (h *DashboardHandler) renderPage(w http.ResponseWriter, page string, data map[string]interface{}) {
	tmpl, ok := pageTemplates[page]
	if !ok {
		http.Error(w, "Template bulunamadı", http.StatusInternalServerError)
		return
	}
	if err := tmpl.ExecuteTemplate(w, "base", data); err != nil {
		log.Printf("Template hatası (%s): %v", page, err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func (h *DashboardHandler) Dashboard(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}

	data := h.baseData("dashboard")
	data["Title"] = "Dashboard"

	if h.db != nil {
		stats, _ := h.db.GetStats()
		data["Stats"] = stats
		recent, _ := h.db.GetRecent(15)
		data["Recent"] = recent
	}
	data["Focus"] = h.loadFocusData()

	h.renderPage(w, "dashboard", data)
}

func (h *DashboardHandler) Activities(w http.ResponseWriter, r *http.Request) {
	data := h.baseData("activities")
	data["Title"] = "Aktiviteler"

	date := r.URL.Query().Get("date")
	if date == "" {
		date = time.Now().Format("2006-01-02")
	}

	if h.db != nil {
		stats, _ := h.db.GetStats()
		data["Stats"] = stats

		if r.URL.Query().Get("date") != "" {
			records, _ := h.db.GetByDate(date)
			data["Records"] = records
			data["FilteredCount"] = len(records)
		} else {
			records, _ := h.db.GetRecent(100)
			data["Records"] = records
			data["FilteredCount"] = len(records)
		}

		tags, _ := h.db.GetTagStats(50)
		data["Tags"] = tags
	}

	h.renderPage(w, "activities", data)
}

func (h *DashboardHandler) Analytics(w http.ResponseWriter, r *http.Request) {
	data := h.baseData("analytics")
	data["Title"] = "Analitik"

	date := r.URL.Query().Get("date")
	if date == "" {
		date = time.Now().Format("2006-01-02")
	}

	data["Focus"] = h.loadFocusData()

	if h.db != nil {
		hourlyStats, _ := h.db.GetHourlyStats(date)
		hourlyData := make([]int, 24)
		for i := 0; i < 24; i++ {
			if count, ok := hourlyStats[i]; ok {
				hourlyData[i] = count
			}
		}
		hourlyJSON, _ := json.Marshal(hourlyData)
		data["HourlyData"] = template.JS(hourlyJSON)

		tags, _ := h.db.GetTagStats(8)
		data["Tags"] = tags

		var tagLabels []string
		var tagData []int
		for label, count := range tags {
			parts := strings.Split(label, ",")
			if len(parts) > 0 {
				tagLabels = append(tagLabels, strings.TrimSpace(parts[0]))
			} else {
				tagLabels = append(tagLabels, label)
			}
			tagData = append(tagData, count)
		}

		labelsJSON, _ := json.Marshal(tagLabels)
		dataJSON, _ := json.Marshal(tagData)
		data["TagLabels"] = template.JS(labelsJSON)
		data["TagData"] = template.JS(dataJSON)
	} else {
		data["HourlyData"] = template.JS("[]")
		data["TagLabels"] = template.JS("[]")
		data["TagData"] = template.JS("[]")
		data["Tags"] = map[string]int{}
	}

	h.renderPage(w, "analytics", data)
}

func (h *DashboardHandler) Planner(w http.ResponseWriter, r *http.Request) {
	data := h.baseData("planner")
	data["Title"] = "Planlayıcı"

	if h.db != nil {
		logs, _ := h.db.GetRecent(20)
		data["RecentLogs"] = logs
	}

	h.renderPage(w, "planner", data)
}

func (h *DashboardHandler) Chat(w http.ResponseWriter, r *http.Request) {
	data := h.baseData("chat")
	data["Title"] = "Hafıza Chat"

	h.renderPage(w, "chat", data)
}

func (h *DashboardHandler) APIFocus(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(h.loadFocusData())
}

func (h *DashboardHandler) loadFocusData() map[string]interface{} {
	today := time.Now().Format("2006-01-02")
	defaultData := map[string]interface{}{
		"used_seconds":        int64(0),
		"remaining_seconds":   int64(7200),
		"percentage":          float64(0),
		"limit_reached":       false,
		"formatted_used":      "0sn",
		"formatted_remaining": "2s 0dk",
	}

	data, err := os.ReadFile(h.focusFile)
	if err != nil {
		return defaultData
	}

	var focusData map[string]map[string]interface{}
	if err := json.Unmarshal(data, &focusData); err != nil {
		return defaultData
	}

	todayData, ok := focusData[today]
	if !ok {
		return defaultData
	}

	used := int64(0)
	if v, ok := todayData["distraction_seconds"].(float64); ok {
		used = int64(v)
	}

	limit := int64(7200)
	remaining := limit - used
	if remaining < 0 {
		remaining = 0
	}

	return map[string]interface{}{
		"used_seconds":        used,
		"remaining_seconds":   remaining,
		"percentage":          float64(used) / float64(limit) * 100,
		"limit_reached":       todayData["limit_reached"],
		"formatted_used":      formatDuration(used),
		"formatted_remaining": formatDuration(remaining),
	}
}

func formatDuration(seconds int64) string {
	hours := seconds / 3600
	minutes := (seconds % 3600) / 60
	secs := seconds % 60

	if hours > 0 {
		return fmt.Sprintf("%ds %ddk", hours, minutes)
	} else if minutes > 0 {
		return fmt.Sprintf("%ddk %dsn", minutes, secs)
	}
	return fmt.Sprintf("%dsn", secs)
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
