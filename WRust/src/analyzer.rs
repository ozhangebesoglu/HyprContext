//! HyprContext - Akıllı Analiz Modülü
//! Ekran görüntüsü + pencere bilgilerini birleştirerek bağlamsal analiz yapar.

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tracing::{debug, info};

/// Ollama chat isteği
#[derive(Debug, Serialize)]
struct OllamaRequest {
    model: String,
    messages: Vec<Message>,
    stream: bool,
    options: Options,
}

#[derive(Debug, Serialize)]
struct Message {
    role: String,
    content: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    images: Option<Vec<String>>,
}

#[derive(Debug, Serialize)]
struct Options {
    temperature: f32,
    num_predict: u32,
}

#[derive(Debug, Deserialize)]
struct OllamaResponse {
    message: ResponseMessage,
}

#[derive(Debug, Deserialize)]
struct ResponseMessage {
    content: String,
}

/// Pencere bağlamı - AI'a gönderilecek zengin bilgi
#[derive(Debug, Clone)]
pub struct WindowContext {
    /// Aktif pencere class (cursor, firefox, kitty vb.)
    pub app_class: String,
    /// Aktif pencere başlığı (dosya adı, sayfa başlığı vb.)
    pub window_title: String,
    /// Tespit edilen programlama dili
    pub detected_language: Option<String>,
    /// Tespit edilen proje/dosya adı
    pub detected_file: Option<String>,
    /// Arka plandaki uygulamalar
    pub background_apps: Vec<String>,
    /// Arka planda yasaklı uygulama var mı
    pub has_distraction: bool,
}

impl WindowContext {
    /// Hyprland bilgilerinden WindowContext oluşturur
    pub fn from_hyprland(active_window: &str, background_info: &str) -> Self {
        // Aktif pencereyi parse et: "class | title"
        let parts: Vec<&str> = active_window.splitn(2, " | ").collect();
        let app_class = parts.first().unwrap_or(&"unknown").trim().to_lowercase();
        let window_title = parts.get(1).unwrap_or(&"").trim().to_string();

        // Dosya ve dil tespiti
        let (detected_file, detected_language) = detect_file_and_language(&window_title);

        // Arka plan uygulamalarını parse et
        let background_apps = parse_background_apps(background_info);

        // Yasaklı uygulama kontrolü
        let distractions = ["youtube", "instagram", "twitter", "reddit", "netflix", "tiktok"];
        let all_text = format!("{} {} {}", app_class, window_title, background_info).to_lowercase();
        let has_distraction = distractions.iter().any(|d| all_text.contains(d));

        Self {
            app_class,
            window_title,
            detected_language,
            detected_file,
            background_apps,
            has_distraction,
        }
    }

    /// AI için zengin prompt oluşturur
    pub fn to_prompt(&self) -> String {
        let mut prompt = String::new();

        // Aktif uygulama
        prompt.push_str(&format!("AKTİF UYGULAMA: {}\n", self.app_class));
        prompt.push_str(&format!("PENCERE BAŞLIĞI: {}\n", self.window_title));

        // Dosya/dil bilgisi
        if let Some(ref file) = self.detected_file {
            prompt.push_str(&format!("AÇIK DOSYA: {}\n", file));
        }
        if let Some(ref lang) = self.detected_language {
            prompt.push_str(&format!("PROGRAMLAMA DİLİ: {}\n", lang));
        }

        // Arka plan
        if !self.background_apps.is_empty() {
            prompt.push_str(&format!("ARKA PLAN: {}\n", self.background_apps.join(", ")));
        }

        // Dikkat dağıtıcı uyarısı
        if self.has_distraction {
            prompt.push_str("⚠️ ARKA PLANDA DİKKAT DAĞITICI UYGULAMA VAR\n");
        }

        prompt
    }
}

/// Dosya uzantısından dil tespiti
fn detect_file_and_language(title: &str) -> (Option<String>, Option<String>) {
    // Dosya adını bul (genellikle başlıkta)
    let file_extensions: HashMap<&str, &str> = [
        (".rs", "Rust"),
        (".go", "Go"),
        (".py", "Python"),
        (".js", "JavaScript"),
        (".ts", "TypeScript"),
        (".tsx", "React/TypeScript"),
        (".jsx", "React/JavaScript"),
        (".vue", "Vue.js"),
        (".svelte", "Svelte"),
        (".html", "HTML"),
        (".css", "CSS"),
        (".scss", "SCSS"),
        (".json", "JSON"),
        (".yaml", "YAML"),
        (".yml", "YAML"),
        (".toml", "TOML"),
        (".md", "Markdown"),
        (".sql", "SQL"),
        (".sh", "Shell"),
        (".bash", "Bash"),
        (".zsh", "Zsh"),
        (".c", "C"),
        (".cpp", "C++"),
        (".h", "C/C++ Header"),
        (".java", "Java"),
        (".kt", "Kotlin"),
        (".swift", "Swift"),
        (".rb", "Ruby"),
        (".php", "PHP"),
        (".lua", "Lua"),
        (".zig", "Zig"),
        (".nim", "Nim"),
    ].iter().cloned().collect();

    // Başlıktan dosya adını çıkar
    let mut detected_file = None;
    let mut detected_lang = None;

    // Yaygın kalıpları dene: "dosya.ext - Uygulama", "Uygulama - dosya.ext"
    for part in title.split(&['-', '—', '|', '●'][..]) {
        let part = part.trim();
        for (ext, lang) in &file_extensions {
            if part.ends_with(ext) || part.contains(&format!("{} ", ext)) {
                // Dosya adını bul
                let words: Vec<&str> = part.split_whitespace().collect();
                for word in words {
                    if word.contains('.') && word.ends_with(ext) {
                        detected_file = Some(word.to_string());
                        detected_lang = Some(lang.to_string());
                        break;
                    }
                }
                if detected_file.is_some() {
                    break;
                }
            }
        }
        if detected_file.is_some() {
            break;
        }
    }

    (detected_file, detected_lang)
}

/// Arka plan bilgisinden uygulama listesi çıkar
fn parse_background_apps(info: &str) -> Vec<String> {
    let mut apps = Vec::new();
    
    for line in info.lines() {
        // "WS1: app1: title | app2: title" formatını parse et
        if let Some(colon_idx) = line.find(':') {
            let apps_part = &line[colon_idx + 1..];
            for app in apps_part.split('|') {
                let app = app.trim();
                if let Some(app_colon) = app.find(':') {
                    let app_name = app[..app_colon].trim();
                    if !app_name.is_empty() {
                        apps.push(app_name.to_string());
                    }
                }
            }
        }
    }
    
    // Benzersiz yap
    apps.sort();
    apps.dedup();
    apps
}

/// Sistem prompt'u - Daha akıllı ve bağlamsal
const SYSTEM_PROMPT: &str = r#"Sen akıllı bir aktivite analistisin. Kullanıcının bilgisayar aktivitesini analiz ediyorsun.

GÖREV:
1. Verilen pencere bilgilerini ve ekran görüntüsünü birlikte değerlendir
2. Kullanıcının NE YAPTIĞINI açıkla (sadece "X uygulaması açık" deme)
3. Arka plandaki uygulamaları da değerlendir

YORUM KURALLARI:
- Cursor/VSCode + dosya.go → "Go dili ile X geliştiriyor"
- Cursor/VSCode + dosya.rs → "Rust ile X kodluyor"  
- Cursor/VSCode + dosya.py → "Python ile X yazıyor"
- YouTube + Tutorial başlığı → "YouTube'da X öğreniyor"
- YouTube + Müzik → "Arka planda müzik dinliyor"
- Terminal aktif → "Terminalde komut çalıştırıyor"
- Aktif kod editörü + arka plan YouTube → "Kodlama yaparken arka planda YouTube açık"

FORMAT: Tek cümle açıklama + [Etiket1, Etiket2, Etiket3]
Etiketler: Dil/Teknoloji, Uygulama, Aktivite türü

DİL: Türkçe yaz."#;

/// Kullanıcı prompt şablonu
const USER_PROMPT_TEMPLATE: &str = r#"PENCERE BİLGİLERİ:
{context}

GÖREV:
Ekran görüntüsüne ve yukarıdaki bilgilere bakarak kullanıcının ne yaptığını YORUMLA.

DOĞRU ÖRNEKLER:
✅ "Cursor'da api.go dosyasını düzenliyor, Go ile REST API geliştiriyor. [Go, Cursor, API Geliştirme]"
✅ "VSCode'da React projesi üzerinde çalışıyor, App.tsx dosyasını düzenliyor. [React, TypeScript, Frontend]"
✅ "Terminalde git komutları çalıştırıyor, commit işlemi yapıyor. [Git, Terminal, Versiyon Kontrol]"
✅ "YouTube'da Rust programlama eğitimi izliyor. [Rust, YouTube, Öğrenme]"
✅ "Cursor'da Python kodu yazarken arka planda Spotify müzik çalıyor. [Python, Cursor, Geliştirme]"

YANLIŞ ÖRNEKLER:
❌ "Cursor uygulaması açık." (çok yüzeysel)
❌ "Ekranda terminal var." (yorum yok)
❌ "Bir şeyler yapılıyor." (belirsiz)

ŞİMDİ ANALİZ ET:"#;

/// Ekran görüntüsünü bağlamsal analiz eder
pub async fn analyze_image(
    ollama_url: &str,
    model: &str,
    image_base64: &str,
    active_window: &str,
    background_info: &str,
) -> Result<String> {
    let client = reqwest::Client::new();

    // Zengin bağlam oluştur
    let context = WindowContext::from_hyprland(active_window, background_info);
    let context_prompt = context.to_prompt();

    // Kullanıcı prompt'unu oluştur
    let user_prompt = USER_PROMPT_TEMPLATE.replace("{context}", &context_prompt);

    let request = OllamaRequest {
        model: model.to_string(),
        messages: vec![
            Message {
                role: "system".to_string(),
                content: SYSTEM_PROMPT.to_string(),
                images: None,
            },
            Message {
                role: "user".to_string(),
                content: user_prompt,
                images: Some(vec![image_base64.to_string()]),
            },
        ],
        stream: false,
        options: Options {
            temperature: 0.2, // Biraz daha yaratıcı olabilir
            num_predict: 200, // Daha uzun yanıt için
        },
    };

    let url = format!("{}/api/chat", ollama_url);

    debug!("Bağlam: {:?}", context);
    debug!("Ollama'ya istek gönderiliyor: {}", model);
    let start = std::time::Instant::now();

    let response = client
        .post(&url)
        .json(&request)
        .timeout(std::time::Duration::from_secs(60))
        .send()
        .await
        .context("Ollama'ya bağlanılamadı")?;

    if !response.status().is_success() {
        anyhow::bail!("Ollama hata: {}", response.status());
    }

    let result: OllamaResponse = response
        .json()
        .await
        .context("Ollama yanıtı parse edilemedi")?;

    let elapsed = start.elapsed();
    info!("Analiz tamamlandı ({:.2}s)", elapsed.as_secs_f32());

    // Çıktıyı temizle ve zenginleştir
    let cleaned = clean_and_enrich_output(&result.message.content, &context);
    debug!("Ham: {}", &result.message.content);
    debug!("Temiz: {}", &cleaned);

    Ok(cleaned)
}

/// Model çıktısını temizler ve gerekirse zenginleştirir
fn clean_and_enrich_output(raw: &str, context: &WindowContext) -> String {
    let text = raw.trim();

    // İngilizce giriş cümlelerini temizle
    let patterns = [
        "Okay,", "Okay.", "Here's", "Let's analyze", "Based on", "Looking at",
        "**Analysis:**", "**Output:**", "## Analysis", "## Output", "I can see",
    ];

    let mut result = text.to_string();
    for pattern in patterns {
        if let Some(idx) = result.find(pattern) {
            if idx < 50 {
                result = result[idx + pattern.len()..].trim().to_string();
            }
        }
    }

    // Markdown temizle
    result = result.replace("**", "");
    result = result.replace("##", "");

    // Satır başı tire/yıldız temizle
    let lines: Vec<&str> = result.lines().collect();
    if let Some(first_line) = lines.first() {
        let first = first_line.trim();
        if first.starts_with('-') || first.starts_with('*') || first.starts_with('•') {
            result = first.trim_start_matches(&['-', '*', '•', ' '][..]).to_string();
        }
    }

    // Etiket kontrolü
    if !result.contains('[') || !result.contains(']') {
        let tags = infer_smart_tags(&result, context);
        result = format!("{} [{}]", result.trim(), tags);
    }

    // İlk satırı al (çok uzunsa)
    if let Some(first_line) = result.lines().next() {
        if first_line.contains('[') && first_line.contains(']') {
            result = first_line.to_string();
        }
    }

    result.trim().to_string()
}

/// Akıllı etiket çıkarımı
fn infer_smart_tags(text: &str, context: &WindowContext) -> String {
    let mut tags = Vec::new();

    // 1. Programlama dili (en önemli)
    if let Some(ref lang) = context.detected_language {
        tags.push(lang.clone());
    } else {
        // Metinden dil çıkar
        let text_lower = text.to_lowercase();
        let lang_keywords = [
            ("rust", "Rust"), ("go ", "Go"), ("golang", "Go"),
            ("python", "Python"), ("javascript", "JavaScript"), ("typescript", "TypeScript"),
            ("react", "React"), ("vue", "Vue"), ("svelte", "Svelte"),
        ];
        for (kw, lang) in lang_keywords {
            if text_lower.contains(kw) {
                tags.push(lang.to_string());
                break;
            }
        }
    }

    // 2. Uygulama
    let app_names = [
        ("cursor", "Cursor"), ("vscode", "VSCode"), ("code", "VSCode"),
        ("terminal", "Terminal"), ("kitty", "Terminal"), ("alacritty", "Terminal"),
        ("firefox", "Firefox"), ("chrome", "Chrome"), ("zen", "Zen Browser"),
        ("obsidian", "Obsidian"), ("notion", "Notion"),
        ("youtube", "YouTube"), ("spotify", "Spotify"), ("discord", "Discord"),
    ];
    
    let class_lower = context.app_class.to_lowercase();
    for (kw, name) in app_names {
        if class_lower.contains(kw) {
            tags.push(name.to_string());
            break;
        }
    }

    // 3. Aktivite türü
    let text_lower = text.to_lowercase();
    if text_lower.contains("kodl") || text_lower.contains("yazıyor") || text_lower.contains("geliştir") {
        tags.push("Geliştirme".to_string());
    } else if text_lower.contains("izliyor") || text_lower.contains("video") {
        tags.push("Video".to_string());
    } else if text_lower.contains("öğren") || text_lower.contains("tutorial") {
        tags.push("Öğrenme".to_string());
    } else if text_lower.contains("terminal") || text_lower.contains("komut") {
        tags.push("Sistem".to_string());
    } else if text_lower.contains("api") {
        tags.push("API".to_string());
    }

    // En az 2 etiket olsun
    if tags.is_empty() {
        tags.push("Aktivite".to_string());
    }

    tags.into_iter().take(4).collect::<Vec<_>>().join(", ")
}

/// Özetten etiketleri çıkarır
pub fn extract_summary(text: &str) -> String {
    if let Some(idx) = text.rfind('[') {
        text[..idx].trim().to_string()
    } else {
        text.trim().to_string()
    }
}

/// Özetten etiketleri ayıklar
pub fn extract_tags(text: &str) -> Vec<String> {
    if let Some(start) = text.rfind('[') {
        if let Some(end) = text.rfind(']') {
            if start < end {
                let tags_str = &text[start + 1..end];
                return tags_str
                    .split(',')
                    .map(|s| s.trim().to_string())
                    .filter(|s| !s.is_empty())
                    .collect();
            }
        }
    }
    vec![]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_file_and_language() {
        let (file, lang) = detect_file_and_language("api.go - Cursor");
        assert_eq!(file, Some("api.go".to_string()));
        assert_eq!(lang, Some("Go".to_string()));

        let (file, lang) = detect_file_and_language("main.rs - HyprContext - Cursor");
        assert_eq!(file, Some("main.rs".to_string()));
        assert_eq!(lang, Some("Rust".to_string()));
    }

    #[test]
    fn test_window_context() {
        let ctx = WindowContext::from_hyprland(
            "cursor | api.go - HyprContext - Cursor",
            "WS1: spotify: Music | WS2: firefox: YouTube"
        );
        
        assert_eq!(ctx.app_class, "cursor");
        assert_eq!(ctx.detected_language, Some("Go".to_string()));
        assert!(ctx.has_distraction); // YouTube var
    }
}
