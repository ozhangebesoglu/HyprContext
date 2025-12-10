//! HyprContext - Hyprland Pencere Yardımcıları
//! hyprctl ile aktif pencere ve workspace bilgilerini toplar.

use anyhow::{Context, Result};
use serde::Deserialize;
use std::process::Command;
use tracing::{debug, warn};

/// Hyprland pencere bilgisi
#[derive(Debug, Deserialize)]
pub struct HyprWindow {
    pub class: String,
    pub title: String,
    #[serde(default)]
    pub workspace: HyprWorkspace,
}

#[derive(Debug, Default, Deserialize)]
pub struct HyprWorkspace {
    #[serde(default)]
    pub id: i32,
}

/// Aktif pencere bilgisini döndürür
pub fn get_active_window() -> Result<String> {
    let output = Command::new("hyprctl")
        .args(["activewindow", "-j"])
        .output()
        .context("hyprctl çalıştırılamadı. Hyprland kurulu mu?")?;

    if !output.status.success() {
        warn!("hyprctl hata kodu: {}", output.status);
        return Ok("Aktif pencere bilgisi alınamadı".to_string());
    }

    let window: HyprWindow = serde_json::from_slice(&output.stdout)
        .context("JSON parse hatası")?;

    debug!("Aktif pencere: {} | {}", window.class, window.title);
    Ok(format!("{} | {}", window.class, window.title))
}

/// Tüm workspace'lerdeki pencereleri döndürür
pub fn get_all_clients() -> Result<Vec<HyprWindow>> {
    let output = Command::new("hyprctl")
        .args(["clients", "-j"])
        .output()
        .context("hyprctl clients çalıştırılamadı")?;

    if !output.status.success() {
        warn!("hyprctl hata kodu: {}", output.status);
        return Ok(vec![]);
    }

    let clients: Vec<HyprWindow> = serde_json::from_slice(&output.stdout)
        .unwrap_or_default();

    Ok(clients)
}

/// Tüm workspace bilgisini formatlanmış string olarak döndürür
pub fn get_all_workspaces_info() -> Result<String> {
    let clients = get_all_clients()?;

    if clients.is_empty() {
        return Ok("Arka plan boş".to_string());
    }

    // Workspace'e göre grupla
    let mut workspace_map: std::collections::HashMap<i32, Vec<String>> = 
        std::collections::HashMap::new();

    for client in clients {
        if client.workspace.id > 0 {
            // UTF-8 safe truncation - char boundary'lere dikkat et
            let title = if client.title.chars().count() > 25 {
                let truncated: String = client.title.chars().take(25).collect();
                format!("{}...", truncated)
            } else {
                client.title.clone()
            };
            
            workspace_map
                .entry(client.workspace.id)
                .or_default()
                .push(format!("{}: {}", client.class, title));
        }
    }

    // Formatla
    let mut lines: Vec<String> = workspace_map
        .iter()
        .map(|(ws, apps)| format!("WS{}: {}", ws, apps.join(" | ")))
        .collect();
    
    lines.sort();
    Ok(lines.join("\n"))
}

/// Herhangi bir pencerede yasaklı içerik var mı kontrol eder
pub fn check_any_distraction(banned_keywords: &[String]) -> Result<Option<String>> {
    // Önce aktif pencereyi kontrol et
    if let Ok(active) = get_active_window() {
        let active_lower = active.to_lowercase();
        for keyword in banned_keywords {
            if active_lower.contains(keyword) {
                return Ok(Some(keyword.clone()));
            }
        }
    }

    // Tüm pencereleri kontrol et
    let clients = get_all_clients()?;
    for client in clients {
        let combined = format!("{} {}", client.class, client.title).to_lowercase();
        for keyword in banned_keywords {
            if combined.contains(keyword) {
                return Ok(Some(keyword.clone()));
            }
        }
    }

    Ok(None)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hyprwindow_deserialize() {
        let json = r#"{"class":"firefox","title":"GitHub","workspace":{"id":1}}"#;
        let window: HyprWindow = serde_json::from_str(json).unwrap();
        assert_eq!(window.class, "firefox");
        assert_eq!(window.workspace.id, 1);
    }
}

