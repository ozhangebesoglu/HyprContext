// HyprContext - Ollama API Client
package ollama

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// Client - Ollama HTTP client
type Client struct {
	baseURL    string
	httpClient *http.Client
}

// ChatRequest - Ollama chat isteği
type ChatRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
	Stream   bool      `json:"stream"`
	Options  *Options  `json:"options,omitempty"`
}

// Message - Chat mesajı
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// Options - Model options
type Options struct {
	Temperature   float64 `json:"temperature,omitempty"`
	NumPredict    int     `json:"num_predict,omitempty"`
	RepeatPenalty float64 `json:"repeat_penalty,omitempty"`
}

// ChatResponse - Ollama chat yanıtı
type ChatResponse struct {
	Model   string  `json:"model"`
	Message Message `json:"message"`
	Done    bool    `json:"done"`
}

// New - Yeni Ollama client oluşturur
func New(baseURL string) *Client {
	return &Client{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 120 * time.Second, // AI yanıtları uzun sürebilir
		},
	}
}

// Chat - Chat completion isteği gönderir
func (c *Client) Chat(model string, messages []Message, options *Options) (string, error) {
	req := ChatRequest{
		Model:    model,
		Messages: messages,
		Stream:   false,
		Options:  options,
	}

	body, err := json.Marshal(req)
	if err != nil {
		return "", fmt.Errorf("JSON marshal hatası: %w", err)
	}

	resp, err := c.httpClient.Post(
		c.baseURL+"/api/chat",
		"application/json",
		bytes.NewReader(body),
	)
	if err != nil {
		return "", fmt.Errorf("HTTP isteği hatası: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("Ollama hatası: %s - %s", resp.Status, string(bodyBytes))
	}

	var chatResp ChatResponse
	if err := json.NewDecoder(resp.Body).Decode(&chatResp); err != nil {
		return "", fmt.Errorf("JSON decode hatası: %w", err)
	}

	return chatResp.Message.Content, nil
}

// GeneratePlan - Günlük plan oluşturur
func (c *Client) GeneratePlan(model string, profile string, history string, note string) (string, error) {
	systemPrompt := `Sen bir günlük planlama asistanısın.
Sadece verilen şablonu doldur, ekstra açıklama yapma.
Dil: Türkçe.

` + profile

	userPrompt := fmt.Sprintf(`Bugünün planını oluştur.

VERİLER:
- Not: %s
- Geçmiş Aktiviteler:
%s

ŞABLON:
# 🎯 Günün Misyonu: [Tek cümle hedef]

## 🌅 Sabah (09:00 - 12:00)
* [Saat]: [Görev]

## ☀️ Öğle (13:00 - 17:00)
* [Saat]: [Görev]

## 🌙 Akşam (18:00 - 22:00)
* [Saat]: [Görev]

## ⚠️ Asistan Notu
[Kısa motivasyon notu]`, note, history)

	messages := []Message{
		{Role: "system", Content: systemPrompt},
		{Role: "user", Content: userPrompt},
	}

	options := &Options{
		Temperature:   0.1,
		RepeatPenalty: 1.2,
		NumPredict:    1024,
	}

	return c.Chat(model, messages, options)
}

// GenerateReport - Günlük rapor oluşturur
func (c *Client) GenerateReport(model string, date string, logs string) (string, error) {
	systemPrompt := `Sen bir veri analistisin.
Logları analiz et ve Markdown rapor oluştur.
Yorum yapma, sohbet etme. Sadece raporu yaz.
Dil: Türkçe.`

	userPrompt := fmt.Sprintf(`LOGLAR:
%s

ŞABLON:
# 📅 Günlük Rapor: %s

## 🎯 Günün Özeti
(Ana odak noktası, hangi projeler üzerinde çalışıldı. 2-3 cümle.)

## 🛠️ Kullanılan Teknolojiler
(Tespit edilen araçlar, diller, kütüphaneler. Liste halinde.)

## ⏱️ Zaman Çizelgesi
(Günü bloklara böl. Sabah, öğle, akşam ne yapıldı.)

## 💡 Verimlilik Notları
(Odaklanma seviyesi, çoklu görev durumu.)`, logs, date)

	messages := []Message{
		{Role: "system", Content: systemPrompt},
		{Role: "user", Content: userPrompt},
	}

	options := &Options{
		Temperature: 0.2,
		NumPredict:  2048,
	}

	return c.Chat(model, messages, options)
}

// AskMemory - Hafıza sorgusu yapar
func (c *Client) AskMemory(model string, question string, context string) (string, error) {
	prompt := fmt.Sprintf(`Sen kişisel bir asistansın.
Kullanıcının geçmiş aktivitelerine erişimin var.

GEÇMİŞ KAYITLAR:
%s

SORU: %s

Sadece kayıtlara dayanarak Türkçe ve samimi cevap ver.`, context, question)

	messages := []Message{
		{Role: "user", Content: prompt},
	}

	return c.Chat(model, messages, nil)
}






