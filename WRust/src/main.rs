//! HyprContext - Rust Core Daemon
//! Kişisel AI Hafıza Ajanı
//!
//! Ekranı analiz eder, aktiviteleri kaydeder, odak takibi yapar.

mod analyzer;
mod capture;
mod config;
mod database;
mod focus;
mod notifier;
mod window;

use anyhow::Result;
use clap::{Parser, Subcommand};
use std::time::{Duration, Instant};
use tokio::signal;
use tokio::time::interval;
use tracing::{error, info, warn, Level};
use tracing_subscriber::FmtSubscriber;

use crate::config::Config;
use crate::database::Database;
use crate::focus::{format_duration, FocusTracker};

/// HyprContext - Kişisel AI Hafıza Ajanı
#[derive(Parser)]
#[command(name = "hyprcontext")]
#[command(about = "Ekranı analiz eden, aktiviteleri kaydeden AI asistanı", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,

    /// Verbose logging
    #[arg(short, long)]
    verbose: bool,
}

#[derive(Subcommand)]
enum Commands {
    /// Ana izleme servisini başlat
    Run,
    
    /// Odak istatistiklerini göster
    Stats,
    
    /// Veritabanı istatistiklerini göster
    DbStats,
    
    /// Son kayıtları listele
    Recent {
        /// Kaç kayıt gösterilsin
        #[arg(short, long, default_value = "10")]
        limit: u32,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // Logging ayarla
    let log_level = if cli.verbose { Level::DEBUG } else { Level::INFO };
    let subscriber = FmtSubscriber::builder()
        .with_max_level(log_level)
        .with_target(false)
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    // Config yükle
    let config = Config::load()?;

    match cli.command {
        Some(Commands::Stats) => show_focus_stats(&config)?,
        Some(Commands::DbStats) => show_db_stats(&config)?,
        Some(Commands::Recent { limit }) => show_recent(&config, limit)?,
        Some(Commands::Run) | None => run_daemon(config).await?,
    }

    Ok(())
}

/// Ana daemon döngüsü
async fn run_daemon(config: Config) -> Result<()> {
    info!("🚀 HyprContext Rust Core başlatıldı");
    info!("📊 Capture interval: {}s", config.capture_interval);
    info!("🔍 Model: {}", config.model_vision);
    info!("🚫 Yasaklı: {:?}", config.banned_keywords);

    // Veritabanı
    let db = Database::new(&config.db_path)?;
    
    // Odak takipçisi
    let focus_file = config.db_path.with_file_name("focus_data.json");
    let mut focus_tracker = FocusTracker::new(&focus_file, config.daily_distraction_limit)?;

    // Dikkat dağıtma sayacı
    let mut distraction_count: u32 = 0;

    // Ana döngü
    let mut ticker = interval(Duration::from_secs(config.capture_interval));

    loop {
        tokio::select! {
            _ = signal::ctrl_c() => {
                info!("👋 Kapatılıyor...");
                focus_tracker.save()?;
                break;
            }
            _ = ticker.tick() => {
                let loop_start = Instant::now();

                // Odak kontrolü (her tick'te)
                if let Ok(Some(keyword)) = window::check_any_distraction(&config.banned_keywords) {
                    // Yasaklı uygulama açık
                    if let Some(warning) = focus_tracker.add_distraction_time(config.capture_interval) {
                        if warning.is_limit {
                            notifier::send_limit_warning(&warning.label)?;
                        } else {
                            let remaining = format_duration(warning.remaining);
                            notifier::send_time_warning(&warning.label, &remaining)?;
                        }
                    }
                    
                    distraction_count += 1;
                    
                    if distraction_count >= config.distraction_threshold {
                        notifier::send_focus_warning(
                            &format!("{} döngüdür '{}' açık. İşine dön!", 
                                     config.distraction_threshold, keyword)
                        )?;
                        distraction_count = 0;
                    }
                    
                    info!("🚨 Dikkat dağıtıcı: {} | Kullanılan: {} | Kalan: {}", 
                          keyword,
                          format_duration(focus_tracker.used_time()),
                          format_duration(focus_tracker.remaining_time()));
                } else {
                    // Normal aktivite - distraction sayacını azalt
                    distraction_count = distraction_count.saturating_sub(1);
                }

                // Screenshot al ve analiz et
                match process_capture(&config, &db).await {
                    Ok(analysis) => {
                        info!("📝 {}", analysis);
                    }
                    Err(e) => {
                        warn!("Capture hatası: {}", e);
                    }
                }

                let elapsed = loop_start.elapsed();
                if elapsed.as_secs() < config.min_cooldown {
                    tokio::time::sleep(Duration::from_secs(config.min_cooldown) - elapsed).await;
                }
            }
        }
    }

    Ok(())
}

/// Tek bir capture döngüsü
async fn process_capture(config: &Config, db: &Database) -> Result<String> {
    // Screenshot al
    capture::take_screenshot(&config.temp_screenshot_path)?;

    // Window bilgileri - aktif + arka plan
    let active_window = window::get_active_window().unwrap_or_else(|_| "Bilinmiyor".to_string());
    let background_info = window::get_all_workspaces_info().unwrap_or_else(|_| "".to_string());

    // Base64'e çevir
    let image_b64 = capture::read_as_base64(&config.temp_screenshot_path)?;

    // AI analiz - zengin bağlam ile
    let analysis = analyzer::analyze_image(
        &config.ollama_url,
        &config.model_vision,
        &image_b64,
        &active_window,
        &background_info,
    )
    .await?;

    // Veritabanına kaydet
    let tags = analyzer::extract_tags(&analysis).join(", ");
    db.save(&analysis, &tags)?;

    // Temizlik
    capture::cleanup_screenshot(&config.temp_screenshot_path);

    Ok(analysis)
}

/// Odak istatistiklerini gösterir
fn show_focus_stats(config: &Config) -> Result<()> {
    let focus_file = config.db_path.with_file_name("focus_data.json");
    let mut tracker = FocusTracker::new(&focus_file, config.daily_distraction_limit)?;
    let stats = tracker.stats();

    println!("\n{}", "=".repeat(40));
    println!("📊 Bugünün Odak İstatistikleri");
    println!("{}", "=".repeat(40));
    println!("📅 Tarih: {}", chrono::Local::now().format("%Y-%m-%d"));
    println!("⏱️  Kullanılan: {}", format_duration(stats.used_seconds));
    println!("⏳ Kalan: {}", format_duration(stats.remaining_seconds));
    println!("📈 Yüzde: {:.1}%", stats.percentage);
    
    if stats.limit_reached {
        println!("🛑 Durum: LİMİT AŞILDI!");
    } else if stats.percentage > 75.0 {
        println!("⚠️  Durum: Kritik seviye!");
    } else if stats.percentage > 50.0 {
        println!("🟡 Durum: Dikkatli ol");
    } else {
        println!("🟢 Durum: İyi gidiyorsun!");
    }
    
    println!("{}\n", "=".repeat(40));
    Ok(())
}

/// Veritabanı istatistiklerini gösterir
fn show_db_stats(config: &Config) -> Result<()> {
    let db = Database::new(&config.db_path)?;
    let stats = db.stats()?;

    println!("\n{}", "=".repeat(40));
    println!("🗄️  Veritabanı İstatistikleri");
    println!("{}", "=".repeat(40));
    println!("📊 Toplam Kayıt: {}", stats.total_records);
    if let Some(oldest) = stats.oldest_date {
        println!("📅 En Eski: {}", oldest);
    }
    if let Some(newest) = stats.newest_date {
        println!("📅 En Yeni: {}", newest);
    }
    println!("{}\n", "=".repeat(40));
    Ok(())
}

/// Son kayıtları listeler
fn show_recent(config: &Config, limit: u32) -> Result<()> {
    let db = Database::new(&config.db_path)?;
    let records = db.get_recent(limit)?;

    println!("\n{}", "=".repeat(60));
    println!("📋 Son {} Kayıt", limit);
    println!("{}", "=".repeat(60));

    if records.is_empty() {
        println!("Henüz kayıt yok.");
    } else {
        for record in records {
            let time = record.timestamp.format("%H:%M:%S");
            let summary = analyzer::extract_summary(&record.summary);
            let summary_short = if summary.len() > 50 {
                format!("{}...", &summary[..50])
            } else {
                summary
            };
            println!("[{}] {} | {}", time, record.tags, summary_short);
        }
    }

    println!("{}\n", "=".repeat(60));
    Ok(())
}

