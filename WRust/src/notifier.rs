//! HyprContext - Bildirim Modülü
//! Sistem bildirimleri gönderir.

use anyhow::Result;
use notify_rust::{Notification, Urgency};
use std::process::Command;
use tracing::{debug, warn};

/// Bildirim seviyesi
#[derive(Debug, Clone, Copy)]
pub enum NotifyLevel {
    Normal,
    Warning,
    Critical,
}

impl From<NotifyLevel> for Urgency {
    fn from(level: NotifyLevel) -> Self {
        match level {
            NotifyLevel::Normal => Urgency::Normal,
            NotifyLevel::Warning => Urgency::Normal,
            NotifyLevel::Critical => Urgency::Critical,
        }
    }
}

/// Bildirim gönderir
pub fn send_notification(title: &str, body: &str, level: NotifyLevel) -> Result<()> {
    Notification::new()
        .summary(title)
        .body(body)
        .urgency(level.into())
        .timeout(5000)
        .show()?;

    debug!("Bildirim gönderildi: {}", title);
    Ok(())
}

/// Odak uyarısı gönderir
pub fn send_focus_warning(message: &str) -> Result<()> {
    send_notification("🛑 ODAK UYARISI", message, NotifyLevel::Critical)?;
    
    // Ses çal
    play_sound(SoundType::Critical);
    
    Ok(())
}

/// Süre uyarısı gönderir
pub fn send_time_warning(label: &str, remaining: &str) -> Result<()> {
    let body = format!(
        "Yasaklı uygulamalarda {} geçirdin.\nKalan: {}",
        label, remaining
    );
    
    send_notification("⏰ Süre Uyarısı", &body, NotifyLevel::Warning)?;
    play_sound(SoundType::Warning);
    
    Ok(())
}

/// Limit uyarısı gönderir
pub fn send_limit_warning(label: &str) -> Result<()> {
    let body = format!(
        "Yasaklı uygulamalarda {} geçirdin!\nBugünlük yeter, işine dön!",
        label
    );
    
    send_notification("🛑 GÜNLÜK LİMİT DOLDU!", &body, NotifyLevel::Critical)?;
    play_sound(SoundType::Critical);
    
    // TTS ile sesli uyarı
    speak("Dikkat! Günlük limit doldu. Lütfen işine dön!");
    
    Ok(())
}

/// Ses türü
#[derive(Debug, Clone, Copy)]
pub enum SoundType {
    Warning,
    Critical,
}

/// Sistem sesi çalar
pub fn play_sound(sound_type: SoundType) {
    let sound_file = match sound_type {
        SoundType::Warning => "/usr/share/sounds/freedesktop/stereo/message.oga",
        SoundType::Critical => "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga",
    };

    // Arka planda çal
    if let Err(e) = Command::new("paplay")
        .arg(sound_file)
        .spawn()
    {
        debug!("Ses çalınamadı: {}", e);
    }
}

/// TTS ile konuşma (opsiyonel)
pub fn speak(message: &str) {
    // espeak-ng varsa kullan (daha yaygın)
    let result = Command::new("espeak-ng")
        .args(["-v", "tr", message])
        .spawn();

    if result.is_err() {
        // espeak dene
        let _ = Command::new("espeak")
            .args(["-v", "tr", message])
            .spawn();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[ignore] // CI'da bildirim olmayabilir
    fn test_notification() {
        let result = send_notification("Test", "Test mesajı", NotifyLevel::Normal);
        // Sistem desteği olmayabilir
        assert!(result.is_ok() || result.is_err());
    }
}






