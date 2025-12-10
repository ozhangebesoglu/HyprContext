//! HyprContext - Ekran Görüntüsü Modülü
//! grim ile screenshot alır.

use anyhow::{Context, Result};
use std::path::Path;
use std::process::Command;
use tracing::{debug, warn};

/// Ekran görüntüsü alır ve dosya yolunu döndürür
pub fn take_screenshot(output_path: &Path) -> Result<()> {
    // Eski dosyayı sil
    if output_path.exists() {
        std::fs::remove_file(output_path).ok();
    }

    let status = Command::new("grim")
        .arg(output_path)
        .status()
        .context("grim çalıştırılamadı. 'sudo pacman -S grim' ile kur.")?;

    if !status.success() {
        anyhow::bail!("grim hata kodu: {}", status);
    }

    if !output_path.exists() {
        anyhow::bail!("Screenshot oluşturulamadı");
    }

    debug!("Screenshot alındı: {:?}", output_path);
    Ok(())
}

/// Screenshot dosyasını temizler
pub fn cleanup_screenshot(path: &Path) {
    if path.exists() {
        if let Err(e) = std::fs::remove_file(path) {
            warn!("Screenshot silinemedi: {}", e);
        }
    }
}

/// Screenshot'ı base64 olarak encode eder
pub fn read_as_base64(path: &Path) -> Result<String> {
    use base64::Engine;
    
    let bytes = std::fs::read(path)
        .context("Screenshot dosyası okunamadı")?;
    
    Ok(base64::engine::general_purpose::STANDARD.encode(&bytes))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    #[ignore] // CI'da grim olmayabilir
    fn test_take_screenshot() {
        let path = PathBuf::from("/tmp/test_screenshot.png");
        let result = take_screenshot(&path);
        // Hyprland yoksa hata verir, normal
        if result.is_ok() {
            assert!(path.exists());
            cleanup_screenshot(&path);
        }
    }
}






