//! HyprContext - Konfigürasyon Modülü
//! .env dosyasından ayarları okur.

use anyhow::Result;
use serde::Deserialize;
use std::path::PathBuf;

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    /// Ekran görüntüsü aralığı (saniye)
    #[serde(default = "default_capture_interval")]
    pub capture_interval: u64,

    /// Minimum bekleme süresi (saniye)
    #[serde(default = "default_min_cooldown")]
    pub min_cooldown: u64,

    /// Ollama vision modeli
    #[serde(default = "default_model_vision")]
    pub model_vision: String,

    /// Yasaklı kelimeler (virgülle ayrılmış)
    #[serde(default = "default_banned_keywords")]
    pub banned_keywords: Vec<String>,

    /// Dikkat dağıtma eşiği
    #[serde(default = "default_distraction_threshold")]
    pub distraction_threshold: u32,

    /// Günlük dikkat dağıtma limiti (saniye)
    #[serde(default = "default_daily_limit")]
    pub daily_distraction_limit: u64,

    /// Veritabanı yolu
    #[serde(default = "default_db_path")]
    pub db_path: PathBuf,

    /// Geçici dosya yolu
    #[serde(default = "default_temp_path")]
    pub temp_screenshot_path: PathBuf,

    /// Ollama API URL
    #[serde(default = "default_ollama_url")]
    pub ollama_url: String,
}

// Default değerler
fn default_capture_interval() -> u64 { 20 }
fn default_min_cooldown() -> u64 { 5 }
fn default_model_vision() -> String { "gemma3".to_string() }
fn default_distraction_threshold() -> u32 { 3 }
fn default_daily_limit() -> u64 { 7200 } // 2 saat
fn default_db_path() -> PathBuf { PathBuf::from("hyprcontext.db") }
fn default_temp_path() -> PathBuf { PathBuf::from("/tmp/hypr_context_snap.png") }
fn default_ollama_url() -> String { "http://localhost:11434".to_string() }

fn default_banned_keywords() -> Vec<String> {
    vec![
        "youtube".to_string(),
        "instagram".to_string(),
        "twitter".to_string(),
        "reddit".to_string(),
        "netflix".to_string(),
        "tiktok".to_string(),
    ]
}

impl Config {
    /// Konfigürasyonu yükler (.env + environment variables)
    pub fn load() -> Result<Self> {
        // .env dosyasını yükle (varsa)
        dotenvy::dotenv().ok();

        let config = config::Config::builder()
            .add_source(config::Environment::with_prefix("HYPR"))
            .build()?;

        // Deserialize et veya default kullan
        let cfg: Config = config.try_deserialize().unwrap_or_else(|_| Config::default());

        Ok(cfg)
    }

    /// Yasaklı kelime kontrolü
    pub fn is_banned(&self, text: &str) -> bool {
        let text_lower = text.to_lowercase();
        self.banned_keywords.iter().any(|kw| text_lower.contains(kw))
    }
}

impl Default for Config {
    fn default() -> Self {
        Self {
            capture_interval: default_capture_interval(),
            min_cooldown: default_min_cooldown(),
            model_vision: default_model_vision(),
            banned_keywords: default_banned_keywords(),
            distraction_threshold: default_distraction_threshold(),
            daily_distraction_limit: default_daily_limit(),
            db_path: default_db_path(),
            temp_screenshot_path: default_temp_path(),
            ollama_url: default_ollama_url(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_banned() {
        let config = Config::default();
        assert!(config.is_banned("YouTube video izliyorum"));
        assert!(config.is_banned("NETFLIX dizisi"));
        assert!(!config.is_banned("VSCode'da kod yazıyorum"));
    }
}






