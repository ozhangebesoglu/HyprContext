//! HyprContext - Odak Takipçisi
//! Yasaklı uygulamalarda geçirilen süreyi takip eder.

use anyhow::Result;
use chrono::{Local, NaiveDate};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;
use tracing::{debug, info, warn};

/// Günlük odak verisi
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DailyFocusData {
    pub distraction_seconds: u64,
    pub warnings_sent: Vec<u64>,
    pub limit_reached: bool,
}

impl Default for DailyFocusData {
    fn default() -> Self {
        Self {
            distraction_seconds: 0,
            warnings_sent: vec![],
            limit_reached: false,
        }
    }
}

/// Odak takipçisi
pub struct FocusTracker {
    data: HashMap<String, DailyFocusData>,
    file_path: std::path::PathBuf,
    daily_limit: u64,
    warning_thresholds: Vec<(u64, &'static str)>,
}

impl FocusTracker {
    /// Yeni tracker oluşturur
    pub fn new(file_path: &Path, daily_limit: u64) -> Result<Self> {
        let data = if file_path.exists() {
            let content = std::fs::read_to_string(file_path)?;
            serde_json::from_str(&content).unwrap_or_default()
        } else {
            HashMap::new()
        };

        let warning_thresholds = vec![
            (30 * 60, "30 dakika"),
            (60 * 60, "1 saat"),
            (90 * 60, "1.5 saat"),
            (110 * 60, "1 saat 50 dk"),
            (daily_limit, "LİMİT DOLDU!"),
        ];

        Ok(Self {
            data,
            file_path: file_path.to_path_buf(),
            daily_limit,
            warning_thresholds,
        })
    }

    /// Bugünün anahtarını döndürür
    fn today_key(&self) -> String {
        Local::now().format("%Y-%m-%d").to_string()
    }

    /// Bugünün verisini döndürür
    pub fn today_data(&mut self) -> &mut DailyFocusData {
        let key = self.today_key();
        self.data.entry(key).or_default()
    }

    /// Dikkat dağıtma süresini artırır
    pub fn add_distraction_time(&mut self, seconds: u64) -> Option<FocusWarning> {
        let key = self.today_key();
        let data = self.data.entry(key).or_default();
        
        data.distraction_seconds += seconds;
        let used = data.distraction_seconds;

        // Uyarı kontrolü
        for (threshold, label) in &self.warning_thresholds {
            if used >= *threshold && !data.warnings_sent.contains(threshold) {
                data.warnings_sent.push(*threshold);
                
                let is_limit = *threshold >= self.daily_limit;
                if is_limit {
                    data.limit_reached = true;
                }

                // Kaydet
                self.save().ok();

                return Some(FocusWarning {
                    threshold: *threshold,
                    label: label.to_string(),
                    is_limit,
                    remaining: self.daily_limit.saturating_sub(used),
                });
            }
        }

        // Periyodik kaydet
        if used % 60 == 0 {
            self.save().ok();
        }

        None
    }

    /// Kalan süreyi döndürür
    pub fn remaining_time(&mut self) -> u64 {
        let used = self.today_data().distraction_seconds;
        self.daily_limit.saturating_sub(used)
    }

    /// Kullanılan süreyi döndürür
    pub fn used_time(&mut self) -> u64 {
        self.today_data().distraction_seconds
    }

    /// Limit aşıldı mı?
    pub fn is_limit_reached(&mut self) -> bool {
        self.today_data().limit_reached
    }

    /// Veriyi dosyaya kaydeder
    pub fn save(&self) -> Result<()> {
        let content = serde_json::to_string_pretty(&self.data)?;
        std::fs::write(&self.file_path, content)?;
        debug!("Odak verisi kaydedildi");
        Ok(())
    }

    /// İstatistikleri döndürür
    pub fn stats(&mut self) -> FocusStats {
        let used = self.used_time();
        let remaining = self.remaining_time();
        let percentage = (used as f64 / self.daily_limit as f64) * 100.0;

        FocusStats {
            used_seconds: used,
            remaining_seconds: remaining,
            percentage,
            limit_reached: self.is_limit_reached(),
        }
    }
}

/// Odak uyarısı
#[derive(Debug)]
pub struct FocusWarning {
    pub threshold: u64,
    pub label: String,
    pub is_limit: bool,
    pub remaining: u64,
}

/// Odak istatistikleri
#[derive(Debug)]
pub struct FocusStats {
    pub used_seconds: u64,
    pub remaining_seconds: u64,
    pub percentage: f64,
    pub limit_reached: bool,
}

/// Süreyi okunabilir formata çevirir
pub fn format_duration(seconds: u64) -> String {
    let hours = seconds / 3600;
    let minutes = (seconds % 3600) / 60;
    let secs = seconds % 60;

    if hours > 0 {
        format!("{}s {}dk", hours, minutes)
    } else if minutes > 0 {
        format!("{}dk {}sn", minutes, secs)
    } else {
        format!("{}sn", secs)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_duration() {
        assert_eq!(format_duration(30), "30sn");
        assert_eq!(format_duration(90), "1dk 30sn");
        assert_eq!(format_duration(3661), "1s 1dk");
    }
}






